from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from pathlib import Path

app = FastAPI()

# Sử dụng Path để chuẩn hóa đường dẫn
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Convert sang string và thay thế backslashes
STATIC_DIR = str(STATIC_DIR).replace("\\", "/")
TEMPLATES_DIR = str(TEMPLATES_DIR).replace("\\", "/")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/home")

# Giữ nguyên các route khác
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/category", response_class=HTMLResponse)
async def category_page(request: Request):  # Đổi tên hàm để tránh trùng
    return templates.TemplateResponse("category.html", {"request": request})

@app.get("/movies", response_class=HTMLResponse)
async def detail_page(request: Request):  # Đổi tên hàm để tránh trùng
    return templates.TemplateResponse("detail.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)