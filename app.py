from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db
from api import router as api_router

app = FastAPI(title="MarketPlacer", description="Маркетплейс на FastAPI")
app.include_router(api_router)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: int = 1, category: str = "", price_min: float = None, price_max: float = None):
    per_page = 9  # 9 товаров на страницу

    conn = get_db()
    cursor = conn.cursor()

    # Базовый запрос с фильтрами
    query = "SELECT * FROM products WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM products WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        count_query += " AND category = ?"
        params.append(category)
    if price_min:
        query += " AND price >= ?"
        count_query += " AND price >= ?"
        params.append(price_min)
    if price_max:
        query += " AND price <= ?"
        count_query += " AND price <= ?"
        params.append(price_max)

    # Получаем общее количество товаров
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']

    # Пагинация
    offset = (page - 1) * per_page
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    products = cursor.fetchall()

    # Категории для фильтра
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = cursor.fetchall()
    conn.close()

    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": products,
        "categories": categories,
        "page": page,
        "total_pages": total_pages,
        "total": total,
        "per_page": per_page,
        "selected_category": category,
        "price_min": price_min,
        "price_max": price_max
    })


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = ""):
    conn = get_db()
    cursor = conn.cursor()

    if q:
        cursor.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? OR description LIKE ?
        """, (f'%{q}%', f'%{q}%'))
        products = cursor.fetchall()
    else:
        products = []

    conn.close()

    return templates.TemplateResponse("search.html", {
        "request": request,
        "products": products,
        "search_query": q
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


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@app.get("/admin/products")
async def admin_products_page(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id")
    products = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("admin/products.html", {"request": request, "products": products})


@app.get("/admin/comments")
async def admin_comments_page(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT comments.*, products.name as product_name 
        FROM comments 
        LEFT JOIN products ON comments.product_id = products.id 
        ORDER BY comments.id DESC
    """)
    comments = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("admin/comments.html", {"request": request, "comments": comments})


@app.get("/admin/users")
async def admin_users_page(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, is_admin, created_at FROM users ORDER BY id")
    users = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("admin/users.html", {"request": request, "users": users})