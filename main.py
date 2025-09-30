import os
import subprocess
import re
import ssl
import socket
import time
from datetime import timedelta, datetime, timezone
from fastapi import FastAPI, HTTPException
from . import database, models, schemas
import fastapi_notes.services.db_services as db_services
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.hazmat.backends import default_backend

SAVE_TO_DB = os.getenv("SAVE_TO_DB", "false").lower() == "true"

start_time = time.time()
app = FastAPI()

# Routes
@app.post("/ping", response_model=schemas.CommandResult)
def run_ping(target: str):
    try:
        safe_target = validate_target(target)
        output = run_command(["ping", "-q", "-c", "4", safe_target], timeout=10)
        result = {
            "command": "ping",
            "target": target,
            "output": output,
            "created_at": datetime.now(timezone.utc)
        }
        db_services.save_result(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out")

@app.post("/curl", response_model=schemas.CommandResult)
def run_curl(target: str):
    try:
        safe_target = validate_target(target)
        output = run_command(["curl", "-s", safe_target], timeout=10)
        result = {
            "command": "curl",
            "target": target,
            "output": output,
            "created_at": datetime.now(timezone.utc)
        }
        db_services.save_result(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out")

@app.get("/cert")
def get_cert(host: str, port: int = 443):
    try:
        # open TLS connection
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                der_cert = ssock.getpeercert(binary_form=True)

        # parse with cryptography
        cert = x509.load_der_x509_certificate(der_cert, default_backend())

        subject = cert.subject.rfc4514_string()
        issuer = cert.issuer.rfc4514_string()
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
        san = []
        try:
            ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            san = ext.value.get_values_for_type(x509.DNSName)
        except Exception:
            pass

        # fingerprints (SHA1, SHA256)
        fingerprint_sha1 = cert.fingerprint(hashes.SHA1()).hex()
        fingerprint_sha256 = cert.fingerprint(hashes.SHA256()).hex()

        now = datetime.now(timezone.utc)
        days_remaining = (not_after - now).days

        return {
            "subject": subject,
            "issuer": issuer,
            "valid_from": not_before.isoformat(),
            "valid_until": not_after.isoformat(),
            "days_until_expiry": days_remaining,
            "subject_alternative_names": san,
            "fingerprints": {
                "sha1": fingerprint_sha1,
                "sha256": fingerprint_sha256,
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/status", response_model=schemas.Status)
def status():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    uptime_seconds = int(time.time() - start_time)
    uptime_str = str(timedelta(seconds=uptime_seconds))
    return {"status": "ok",
            "ip_address": ip,
            "uptime": uptime_str,
            "pod_name": os.getenv("POD_NAME", "unknown"),
            "namespace": os.getenv("POD_NAMESPACE", "unknown"),
            "node_name": os.getenv("NODE_NAME", "unknown")
        }

def validate_target(target: str):
    # allow IPv4, IPv6, or simple hostnames
    ipv4_regex = r"^([1-2]?[0-9]{1,2}\.?)+"
    hostname_regex = r"^[a-z0-9.]+$"
    url_regex = r"^https?:\/\/[a-z0-9.]+\.[a-z]+$"
    if not (
        re.match(ipv4_regex, target) or
        re.match(hostname_regex, target) or
        re.match(url_regex, target)
    ):
        raise ValueError("Invalid target")
    return target

def run_command(command: list[str], timeout: int = 10) -> str:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    return result.stdout or result.stderr

def get_container_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


# @app.get("/notes", response_model=list[schemas.NoteResponse])
# def read_notes():
#     db = database.SessionLocal()
#     notes = db.query(models.Note).all()
#     db.close()
#     return notes

# @app.get("/notes/{note_id}", response_model=schemas.NoteResponse)
# def read_note(note_id: int):
#     db = database.SessionLocal()
#     note = db.query(models.Note).filter(models.Note.id == note_id).first()
#     db.close()
#     if not note:
#         raise HTTPException(status_code=404, detail="Note not found")
#     return note

# @app.post("/notes", response_model=schemas.NoteResponse)
# def create_note(note: schemas.NoteCreate):
#     db = database.SessionLocal()
#     new_note = models.Note(title=note.title, content=note.content)
#     db.add(new_note)
#     db.commit()
#     db.refresh(new_note)
#     db.close()
#     return new_note

# @app.put("/notes/{note_id}", response_model=schemas.NoteResponse)
# def update_note(note_id: int, note: schemas.NoteUpdate):
#     db = database.SessionLocal()
#     db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
#     if not db_note:
#         db.close()
#         raise HTTPException(status_code=404, detail="Note not found")

#     # Update only provided fields
#     if note.title is not None:
#         db_note.title = note.title
#     if note.content is not None:
#         db_note.content = note.content

#     db.commit()
#     db.refresh(db_note)
#     db.close()
#     return db_note

# @app.delete("/notes/{note_id}")
# def delete_note(note_id: int):
#     db = database.SessionLocal()
#     note = db.query(models.Note).filter(models.Note.id == note_id).first()
#     if not note:
#         db.close()
#         raise HTTPException(status_code=404, detail="Note not found")
#     db.delete(note)
#     db.commit()
#     db.close()
#     return {"detail": "Note deleted"}
