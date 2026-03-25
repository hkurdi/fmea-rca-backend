import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.case import Case, CaseMode
from app.models.user import User, UserRole
from app.models.course import Course
from app.core.security import hash_password


CASES = [
    {
        "title": "Travis Whitaker — CHF Exacerbation & Medication Reconciliation Failure",
        "description": (
            "Travis Whitaker is a 68-year-old male who presented to the ER at 0100 with CHF exacerbation "
            "due to fluid overload. He has a PMH of HFrEF 15-20%, atrial fibrillation (on amiodarone), "
            "CKD, and T2DM. The ER pharmacy satellite operates 0700-2300 only. After hours, nurses obtained "
            "the medication history without a standardized protocol, leading to critical reconciliation gaps "
            "and a dangerous potassium elevation by day 3."
        ),
        "patient_info": {
            "name": "Travis Whitaker",
            "age": 68,
            "gender": "Male",
            "presentation_time": "0100",
            "chief_complaint": "CHF exacerbation due to fluid overload",
            "pmh": [
                "HFrEF 15-20%",
                "Atrial fibrillation (on amiodarone)",
                "Chronic Kidney Disease (CKD)",
                "Type 2 Diabetes Mellitus (T2DM)",
            ],
            "current_medications": "Patient able to provide names only; doses and frequencies unknown",
            "er_pharmacy_satellite_hours": "0700–2300",
            "after_hours_coverage": "Main pharmacy; medication histories obtained by nurses without standardized protocol",
            "rca_details": {
                "admission_unit": "Cardiac Unit",
                "admission_time": "0530",
                "potassium_on_admission": "5.7 mmol/L",
                "potassium_day_3": "6.8 mmol/L",
                "ecg_finding": "Peaked T-waves consistent with hyperkalemia",
                "medication_concern": (
                    "Entresto (sacubitril/valsartan) re-dosed based on previous admission records "
                    "without daily lab monitoring. Combined with ACE inhibitor not identified during "
                    "reconciliation, leading to dangerous potassium accumulation in a CKD patient."
                ),
            },
        },
        "mode": CaseMode.EXERCISE,
        "allow_resubmit": True,
    },
    {
        "title": "Maria Gonzalez — Post-Surgical Handoff Failure & DVT",
        "description": (
            "Maria Gonzalez is a 54-year-old female who underwent elective left total knee replacement. "
            "During transfer from the PACU to the orthopedic floor, critical VTE prophylaxis orders were "
            "not communicated. She developed a DVT on post-op day 2 that progressed to a pulmonary embolism "
            "requiring ICU admission. The case centers on handoff communication gaps and the absence of a "
            "standardized surgical transfer checklist."
        ),
        "patient_info": {
            "name": "Maria Gonzalez",
            "age": 54,
            "gender": "Female",
            "presentation_time": "Elective surgical admission at 0630",
            "chief_complaint": "Elective left total knee replacement (TKR)",
            "pmh": [
                "Osteoarthritis (bilateral knees)",
                "Hypertension",
                "Obesity (BMI 33)",
                "Non-smoker",
            ],
            "current_medications": "Lisinopril 10mg daily, Ibuprofen 400mg PRN",
            "er_pharmacy_satellite_hours": "N/A — inpatient surgical admission",
            "after_hours_coverage": "On-call orthopedic resident; covering floor nurse unfamiliar with patient",
            "rca_details": {
                "admission_unit": "Orthopedic Surgical Floor (4 West)",
                "admission_time": "Transfer from PACU at 1545",
                "potassium_on_admission": "4.1 mmol/L",
                "potassium_day_3": "N/A",
                "ecg_finding": "Sinus tachycardia on day 2 (HR 112)",
                "medication_concern": (
                    "Enoxaparin VTE prophylaxis ordered in PACU but not carried over in transfer note. "
                    "Covering nurse assumed it had been given. First dose delayed by 22 hours. "
                    "DVT detected on post-op day 2 via doppler after new onset leg swelling and shortness of breath."
                ),
            },
        },
        "mode": CaseMode.EXERCISE,
        "allow_resubmit": True,
    },
    {
        "title": "James Okafor — Pediatric Weight-Based Dosing Error in the ED",
        "description": (
            "James Okafor is a 7-year-old male (22 kg) brought to the pediatric ED with status epilepticus. "
            "In the high-stress resuscitation environment, the on-call resident calculated the IV lorazepam "
            "dose using the patient's documented weight from a clinic visit 8 months prior (18 kg). "
            "The resulting underdose failed to terminate the seizure, causing a 12-minute delay before "
            "a second agent was administered. This case focuses on weight verification workflows and "
            "cognitive overload in emergency pediatric dosing."
        ),
        "patient_info": {
            "name": "James Okafor",
            "age": 7,
            "gender": "Male",
            "presentation_time": "2215",
            "chief_complaint": "Status epilepticus — generalized tonic-clonic seizure lasting >5 minutes on arrival",
            "pmh": [
                "Epilepsy (diagnosed age 5, on levetiracetam)",
                "No known drug allergies",
                "Recent fever x2 days (viral URI suspected)",
            ],
            "current_medications": "Levetiracetam 500mg BID (per parent); last dose this morning",
            "er_pharmacy_satellite_hours": "Pediatric ED pharmacy available 0800–2000; after hours on-call",
            "after_hours_coverage": "On-call pharmacist via phone; no bedside pharmacy presence after 2000",
            "rca_details": {
                "admission_unit": "Pediatric Emergency Department → PICU",
                "admission_time": "2215 (ED); PICU transfer at 0130",
                "potassium_on_admission": "3.9 mmol/L",
                "potassium_day_3": "N/A",
                "ecg_finding": "Post-ictal sinus bradycardia (HR 54), resolved spontaneously",
                "medication_concern": (
                    "IV lorazepam dosed at 0.05 mg/kg using stale EHR weight of 18 kg (actual 22 kg). "
                    "Underdose of 0.9 mg administered instead of correct 1.1 mg. Seizure continued for "
                    "12 additional minutes. Second-line levetiracetam IV then administered. No Broselow "
                    "tape or bedside weight obtained on arrival per unit protocol gap."
                ),
            },
        },
        "mode": CaseMode.EXERCISE,
        "allow_resubmit": True,
    },
    {
        "title": "Dorothy Chen — High-Alert Insulin Overdose on Med-Surg Floor",
        "description": (
            "Dorothy Chen is a 71-year-old female admitted for cellulitis of the right lower extremity. "
            "She has a known history of T2DM managed with insulin glargine. During the night shift, a "
            "nurse scanned the wrong patient's MAR on a shared workstation and administered 40 units of "
            "insulin glargine intended for a different patient. Dorothy's prescribed dose was 12 units. "
            "She was found unresponsive at 0330 with a glucose of 28 mg/dL. This case examines "
            "barcode medication administration failures and alert fatigue."
        ),
        "patient_info": {
            "name": "Dorothy Chen",
            "age": 71,
            "gender": "Female",
            "presentation_time": "Admitted via ED at 1400 for right lower extremity cellulitis",
            "chief_complaint": "Right lower extremity cellulitis with systemic signs of infection",
            "pmh": [
                "Type 2 Diabetes Mellitus (on insulin)",
                "Hypertension",
                "Mild cognitive impairment",
                "Hypothyroidism",
            ],
            "current_medications": (
                "Insulin glargine 12 units QHS, Lisinopril 5mg daily, "
                "Levothyroxine 50mcg daily, Cephalexin 500mg QID (new)"
            ),
            "er_pharmacy_satellite_hours": "0700–2300 (Med-Surg satellite); overnight on-call pharmacist",
            "after_hours_coverage": "Overnight nurse-to-pharmacist phone consultation only; no pharmacist rounding",
            "rca_details": {
                "admission_unit": "Medical-Surgical Floor (6 North)",
                "admission_time": "1600 (floor admission)",
                "potassium_on_admission": "4.3 mmol/L",
                "potassium_day_3": "3.8 mmol/L",
                "ecg_finding": "Normal sinus rhythm on admission; tachycardia (HR 118) noted at 0330 incident",
                "medication_concern": (
                    "Night nurse logged into shared workstation, previous session still active for adjacent "
                    "patient. BCMA scan performed on wrong MAR. Override alert for dose variance (40u vs 12u) "
                    "was acknowledged and bypassed — nurse assumed it was a legitimate high dose for a "
                    "different patient profile. Patient found unresponsive at 0330, glucose 28 mg/dL. "
                    "D50 administered x2, transferred to ICU for monitoring."
                ),
            },
        },
        "mode": CaseMode.ASSESSMENT,
        "allow_resubmit": False,
    },
    {
        "title": "Robert Anand — Delayed Sepsis Recognition in a Long-Term Care Transfer",
        "description": (
            "Robert Anand is an 83-year-old male transferred from a skilled nursing facility (SNF) to the "
            "hospital ED with altered mental status and a documented 'urinary tract infection' per SNF staff. "
            "Initial ED triage classified him as low-acuity. Over 4 hours, his condition deteriorated. "
            "Sepsis criteria were met on arrival but not recognized until lactic acid returned at 6.2 mmol/L. "
            "The 4-hour delay in the sepsis bundle initiation is the focus of this FMEA and RCA."
        ),
        "patient_info": {
            "name": "Robert Anand",
            "age": 83,
            "gender": "Male",
            "presentation_time": "1340 (ED arrival via SNF transport)",
            "chief_complaint": "Altered mental status, low-grade fever, decreased urine output per SNF report",
            "pmh": [
                "Dementia (moderate stage)",
                "Benign Prostatic Hyperplasia (BPH)",
                "Atrial fibrillation (on apixaban)",
                "Type 2 Diabetes Mellitus",
                "Prior CVA with residual right-sided weakness",
            ],
            "current_medications": (
                "Apixaban 2.5mg BID, Metformin 500mg BID (held per SNF), "
                "Tamsulosin 0.4mg QHS, Donepezil 10mg QHS, Aspirin 81mg daily"
            ),
            "er_pharmacy_satellite_hours": "0700–2300 (ED pharmacy); overnight on-call",
            "after_hours_coverage": "Afternoon shift handoff occurred at 1500 during patient workup; new team assumed prior team had initiated sepsis screen",
            "rca_details": {
                "admission_unit": "Emergency Department → Medical ICU",
                "admission_time": "1340 (ED); MICU transfer at 1820",
                "potassium_on_admission": "5.1 mmol/L",
                "potassium_day_3": "4.6 mmol/L",
                "ecg_finding": "Atrial fibrillation with rapid ventricular response (HR 128) on arrival ECG",
                "medication_concern": (
                    "Sepsis bundle (blood cultures x2, IV fluids 30 mL/kg, broad-spectrum antibiotics, "
                    "lactate) delayed 4 hours from ED arrival. Triage nurse documented AMS as 'baseline per SNF' "
                    "without SIRS screen. Handoff at 1500 shift change did not flag pending sepsis workup. "
                    "Lactic acid resulted at 1740 (6.2 mmol/L). Antibiotics not initiated until 1755. "
                    "MICU team noted apixaban on board — held TPA as thrombolysis option. "
                    "Patient required vasopressors within 2 hours of MICU admission."
                ),
            },
        },
        "mode": CaseMode.ASSESSMENT,
        "allow_resubmit": False,
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@fmea.com"))
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
            print("✓ Admin user created — admin@fmea.com / admin123")
        else:
            print("· Admin already exists")
            
        result = await db.execute(select(User).where(User.email == "instructor@fmea.com"))
        instructor = result.scalar_one_or_none()
        if not instructor:
            instructor = User(
                email="instructor@fmea.com",
                hashed_password=hash_password("instructor123"),
                full_name="Dr. John Templeton",
                role=UserRole.INSTRUCTOR,
                is_usf=True,
            )
            db.add(instructor)
            await db.flush()
            await db.refresh(instructor)
            print("✓ Instructor created — instructor@fmea.com / instructor123")
        else:
            print("· Instructor already exists")
            
        result = await db.execute(select(User).where(User.email == "student@fmea.com"))
        student = result.scalar_one_or_none()
        if not student:
            student = User(
                email="student@fmea.com",
                hashed_password=hash_password("student123"),
                full_name="Alex Rivera",
                role=UserRole.STUDENT,
                is_usf=True,
            )
            db.add(student)
            await db.flush()
            await db.refresh(student)
            print("✓ Demo student created — student@fmea.com / student123")
        else:
            print("· Demo student already exists")

        result = await db.execute(select(Course).where(Course.name == "CAP6505 — Smart Health Spring 2026"))
        course = result.scalar_one_or_none()
        if not course:
            course = Course(
                name="CAP6505 — Smart Health Spring 2026",
                description="Healthcare FMEA and Root Cause Analysis — Spring 2026",
                instructor_id=instructor.id,
            )
            db.add(course)
            await db.flush()
            await db.refresh(course)
            print(f"✓ Course created — ID: {course.id}")
        else:
            print(f"· Course already exists — ID: {course.id}")
            
        for case_data in CASES:
            result = await db.execute(select(Case).where(Case.title == case_data["title"]))
            existing = result.scalar_one_or_none()
            if not existing:
                case = Case(
                    title=case_data["title"],
                    description=case_data["description"],
                    patient_info=case_data["patient_info"],
                    mode=case_data["mode"],
                    allow_resubmit=case_data["allow_resubmit"],
                    created_by=instructor.id,
                )
                db.add(case)
                await db.flush()
                print(f"✓ Case seeded — {case_data['title'][:60]}...")
            else:
                print(f"· Case already exists — {case_data['title'][:60]}...")

        await db.commit()
        print("\nSeeding complete.")
        print("─────────────────────────────────────────")
        print("Credentials:")
        print("  Admin:      admin@fmea.com / admin123")
        print("  Instructor: instructor@fmea.com / instructor123")
        print("  Student:    student@fmea.com / student123")


if __name__ == "__main__":
    asyncio.run(seed())