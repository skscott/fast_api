from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine, SessionLocal
from app.db.models import UIComponent as UIModel, User as UserModel, Reading
from app.core.security import get_password_hash

from app.db.models.user import User as UserModel
from app.db.models.uicomponent import UIComponent as UIModel
from app.db import uicomponent

from app.db.models.supplier import Supplier as SupplierModel
import app.db.supplier as supplier_models  # ← renamed
import app.routes.supplier as supplier_routes  # ← renamed


from app.routes import reading, auth, uicomponent, supplier

from sqlalchemy.exc import IntegrityError
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🛠️ Create tables
    print("🔍 Registered tables:", Base.metadata.tables.keys())
    
    Base.metadata.create_all(bind=engine)

    # 🧬 Seed data
    db = SessionLocal()
    try:
        if db.query(UserModel).count() == 0:
            admin = UserModel(
                username="s.scott@casema.nl",
                hashed_password=get_password_hash("0394Scotty")
            )
            db.add(admin)
            print("✅ Default admin user created.")

        if db.query(UIModel).count() == 0:
            default_components = [
                UIModel(name="Dashboards", is_visible=True),
                UIModel(name="HiveMind", is_visible=True),
                # UIModel(name="ShutdownButton", is_visible=True),
            ]
            db.add_all(default_components)
            print("✅ Default UI components created.")

        from decimal import Decimal

        try:
            print("👀 Checking supplier count...")
            count = db.query(SupplierModel).count()
            print(f"📊 Supplier count = {count}")
            if db.query(SupplierModel).count() == 0:
                default_suppliers = [
                    SupplierModel(name="Essent Retail Energie B.V.",
                                address="Postbus 1484, 5200 BM Hertogenbosch.",
                                client_number="172351027",
                                monthly_payment=Decimal("115")),
                    SupplierModel(name="N.V. Nuon Energie",
                                address="Hoekenrode 8 1102 BR Amsterdam",
                                client_number="257081321",
                                monthly_payment=Decimal("100")),
                    SupplierModel(name="Vandenbron",
                                address="Torenallee 32-10 5617 BD Eindhoven",
                                client_number="2117826",
                                monthly_payment=Decimal("0")),
                    SupplierModel(name="EnergieFlex",
                                address="Johan Huizingalaan  400  1066JS Amsterdam",
                                client_number="67414",
                                monthly_payment=Decimal("132")),
                    SupplierModel(name="Nederlandse Energie Matschappij",
                                address="Aert van Nesstraat 45 3012 CA Rotterdam",
                                client_number="3000442533",
                                monthly_payment=Decimal("175")),
                    SupplierModel(name="Budget Energie",
                                address="tba",
                                client_number="3285822",
                                monthly_payment=Decimal("0")),
                    SupplierModel(name="Eneco",
                                address="Postbus 10",
                                client_number="Postbus 10",
                                monthly_payment=Decimal("331")),
                ]

                db.add_all(default_suppliers)
                db.commit()
                print("✅ Default Suppliers created.")
        except Exception as e:
            print("❌ Exception when querying suppliers:", e)

        db.commit()
    except IntegrityError:
        db.rollback()
        print("⚠️ Seed data conflict — skipping.")
    finally:
        db.close()

    yield  # Let the app run

# 🚀 Create the FastAPI app using the lifespan
app = FastAPI(lifespan=lifespan)

# 📡 Include your routers
# hivemind routes
app.include_router(reading.router)
app.include_router(auth.router)
app.include_router(uicomponent.router)
app.include_router(reading.router)
app.include_router(supplier_routes.router)


# 🌐 CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
