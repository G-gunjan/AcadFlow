import hashlib
from database.db import get_session, User


def hash_password(password: str) -> str:
    """Simple SHA-256 hash for mini project."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


def authenticate_user(email: str, password: str):
    """Authenticate user and return User object or None."""
    db = get_session()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        # Detach from session
        db.expunge(user)
        return user
    finally:
        db.close()


def get_user_by_id(user_id: int):
    db = get_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.expunge(user)
        return user
    finally:
        db.close()


def get_all_faculty_and_hod():
    """Return list of faculty and HOD for assignment dropdown."""
    db = get_session()
    try:
        users = db.query(User).filter(User.role.in_(["faculty", "hod"])).all()
        result = []
        for u in users:
            result.append({
                "id": u.id,
                "name": u.name,
                "role": u.role,
                "department": u.department,
                "display": f"{u.name} ({u.role.upper()} - {u.department})"
            })
        return result
    finally:
        db.close()
