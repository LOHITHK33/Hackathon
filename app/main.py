import asyncio
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .config import MODEL
from .llm import get_llm

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="Nexus")


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL}


@app.get("/api/stream")
async def stream(q: str):
    async def gen():
        yield sse("status", {"stage": "starting", "model": MODEL})
        await asyncio.sleep(0)
        try:
            llm = get_llm()
            yield sse("status", {"stage": "thinking"})
            async for chunk in llm.astream(q):
                text = getattr(chunk, "content", "") or ""
                if text:
                    yield sse("token", {"text": text})
            yield sse("done", {})
        except Exception as exc:
            yield sse("error", {"message": str(exc)})

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")