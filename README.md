# CPL Falcon

A voice AI butler built with [LiveKit Agents](https://docs.livekit.io/agents/) for Python. CPL Falcon answers calls with a Gemini realtime voice model and can browse the web on your behalf through an agent-controlled Playwright browser.

## Features

- **Realtime voice** — Gemini 3.1 Flash Live (`gemini-3.1-flash-live-preview`) with a British-English butler persona
- **Browser control** — open URLs, search DuckDuckGo, read/inspect pages, click, type, scroll, and press keys via Playwright
- **Confirmations for risky actions** — sends, submissions, purchases, and deletes require explicit user confirmation before the click is performed
- **Noise cancellation and VAD** — ai-coustics audio enhancement and voice activity detection
- **Smart turn handling** — cloud turn detector with adaptive interruptions and preemptive generation
- **AVX2 compatibility** — `local_inference_compat` lets the agent run on older CPUs that lack AVX2 by stubbing LiveKit's bundled local inference module
- **Docker support** — multi-stage build for deployment as a LiveKit agent worker

## Architecture

```
src/
  agent.py                  # LiveKit AgentServer, Assistant agent, session setup
  browser.py                # Playwright BrowserManager (one isolated browser per room)
  tools.py                  # Browser function tools exposed to the LLM
  prompts.py                # Agent instructions
  local_inference_compat.py # AVX2 compatibility shim (must import before livekit)
tests/                      # pytest suite
```

## Prerequisites

- Python 3.10 – 3.14
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A [LiveKit Cloud](https://cloud.livekit.io/) project (or self-hosted LiveKit server)
- A Google AI API key (for the Gemini realtime model)
- Playwright browsers (installed below)

## Setup

1. **Install dependencies**

   ```bash
   uv sync
   ```

2. **Install Playwright browsers**

   ```bash
   uv run playwright install chromium
   ```

3. **Configure environment**

   Copy `.env.example` to `.env.local` and fill in your credentials:

   ```bash
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   GOOGLE_API_KEY=your_google_api_key
   ```

## Running

### Local development

```bash
uv run src/agent.py dev
```

This starts the agent and opens a local dev console at [http://localhost:3000](http://3000) where you can join a room and talk to CPL Falcon.

### Production

```bash
uv run src/agent.py start
```

The worker connects to LiveKit and waits for sessions. Assign it the agent name `my-agent` when dispatching a room.

### Docker

```bash
docker build -t cpl-falcon .
docker run --env-file .env.local cpl-falcon
```

## Tests

```bash
uv run pytest
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
```

## Browser tools

| Tool | Purpose |
| --- | --- |
| `open_url` | Open a specific website directly |
| `search_the_web` | Fall back to DuckDuckGo for general searches |
| `read_page` | Read visible text from the current page |
| `inspect_page` | List interactive elements with accessible names (use before click/type) |
| `click` | Click a control by accessible name (confirmation required for risky targets) |
| `confirm_browser_action` | Authorize a previously discussed consequential click |
| `type_text` | Fill a text field by label or accessible name |
| `scroll` | Scroll the page up or down |
| `press_key` | Press a navigation key (Enter, Escape, Tab, arrows, Backspace) |
| `go_back` | Navigate back |
| `take_screenshot` | Capture the page for diagnostics |

## License

See repository for license details.
