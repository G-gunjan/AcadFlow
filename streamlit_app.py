"""
CollegeApprove AI Agent - Digital Signature & Approval System
Mini Project for College Database Systems
"""

import streamlit as st
import os
import hashlib
import base64
from datetime import datetime
from pathlib import Path

# Local imports
from database.db import get_session, User, ApprovalRequest, Approval, RequestStatus, init_db
from app.auth import authenticate_user, get_all_faculty_and_hod, get_user_by_id
from agents.approval_agent import ApprovalAgent

# Page config
st.set_page_config(
    page_title="CollegeApprove AI Agent",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #5A6A7A;
        margin-bottom: 1.5rem;
    }
    .status-pending { color: #F59E0B; font-weight: 600; }
    .status-approved { color: #10B981; font-weight: 600; }
    .status-rejected { color: #EF4444; font-weight: 600; }
    .card {
        background: #F8FAFC;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Ensure uploads folder exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize DB on first run
@st.cache_resource
def setup_database():
    init_db()
    # Auto-seed if empty
    db = get_session()
    if db.query(User).count() == 0:
        from database.init_db import seed_data
        seed_data()
    db.close()
    return True

setup_database()


# ==================== SESSION STATE ====================
if "user" not in st.session_state:
    st.session_state.user = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==================== HELPER FUNCTIONS ====================
def generate_signature_hash(request_id: int, approver_id: int, action: str) -> str:
    raw = f"{request_id}|{approver_id}|{action}|{datetime.utcnow().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32].upper()


def login_page():
    st.markdown('<p class="main-header">📝 CollegeApprove AI Agent</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Digital Signature & Approval System for College Reports</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="rahul@college.edu")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if not email or not password:
                    st.error("Please enter email and password")
                else:
                    user = authenticate_user(email.strip(), password)
                    if user:
                        st.session_state.user = {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "role": user.role,
                            "department": user.department
                        }
                        st.session_state.agent = ApprovalAgent(
                            user_name=user.name,
                            user_role=user.role,
                            department=user.department or ""
                        )
                        st.session_state.chat_history = []
                        st.success(f"Welcome, {user.name}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")

        st.markdown("---")
        with st.expander("📌 Demo Login Credentials"):
            st.markdown("""
            **Students**  
            `rahul@college.edu` / `student123`  
            `priya@college.edu` / `student123`

            **Faculty**  
            `suresh@college.edu` / `faculty123`  
            `anjali@college.edu` / `faculty123`

            **HOD**  
            `hod.cs@college.edu` / `hod123`  
            `hod.ece@college.edu` / `hod123`
            """)


def student_dashboard():
    user = st.session_state.user
    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.caption(f"{user['role'].upper()} | {user['department']}")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "📝 New Request", "📋 My Requests", "🔐 Verify Signature", "🤖 AI Agent Chat", "ℹ️ About"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.agent = None
        st.session_state.chat_history = []
        st.rerun()

    if menu == "🏠 Dashboard":
        show_student_dashboard()
    elif menu == "📝 New Request":
        show_new_request_form()
    elif menu == "📋 My Requests":
        show_my_requests()
    elif menu == "🔐 Verify Signature":
        show_verify_signature()
    elif menu == "🤖 AI Agent Chat":
        show_ai_chat()
    elif menu == "ℹ️ About":
        show_about()


def faculty_dashboard():
    user = st.session_state.user
    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.caption(f"{user['role'].upper()} | {user['department']}")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "✅ Pending Approvals", "📜 Approval History", "🔐 Verify Signature", "🤖 AI Agent Chat", "ℹ️ About"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.agent = None
        st.session_state.chat_history = []
        st.rerun()

    if menu == "🏠 Dashboard":
        show_faculty_dashboard()
    elif menu == "✅ Pending Approvals":
        show_pending_approvals()
    elif menu == "🔐 Verify Signature":
        show_verify_signature()
    elif menu == "📜 Approval History":
        show_approval_history()
    elif menu == "🤖 AI Agent Chat":
        show_ai_chat()
    elif menu == "ℹ️ About":
        show_about()


def show_student_dashboard():
    user = st.session_state.user
    st.markdown(f'<p class="main-header">Welcome, {user["name"]} 👋</p>', unsafe_allow_html=True)
    st.markdown("Your digital approval dashboard")

    db = get_session()
    total = db.query(ApprovalRequest).filter(ApprovalRequest.student_id == user["id"]).count()
    pending = db.query(ApprovalRequest).filter(
        ApprovalRequest.student_id == user["id"],
        ApprovalRequest.status == "pending"
    ).count()
    approved = db.query(ApprovalRequest).filter(
        ApprovalRequest.student_id == user["id"],
        ApprovalRequest.status == "approved"
    ).count()
    rejected = db.query(ApprovalRequest).filter(
        ApprovalRequest.student_id == user["id"],
        ApprovalRequest.status == "rejected"
    ).count()
    db.close()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Requests", total)
    c2.metric("Pending", pending)
    c3.metric("Approved", approved)
    c4.metric("Rejected", rejected)

    st.markdown("---")
    st.info("💡 **Tip:** Use the **AI Agent Chat** to draft formal letters instantly, or go to **New Request** to submit.")


def show_new_request_form():
    st.markdown('<p class="main-header">📝 Submit New Approval Request</p>', unsafe_allow_html=True)

    faculty_list = get_all_faculty_and_hod()
    options = {f["display"]: f["id"] for f in faculty_list}

    with st.form("new_request_form", clear_on_submit=True):
        title = st.text_input("Request Title *", placeholder="e.g. Internship NOC - TCS")
        request_type = st.selectbox(
            "Request Type *",
            ["internship", "project", "leave", "certificate", "event", "general"]
        )
        description = st.text_area(
            "Detailed Description *",
            height=150,
            placeholder="Write the full details of your request here..."
        )
        assigned_display = st.selectbox("Assign to (Faculty / HOD) *", list(options.keys()))
        uploaded_file = st.file_uploader("Upload Supporting Document (PDF/DOCX)", type=["pdf", "docx", "doc"])

        submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True)

        if submitted:
            if not title or not description:
                st.error("Title and Description are required.")
            else:
                db = get_session()
                try:
                    doc_path = None
                    if uploaded_file:
                        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                        doc_path = str(UPLOAD_DIR / filename)
                        with open(doc_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                    new_req = ApprovalRequest(
                        student_id=st.session_state.user["id"],
                        title=title,
                        description=description,
                        document_path=doc_path,
                        status="pending",
                        assigned_to=options[assigned_display],
                        request_type=request_type
                    )
                    db.add(new_req)
                    db.commit()
                    st.success("✅ Request submitted successfully! You can track it in **My Requests**.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    db.close()


def show_my_requests():
    st.markdown('<p class="main-header">📋 My Requests</p>', unsafe_allow_html=True)

    db = get_session()
    requests = db.query(ApprovalRequest).filter(
        ApprovalRequest.student_id == st.session_state.user["id"]
    ).order_by(ApprovalRequest.created_at.desc()).all()

    if not requests:
        st.info("You have not submitted any requests yet.")
        db.close()
        return

    for req in requests:
        status_class = f"status-{req.status}"
        status_emoji = {"pending": "🟡", "approved": "🟢", "rejected": "🔴"}.get(req.status, "⚪")

        with st.expander(f"{status_emoji} {req.title}  —  {req.status.upper()}"):
            st.markdown(f"**Request ID:** `{req.id}`")
            st.markdown(f"**Type:** {req.request_type.title()}")
            st.markdown(f"**Submitted:** {req.created_at.strftime('%d %b %Y, %H:%M')}")
            st.markdown(f"**Description:**\n{req.description}")

            if req.assigned_to:
                approver = db.query(User).filter(User.id == req.assigned_to).first()
                if approver:
                    st.markdown(f"**Assigned to:** {approver.name} ({approver.role.upper()})")

            # Show approval details if any
            approval = db.query(Approval).filter(Approval.request_id == req.id).first()
            if approval:
                st.markdown("---")
                st.success(f"✅ **DIGITALLY SIGNED**")
                st.markdown(f"**Action:** {approval.action.upper()}")
                st.markdown(f"**Remarks:** {approval.remarks or '—'}")
                st.markdown(f"**🔐 Digital Signature Hash:** `{approval.signature_hash}`")
                st.markdown(f"**Signed By:** Approver ID {approval.approver_id}")
                st.markdown(f"**Action Date:** {approval.approved_at.strftime('%d %b %Y, %H:%M')}")
                st.caption("👉 Copy the Request ID and Signature Hash above to verify this signature in **Verify Signature** page.")

            if req.document_path and os.path.exists(req.document_path):
                st.markdown(f"**Document:** `{os.path.basename(req.document_path)}`")
                try:
                    with open(req.document_path, "rb") as f:
                        file_bytes = f.read()
                    st.download_button(
                        label="📥 Download Document",
                        data=file_bytes,
                        file_name=os.path.basename(req.document_path),
                        mime="application/pdf" if req.document_path.lower().endswith(".pdf") else "application/octet-stream",
                        key=f"stud_download_{req.id}"
                    )
                    # PDF Viewer for student too
                    if req.document_path.lower().endswith(".pdf"):
                        with st.expander("📄 View PDF", expanded=False):
                            b64_pdf = base64.b64encode(file_bytes).decode("utf-8")
                            pdf_display = f'''
                                <iframe src="data:application/pdf;base64,{b64_pdf}"
                                        width="100%" height="500"
                                        type="application/pdf"
                                        style="border:1px solid #ccc; border-radius:8px;">
                                </iframe>
                            '''
                            st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception:
                    pass

    db.close()


def show_faculty_dashboard():
    user = st.session_state.user
    st.markdown(f'<p class="main-header">Welcome, {user["name"]} 👋</p>', unsafe_allow_html=True)

    db = get_session()
    pending = db.query(ApprovalRequest).filter(
        ApprovalRequest.assigned_to == user["id"],
        ApprovalRequest.status == "pending"
    ).count()
    total_handled = db.query(Approval).filter(Approval.approver_id == user["id"]).count()
    db.close()

    c1, c2 = st.columns(2)
    c1.metric("Pending Approvals", pending)
    c2.metric("Total Handled", total_handled)

    st.markdown("---")
    st.info("Go to **Pending Approvals** to review and digitally sign requests.")


def show_pending_approvals():
    st.markdown('<p class="main-header">✅ Pending Approvals</p>', unsafe_allow_html=True)

    db = get_session()
    pending_reqs = db.query(ApprovalRequest).filter(
        ApprovalRequest.assigned_to == st.session_state.user["id"],
        ApprovalRequest.status == "pending"
    ).order_by(ApprovalRequest.created_at.asc()).all()

    if not pending_reqs:
        st.success("🎉 No pending requests. You're all caught up!")
        db.close()
        return

    for req in pending_reqs:
        student = db.query(User).filter(User.id == req.student_id).first()
        with st.container():
            st.markdown(f"### {req.title}")
            st.caption(f"From: **{student.name}** ({student.department}) | Type: {req.request_type} | Submitted: {req.created_at.strftime('%d %b %Y')}")
            st.markdown(req.description)

            # Show, View & Download Document
            if req.document_path and os.path.exists(req.document_path):
                st.markdown(f"📎 **Document:** `{os.path.basename(req.document_path)}`")
                try:
                    with open(req.document_path, "rb") as f:
                        file_bytes = f.read()

                    # Download button
                    st.download_button(
                        label="📥 Download Document",
                        data=file_bytes,
                        file_name=os.path.basename(req.document_path),
                        mime="application/pdf" if req.document_path.lower().endswith(".pdf") else "application/octet-stream",
                        key=f"download_{req.id}"
                    )

                    # In-app PDF Viewer
                    if req.document_path.lower().endswith(".pdf"):
                        with st.expander("📄 View PDF Document (Click to expand)", expanded=False):
                            b64_pdf = base64.b64encode(file_bytes).decode("utf-8")
                            pdf_display = f'''
                                <iframe
                                    src="data:application/pdf;base64,{b64_pdf}"
                                    width="100%"
                                    height="600"
                                    type="application/pdf"
                                    style="border: 1px solid #ccc; border-radius: 8px;">
                                </iframe>
                            '''
                            st.markdown(pdf_display, unsafe_allow_html=True)
                    else:
                        st.info("Preview available only for PDF files. Please download to view other formats.")

                except Exception as e:
                    st.warning(f"Could not load document: {e}")
            else:
                st.caption("No document uploaded.")

            col1, col2 = st.columns(2)
            with col1:
                remarks = st.text_area("Remarks (optional)", key=f"remarks_{req.id}", height=80)
            with col2:
                st.write("")
                st.write("")
                if st.button("✅ Approve & Sign", key=f"approve_{req.id}", type="primary"):
                    _process_approval(db, req, "approved", remarks)
                    st.rerun()
                if st.button("❌ Reject", key=f"reject_{req.id}"):
                    _process_approval(db, req, "rejected", remarks or "Rejected by approver")
                    st.rerun()

            st.markdown("---")

    db.close()


def _process_approval(db, req, action, remarks):
    sig_hash = generate_signature_hash(req.id, st.session_state.user["id"], action)
    approval = Approval(
        request_id=req.id,
        approver_id=st.session_state.user["id"],
        action=action,
        remarks=remarks,
        signature_hash=sig_hash
    )
    req.status = action
    req.updated_at = datetime.utcnow()
    db.add(approval)
    db.commit()
    st.success(f"Request has been **{action.upper()}** with digital signature.")


def show_approval_history():
    st.markdown('<p class="main-header">📜 Approval History</p>', unsafe_allow_html=True)

    db = get_session()
    history = db.query(Approval).filter(
        Approval.approver_id == st.session_state.user["id"]
    ).order_by(Approval.approved_at.desc()).all()

    if not history:
        st.info("No approval history yet.")
        db.close()
        return

    for appr in history:
        req = db.query(ApprovalRequest).filter(ApprovalRequest.id == appr.request_id).first()
        student = db.query(User).filter(User.id == req.student_id).first() if req else None
        emoji = "✅" if appr.action == "approved" else "❌"
        with st.expander(f"{emoji} {req.title if req else 'Unknown'} — {appr.action.upper()}"):
            st.markdown(f"**Request ID:** `{req.id if req else '—'}`")
            st.markdown(f"**Student:** {student.name if student else '—'}")
            st.markdown(f"**Remarks:** {appr.remarks or '—'}")
            st.markdown(f"**🔐 Signature Hash:** `{appr.signature_hash}`")
            st.markdown(f"**Date:** {appr.approved_at.strftime('%d %b %Y, %H:%M')}")
            st.caption("👉 Use Request ID + Signature Hash in **Verify Signature** page to verify authenticity.")

    db.close()


def show_verify_signature():
    st.markdown('<p class="main-header">🔐 Digital Signature Verification</p>', unsafe_allow_html=True)
    st.caption("Enter Request ID and Signature Hash to verify authenticity of an approval.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        request_id = st.number_input("Request ID *", min_value=1, step=1, value=1)
    with col2:
        signature_hash = st.text_input("Digital Signature Hash *", placeholder="Paste the signature hash here...")

    if st.button("🔍 Verify Signature", type="primary", use_container_width=True):
        if not signature_hash or not signature_hash.strip():
            st.error("Please enter the Signature Hash.")
            return

        db = get_session()
        try:
            # Look up the approval by request_id + signature_hash
            approval = db.query(Approval).filter(
                Approval.request_id == int(request_id),
                Approval.signature_hash == signature_hash.strip()
            ).first()

            if not approval:
                st.error("❌ **Invalid Signature** — No matching digital signature found for this Request ID and Hash.")
                st.info("Possible reasons: wrong Request ID, wrong Hash, or the request was never approved.")
            else:
                req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval.request_id).first()
                student = db.query(User).filter(User.id == req.student_id).first() if req else None
                approver = db.query(User).filter(User.id == approval.approver_id).first()

                st.success("✅ **Signature Verified Successfully!** This is a genuine digital approval.")

                st.markdown("### Verification Details")
                st.markdown(f"""
| Field | Value |
|-------|-------|
| **Request ID** | `{req.id if req else '—'}` |
| **Request Title** | {req.title if req else '—'} |
| **Student** | {student.name if student else '—'} ({student.department if student else ''}) |
| **Status** | **{req.status.upper() if req else '—'}** |
| **Action** | **{approval.action.upper()}** |
| **Signed By** | {approver.name if approver else '—'} ({approver.role.upper() if approver else ''}) |
| **Department** | {approver.department if approver else '—'} |
| **Remarks** | {approval.remarks or '—'} |
| **Signature Hash** | `{approval.signature_hash}` |
| **Signed On** | {approval.approved_at.strftime('%d %b %Y at %H:%M:%S')} |
""")

                st.markdown("---")
                st.markdown("### How Verification Works")
                st.info("""
The system stores a unique **SHA-256 based Digital Signature Hash** when Faculty/HOD approves a request.
This hash is generated from: `request_id + approver_id + action + timestamp`.

If the hash matches the database record, the signature is considered **authentic** and cannot be forged easily.
""")
        except Exception as e:
            st.error(f"Error during verification: {e}")
        finally:
            db.close()

    st.markdown("---")
    with st.expander("ℹ️ How to get Request ID and Signature Hash?"):
        st.markdown("""
1. Go to **My Requests** (if you are a student) or **Approval History** (if Faculty/HOD)
2. Open an **Approved** request
3. You will see:
   - **Request ID** (shown in the expander or you can note it)
   - **Digital Signature Hash** (long alphanumeric string)
4. Copy both and paste them here to verify
        """)


def show_ai_chat():
    st.markdown('<p class="main-header">🤖 CollegeApprove AI Agent</p>', unsafe_allow_html=True)
    st.caption("Ask me to draft letters, explain processes, or check how the system works.")

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message... (e.g. Draft an internship NOC letter)"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.agent.chat(prompt)
                st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        if st.session_state.agent:
            st.session_state.agent.reset()
        st.rerun()


def show_about():
    st.markdown('<p class="main-header">ℹ️ About CollegeApprove</p>', unsafe_allow_html=True)
    st.markdown("""
    ### Problem Solved
    Students waste a lot of time collecting physical signatures from Faculty and HOD for reports, 
    internship NOCs, leave applications, certificates etc.

    ### Solution
    **CollegeApprove AI Agent** is a complete digital workflow:
    - Students submit requests online
    - AI Agent helps draft formal letters
    - Faculty / HOD can approve or reject with one click
    - Digital signature (hash) is generated automatically
    - Full history and status tracking

    ### Tech Stack
    - **Frontend & UI:** Streamlit
    - **Database:** SQLite + SQLAlchemy
    - **AI Agent:** Rule-based + optional OpenAI
    - **Language:** Python

    ### Mini Project Highlights
    - Proper database design (Users, Requests, Approvals)
    - Role-based access (Student / Faculty / HOD)
    - AI-assisted drafting
    - Digital signature generation + **verification**
    - Clean and modern UI
    """)


# ==================== MAIN ====================
def main():
    if st.session_state.user is None:
        login_page()
    else:
        role = st.session_state.user["role"]
        if role == "student":
            student_dashboard()
        else:
            faculty_dashboard()  # works for both faculty and hod


if __name__ == "__main__":
    main()