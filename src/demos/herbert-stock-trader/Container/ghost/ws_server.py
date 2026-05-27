#!/usr/bin/env python3
"""Standalone WebSocket relay server for Herbert.

Runs on port 8765 and acts as the communication bridge between
the container and the host app. Clients can connect to receive
trade events and (in future) send commands to the ghost.
"""

import asyncio
import json
import signal
import time

try:
    import websockets
    import websockets.server
except ImportError:
    print("ERROR: websockets package not installed")
    raise

clients = set()
message_queue = asyncio.Queue()


SIGNAL_FILE = "/tmp/go_back_to_work"


async def handler(websocket):
    clients.add(websocket)
    print(f"[ws_server] Client connected ({len(clients)} total)")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "command" and data.get("action") == "go_back_to_work":
                    with open(SIGNAL_FILE, "w") as f:
                        f.write(str(time.time()))
                    print("[ws_server] Command received: go_back_to_work")
                else:
                    print(f"[ws_server] Received unknown message: {message}")
            except (json.JSONDecodeError, Exception) as e:
                print(f"[ws_server] Bad message: {e}")
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.discard(websocket)
        print(f"[ws_server] Client disconnected ({len(clients)} total)")


async def broadcaster():
    """Read from the queue and broadcast to all connected clients."""
    while True:
        message = await message_queue.get()
        if clients:
            dead = set()
            for client in clients:
                try:
                    await client.send(message)
                except Exception:
                    dead.add(client)
            clients.difference_update(dead)


async def stdin_reader():
    """Read JSON lines from stdin and enqueue them for broadcast.

    This lets other processes (like stock_ticker.py) pipe messages
    into the WebSocket server without needing their own WS code.
    """
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    transport, _ = await loop.connect_read_pipe(
        lambda: asyncio.StreamReaderProtocol(reader), 
        open('/tmp/ws_server.fifo', 'r')
    )

    while True:
        line = await reader.readline()
        if not line:
            await asyncio.sleep(0.1)
            continue
        try:
            decoded = line.decode().strip()
            if decoded:
                await message_queue.put(decoded)
        except Exception:
            pass


async def main():
    print("[ws_server] Starting on 0.0.0.0:8765")

    async with websockets.server.serve(handler, "0.0.0.0", 8765):
        print("[ws_server] Ready — waiting for connections")
        broadcaster_task = asyncio.create_task(broadcaster())
        stdin_task = asyncio.create_task(stdin_reader())
        await asyncio.gather(broadcaster_task, stdin_task)


if __name__ == "__main__":
    asyncio.run(main())
