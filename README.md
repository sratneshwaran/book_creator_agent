# Agno Book Creator

Small Flask web app that streams book generation using an Agno agent backed by a vLLM/OpenAI-compatible endpoint. It produces a draft (markdown/plaintext) in the browser and lets you download RTF or HTML.

## Features
- Streams chapter-by-chapter draft text while the LLM writes.
- Proofreads and converts the final manuscript to RTF via the model; also renders HTML for download.
- Simple UI with SSE for status and draft updates; supports RTF/HTML downloads.

## Prerequisites
- Python 3.10+ recommended.
- Access to a vLLM/OpenAI-compatible endpoint (can be local). Configure via env vars:
  - `VLLM_API_BASE` (default `http://localhost:11434/v1`)
  - `VLLM_API_KEY` (default `EMPTY` for local vLLM)
  - `MODEL_NAME` (default `gpt-oss:20b`)

## Setup (one-time)
1) Clone and enter the project directory.
2) Create a virtual environment (example on Windows PowerShell):
	```pwsh
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```
3) Install pinned dependencies:
	```pwsh
	pip install --upgrade pip
	pip install -r requirements.txt
	```

## Configure
Set environment variables as needed before running (PowerShell examples):
```pwsh
$env:VLLM_API_BASE="http://localhost:11434/v1"
$env:VLLM_API_KEY="EMPTY"
$env:MODEL_NAME="gpt-oss:20b"
```
`Config.SECRET_KEY` is generated at runtime; override by exporting `SECRET_KEY` if you prefer a fixed value.

Pinned versions are defined in `requirements.txt`; update them intentionally if you need newer releases.

## Run the app
```pwsh
python app.py
```
The server starts on `http://localhost:5000` with Flask debug mode enabled.

## Using the website
- Open `http://localhost:5000`.
- Enter a detailed topic and click **Write Book**.
- Watch the status text ("thinking" steps) and streamed draft in the output box.
- When complete, use **Download RTF** or **Download HTML** to save the generated book.

## How it works (code map)
- `app.py`: Flask app; SSE stream at `/generate` orchestrates outline → chapters → proofreading/RTF, stores latest outputs, and serves downloads at `/download/<fmt>`.
- `book_agent.py`: Wraps an Agno `Agent` with the configured OpenAI-compatible endpoint; handles outline, chapter writing, and RTF-proofreading prompts.
- `config.py`: Env-driven config defaults for model base URL, API key, and model name.
- `templates/index.html`: Minimal UI, status bar, streamed updates, and download buttons.

## Tips
- If markdown is not installed, HTML downloads fall back to escaped plaintext.
- Large topics may take time; the browser stream keeps connection open until completion.
- For production, store generated files persistently and disable Flask debug mode.
