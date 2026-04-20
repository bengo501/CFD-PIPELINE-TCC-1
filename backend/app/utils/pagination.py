from datetime import datetime, time
from math import ceil
from typing import Any, Optional


def resolve_page_limit(
    page: int = 1,
    limit: Optional[int] = None,
    per_page: Optional[int] = None,
    max_limit: int = 100,
) -> tuple[int, int, int]:
    page = max(1, page or 1)
    chosen_limit = limit if limit is not None else per_page
    chosen_limit = chosen_limit or 20
    chosen_limit = max(1, min(chosen_limit, max_limit))
    offset = (page - 1) * chosen_limit
    return page, chosen_limit, offset


def total_pages(total: int, limit: int) -> int:
    if limit <= 0:
        return 1
    return ceil(total / limit) if total > 0 else 1


def clean_filters(**filters: Any) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in filters.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        cleaned[key] = value
    return cleaned


def build_paginated_payload(
    *,
    items: list[Any],
    total: int,
    page: int,
    limit: int,
    applied_filters: Optional[dict[str, Any]] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    payload = {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages(total, limit),
        "applied_filters": applied_filters or {},
        # campos legados preservados para o frontend antigo
        "per_page": limit,
        "pages": total_pages(total, limit),
    }
    if extra:
        payload.update(extra)
    return payload


def parse_datetime_filter(value: Optional[str], *, end_of_day: bool = False) -> Optional[datetime]:
    if value is None:
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        if len(raw) == 10:
            parsed = datetime.fromisoformat(raw)
            return datetime.combine(parsed.date(), time.max if end_of_day else time.min)
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed
    except ValueError:
        return None
