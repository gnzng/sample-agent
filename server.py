from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio
import subprocess

app = FastAPI()

# Serve static files (HTML/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.websocket("/ws")
async def websocket_terminal(websocket: WebSocket):
    await websocket.accept()

    # Start your Python program as a subprocess
    process = await asyncio.create_subprocess_exec(
        "python", "-u", "main.py",  # Replace with your program
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async def read_output():
        while True:
            output = await process.stdout.read(1024)
            if not output:
                break
            await websocket.send_text(output.decode())

    async def read_input():
        while True:
            user_input = await websocket.receive_text()
            process.stdin.write(user_input.encode() + b"\n")
            await process.stdin.drain()

    await asyncio.gather(read_output(), read_input())
