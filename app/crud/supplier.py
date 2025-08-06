# hive_api/app/db/uicomponent.py
from contextlib import contextmanager
from typing import List

from app.db.database import SessionLocal
from app.db.models.supplier import Supplier as SupplierModel
from app.db.schemas.supplier import SupplierCreate

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

def get_all_suppliers() -> List[dict]:
    with session_scope() as db:
        rows = (
            db.query(SupplierModel.id, SupplierModel.name, SupplierModel.address, SupplierModel.client_number, 
                     SupplierModel.monthly_payment)
            .order_by(SupplierModel.name)
            .all()
        )
        return [
            {"id": r.id, "name": r.name, "address": r.address, "client_Number": r.client_number,
             "monthly_payment": r.monthly_payment } for r in rows
        ]


def create_supplier(data: SupplierCreate) -> dict:
    with session_scope() as db:
        new_supplier = SupplierModel(SupplierModel.id, SupplierModel.name, SupplierModel.address, SupplierModel.client_number, 
                               SupplierModel.monthly_payment)
        db.add(new_supplier)
        db.flush()           # assign PK without separate SELECT
        return {
            "id": new_supplier.id,
            "name": new_supplier.name,
            "address": new_supplier.address,
            "client_number": new_supplier.client_number,
            "monthly_payment": new_supplier.monthly_payment,
        }
