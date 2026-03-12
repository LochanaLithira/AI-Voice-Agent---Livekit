import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from livekit import api

load_dotenv(".env.local")

AGENT_NAME = os.getenv("AGENT_NAME", "voice-assistant")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/token")
async def create_token(request: Request):
    body = await request.json()

    room_name = body.get("room_name") or "voice-assistant-room"
    participant_identity = body.get("participant_identity") or f"user-{os.urandom(4).hex()}"
    participant_name = body.get("participant_name") or "User"

    token = (
        api.AccessToken(
            os.getenv("LIVEKIT_API_KEY"),
            os.getenv("LIVEKIT_API_SECRET"),
        )
        .with_identity(participant_identity)
        .with_name(participant_name)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .with_room_config(
            api.RoomConfiguration(
                agents=[api.RoomAgentDispatch(agent_name=AGENT_NAME)]
            )
        )
    )

    return {
        "server_url": os.getenv("LIVEKIT_URL"),
        "participant_token": token.to_jwt(),
    }
