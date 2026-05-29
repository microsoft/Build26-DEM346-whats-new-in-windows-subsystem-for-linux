"""
GPU-Accelerated N-Body Galaxy Collision Simulation
===================================================
Real-time gravitational N-body simulation using CUDA (via CuPy),
streamed to the browser over binary WebSocket.
"""

import asyncio
import struct
import time
import math

import cupy as cp
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# ---------------------------------------------------------------------------
# CUDA kernel: all-pairs gravitational force with shared-memory tiling
# ---------------------------------------------------------------------------
NBODY_KERNEL = r"""
extern "C" __global__
void nbody_forces(
    const float* __restrict__ px,
    const float* __restrict__ py,
    const float* __restrict__ pz,
    const float* __restrict__ mass,
    float* __restrict__ ax,
    float* __restrict__ ay,
    float* __restrict__ az,
    const int N,
    const float softening_sq
) {
    extern __shared__ float shmem[];
    float* sx = shmem;
    float* sy = sx + blockDim.x;
    float* sz = sy + blockDim.x;
    float* sm = sz + blockDim.x;

    int i = blockIdx.x * blockDim.x + threadIdx.x;
    float xi, yi, zi;
    float fax = 0.0f, fay = 0.0f, faz = 0.0f;

    if (i < N) {
        xi = px[i]; yi = py[i]; zi = pz[i];
    }

    for (int tile = 0; tile < (N + blockDim.x - 1) / blockDim.x; tile++) {
        int j = tile * blockDim.x + threadIdx.x;
        if (j < N) {
            sx[threadIdx.x] = px[j];
            sy[threadIdx.x] = py[j];
            sz[threadIdx.x] = pz[j];
            sm[threadIdx.x] = mass[j];
        } else {
            sx[threadIdx.x] = 0.0f;
            sy[threadIdx.x] = 0.0f;
            sz[threadIdx.x] = 0.0f;
            sm[threadIdx.x] = 0.0f;
        }
        __syncthreads();

        if (i < N) {
            for (int k = 0; k < blockDim.x; k++) {
                float dx = sx[k] - xi;
                float dy = sy[k] - yi;
                float dz = sz[k] - zi;
                float dist_sq = dx*dx + dy*dy + dz*dz + softening_sq;
                float inv_dist = rsqrtf(dist_sq);
                float inv_dist3 = inv_dist * inv_dist * inv_dist;
                float f = sm[k] * inv_dist3;
                fax += f * dx;
                fay += f * dy;
                faz += f * dz;
            }
        }
        __syncthreads();
    }

    if (i < N) {
        ax[i] = fax;
        ay[i] = fay;
        az[i] = faz;
    }
}
"""

# Compile the kernel
nbody_kernel = cp.RawKernel(NBODY_KERNEL, "nbody_forces")

# ---------------------------------------------------------------------------
# Simulation parameters
# ---------------------------------------------------------------------------
G = 1.0
SOFTENING = 0.3
SOFTENING_SQ = cp.float32(SOFTENING * SOFTENING)
DT = 0.005
BLOCK_SIZE = 256

# ---------------------------------------------------------------------------
# Galaxy initialization
# ---------------------------------------------------------------------------
def create_galaxy(n_particles, center, velocity, disk_radius, disk_height,
                  central_mass, tilt_angle, seed):
    """Create a disk galaxy with a massive central body and orbiting particles.

    Particles are sorted by radius so enclosed-mass calculations are correct.
    Circular velocities are Keplerian around the central body for stability.
    """
    rng = np.random.RandomState(seed)

    # Radial distribution: exponential disk profile, sorted by radius
    r = rng.exponential(scale=disk_radius / 3.0, size=n_particles).astype(np.float32)
    r = np.clip(r, SOFTENING, disk_radius * 1.5)
    r.sort()

    # Azimuthal angle — add slight spiral structure
    theta = rng.uniform(0, 2 * np.pi, size=n_particles).astype(np.float32)
    theta += r * 1.5  # spiral arm winding

    # Positions in disk plane (x-y)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = rng.normal(0, disk_height, size=n_particles).astype(np.float32)

    # Equal particle masses; total disk mass is small relative to central body
    disk_mass = central_mass * 0.3
    particle_mass = disk_mass / n_particles
    mass = np.full(n_particles, particle_mass, dtype=np.float32)

    # First particle = central massive body at origin of galaxy
    r[0] = 0.0
    x[0] = 0.0
    y[0] = 0.0
    z[0] = 0.0
    mass[0] = central_mass

    # Circular velocity: Keplerian around the central body
    # v_circ = sqrt(G * M_central / (r + softening))
    # Using softened radius to prevent extreme velocities near center
    v_circ = np.sqrt(G * central_mass / (r + SOFTENING))
    v_circ[0] = 0.0  # central body doesn't orbit

    # Tangential velocity (perpendicular to radius in disk plane)
    vx = -v_circ * np.sin(theta)
    vy = v_circ * np.cos(theta)
    vz = np.zeros(n_particles, dtype=np.float32)

    # Apply tilt rotation (rotate around x-axis by tilt_angle)
    cos_t = np.cos(tilt_angle).astype(np.float32)
    sin_t = np.sin(tilt_angle).astype(np.float32)

    y_rot = y * cos_t - z * sin_t
    z_rot = y * sin_t + z * cos_t
    vy_rot = vy * cos_t - vz * sin_t
    vz_rot = vy * sin_t + vz * cos_t

    y = y_rot
    z = z_rot
    vy = vy_rot
    vz = vz_rot

    # Translate to center and add bulk velocity
    x += center[0]
    y += center[1]
    z += center[2]
    vx += velocity[0]
    vy += velocity[1]
    vz += velocity[2]

    return x, y, z, vx, vy, vz, mass


def init_galaxy_collision(n_total, seed=42):
    """Initialize two galaxies on a collision course."""
    n_per_galaxy = n_total // 2

    # Galaxy 1: left side, moving right
    x1, y1, z1, vx1, vy1, vz1, m1 = create_galaxy(
        n_per_galaxy,
        center=(-3.0, 0.5, 0.0),
        velocity=(0.15, -0.02, 0.0),
        disk_radius=2.0,
        disk_height=0.04,
        central_mass=5.0,
        tilt_angle=0.0,
        seed=seed
    )

    # Galaxy 2: right side, moving left, tilted 45 degrees
    x2, y2, z2, vx2, vy2, vz2, m2 = create_galaxy(
        n_per_galaxy,
        center=(3.0, -0.5, 0.0),
        velocity=(-0.15, 0.02, 0.0),
        disk_radius=1.8,
        disk_height=0.04,
        central_mass=4.0,
        tilt_angle=math.radians(45),
        seed=seed + 1
    )

    # Concatenate
    px = np.concatenate([x1, x2])
    py = np.concatenate([y1, y2])
    pz = np.concatenate([z1, z2])
    vx = np.concatenate([vx1, vx2])
    vy = np.concatenate([vy1, vy2])
    vz = np.concatenate([vz1, vz2])
    mass = np.concatenate([m1, m2])

    return px, py, pz, vx, vy, vz, mass


# ---------------------------------------------------------------------------
# Simulation state
# ---------------------------------------------------------------------------
class Simulation:
    def __init__(self, n_particles=20000):
        self.n = n_particles
        self.step_count = 0
        self.sim_time = 0.0

        # Initialize on CPU, transfer to GPU
        px, py, pz, vx, vy, vz, mass = init_galaxy_collision(n_particles)

        self.px = cp.asarray(px)
        self.py = cp.asarray(py)
        self.pz = cp.asarray(pz)
        self.vx = cp.asarray(vx)
        self.vy = cp.asarray(vy)
        self.vz = cp.asarray(vz)
        self.mass = cp.asarray(mass)

        # Acceleration buffers
        self.ax = cp.zeros(n_particles, dtype=cp.float32)
        self.ay = cp.zeros(n_particles, dtype=cp.float32)
        self.az = cp.zeros(n_particles, dtype=cp.float32)

        # Compute initial accelerations
        self._compute_forces()

    def _compute_forces(self):
        grid = ((self.n + BLOCK_SIZE - 1) // BLOCK_SIZE,)
        block = (BLOCK_SIZE,)
        shared_mem = BLOCK_SIZE * 4 * 4  # 4 arrays × BLOCK_SIZE × sizeof(float)

        nbody_kernel(
            grid, block,
            (self.px, self.py, self.pz, self.mass,
             self.ax, self.ay, self.az,
             np.int32(self.n), SOFTENING_SQ),
            shared_mem=shared_mem
        )

    def step(self):
        """Leapfrog (kick-drift-kick) integration step."""
        dt = cp.float32(DT)
        half_dt = cp.float32(DT * 0.5)

        # Kick (half step)
        self.vx += self.ax * half_dt
        self.vy += self.ay * half_dt
        self.vz += self.az * half_dt

        # Drift (full step)
        self.px += self.vx * dt
        self.py += self.vy * dt
        self.pz += self.vz * dt

        # Compute new forces
        self._compute_forces()

        # Kick (half step)
        self.vx += self.ax * half_dt
        self.vy += self.ay * half_dt
        self.vz += self.az * half_dt

        self.step_count += 1
        self.sim_time += DT

    def get_state_binary(self):
        """Return particle state as a binary buffer: [x, y, z, speed] × N particles."""
        speed = cp.sqrt(self.vx**2 + self.vy**2 + self.vz**2)

        # Interleave into [x0,y0,z0,s0, x1,y1,z1,s1, ...]
        buf = cp.empty(self.n * 4, dtype=cp.float32)
        buf[0::4] = self.px
        buf[1::4] = self.py
        buf[2::4] = self.pz
        buf[3::4] = speed

        return buf.get().tobytes()


# ---------------------------------------------------------------------------
# GPU info
# ---------------------------------------------------------------------------
def get_gpu_info():
    dev = cp.cuda.Device(0)
    props = cp.cuda.runtime.getDeviceProperties(dev.id)
    name = props["name"].decode("utf-8") if isinstance(props["name"], bytes) else props["name"]
    mem_gb = round(dev.mem_info[1] / (1024**3), 1)
    return {"name": name, "memory_gb": mem_gb}


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI()

# Store simulations keyed by particle count
simulations: dict[int, Simulation] = {}

# Warmup: precompile kernel
print("Warming up CUDA kernel...")
warmup_sim = Simulation(256)
for _ in range(5):
    warmup_sim.step()
del warmup_sim
cp.cuda.Stream.null.synchronize()
print("Kernel warm-up complete.")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/api/gpu-info")
async def gpu_info():
    info = get_gpu_info()
    return JSONResponse(info)


@app.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket):
    await websocket.accept()

    # Parse particle count from query params
    n_particles = 10000
    try:
        q = websocket.query_params.get("particles", "20000")
        n_particles = int(q)
        n_particles = max(1000, min(n_particles, 50000))
    except (ValueError, TypeError):
        pass

    # Create or reset simulation
    sim = Simulation(n_particles)
    print(f"Simulation started: {n_particles} particles")

    target_fps = 30
    frame_time = 1.0 / target_fps
    steps_per_frame = 3  # Multiple physics steps per rendered frame

    try:
        while True:
            t0 = time.perf_counter()

            # Advance simulation
            for _ in range(steps_per_frame):
                sim.step()

            # Synchronize GPU
            cp.cuda.Stream.null.synchronize()

            # Get state as binary and send
            state_bytes = sim.get_state_binary()

            # Prepend metadata: [sim_time(f32), step_count(u32)]
            header = struct.pack("fI", sim.sim_time, sim.step_count)
            await websocket.send_bytes(header + state_bytes)

            # Frame pacing
            elapsed = time.perf_counter() - t0
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"WebSocket error: {e}")


app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    gpu = get_gpu_info()
    print(f"GPU: {gpu['name']} ({gpu['memory_gb']} GB)")
    print(f"Starting server on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
