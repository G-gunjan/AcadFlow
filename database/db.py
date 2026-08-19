from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os

# SQLite database path - uses project folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "college_approval.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserRole(str, enum.Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    HOD = "hod"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # student / faculty / hod
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    requests = relationship("ApprovalRequest", back_populates="student", foreign_keys="ApprovalRequest.student_id")
    assigned_requests = relationship("ApprovalRequest", back_populates="approver", foreign_keys="ApprovalRequest.assigned_to")
    approvals = relationship("Approval", back_populates="approver")


class ApprovalRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    document_path = Column(String(500), nullable=True)
    status = Column(String(20), default=RequestStatus.PENDING.value)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    request_type = Column(String(50), default="general")  # internship, project, leave, certificate, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("User", back_populates="requests", foreign_keys=[student_id])
    approver = relationship("User", back_populates="assigned_requests", foreign_keys=[assigned_to])
    approvals = relationship("Approval", back_populates="request")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(20), nullable=False)  # approved / rejected
    remarks = Column(Text, nullable=True)
    signature_hash = Column(String(255), nullable=True)
    approved_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("ApprovalRequest", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session():
    return SessionLocal()
