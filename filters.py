def apply_filters(query: str, params: list, category: str = "", price_min: float = None, price_max: float = None):
    """Применяет фильтры к SQL запросу"""
    if category:
        query += " AND category = ?"
        params.append(category)
    if price_min is not None:
        query += " AND price >= ?"
        params.append(price_min)
    if price_max is not None:
        query += " AND price <= ?"
        params.append(price_max)
    return query, params