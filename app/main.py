from fastapi import FastAPI, Request, BackgroundTasks, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import asyncio
import sqlite3
from eparkai_scraper import fetch_all_projects, save_projects_to_db, create_table

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def find_and_delete_duplicates():
    conn = sqlite3.connect('eparkai_projects.db')
    c = conn.cursor()
    c.execute('''DELETE FROM projects WHERE rowid NOT IN (
                  SELECT MIN(rowid) 
                  FROM projects 
                  GROUP BY title, image_url, small_image_url, purchase_price, old_price, maintenance_price,
                  status, total_kw, progress_percentage, reserved_percentage, reserved_kw, remaining_percentage, remaining_kw
                  )''')
    conn.commit()
    conn.close()

def get_paginated_data(page: int, items_per_page: int):
    offset = (page - 1) * items_per_page
    try:
        conn = sqlite3.connect('eparkai_projects.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM projects")
        total_items = c.fetchone()[0]
        c.execute("SELECT * FROM projects LIMIT ? OFFSET ?", (items_per_page, offset))
        projects = c.fetchall()
        conn.close()
        return projects, total_items
    except sqlite3.OperationalError as e:
        print("No database found. Error:", e)
        raise HTTPException(status_code=503, detail="Service currently unavailable, try again later.")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, page: int = 1, items_per_page: int = 10):
    try:
        projects, total_items = get_paginated_data(page, items_per_page)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": projects,
            "message": "",
            "page": page,
            "items_per_page": items_per_page,
            "total_pages": total_pages
        })
    except HTTPException as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": [],
            "message": e.detail,
            "page": 1,
            "items_per_page": 10,
            "total_pages": 0
        })

@app.post("/fetch-data", response_class=HTMLResponse)
async def fetch_data(request: Request, background_tasks: BackgroundTasks):
    try:
        projects = await fetch_all_projects()
        save_projects_to_db(projects)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{len(projects)} projects scraped at {timestamp}"
        background_tasks.add_task(lambda: asyncio.sleep(5))
        background_tasks.add_task(lambda: None)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": projects,
            "message": message,
            "page": 1,
            "items_per_page": 10,
            "total_pages": (len(projects) + 10 - 1) // 10
        })
    except Exception as e:
        print("Error during data fetching:", e)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": [],
            "message": "Service currently unavailable, try again later.",
            "page": 1,
            "items_per_page": 10,
            "total_pages": 0
        })

@app.post("/delete-duplicates", response_class=HTMLResponse)
async def delete_duplicates(request: Request):
    try:
        find_and_delete_duplicates()
        projects, total_items = get_paginated_data(1, 10)
        message = "Duplicates have been deleted"
        total_pages = (total_items + 10 - 1) // 10
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": projects,
            "message": message,
            "page": 1,
            "items_per_page": 10,
            "total_pages": total_pages
        })
    except HTTPException as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": [],
            "message": e.detail,
            "page": 1,
            "items_per_page": 10,
            "total_pages": 0
        })

@app.post("/set-items-per-page", response_class=HTMLResponse)
async def set_items_per_page(request: Request, items_per_page: int = Form(...)):
    try:
        projects, total_items = get_paginated_data(1, items_per_page)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": projects,
            "message": "",
            "page": 1,
            "items_per_page": items_per_page,
            "total_pages": total_pages
        })
    except HTTPException as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects": [],
            "message": e.detail,
            "page": 1,
            "items_per_page": items_per_page,
            "total_pages": 0
        })
