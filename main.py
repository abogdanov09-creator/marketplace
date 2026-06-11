from app import app
import webbrowser
import threading
import time


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    import uvicorn

    threading.Thread(target=open_browser, daemon=True).start()

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         🚀 MarketPlacer на FastAPI запущен!                  ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🌐 Веб-интерфейс:  http://localhost:8000                    ║
    ║  🛒 Корзина:        http://localhost:8000/cart               ║
    ║  ❤️ Избранное:      http://localhost:8000/wishlist           ║
    ║  🔍 Поиск:          http://localhost:8000/search             ║
    ║  👑 Админ-панель:   http://localhost:8000/admin              ║
    ║  📡 API:            http://localhost:8000/api/products       ║
    ║  📚 Документация:   http://localhost:8000/docs               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000)