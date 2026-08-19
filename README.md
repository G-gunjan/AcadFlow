# CollegeApprove AI Agent  
**Digital Signature & Approval System for College Reports**

> Mini Project – Database Systems / AI Agent

---

## 📌 Problem Statement

In colleges, students face a major problem of collecting **physical signatures** from Faculty members and HODs for:

- Internship NOC
- Final Year Project Reports
- Leave Applications
- Bonafide / Character Certificates
- Event Permissions

This leads to delays, multiple visits, lost papers, and frustration.

---

## 💡 Solution

**CollegeApprove AI Agent** is a complete web-based system that:

1. Allows students to **submit approval requests online**
2. Uses an **AI Agent** to help draft formal request letters
3. Routes requests to the correct **Faculty / HOD**
4. Enables **one-click digital approval / rejection**
5. Generates a **Digital Signature Hash** for every approval
6. Provides real-time status tracking
7. Stores everything in a proper **SQL database (SQLite)**

---

## 🛠️ Tech Stack

| Component       | Technology              |
|-----------------|-------------------------|
| Frontend / UI   | Streamlit               |
| Backend Logic   | Python                  |
| Database        | SQLite + SQLAlchemy     |
| AI Agent        | Custom Rule-based + Optional OpenAI |
| Authentication  | Passlib (bcrypt)        |
| Language        | Python 3.9+             |

---

## 📁 Project Structure

```
college_approval_agent/
├── app/
│   └── auth.py                 # Authentication helpers
├── agents/
│   ├── approval_agent.py       # Main AI Agent
│   └── prompts.py              # Prompt templates
├── database/
│   ├── db.py                   # SQLAlchemy models & engine
│   └── init_db.py              # Database initialization + seed data
├── uploads/                    # Uploaded documents
├── docs/
│   └── demo_script.md          # 2-minute video script
├── streamlit_app.py            # Main application
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema

### 1. `users`
- id, name, email, password, role (student/faculty/hod), department

### 2. `requests`
- id, student_id, title, description, document_path, status, assigned_to, request_type, timestamps

### 3. `approvals`
- id, request_id, approver_id, action, remarks, signature_hash, approved_at

---

## 🚀 How to Run

### 1. Install dependencies

```bash
cd college_approval_agent
pip install -r requirements.txt
```

### 2. Initialize Database (first time only)

```bash
python -m database.init_db
```

### 3. Run the Application

```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

---

## 🔑 Demo Login Credentials

| Role     | Email                  | Password    |
|----------|------------------------|-------------|
| Student  | rahul@college.edu      | student123  |
| Student  | priya@college.edu      | student123  |
| Faculty  | suresh@college.edu     | faculty123  |
| Faculty  | anjali@college.edu     | faculty123  |
| HOD      | hod.cs@college.edu     | hod123      |
| HOD      | hod.ece@college.edu    | hod123      |

---

## ✨ Key Features

- ✅ Role-based login (Student / Faculty / HOD)
- ✅ Submit new approval requests with document upload
- ✅ AI Agent that drafts formal letters
- ✅ Pending approval queue for Faculty/HOD
- ✅ One-click Approve / Reject with remarks
- ✅ Digital Signature Hash generation
- ✅ Complete request history & status tracking
- ✅ Clean modern UI

---

## 🤖 AI Agent Capabilities

The AI Agent can:

- Draft formal request letters (Internship, Project, Leave, Certificate…)
- Explain the approval process
- Suggest correct Faculty/HOD
- Guide users on how to use the system

> Optional: Set `OPENAI_API_KEY` environment variable to enable real LLM responses.

---

## 🎥 2-Minute Video Demo Script

See `docs/demo_script.md`

---

## 👨‍🎓 Suitable For

- Mini Project (Database Management Systems)
- AI / Agent based Mini Project
- Final Year Mini Project
- College Internal Project

---

**Made for College Mini Project – 2026**
