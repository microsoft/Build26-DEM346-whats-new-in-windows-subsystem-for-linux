FROM nvidia/cuda:12.6.3-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages \
    cupy-cuda12x \
    fastapi \
    uvicorn[standard] \
    websockets

WORKDIR /app
COPY server.py .
COPY static/ static/

EXPOSE 8080

CMD ["python3", "server.py"]
