from typing import List, Any, Dict
from pydantic import BaseModel


class Pagination(BaseModel):
    total: int
    page: int
    size: int
    data: List[Any]

def paginate(items: List[Any], page: int, size: int) -> Pagination:
    offset = (page - 1) * size
    total = len(items)
    paginated_items = items[offset:offset + size]
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "data": paginated_items
    }