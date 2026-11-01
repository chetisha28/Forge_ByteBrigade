#!/usr/bin/env python3
import uvicorn
import os
import socket
from dotenv import load_dotenv

load_dotenv()

def get_free_port(preferred_port=8080):
    # Check if preferred port is free
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', preferred_port)) != 0:
            return preferred_port
    # Fallbacks
    for p in [8002, 8088, 8888, 9000]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', p)) != 0:
                return p
    return preferred_port

if __name__ == "__main__":
    env_port = os.getenv("PORT")
    port = int(env_port) if env_port else get_free_port(8080)
    host = os.getenv("HOST", "0.0.0.0")

    print("\n" + "="*70)
    print("  🚀 Starting CivicPilot Backend API Server (FastAPI + LangGraph)")
    print("="*70)
    print(f"  • Live API:        http://localhost:{port}")
    print(f"  • Interactive Docs:http://localhost:{port}/docs")
    print(f"  • Alternative Docs:http://localhost:{port}/redoc")
    print("="*70 + "\n")

    uvicorn.run("src.api:app", host=host, port=port, reload=False)
