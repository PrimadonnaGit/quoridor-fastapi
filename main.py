import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.endpoint.websocket import manager
from api.router import api_router
from core.database import create_supabase_client

app = FastAPI(title="Quoridor API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://quoridor-web-koreaboardgamearena.koyeb.app",
        "https://battlequoridor.com",
        "https://www.battlequoridor.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    await create_supabase_client()


@app.on_event("shutdown")
async def shutdown_event():
    await manager.close_all_connections()


@app.get("/")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
