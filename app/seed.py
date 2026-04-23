from app.database import SessionLocal
from app.models import Committee, SystemSettings

# Committees ordered by difficulty/prestige (hardest first)
COMMITTEES = [
    # Hardest/Most Prestigious
    {"short_name": "UNSC",   "full_name": "United Nations Security Council",               "language": "English",       "total_seats": 50, "last_sequence": 0},
    {"short_name": "UNGA",   "full_name": "United Nations General Assembly",              "language": "English",       "total_seats": 50, "last_sequence": 0},
    {"short_name": "UNHRC",  "full_name": "United Nations Human Rights Council",           "language": "English",       "total_seats": 50, "last_sequence": 0},
    {"short_name": "DISEC",  "full_name": "Disarmament and International Security Committee", "language": "English",   "total_seats": 50, "last_sequence": 0},
    {"short_name": "UNODC",  "full_name": "United Nations Office on Drugs and Crime",     "language": "English",       "total_seats": 50, "last_sequence": 0},
    {"short_name": "PNA",    "full_name": "Pakistan National Assembly",                   "language": "Urdu & English", "total_seats": 50, "last_sequence": 0},
    # New Committees
    {"short_name": "UNW",    "full_name": "United Nations for Women", "language": "English", "total_seats": 50, "last_sequence": 0},
    {"short_name": "JSP",    "full_name": "Joint Session of Parliament",                  "language": "Urdu & English", "total_seats": 50, "last_sequence": 0},
    {"short_name": "NCC",    "full_name": "National Crisis Committee",                    "language": "English", "total_seats": 50, "last_sequence": 0},
]

SETTINGS = [
    {"key": "event_name", "value": "LGUMUN 2026 — Inter-University MUN", "description": "Official title of the event"},
    {"key": "event_date", "value": "2026-06-15", "description": "Main event date"},
    {"key": "event_venue", "value": "Lahore Garrison University, Lahore", "description": "Venue address"},
    {"key": "registration_open", "value": "true", "description": "Whether new registrations are allowed"},
    {"key": "transfers_open", "value": "true", "description": "Whether committee transfers are allowed"},
]

def seed():
    db = SessionLocal()
    try:
        print("Seeding committees...")
        for data in COMMITTEES:
            exists = db.query(Committee).filter_by(short_name=data["short_name"]).first()
            if not exists:
                db.add(Committee(**data))
                print(f"  Inserted: {data['short_name']}")
            else:
                print(f"  Skipped (exists): {data['short_name']}")

        print("\nSeeding settings...")
        for data in SETTINGS:
            exists = db.query(SystemSettings).filter_by(key=data["key"]).first()
            if not exists:
                db.add(SystemSettings(**data))
                print(f"  Inserted: {data['key']}")
            else:
                print(f"  Skipped (exists): {data['key']}")

        db.commit()
        print("\nSeed complete.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()

