from app.database import SessionLocal
from app.models import Committee

COMMITTEES = [
    {"short_name": "UNGA",   "full_name": "United Nations General Assembly",              "language": "English",       "total_seats": 30},
    {"short_name": "UNSC",   "full_name": "United Nations Security Council",               "language": "English",       "total_seats": 15},
    {"short_name": "UNHRC",  "full_name": "United Nations Human Rights Council",           "language": "English",       "total_seats": 30},
    {"short_name": "ECOSOC", "full_name": "United Nations Economic and Social Council",    "language": "English",       "total_seats": 30},
    {"short_name": "WHO",    "full_name": "World Health Organization",                     "language": "English",       "total_seats": 30},
    {"short_name": "UNDP",   "full_name": "United Nations Development Programme",          "language": "English",       "total_seats": 30},
    {"short_name": "DISEC",  "full_name": "Disarmament and International Security Committee", "language": "English",   "total_seats": 30},
    {"short_name": "UNODC",  "full_name": "United Nations Office on Drugs and Crime",     "language": "English",       "total_seats": 30},
    {"short_name": "PNA",    "full_name": "Pakistan National Assembly",                   "language": "Urdu & English", "total_seats": 30},
]

def seed():
    db = SessionLocal()
    try:
        for data in COMMITTEES:
            exists = db.query(Committee).filter_by(short_name=data["short_name"]).first()
            if not exists:
                db.add(Committee(**data))
                print(f"  Inserted: {data['short_name']}")
            else:
                print(f"  Skipped (exists): {data['short_name']}")
        db.commit()
        print("Seed complete.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
