from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .main import agent_respond


app = FastAPI(title="Ozorio Test Agent")


HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Ozorio Test Agent</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; background: #f6f7f9; }
    .container { max-width: 720px; margin: 0 auto; padding: 24px; }
    .card { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 20px; }
    .title { margin: 0 0 12px; font-size: 20px; }
    .chat { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; height: 360px; overflow-y: auto; background: #fafafa; }
    .msg { margin: 8px 0; }
    .user { color: #111827; }
    .bot { color: #1f2937; }
    form { display: flex; gap: 8px; margin-top: 12px; }
    input[type=text] { flex: 1; padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px; }
    button { padding: 10px 14px; background: #111827; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
    button:disabled { opacity: .6; cursor: not-allowed; }
  </style>
  <script>
    async function sendMessage(event) {
      event.preventDefault();
      const input = document.getElementById('prompt');
      const chat = document.getElementById('chat');
      const text = input.value.trim();
      if (!text) return;
      chat.innerHTML += `<div class=\"msg user\"><strong>You:</strong> ${text}</div>`;
      input.value = '';
      const res = await fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ prompt: text })});
      const data = await res.json();
      chat.innerHTML += `<div class=\"msg bot\"><strong>Agent:</strong> ${data.reply}</div>`;
      chat.scrollTop = chat.scrollHeight;
    }
  </script>
  </head>
  <body>
    <div class=\"container\">
      <div class=\"card\">
        <h1 class=\"title\">Ozorio Test Agent</h1>
        <div id=\"chat\" class=\"chat\"></div>
        <form onsubmit=\"sendMessage(event)\">
          <input id=\"prompt\" type=\"text\" placeholder=\"Type a message (e.g., sum 3 and 5)\" />
          <button type=\"submit\">Send</button>
        </form>
      </div>
    </div>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@app.post("/chat")
async def chat(payload: dict) -> JSONResponse:
    prompt = str(payload.get("prompt", "")).strip()
    if not prompt:
        return JSONResponse({"reply": "Please enter a prompt."})
    reply = agent_respond(prompt)
    return JSONResponse({"reply": reply})


