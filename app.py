from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db
from api import router as api_router

app = FastAPI(title="MarketPlacer", description="Маркетплейс на FastAPI")
app.include_router(api_router)
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


@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})


@app.get("/wishlist", response_class=HTMLResponse)
async def wishlist_page(request: Request):
    return templates.TemplateResponse("wishlist.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, is_admin, created_at FROM users WHERE id = ?", (int(user_id),))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("profile.html", {"request": request, "user": user})