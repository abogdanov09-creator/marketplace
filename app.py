from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db
from api import router as api_router

# Создаём приложение
app = FastAPI(title="MarketPlacer", description="Маркетплейс на FastAPI")

# Подключаем API
app.include_router(api_router)

# Шаблоны
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": products,
        "categories": categories
    })


@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_page(request: Request, product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    cursor.execute("SELECT * FROM comments WHERE product_id = ?", (product_id,))
    comments = cursor.fetchall()
    conn.close()

    if not product:
        return HTMLResponse("Товар не найден", status_code=404)

    return templates.TemplateResponse("product.html", {
        "request": request,
        "product": product,
        "comments": comments
    })


@app.post("/add_comment")
async def add_comment(product_id: int = Form(...), author: str = Form(...), text: str = Form(...)):
    if author and text:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (product_id, author, text) VALUES (?, ?, ?)",
                       (product_id, author, text))
        conn.commit()
        conn.close()
    return RedirectResponse(url=f"/product/{product_id}", status_code=303)