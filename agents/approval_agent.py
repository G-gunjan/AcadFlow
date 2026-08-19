"""
CollegeApprove AI Agent
Supports both rule-based responses and optional OpenAI/LangChain integration.
"""

import os
from datetime import datetime
from agents.prompts import SYSTEM_PROMPT, DRAFT_REQUEST_PROMPT, GENERAL_HELP

# Optional OpenAI support
USE_OPENAI = False
try:
    from openai import OpenAI
    if os.getenv("OPENAI_API_KEY"):
        client = OpenAI()
        USE_OPENAI = True
except Exception:
    USE_OPENAI = False


class ApprovalAgent:
    def __init__(self, user_name: str = "Student", user_role: str = "student", department: str = ""):
        self.user_name = user_name
        self.user_role = user_role
        self.department = department
        self.conversation_history = []

    def _rule_based_response(self, user_input: str) -> str:
        """Fallback intelligent rule-based responses when no LLM is available."""
        text = user_input.lower().strip()

        # Draft request
        if any(kw in text for kw in ["draft", "write", "letter", "request letter", "help me write"]):
            return self._draft_letter(user_input)

        # Status related
        if any(kw in text for kw in ["status", "track", "where is my", "pending"]):
            return (
                "📋 **To check the status of your requests:**\n\n"
                "1. Go to the **My Requests** tab in the sidebar.\n"
                "2. You will see all your submitted requests with current status:\n"
                "   - 🟡 **Pending** → Waiting for Faculty/HOD action\n"
                "   - 🟢 **Approved** → Digitally signed & approved\n"
                "   - 🔴 **Rejected** → Check remarks for reason\n\n"
                "You can also ask me: *“Show my pending requests”* after logging in."
            )

        # How to submit
        if any(kw in text for kw in ["how to submit", "submit request", "new request", "apply"]):
            return (
                "📝 **How to submit a new approval request:**\n\n"
                "1. Click **New Request** in the sidebar.\n"
                "2. Fill in:\n"
                "   - Title (e.g., Internship NOC – TCS)\n"
                "   - Request Type (Internship / Project / Leave / Certificate etc.)\n"
                "   - Detailed description\n"
                "   - Optionally upload a supporting document (PDF)\n"
                "3. Select the Faculty or HOD who should approve it.\n"
                "4. Click **Submit Request**.\n\n"
                "You will receive real-time status updates here."
            )

        # Who approves what
        if any(kw in text for kw in ["who approves", "faculty", "hod", "whom to send", "assign"]):
            return (
                "👨‍🏫 **Recommended Approvers by Request Type:**\n\n"
                "| Request Type   | First Approver      | Final Approver |\n"
                "|----------------|---------------------|----------------|\n"
                "| Internship     | Faculty Advisor     | HOD            |\n"
                "| Project Report | Project Guide       | HOD            |\n"
                "| Leave          | Class Coordinator   | HOD (if long)  |\n"
                "| Bonafide / Certificate | HOD          | -              |\n"
                "| Event Permission | Faculty Coordinator | HOD          |\n\n"
                "In this system you can directly assign to the correct person."
            )

        # Greeting
        if any(kw in text for kw in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            return (
                f"Hello {self.user_name}! 👋\n\n"
                "I am **CollegeApprove AI Agent**. I can help you with:\n"
                "• Drafting formal request letters\n"
                "• Submitting & tracking approvals\n"
                "• Understanding the process\n"
                "• Suggesting the right Faculty/HOD\n\n"
                "How can I assist you today?"
            )

        # Help
        if any(kw in text for kw in ["help", "what can you do", "features"]):
            return (
                "🤖 **I can help you with:**\n\n"
                "1. **Draft Letter** → “Draft an internship NOC letter for me”\n"
                "2. **How to submit** → “How do I submit a new request?”\n"
                "3. **Status** → “How to check status of my request?”\n"
                "4. **Who to assign** → “Who should approve my project report?”\n"
                "5. **Process explanation** → “Explain the approval workflow”\n\n"
                "Just type naturally!"
            )

        # Default
        return (
            "I'm here to help with college approval requests.\n\n"
            "Try asking me:\n"
            "• “Draft a letter for internship NOC”\n"
            "• “How to submit a request?”\n"
            "• “Who should approve my project report?”\n"
            "• “Explain the approval process”\n\n"
            "Or go to **New Request** tab to submit directly."
        )

    def _draft_letter(self, user_input: str) -> str:
        """Generate a formal letter based on keywords."""
        text = user_input.lower()

        if "internship" in text or "noc" in text:
            subject = "Request for No Objection Certificate (NOC) for Internship"
            body = (
                f"I am {self.user_name}, a student of {self.department} department. "
                "I have received an internship opportunity and request you to kindly issue a "
                "No Objection Certificate (NOC) so that I may join the internship.\n\n"
                "I assure you that I will complete all academic requirements and will not let "
                "this internship affect my studies."
            )
        elif "project" in text:
            subject = "Request for Approval of Final Year Project Report"
            body = (
                f"I am {self.user_name} from {self.department}. "
                "I have completed my final year project and request you to kindly review and "
                "approve my project report for final submission."
            )
        elif "leave" in text or "medical" in text:
            subject = "Application for Medical Leave"
            body = (
                f"I am {self.user_name}, student of {self.department}. "
                "Due to medical reasons I am unable to attend college. "
                "Kindly grant me leave for the mentioned period. Medical documents are attached."
            )
        elif "certificate" in text or "bonafide" in text:
            subject = "Request for Bonafide Certificate"
            body = (
                f"I am {self.user_name} of {self.department} department. "
                "I need a Bonafide Certificate for scholarship / higher studies / bank purpose. "
                "Kindly issue the same at the earliest."
            )
        else:
            subject = "Request for Approval / Signature"
            body = (
                f"I am {self.user_name} from the {self.department} department. "
                "I request you to kindly approve the following matter and provide your signature."
            )

        letter = f"""**Formal Draft Ready to Use:**

---

**Subject:** {subject}

Respected Sir/Madam,

{body}

I shall be highly obliged for your kind consideration.

Thanking you,

Yours sincerely,  
**{self.user_name}**  
{self.department} Department  
Date: {datetime.now().strftime("%d %B %Y")}

---

You can copy this text and paste it into the **New Request** form.
"""
        return letter

    def chat(self, user_input: str) -> str:
        """Main chat interface."""
        self.conversation_history.append({"role": "user", "content": user_input})

        if USE_OPENAI:
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                messages.extend(self.conversation_history[-6:])  # last 3 turns
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.4,
                    max_tokens=600
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = self._rule_based_response(user_input) + f"\n\n_(LLM unavailable: {str(e)[:50]})_"
        else:
            reply = self._rule_based_response(user_input)

        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self.conversation_history = []