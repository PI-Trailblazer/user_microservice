from sqlalchemy.sql import text
from alembic import command, config

from .session import engine
from app.utils import ROOT_DIR
from app.core.config import settings

last_known_revision = "e63d7af6ac9f"

def init_db() -> None:
    if not settings.PRODUCTION:
        # Create schema if not exists
        with engine.connect() as conn:
            cfg = config.Config(f"{ROOT_DIR}/alembic.ini")
            cfg.attributes["connection"] = conn
            cfg.attributes["configure_logger"] = False
            command.upgrade(cfg, last_known_revision)

            conn.commit()