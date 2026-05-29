/**
 * GPU Galaxy Collision — WebGL Particle Renderer
 * ================================================
 * Connects to the CUDA N-body simulation via WebSocket,
 * renders particles with Three.js, additive blending,
 * velocity-based coloring, and motion trails.
 */

(function () {
    "use strict";

    // -----------------------------------------------------------------------
    // Configuration
    // -----------------------------------------------------------------------
    const CONFIG = {
        particleSize: 1.0,
        trailFade: 0.55,        // 0 = no trails, 1 = infinite trails
        trailsEnabled: true,
        autoCameraEnabled: false,
        cameraDistance: 10.0,
        cameraSpeed: 0.06,
        bloomStrength: 0.6,
    };

    // -----------------------------------------------------------------------
    // Color palette: speed → color  (blue → cyan → white → yellow → red)
    // -----------------------------------------------------------------------
    function speedToColor(speed, maxSpeed) {
        const t = Math.min(speed / maxSpeed, 1.0);

        let r, g, b;
        if (t < 0.25) {
            // Blue → Cyan
            const s = t / 0.25;
            r = 0.1;
            g = 0.3 + 0.7 * s;
            b = 0.8 + 0.2 * s;
        } else if (t < 0.5) {
            // Cyan → White
            const s = (t - 0.25) / 0.25;
            r = 0.1 + 0.9 * s;
            g = 1.0;
            b = 1.0;
        } else if (t < 0.75) {
            // White → Yellow
            const s = (t - 0.5) / 0.25;
            r = 1.0;
            g = 1.0 - 0.2 * s;
            b = 1.0 - 1.0 * s;
        } else {
            // Yellow → Red
            const s = (t - 0.75) / 0.25;
            r = 1.0;
            g = 0.8 - 0.8 * s;
            b = 0.0;
        }

        return [r, g, b];
    }

    // -----------------------------------------------------------------------
    // Circular point sprite texture
    // -----------------------------------------------------------------------
    function createPointTexture() {
        const size = 64;
        const canvas = document.createElement("canvas");
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext("2d");

        const gradient = ctx.createRadialGradient(
            size / 2, size / 2, 0,
            size / 2, size / 2, size / 2
        );
        gradient.addColorStop(0.0, "rgba(255, 255, 255, 1.0)");
        gradient.addColorStop(0.05, "rgba(255, 255, 255, 0.5)");
        gradient.addColorStop(0.15, "rgba(200, 220, 255, 0.05)");
        gradient.addColorStop(0.3, "rgba(100, 150, 255, 0.0)");

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, size, size);

        const tex = new THREE.CanvasTexture(canvas);
        tex.needsUpdate = true;
        return tex;
    }

    // -----------------------------------------------------------------------
    // Three.js setup
    // -----------------------------------------------------------------------
    const container = document.getElementById("canvas-container");

    const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000008, 1);
    renderer.autoClear = false;
    container.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
        60, window.innerWidth / window.innerHeight, 0.01, 100
    );
    camera.position.set(0, 5, CONFIG.cameraDistance);
    camera.lookAt(0, 0, 0);

    // Orbit controls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 1;
    controls.maxDistance = 30;
    controls.target.set(0, 0, 0);

    // -----------------------------------------------------------------------
    // Trail effect: fade quad (renders a semi-transparent black quad over
    // the previous frame to create motion persistence)
    // -----------------------------------------------------------------------
    const trailScene = new THREE.Scene();
    const trailCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const trailMaterial = new THREE.MeshBasicMaterial({
        color: 0x000008,
        transparent: true,
        opacity: 1.0 - CONFIG.trailFade,
        depthTest: false,
        depthWrite: false,
    });
    const trailQuad = new THREE.Mesh(
        new THREE.PlaneGeometry(2, 2),
        trailMaterial
    );
    trailScene.add(trailQuad);

    // -----------------------------------------------------------------------
    // Particle system
    // -----------------------------------------------------------------------
    let maxParticles = 50000;
    const positions = new Float32Array(maxParticles * 3);
    const colors = new Float32Array(maxParticles * 3);

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geometry.setDrawRange(0, 0);

    const pointTexture = createPointTexture();

    const material = new THREE.PointsMaterial({
        size: CONFIG.particleSize,
        map: pointTexture,
        vertexColors: true,
        blending: THREE.AdditiveBlending,
        transparent: true,
        opacity: 0.25,
        depthWrite: false,
        sizeAttenuation: true,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Subtle ambient starfield background
    const starCount = 2000;
    const starPositions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
        starPositions[i * 3] = (Math.random() - 0.5) * 80;
        starPositions[i * 3 + 1] = (Math.random() - 0.5) * 80;
        starPositions[i * 3 + 2] = (Math.random() - 0.5) * 80;
    }
    const starGeo = new THREE.BufferGeometry();
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPositions, 3));
    const starMat = new THREE.PointsMaterial({
        size: 0.05,
        color: 0x444466,
        transparent: true,
        opacity: 0.6,
        depthWrite: false,
    });
    scene.add(new THREE.Points(starGeo, starMat));

    // -----------------------------------------------------------------------
    // State
    // -----------------------------------------------------------------------
    let currentParticles = 0;
    let ws = null;
    let simTime = 0;
    let simSteps = 0;
    let frameCount = 0;
    let lastFpsTime = performance.now();
    let renderFps = 0;
    let simFps = 0;
    let lastSimStep = 0;
    let lastSimFpsTime = performance.now();
    let maxSpeed = 1.0; // adaptive

    // HUD elements
    const hudParticles = document.getElementById("hud-particles");
    const hudFps = document.getElementById("hud-fps");
    const hudRenderFps = document.getElementById("hud-render-fps");
    const hudTime = document.getElementById("hud-time");
    const hudSteps = document.getElementById("hud-steps");
    const statusEl = document.getElementById("status");
    const hudEl = document.getElementById("hud");
    const gpuBadge = document.getElementById("gpu-badge");

    // -----------------------------------------------------------------------
    // WebSocket connection
    // -----------------------------------------------------------------------
    function connect(nParticles) {
        if (ws) {
            ws.close();
            ws = null;
        }

        statusEl.classList.remove("hidden");
        hudEl.style.opacity = "0";
        gpuBadge.style.opacity = "0";

        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        const url = `${proto}//${window.location.host}/ws/simulation?particles=${nParticles}`;

        ws = new WebSocket(url);
        ws.binaryType = "arraybuffer";

        ws.onopen = () => {
            statusEl.classList.add("hidden");
            hudEl.style.opacity = "1";
            gpuBadge.style.opacity = "1";
            currentParticles = nParticles;
            console.log(`Connected: ${nParticles} particles`);
        };

        ws.onmessage = (event) => {
            const data = event.data;
            if (!(data instanceof ArrayBuffer)) {
                console.warn("Non-binary message received:", data);
                return;
            }

            if (data.byteLength < 12) {
                console.warn("Message too small:", data.byteLength, "bytes");
                return;
            }

            const view = new DataView(data);
            simTime = view.getFloat32(0, true);
            simSteps = view.getUint32(4, true);

            // Track sim FPS
            const now = performance.now();
            const dtSim = now - lastSimFpsTime;
            const dSteps = simSteps - lastSimStep;
            if (dtSim >= 500) {
                simFps = Math.round((dSteps / dtSim) * 1000);
                lastSimFpsTime = now;
                lastSimStep = simSteps;
            }

            // Parse particle data: [x, y, z, speed] × N
            const headerBytes = 8;
            const floatCount = (data.byteLength - headerBytes) / 4;
            const nParts = Math.floor(floatCount / 4);
            const particleData = new Float32Array(data, headerBytes);

            // Track max speed for adaptive color scaling
            let frameMaxSpeed = 0;
            for (let i = 0; i < nParts; i++) {
                const speed = particleData[i * 4 + 3];
                if (speed > frameMaxSpeed) frameMaxSpeed = speed;
            }
            // Smooth max speed adaptation
            maxSpeed = maxSpeed * 0.95 + frameMaxSpeed * 0.05;
            if (maxSpeed < 0.1) maxSpeed = 0.1;

            // Update positions and colors
            const posAttr = geometry.getAttribute("position");
            const colAttr = geometry.getAttribute("color");

            for (let i = 0; i < nParts && i < maxParticles; i++) {
                const idx = i * 4;
                posAttr.array[i * 3] = particleData[idx];
                posAttr.array[i * 3 + 1] = particleData[idx + 1];
                posAttr.array[i * 3 + 2] = particleData[idx + 2];

                const [r, g, b] = speedToColor(particleData[idx + 3], maxSpeed);
                colAttr.array[i * 3] = r;
                colAttr.array[i * 3 + 1] = g;
                colAttr.array[i * 3 + 2] = b;
            }

            posAttr.needsUpdate = true;
            colAttr.needsUpdate = true;
            geometry.setDrawRange(0, nParts);
        };

        ws.onclose = () => {
            console.log("WebSocket closed");
        };

        ws.onerror = (e) => {
            console.error("WebSocket error:", e);
        };
    }

    // -----------------------------------------------------------------------
    // Fetch GPU info
    // -----------------------------------------------------------------------
    fetch("/api/gpu-info")
        .then((r) => r.json())
        .then((info) => {
            document.getElementById("gpu-name").textContent =
                `⚡ ${info.name} • ${info.memory_gb} GB VRAM`;
        })
        .catch(() => {});

    // -----------------------------------------------------------------------
    // Render loop
    // -----------------------------------------------------------------------
    let cameraAngle = 0;

    function animate() {
        requestAnimationFrame(animate);

        // Auto camera orbit
        if (CONFIG.autoCameraEnabled) {
            cameraAngle += CONFIG.cameraSpeed * 0.016;
            const radius = CONFIG.cameraDistance;
            camera.position.x = Math.sin(cameraAngle) * radius;
            camera.position.z = Math.cos(cameraAngle) * radius;
            camera.position.y = 3.0 + Math.sin(cameraAngle * 0.3) * 2.0;
            camera.lookAt(0, 0, 0);
        }

        controls.update();

        // Render with trails
        if (CONFIG.trailsEnabled) {
            renderer.render(trailScene, trailCamera);
            renderer.render(scene, camera);
        } else {
            renderer.clear();
            renderer.render(scene, camera);
        }

        // FPS counting
        frameCount++;
        const now = performance.now();
        if (now - lastFpsTime >= 1000) {
            renderFps = frameCount;
            frameCount = 0;
            lastFpsTime = now;

            // Update HUD
            hudParticles.textContent = currentParticles.toLocaleString();
            hudFps.textContent = simFps;
            hudRenderFps.textContent = renderFps;
            hudTime.textContent = simTime.toFixed(2) + "s";
            hudSteps.textContent = simSteps.toLocaleString();
        }
    }

    // -----------------------------------------------------------------------
    // Controls
    // -----------------------------------------------------------------------
    document.getElementById("btn-reset").addEventListener("click", () => {
        const n = parseInt(document.getElementById("particle-select").value, 10);
        connect(n);
    });

    document.getElementById("particle-select").addEventListener("change", (e) => {
        connect(parseInt(e.target.value, 10));
    });

    const btnCamera = document.getElementById("btn-camera");
    btnCamera.addEventListener("click", () => {
        CONFIG.autoCameraEnabled = !CONFIG.autoCameraEnabled;
        btnCamera.classList.toggle("active", CONFIG.autoCameraEnabled);
        btnCamera.textContent = CONFIG.autoCameraEnabled
            ? "🎥 Auto Camera"
            : "🎥 Manual Camera";
    });
    // Auto camera starts off — manual orbit by default
    btnCamera.textContent = "🎥 Manual Camera";

    const btnTrails = document.getElementById("btn-trails");
    btnTrails.addEventListener("click", () => {
        CONFIG.trailsEnabled = !CONFIG.trailsEnabled;
        btnTrails.textContent = CONFIG.trailsEnabled
            ? "✨ Trails: ON"
            : "✨ Trails: OFF";
        btnTrails.classList.toggle("active", CONFIG.trailsEnabled);
    });
    btnTrails.classList.add("active");

    // -----------------------------------------------------------------------
    // Window resize
    // -----------------------------------------------------------------------
    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // -----------------------------------------------------------------------
    // Start
    // -----------------------------------------------------------------------
    animate();
    connect(20000);
})();
