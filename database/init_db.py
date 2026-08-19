"""
Initialize database with sample users and data.
Run this once: python -m database.init_db
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, get_session, User, ApprovalRequest, Approval, RequestStatus
import hashlib
from datetime import datetime, timedelta


def hash_password(password: str) -> str:
    """Simple SHA-256 hash for mini project (production should use bcrypt)."""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_data():
    init_db()
    db = get_session()

    # Check if already seeded
    if db.query(User).count() > 0:
        print("Database already seeded. Skipping...")
        db.close()
        return

    print("Seeding database with sample data...")

    # Sample Users
    users = [
        # Students
        User(name="Rahul Sharma", email="rahul@college.edu", password=hash_password("student123"),
             role="student", department="Computer Science"),
        User(name="Priya Patel", email="priya@college.edu", password=hash_password("student123"),
             role="student", department="Electronics"),
        User(name="Amit Kumar", email="amit@college.edu", password=hash_password("student123"),
             role="student", department="Computer Science"),

        # Faculty
        User(name="Dr. Suresh Mehta", email="suresh@college.edu", password=hash_password("faculty123"),
             role="faculty", department="Computer Science"),
        User(name="Prof. Anjali Desai", email="anjali@college.edu", password=hash_password("faculty123"),
             role="faculty", department="Electronics"),
        User(name="Dr. Vikram Singh", email="vikram@college.edu", password=hash_password("faculty123"),
             role="faculty", department="Computer Science"),

        # HOD
        User(name="Prof. Rajesh Iyer", email="hod.cs@college.edu", password=hash_password("hod123"),
             role="hod", department="Computer Science"),
        User(name="Dr. Meena Joshi", email="hod.ece@college.edu", password=hash_password("hod123"),
             role="hod", department="Electronics"),
    ]

    db.add_all(users)
    db.commit()

    # Refresh to get IDs
    students = db.query(User).filter(User.role == "student").all()
    faculties = db.query(User).filter(User.role == "faculty").all()
    hods = db.query(User).filter(User.role == "hod").all()

    # Sample Requests
    sample_requests = [
        ApprovalRequest(
            student_id=students[0].id,
            title="Internship NOC Request - TCS",
            description="I have received an internship offer from TCS for 2 months (June-July 2026). "
                        "Kindly grant No Objection Certificate so that I can join the internship.",
            status=RequestStatus.PENDING.value,
            assigned_to=faculties[0].id,
            request_type="internship",
            created_at=datetime.utcnow() - timedelta(days=2)
        ),
        ApprovalRequest(
            student_id=students[0].id,
            title="Project Report Submission - Final Year",
            description="Requesting approval and signature on my final year project report titled "
                        "'AI-based Attendance System using Face Recognition'.",
            status=RequestStatus.APPROVED.value,
            assigned_to=hods[0].id,
            request_type="project",
            created_at=datetime.utcnow() - timedelta(days=10)
        ),
        ApprovalRequest(
            student_id=students[1].id,
            title="Leave Application - Medical",
            description="I need medical leave from 10th to 15th August 2026 due to fever and doctor's advice. "
                        "Medical certificate is attached.",
            status=RequestStatus.PENDING.value,
            assigned_to=faculties[1].id,
            request_type="leave",
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        ApprovalRequest(
            student_id=students[2].id,
            title="Certificate Request - Bonafide",
            description="I need a Bonafide Certificate for applying to a scholarship program. "
                        "Kindly issue the certificate at the earliest.",
            status=RequestStatus.REJECTED.value,
            assigned_to=hods[0].id,
            request_type="certificate",
            created_at=datetime.utcnow() - timedelta(days=5)
        ),
    ]

    db.add_all(sample_requests)
    db.commit()

    # Sample Approval for the approved request
    approved_req = db.query(ApprovalRequest).filter(ApprovalRequest.status == "approved").first()
    if approved_req:
        approval = Approval(
            request_id=approved_req.id,
            approver_id=approved_req.assigned_to,
            action="approved",
            remarks="Project report reviewed and found satisfactory. Approved.",
            signature_hash=f"SIG-{approved_req.id}-{approved_req.assigned_to}-{datetime.utcnow().timestamp()}",
            approved_at=datetime.utcnow() - timedelta(days=7)
        )
        db.add(approval)
        db.commit()

    print("✅ Database seeded successfully!")
    print("\n📌 Login Credentials:")
    print("-" * 50)
    print("STUDENTS:")
    print("  rahul@college.edu  / student123")
    print("  priya@college.edu  / student123")
    print("  amit@college.edu   / student123")
    print("\nFACULTY:")
    print("  suresh@college.edu / faculty123")
    print("  anjali@college.edu / faculty123")
    print("  vikram@college.edu / faculty123")
    print("\nHOD:")
    print("  hod.cs@college.edu  / hod123")
    print("  hod.ece@college.edu / hod123")
    print("-" * 50)

    db.close()


if __name__ == "__main__":
    seed_data()
