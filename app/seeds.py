import asyncio
from app.database import AsyncSessionLocal
from app.models.case import Case, CaseMode
from app.models.user import User, UserRole
from app.core.security import hash_password


async def seed():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            __import__('sqlalchemy', fromlist=['select']).select(User).where(User.email == "admin@fmea.com")
        )
        admin = result.scalar_one_or_none()

        if not admin:
            admin = User(
                email="admin@fmea.com",
                hashed_password=hash_password("admin123"),
                full_name="Platform Admin",
                role=UserRole.ADMIN,
                is_usf=False,
            )
            db.add(admin)
            await db.flush()
            await db.refresh(admin)
            print("Admin user created")
        else:
            print("Admin already exists")

        result = await db.execute(
            __import__('sqlalchemy', fromlist=['select']).select(Case).where(Case.title == "Travis Whitaker - CHF Exacerbation")
        )
        existing = result.scalar_one_or_none()

        if not existing:
            case = Case(
                title="Travis Whitaker - CHF Exacerbation",
                description=(
                    "Travis Whitaker is a 68 YO male who presented to the ER three days ago during the middle "
                    "of the night (0100) with CHF exacerbation due to fluid overload. He has a PMH of HFrEF "
                    "15-20%, atrial fibrillation (on amiodarone), CKD, and T2DM. TW was able to provide only "
                    "the names of medications he is taking and was unable to provide additional information "
                    "during the medication history process performed upon intake into the ER."
                ),
                patient_info={
                    "name": "Travis Whitaker",
                    "age": 68,
                    "gender": "Male",
                    "presentation_time": "0100",
                    "chief_complaint": "CHF exacerbation due to fluid overload",
                    "pmh": [
                        "HFrEF 15-20%",
                        "Atrial fibrillation (on amiodarone)",
                        "CKD",
                        "T2DM",
                    ],
                    "current_medications": "Patient able to provide names only",
                    "er_pharmacy_satellite_hours": "0700-2300",
                    "after_hours_coverage": "Main pharmacy with nurse-obtained medication histories",
                    "rca_details": {
                        "admission_unit": "Cardiac Unit",
                        "admission_time": "0530",
                        "potassium_on_admission": "5.7 mmol/L",
                        "potassium_day_3": "6.8 mmol/L",
                        "ecg_finding": "Peaked T-waves",
                        "medication_concern": "Entresto dosed from previous admission records without daily lab monitoring",
                    },
                },
                mode=CaseMode.EXERCISE,
                allow_resubmit=True,
                created_by=admin.id,
            )
            db.add(case)
            await db.flush()
            print("Travis Whitaker case seeded")
        else:
            print("Case already exists")

        await db.commit()
        print("Seeding complete")


if __name__ == "__main__":
    asyncio.run(seed())