
# daily_task_tracker_app.py
"""
Streamlit Daily Task Tracker

Features
--------
* Add / update tasks with Date | Task | Status | Deadline
* Persist data locally to **tasks.csv** (default) – switch to SQLite/Google Sheets easily
* Inline editing with **st.data_editor**
* Helper `send_daily_reminder()` for automated email
  – schedule via cron / APScheduler / `schedule` lib
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import os
import smtplib
import ssl
from email.message import EmailMessage

# ----- Config --------------------------------------------------------------
DATA_FILE = Path("tasks.csv")  # CSV in repo root

EMAIL_SENDER = os.getenv("EMAIL_SENDER")          # e.g. "yourbot@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")      # app‑password / API key
RECIPIENTS = os.getenv("RECIPIENTS", "").split(",")  # comma‑separated list
DEFAULT_DASHBOARD_URL = "http://localhost:8501"   # fallback

# ----- Data helpers --------------------------------------------------------
def load_data() -> pd.DataFrame:
    """Load existing task data or create an empty DataFrame."""
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE, parse_dates=["date", "deadline"])
    return pd.DataFrame(columns=["date", "task", "status", "deadline"])

def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)

# ----- Email reminder ------------------------------------------------------
def send_daily_reminder() -> None:
    """Send an email asking recipients to update today's tasks."""
    if not (EMAIL_SENDER and EMAIL_PASSWORD and any(RECIPIENTS)):
        print("[Reminder] Email creds or recipients missing; skip.")
        return

    subject = "Daily Task Tracker – please update your tasks"
    dashboard_url = st.secrets.get("app_url", DEFAULT_DASHBOARD_URL)
    body = f"""Hi,

This is your automated reminder to update today's tasks.

Dashboard: {dashboard_url}

Regards,
Task Tracker Bot"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(RECIPIENTS)
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("[Reminder] Email sent.")

# ----- Streamlit UI --------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="Daily Task Tracker", layout="wide")
    st.title("📋 Daily Task Tracker")

    df = load_data()

    # ---------- Task entry form ----------
    with st.form("task_form", clear_on_submit=False):
        col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
        task_date = col1.date_input("Date", date.today())
        task_name = col2.text_input("Task description")
        status = col3.selectbox("Status", ["Yet to Start", "In Progress", "Completed"])
        deadline = col4.date_input("Deadline", date.today())
        submitted = st.form_submit_button("Add / Update")

        if submitted and task_name.strip():
            task_date_pd = pd.to_datetime(task_date)
            deadline_pd = pd.to_datetime(deadline)
            mask = (df["date"] == task_date_pd) & (df["task"] == task_name)

            if mask.any():  # Update
                df.loc[mask, ["status", "deadline"]] = [status, deadline_pd]
            else:           # Append
                df.loc[len(df)] = [task_date_pd, task_name, status, deadline_pd]
            save_data(df)
            st.success("Task saved.")

    # ---------- Task table  ----------
    st.subheader("Task list")
    df_display = df.sort_values(["date", "deadline"]).reset_index(drop=True)
    edited_df = st.data_editor(
        df_display,
        num_rows="dynamic",
        use_container_width=True,
        key="editor",
    )
    if st.button("💾 Save changes"):
        save_data(edited_df)
        st.success("Updates saved.")

    st.markdown("---")
    st.caption(
        "Schedule `send_daily_reminder()` via `cron`, `schedule`, or any serverless job "
        "to automate daily email reminders."
    )

if __name__ == "__main__":
    main()
