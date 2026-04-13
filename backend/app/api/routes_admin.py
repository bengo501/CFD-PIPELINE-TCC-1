"""
rotas administrativas apenas para desenvolvimento (encerrar o processo do servidor).
protegidas por variável de ambiente ALLOW_DEV_SHUTDOWN.
"""
import os
import threading
import time

from fastapi import APIRouter, HTTPException

router = APIRouter()


def _shutdown_allowed() -> bool:
    v = os.getenv("ALLOW_DEV_SHUTDOWN", "").strip().lower()
    return v in ("1", "true", "yes", "on")


@router.post("/admin/dev/shutdown", tags=["admin"])
async def dev_shutdown():
    """
    encerra o processo python do uvicorn após uma breve pausa.
    o reinício real depende de systemd, docker compose, script manual, etc.
    """
    if not _shutdown_allowed():
        raise HTTPException(
            status_code=403,
            detail="encerramento via api desativado (defina ALLOW_DEV_SHUTDOWN=1 no ambiente do servidor)",
        )

    def _delayed_exit():
        time.sleep(0.4)
        os._exit(0)

    threading.Thread(target=_delayed_exit, daemon=True).start()
    return {"ok": True, "detail": "servidor a encerrar"}

