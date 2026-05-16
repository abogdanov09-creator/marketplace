from fastapi import APIRouter, HTTPException, Request, Response
from database import get_db
import json

router = APIRouter(prefix="/api", tags=["API"])


# ==================== ТОВАРЫ ====================

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


# ==================== КОРЗИНА ====================

def get_cart_from_cookie(request: Request):
    cart = request.cookies.get("cart")
    if cart:
        return json.loads(cart)
    return {}


def save_cart_to_cookie(response: Response, cart: dict):
    response.set_cookie(key="cart", value=json.dumps(cart), max_age=30 * 24 * 60 * 60, path="/")


@router.get("/cart")
async def get_cart(request: Request):
    cart = get_cart_from_cookie(request)

    cart_items = []
    total = 0
    conn = get_db()
    cursor = conn.cursor()

    for product_id, item in cart.items():
        cursor.execute("SELECT * FROM products WHERE id = ?", (int(product_id),))
        product = cursor.fetchone()
        if product:
            quantity = item.get("quantity", 1)
            subtotal = product["price"] * quantity
            total += subtotal
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "subtotal": subtotal,
                "stock": product["stock"]
            })

    conn.close()
    return {"items": cart_items, "total": round(total, 2), "count": len(cart_items)}


@router.post("/cart/add/{product_id}")
async def add_to_cart(request: Request, product_id: int):
    from fastapi.responses import JSONResponse

    cart = get_cart_from_cookie(request)
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]["quantity"] += 1
    else:
        cart[product_id_str] = {"quantity": 1}

    response = JSONResponse(content={"message": "Товар добавлен в корзину"})
    save_cart_to_cookie(response, cart)
    return response


@router.post("/cart/update/{product_id}/{quantity}")
async def update_cart(request: Request, product_id: int, quantity: int):
    from fastapi.responses import JSONResponse

    cart = get_cart_from_cookie(request)
    product_id_str = str(product_id)

    if quantity <= 0:
        if product_id_str in cart:
            del cart[product_id_str]
    else:
        if product_id_str in cart:
            cart[product_id_str]["quantity"] = quantity

    response = JSONResponse(content={"message": "Корзина обновлена"})
    save_cart_to_cookie(response, cart)
    return response


@router.post("/cart/remove/{product_id}")
async def remove_from_cart(request: Request, product_id: int):
    from fastapi.responses import JSONResponse

    cart = get_cart_from_cookie(request)
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    response = JSONResponse(content={"message": "Товар удалён из корзины"})
    save_cart_to_cookie(response, cart)
    return response


@router.post("/cart/clear")
async def clear_cart():
    from fastapi.responses import JSONResponse

    response = JSONResponse(content={"message": "Корзина очищена"})
    save_cart_to_cookie(response, {})
    return response