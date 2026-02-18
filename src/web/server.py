from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import logging
from src.brain.personas import get_system_prompt, update_system_prompt
from src.config import Config

# Import the main routine function to trigger it manually
# Note: We need to import it carefully to avoid circular imports if main imports server
# Better to pass the function or import inside the endpoint
import importlib

app = FastAPI()
templates = Jinja2Templates(directory="src/web/templates")

# Global reference to scheduler or running state
# In a real app, use a proper state manager
is_running = False

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    current_prompt = get_system_prompt()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "system_prompt": current_prompt,
        "is_running": is_running
    })

@app.post("/update_prompt")
async def update_prompt(system_prompt: str = Form(...)):
    update_system_prompt(system_prompt)
    return RedirectResponse(url="/", status_code=303)

@app.post("/trigger_routine")
async def trigger_routine(background_tasks: BackgroundTasks):
    from main import daily_routine # Delayed import to avoid circular dependency
    background_tasks.add_task(daily_routine)
    return RedirectResponse(url="/", status_code=303)

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)
