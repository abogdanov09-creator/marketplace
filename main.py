from app import app

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     🚀 MarketPlacer на FastAPI запущен!                      ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🌐 Веб-интерфейс:  http://localhost:8001                    ║
    ║  🛒 Корзина:        http://localhost:8001/cart               ║
    ║  📡 API:            http://localhost:8001/api/products       ║
    ║  📚 Документация:   http://localhost:8001/docs               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8001)