# hive_api/app/db/uicomponent.py
from contextlib import contextmanager
from typing import List

from app.db.database import SessionLocal
from app.db.models.uicomponent import UIComponent as UIModel
from app.db.schemas import UIComponentCreate

@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ---------- Public helpers ----------

def get_all_uicomponents() -> List[dict]:
    with session_scope() as db:
        rows = (
            db.query(UIModel.id, UIModel.name, UIModel.is_visible)
            .order_by(UIModel.name)
            .all()
        )
        return [
            {"id": r.id, "name": r.name, "is_visible": r.is_visible} for r in rows
        ]


def create_uicomponent(data: UIComponentCreate) -> dict:
    with session_scope() as db:
        new_ui = UIModel(name=data.name, is_visible=data.is_visible)
        db.add(new_ui)
        db.flush()           # assign PK without separate SELECT
        return {
            "id": new_ui.id,
            "name": new_ui.name,
            "is_visible": new_ui.is_visible,
        }
