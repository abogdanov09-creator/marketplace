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


# ==================== ИЗБРАННОЕ ====================

def get_wishlist_from_cookie(request: Request):
    wishlist = request.cookies.get("wishlist")
    if wishlist:
        return json.loads(wishlist)
    return []


def save_wishlist_to_cookie(response: Response, wishlist: list):
    response.set_cookie(key="wishlist", value=json.dumps(wishlist), max_age=30 * 24 * 60 * 60, path="/")


@router.get("/wishlist")
async def get_wishlist(request: Request):
    wishlist_ids = get_wishlist_from_cookie(request)

    wishlist_items = []
    conn = get_db()
    cursor = conn.cursor()

    for product_id in wishlist_ids:
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if product:
            wishlist_items.append(dict(product))

    conn.close()
    return wishlist_items


@router.post("/wishlist/add/{product_id}")
async def add_to_wishlist(request: Request, product_id: int):
    from fastapi.responses import JSONResponse

    wishlist = get_wishlist_from_cookie(request)

    if product_id not in wishlist:
        wishlist.append(product_id)

    response = JSONResponse(content={"message": "Товар добавлен в избранное"})
    save_wishlist_to_cookie(response, wishlist)
    return response


@router.post("/wishlist/remove/{product_id}")
async def remove_from_wishlist(request: Request, product_id: int):
    from fastapi.responses import JSONResponse

    wishlist = get_wishlist_from_cookie(request)

    if product_id in wishlist:
        wishlist.remove(product_id)

    response = JSONResponse(content={"message": "Товар удалён из избранного"})
    save_wishlist_to_cookie(response, wishlist)
    return response


@router.get("/wishlist/check/{product_id}")
async def check_wishlist(request: Request, product_id: int):
    wishlist = get_wishlist_from_cookie(request)
    return {"in_wishlist": product_id in wishlist}


# ==================== АДМИН-ПАНЕЛЬ ====================

@router.get("/admin/stats")
async def admin_stats(request: Request):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM products")
    total_products = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM comments")
    total_comments = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as low_stock FROM products WHERE stock < 5")
    low_stock = cursor.fetchone()['low_stock']

    conn.close()

    return {
        "total_products": total_products,
        "total_comments": total_comments,
        "total_users": total_users,
        "low_stock": low_stock
    }


@router.get("/admin/products")
async def admin_products(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products


@router.post("/admin/products")
async def admin_create_product(request: Request, name: str, category: str, price: float, description: str, stock: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, price, description, stock) VALUES (?, ?, ?, ?, ?)",
        (name, category, price, description, stock)
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return {"id": product_id, "message": "Товар создан"}


@router.put("/admin/products/{product_id}")
async def admin_update_product(request: Request, product_id: int, name: str, category: str, price: float,
                               description: str, stock: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name=?, category=?, price=?, description=?, stock=? WHERE id=?",
        (name, category, price, description, stock, product_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Товар обновлён"}


@router.delete("/admin/products/{product_id}")
async def admin_delete_product(request: Request, product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Товар удалён"}


@router.get("/admin/comments")
async def admin_comments(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT comments.*, products.name as product_name 
        FROM comments 
        LEFT JOIN products ON comments.product_id = products.id 
        ORDER BY comments.id DESC
    """)
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return comments


@router.delete("/admin/comments/{comment_id}")
async def admin_delete_comment(request: Request, comment_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    return {"message": "Комментарий удалён"}


@router.get("/admin/users")
async def admin_users(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, is_admin, created_at FROM users ORDER BY id")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


@router.post("/admin/users/{user_id}/toggle-admin")
async def admin_toggle_admin(request: Request, user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = NOT is_admin WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "Права пользователя изменены"}