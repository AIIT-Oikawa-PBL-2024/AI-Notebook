# Description: Mock server to test the stream output of the backend FastAPI
# Usage: uvicorn stream_mock_server:app --reload

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


async def mock_stream() -> str:
    for i in range(10):
        yield f"## line {i}\n"
        await asyncio.sleep(1)


@app.post("/outputs/request")
async def get_stream(request: Request) -> StreamingResponse:
    return StreamingResponse(mock_stream(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
