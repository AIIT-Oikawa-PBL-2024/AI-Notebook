from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import files, users

app = FastAPI()
app.include_router(users.router)
app.include_router(files.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello World"}
