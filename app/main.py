# main.py
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime, date

from app.crud import contract
from app.db.database import Base, engine, SessionLocal
from app.db.models import UIComponent as UIModel, User as UserModel, Supplier as SupplierModel, Contract as ContractModel, UIComponent as UIModel
from app.db.models.utility import Utility as UtilityModel
from app.core.security import get_password_hash

from app.routes import import_readings, reading, auth, uicomponent, contract, supplier, utility
from decimal import Decimal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only enable debug if explicitly requested
    if os.getenv("DEBUG_MODE") == "1":
        try:
            import debugpy
            base_port = 5678
            port = base_port
            while port < base_port + 10:  # Try 10 ports max
                try:
                    debugpy.listen(("0.0.0.0", port))
                    print(f"✅ debugpy listening on port {port}")
                    break
                except OSError:
                    print(f"⚠️ Port {port} in use, trying {port + 1}...")
                    port += 1
            else:
                print("❌ No free debugpy port found in range.")
        except ImportError:
            print("⚠️ debugpy not installed, skipping remote debugging")
            
    yield
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
                SupplierModel(name="SBSS Solar Energy",
                            address="Marshallsingel 38",
                            client_number="1",
                            monthly_payment=Decimal("0")),
            ]

            db.add_all(default_suppliers)
            db.commit()
            print("✅ Default Suppliers created.")

        print("👀 Checking contract count...")
        count = db.query(ContractModel).count()
        print(f"📊 Contract count = {count}")        

        if db.query(ContractModel).count() == 0:
            sbss = db.query(SupplierModel).filter_by(name="SBSS Solar Energy").first()
            #
            # Gas and electric
            #
            default_contracts = [
            ContractModel(
                name="2014-2015 NLE",
                description="NLE Gas and Electra",
                start_date=date(2014, 9, 4),
                end_date=date(2015, 9, 3),
                monthly_payment=Decimal("175"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=5
            ),
            ContractModel(
                name="2016-2017 Vandebron Gas and Electra",
                description="2016-2017 Vandenbron Gas and Electra 1 Jaar Vast Consumentenbond",
                start_date=date(2015, 9, 5),
                end_date=date(2017, 9, 30),
                monthly_payment=Decimal("100"),
                settlement_pdf="",
                contract_pdf="Contract_1187LG38_2016-09-23.pdf",
                supplier_id=3
            ),
            ContractModel(
                name="2018 EnergyFlex",
                description="EnergyFlex Gas and electric",
                start_date=date(2017, 10, 1),
                end_date=date(2019, 11, 30),
                monthly_payment=Decimal("100"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=4
            ),
            ContractModel(
                name="2019 Nuon",
                description="Nuon gas and electric",
                start_date=date(2019, 12, 1),
                end_date=date(2020, 11, 30),
                monthly_payment=Decimal("100"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=2
            ),
            ContractModel(
                name="2020 Essent Combo",
                description="Essent Gas and electric",
                start_date=date(2020, 12, 1),
                end_date=date(2022, 11, 30),
                monthly_payment=Decimal("115"),
                settlement_pdf="Jaarrekening.pdf",
                contract_pdf="Essent 2020 tarieven.pdf",
                supplier_id=1
            ),
            ContractModel(
                name="2022 Essent",
                description="Essent gas and electric 2022",
                start_date=date(2022, 12, 1),
                end_date=date(2023, 10, 31),
                monthly_payment=Decimal("150"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=1
            ),
            ContractModel(
                name="2023 Essent",
                description="Essent gas and electric 2023",
                start_date=date(2022, 12, 1),
                end_date=date(2023, 10, 31),
                monthly_payment=Decimal("150"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=1
            ),
            ContractModel(
                name="2024 Eneco Stroom en Gas",
                description="Eneco Wind, Zon en Gas",
                start_date=date(2023, 11, 1),
                end_date=date(2024, 11, 17),
                monthly_payment=Decimal("39"),
                settlement_pdf="",
                contract_pdf="Contract_Eneco_2024.pdf",
                supplier_id=7
            ),
            ContractModel(
                name="Essent 2025",
                description="Gas and Electra",
                start_date=date(2024, 11, 18),
                end_date=date(2025, 11, 30),
                monthly_payment=Decimal("66"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=1
            ),
            # 
            # Solar
            #
            ContractModel(
                name="SBSS Solar Energy 2023",
                description="Solar energy from 10 solar panels",
                start_date=date(2023, 2, 16),
                end_date=date(2023, 12, 31),
                monthly_payment=Decimal("0"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=sbss.id
            ),
            ContractModel(
                name="SBSS Solar Energy 2024",
                description="Solar energy from 10 solar panels",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                monthly_payment=Decimal("0"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=sbss.id
            ),
            ContractModel(
                name="SBSS Solar Energy 2025",
                description="Solar energy from 10 solar panels",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                monthly_payment=Decimal("0"),
                settlement_pdf="",
                contract_pdf="",
                supplier_id=sbss.id
            ),
            ]
            db.add_all(default_contracts)
            db.commit()
            print("✅ Default Contracts created.")

        # Add this to your lifespan() block after contracts
        print("\U0001F50D Checking utility count...")
        if db.query(UtilityModel).count() == 0:
            nuon_2019 = db.query(ContractModel).filter_by(name="2019 Nuon").first()
            essent_2021 = db.query(ContractModel).filter_by(name="2020 Essent Combo").first()
            essent_2022 = db.query(ContractModel).filter_by(name="2022 Essent").first()
            essent_2023 = db.query(ContractModel).filter_by(name="2023 Essent").first()
            eneco_2024 = db.query(ContractModel).filter_by(name="2024 Eneco Stroom en Gas").first()
            essent_2025 = db.query(ContractModel).filter_by(name="Essent 2025").first()
            eflex_2018 = db.query(ContractModel).filter_by(name="2018 EnergyFlex").first()

            sbss_solar_2023 = db.query(ContractModel).filter_by(name="SBSS Solar Energy 2023").first()
            sbss_solar_2024 = db.query(ContractModel).filter_by(name="SBSS Solar Energy 2024").first()
            sbss_solar_2025 = db.query(ContractModel).filter_by(name="SBSS Solar Energy 2025").first()
 
            default_utilities = [
                UtilityModel(
                    type="NORMAL",
                    text="Energyflex Electra 2018",
                    description="Electricity for 2018",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=eflex_2018.id
                ),
                UtilityModel(
                    type="REDUCED",
                    text="Energyflex Reduced Electra 2018",
                    description="Electricity for 2018",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=eflex_2018.id
                ),
                UtilityModel(
                    type="GAS",
                    text="Energyflex Gas 2018",
                    description="Gas for 2018",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=eflex_2018.id
                ),

                UtilityModel(
                    type="NORMAL",
                    text="Nuon Electra 2019",
                    description="Electricity for 2019",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=nuon_2019.id
                ),
                UtilityModel(
                    type="REDUCED",
                    text="Nuon Electra 2019",
                    description="Electricity for 2019",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=nuon_2019.id
                ),
                UtilityModel(
                    type="GAS",
                    text="Nuon Gas 2019",
                    description="Gas for 2019",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=nuon_2019.id
                ),
                UtilityModel(
                    type="NORMAL",
                    text="Essent Electra 2021",
                    description="Electricity for 2021",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2021.id
                ),
                UtilityModel(
                    type="REDUCED",
                    text="Essent Electra 2021",
                    description="Electricity for 2021",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2021.id
                ),
                UtilityModel(
                    type="GAS",
                    text="Essent Gas 2021",
                    description="Gas for 2021",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2021.id
                ),
                UtilityModel(
                    type="NORMAL",
                    text="Essent Electra 2022",
                    description="Electricity for 2022",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2022.id
                ),
                UtilityModel(
                    type="REDUCED",
                    text="Essent Electra 2022",
                    description="Electricity for 2022",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2022.id
                ),
                UtilityModel(
                    type="GAS",
                    text="Essent Gas 2022",
                    description="Gas for 2022",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2022.id
                ),
                UtilityModel(
                    type="NORMAL",
                    text="Eelectric 2023",
                    description="Gas and Electric 2023",
                    start_reading=Decimal("51305"),
                    end_reading=Decimal("51931"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2023.id
                ),                UtilityModel(
                type="REDUCED",
                    text="Eelectric 2023",
                    description="Gas and Electric 2023",
                    start_reading=Decimal("51305"),
                    end_reading=Decimal("51931"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2023.id
                ),
                UtilityModel(
                    type="GAS",
                    text="Gas 2023",
                    description="Essent gas and electric 2023",
                    start_reading=Decimal("39122"),
                    end_reading=Decimal("39437.63"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2023.id
                ),
                UtilityModel(
                    type="NORMAL",
                    text="Startdatum levering : 31 oktober 2023 Einddatum vaste looptijd : 30 oktober 2024",
                    description="Eneco HollandseWind & Zon Actie 1 jaar",
                    start_reading=Decimal("51904"),
                    end_reading=Decimal("53067"),
                    estimated_use=Decimal("0"),
                    contract_id=eneco_2024.id
                ),
                UtilityModel(
                    type="REDUCED",
                    text="Startdatum levering : 31 oktober 2023 Einddatum vaste looptijd : 30 oktober 2024",
                    description="Eneco HollandseWind & Zon Actie 1 jaar",
                    start_reading=Decimal("51904"),
                    end_reading=Decimal("53067"),
                    estimated_use=Decimal("0"),
                    contract_id=eneco_2024.id
                ),
                UtilityModel(
                    type="GAS",
                    text="Startdatum levering : 31 oktober 2023 Einddatum vaste looptijd : 30 oktober 2024",
                    description="Eneco Gas Actie 1 jaar",
                    start_reading=Decimal("39436.05"),
                    end_reading=Decimal("39713.25"),
                    estimated_use=Decimal("300"),
                    contract_id=eneco_2024.id
                ),
                UtilityModel(
                    type="NORMAL",
                    text="Essent Electra 2025",
                    description="Essent Electra",
                    start_reading=Decimal("51305"),
                    end_reading=Decimal("53716"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2025.id
                ),
                UtilityModel(
                    type="REDUCED",
                    text="Essent Electra 2025",
                    description="Essent Electra",
                    start_reading=Decimal("51305"),
                    end_reading=Decimal("53716"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2025.id
                ),
                UtilityModel(
                    type="GAS",
                    text="Essent Gas 2025",
                    description="Essent Gas",
                    start_reading=Decimal("51305"),
                    end_reading=Decimal("39911.77"),
                    estimated_use=Decimal("0"),
                    contract_id=essent_2025.id
                ),
                #
                # Solar Utility
                #
                UtilityModel(
                    type="SOLAR",
                    text="Empahse Enlighten Panels",
                    description="Solar Energy 2023",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=sbss_solar_2023.id
                ),
                UtilityModel(
                    type="SOLAR",
                    text="Empahse Enlighten Panels",
                    description="Solar Energy 2024",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=sbss_solar_2024.id
                ),
                UtilityModel(
                    type="SOLAR",
                    text="Empahse Enlighten Panels",
                    description="Solar Energy 2025",
                    start_reading=Decimal("0"),
                    end_reading=Decimal("0"),
                    estimated_use=Decimal("0"),
                    contract_id=sbss_solar_2025.id
                ),
            ]

            db.add_all(default_utilities)
            db.commit()
            print("\u2705 Default Utilities created.")

        db.commit()
    except IntegrityError:
        db.rollback()
        print("⚠️ Seed data conflict — skipping.")
    finally:
        db.close()

    yield  # Let the app run

# 🚀 Create the FastAPI app using the lifespan
app = FastAPI(lifespan=lifespan)

app.include_router(reading.router)
app.include_router(auth.router)
app.include_router(uicomponent.router)
app.include_router(reading.router)
app.include_router(supplier.router)
app.include_router(contract.router)
app.include_router(utility.router)
app.include_router(import_readings.router)

# 🌐 CORS
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
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
