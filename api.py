from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/products")
async def get_products(category: str = "", price_min: float = None, price_max: float = None):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if price_min:
        query += " AND price >= ?"
        params.append(price_min)
    if price_max:
        query += " AND price <= ?"
        params.append(price_max)

    cursor.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products


@router.get("/products/{product_id}")
async def get_product(product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return dict(product)


@router.get("/categories")
async def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    return categories


@router.get("/products/{product_id}/comments")
async def get_comments(product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE product_id = ?", (product_id,))
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return comments


@router.post("/comments")
async def add_comment(product_id: int, author: str, text: str):
    if not author or not text:
        raise HTTPException(status_code=400, detail="Имя и текст обязательны")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (product_id, author, text) VALUES (?, ?, ?)",
                   (product_id, author, text))
    conn.commit()
    conn.close()
    return {"message": "Комментарий добавлен"}


@router.get("/stats")
async def get_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM products")
    total_products = cursor.fetchone()['total']

    cursor.execute("SELECT AVG(price) as avg FROM products")
    avg_price = cursor.fetchone()['avg'] or 0

    cursor.execute("SELECT COUNT(*) as total_comments FROM comments")
    total_comments = cursor.fetchone()['total']

    conn.close()

    return {
        "total_products": total_products,
        "avg_price": round(avg_price, 2),
        "total_comments": total_comments
    }