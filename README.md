# AI Voice Agent — LiveKit

A real-time AI voice agent built on LiveKit Cloud. The agent ("Megan") acts as a solar energy sales consultant, conducting structured outbound conversations using OpenAI's Realtime API for reasoning and Cartesia for voice synthesis.

## Architecture Overview

```
Browser (microphone)
    │
    │  POST /api/token
    ▼
Next.js Frontend (port 3000)
    │
    │  WebRTC via livekit-client
    ▼
LiveKit Cloud Room
    │
    │  Agent dispatched on room join
    ▼
Python Agent (backend/src/agent.py)
    ├── OpenAI Realtime API  — LLM reasoning (text modality only)
    ├── Cartesia TTS         — Voice synthesis (sonic-3 model)
    └── LiveKit BVC          — Microphone noise cancellation
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS v4 |
| Agent Framework | livekit-agents ~1.4 (Python) |
| LLM | OpenAI Realtime API (`gpt-4o-realtime-preview`) |
| TTS | Cartesia (`sonic-3`) |
| WebRTC | LiveKit Cloud |
| Package Managers | pnpm (frontend), uv (backend) |

---

## Prerequisites

Before you begin, make sure you have the following installed and available:

### Tools

| Tool | Install |
|------|---------|
| Node.js 18+ | https://nodejs.org |
| pnpm | `npm install -g pnpm` |
| Python 3.10+ | https://python.org |
| uv (Python package manager) | See below |

**Install uv:**
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Windows (winget)
winget install astral-sh.uv
```

### External Accounts & API Keys

You will need accounts and API keys for the following services:

| Service | Purpose | Get it at |
|---------|---------|-----------|
| **LiveKit Cloud** | WebRTC room management, agent routing | https://cloud.livekit.io |
| **OpenAI** | LLM reasoning via Realtime API | https://platform.openai.com |
| **Cartesia** | Voice synthesis (TTS) | https://cartesia.ai |

> **Note:** OpenAI Realtime API access may require a separate approval or billing tier. Verify your account has access to `gpt-4o-realtime-preview`.

---

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd AI-Voice-Agent---Livekit
```

### 2. Create a LiveKit Cloud Project

1. Log in to [LiveKit Cloud](https://cloud.livekit.io) and create a new project.
2. From the project dashboard, copy:
   - **URL** (e.g. `wss://your-project-name.livekit.cloud`)
   - **API Key** (e.g. `APIxxxxxxxxxxxx`)
   - **API Secret** (long string)

### 3. Configure the Backend

```bash
cd backend
```

Create a `.env.local` file:

```bash
cp .env.example .env.local   # if an example exists, otherwise create it manually
```

Add the following to `backend/.env.local`:

```env
LIVEKIT_URL=wss://your-project-name.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

OPENAI_API_KEY=sk-proj-your_openai_api_key

CARTESIA_API_KEY=sk_car_your_cartesia_api_key

AGENT_NAME=voice-assistant
```

Install Python dependencies:

```bash
uv sync
```

Download the noise cancellation model files (required on first run):

```bash
uv run src/agent.py download-files
```

### 4. Configure the Frontend

```bash
cd ../frontend
```

Create a `.env.local` file:

```bash
cp .env.example .env.local
```

Add the following to `frontend/.env.local`:

```env
LIVEKIT_URL=wss://your-project-name.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

AGENT_NAME=voice-assistant
```

> `AGENT_NAME` must match exactly the agent name used in `backend/src/agent.py` (`"voice-assistant"`).

Install Node.js dependencies:

```bash
pnpm install
```

---

## Running the Project

You need **two terminals** running simultaneously.

### Terminal 1 — Start the AI Agent

```bash
cd backend
uv run src/agent.py dev
```

The agent connects to LiveKit Cloud and waits for rooms. You should see output like:

```
INFO livekit.agents - starting agent worker
INFO livekit.agents - connected to LiveKit Cloud
```

### Terminal 2 — Start the Frontend

```bash
cd frontend
pnpm dev
```

The Next.js dev server starts at [http://localhost:3000](http://localhost:3000).

### Using the App

1. Open [http://localhost:3000](http://localhost:3000) in your browser.
2. Click **Start call**.
3. Allow microphone access when prompted.
4. The agent (Megan) will begin speaking within a few seconds.

---

## Optional: Standalone Token Server

The frontend includes a built-in Next.js token endpoint at `/api/token` that works out of the box for development. However, you can also run the standalone FastAPI token server if you want to decouple the backend:

```bash
cd backend
uv run uvicorn token_server.main:app --reload --port 8000
```

This starts a FastAPI server at `http://localhost:8000`. The token endpoint is:

```
POST http://localhost:8000/api/token
```

Response:
```json
{
  "server_url": "wss://your-project.livekit.cloud",
  "participant_token": "eyJ..."
}
```

> **Security note:** The built-in Next.js token route (`app/api/token/route.ts`) is explicitly marked as development-only. For production, use the FastAPI token server or your own secure backend endpoint.

---

## Project Structure

```
AI-Voice-Agent---Livekit/
├── backend/
│   ├── src/
│   │   └── agent.py          # Main AI agent (Megan persona + LiveKit session)
│   ├── token_server/
│   │   └── main.py           # FastAPI token server (POST /api/token)
│   ├── pyproject.toml        # Python dependencies (uv format)
│   └── .env.local            # Backend environment variables (create this)
│
└── frontend/
    ├── app/
    │   ├── page.tsx           # Entry point
    │   └── api/token/         # Dev-only Next.js token endpoint
    ├── components/
    │   ├── app/               # Session setup, view switching
    │   └── agents-ui/         # Audio visualizers, control bar, transcript
    ├── app-config.ts          # Branding, feature flags, agent name
    ├── package.json
    └── .env.local             # Frontend environment variables (create this)
```

---

## Environment Variables Reference

### Backend (`backend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_URL` | Yes | Your LiveKit Cloud WebSocket URL (`wss://...`) |
| `LIVEKIT_API_KEY` | Yes | LiveKit API key from your project dashboard |
| `LIVEKIT_API_SECRET` | Yes | LiveKit API secret from your project dashboard |
| `OPENAI_API_KEY` | Yes | OpenAI API key with Realtime API access |
| `CARTESIA_API_KEY` | Yes | Cartesia API key for TTS |
| `AGENT_NAME` | Yes | Logical agent name used for dispatch (default: `voice-assistant`) |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_URL` | Yes | Same LiveKit Cloud WebSocket URL as backend |
| `LIVEKIT_API_KEY` | Yes | Same LiveKit API key as backend |
| `LIVEKIT_API_SECRET` | Yes | Same LiveKit API secret as backend |
| `AGENT_NAME` | Yes | Must match `AGENT_NAME` in backend exactly |
| `NEXT_PUBLIC_APP_CONFIG_ENDPOINT` | No | Remote config endpoint (LiveKit Sandbox only) |
| `SANDBOX_ID` | No | LiveKit Cloud Sandbox ID (Sandbox deployments only) |

---

## Customizing the Agent

The agent persona and conversation script are defined in `backend/src/agent.py`.

### Change the Voice

Find the Cartesia TTS configuration and update the `voice` ID:

```python
cartesia.TTS(
    model="sonic-3",
    voice="your-voice-id-here",  # Get voice IDs from Cartesia dashboard
    speed=0.87,
    emotion=["positivity:high"],
)
```

### Change the Persona or Script

The agent's instructions (system prompt) are defined in the `instructions` parameter of the `openai.realtime.RealtimeModel`. Edit the prompt text there to change the persona, name, company, or conversation flow.

### Change the LLM Model

Update the model name in the `RealtimeModel` constructor:

```python
openai.realtime.RealtimeModel(
    model="gpt-4o-realtime-preview",  # change this
    modalities=["text"],
)
```

---

## Troubleshooting

**Agent does not connect**
- Verify `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` are correctly set in `backend/.env.local`.
- Make sure `uv run src/agent.py download-files` completed successfully before running `dev`.

**No audio from agent**
- Confirm `CARTESIA_API_KEY` is valid and your Cartesia account is active.
- Check that your browser allowed microphone access.

**"Agent not found" or no response after clicking Start call**
- Ensure the backend agent is running (`uv run src/agent.py dev`) before opening the frontend.
- Confirm `AGENT_NAME` is identical in both `backend/.env.local` and `frontend/.env.local`.

**OpenAI errors or no LLM response**
- Verify `OPENAI_API_KEY` is valid and has access to `gpt-4o-realtime-preview`.

**pnpm or uv command not found**
- Install pnpm: `npm install -g pnpm`
- Install uv: see [Prerequisites](#prerequisites) section above.

---

## License

See [LICENSE](./LICENSE) for details.
