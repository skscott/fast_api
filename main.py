from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine, SessionLocal
from app.db.models import UIComponent as UIModel, User as UserModel, Reading
from app.core.security import get_password_hash

from app.db.models.user import User as UserModel
from app.db.models.uicomponent import UIComponent as UIModel
from app.db import uicomponent
from app.db.schemas import UIComponentCreate

from app.routes import drone_registry, reading, auth, uicomponent

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
app.include_router(drone_registry.router)


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
