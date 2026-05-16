from app import app
import webbrowser
import threading
import time


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8002")


if __name__ == "__main__":
    import uvicorn

    threading.Thread(target=open_browser, daemon=True).start()

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         🚀 MarketPlacer на FastAPI запущен!                  ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🌐 Веб-интерфейс:  http://localhost:8002                    ║
    ║  🛒 Корзина:        http://localhost:8002/cart               ║
    ║  ❤️ Избранное:      http://localhost:8002/wishlist           ║
    ║  👑 Админ-панель:   http://localhost:8002/admin              ║
    ║  🔍 Поиск:          http://localhost:8002/search             ║
    ║  📡 API:            http://localhost:8002/api/products       ║
    ║  📚 Документация:   http://localhost:8002/docs               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=8002)