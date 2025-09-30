import os
from .. import database, models

# Toggle saving with env var: SAVE_TO_DB=true
SAVE_TO_DB = os.getenv("SAVE_TO_DB", "false").lower() == "true"

def save_result(result: dict):
    if not SAVE_TO_DB or database.SessionLocal is None:
        return None

    try:
        db = database.SessionLocal()
        db_result = models.Result(**result)
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    except Exception as e:
        print(f"[db_service] Failed to save result: {e}")
        return None
    finally:
        if 'db' in locals():
            db.close()