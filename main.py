from app import app

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         🚀 MarketPlacer на FastAPI запущен!                  ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🌐 Веб-интерфейс:  http://localhost:8001                    ║
    ║  🛒 Корзина:        http://localhost:8001/cart               ║
    ║  ❤️ Избранное:      http://localhost:8001/wishlist           ║
    ║  🔐 Вход:           http://localhost:8001/login              ║
    ║  📝 Регистрация:    http://localhost:8001/register           ║
    ║  👤 Профиль:        http://localhost:8001/profile            ║
    ║  📡 API:            http://localhost:8001/api/products       ║
    ║  📚 Документация:   http://localhost:8001/docs               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8001)