# daily_task_tracker_app.py
"""
Streamlit Daily Task Tracker (multi‑user)

Features
--------
* **Named users** – each task is tagged with its owner so work never mixes.
* Add / update tasks with **Date | Task | Status | Deadline | User**.
* Sidebar picker lets each of the 5 members see only their own tasks.
* Persists to **tasks.csv** (swap to DB later).
* Email reminder helper unchanged – optional daily cron.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import os
import smtplib
import ssl
from email.message import EmailMessage

# ────────────────────────────────── CONFIG ────────────────────────────────────
USERS = [
    "Shaurya",   # ⚑ replace with real member names
    "Mukund",
    "Anjan",
    "Pranjal",
    "Lekha",
]

DATA_FILE = Path("tasks.csv")  # or a full path

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENTS = os.getenv("RECIPIENTS", "").split(",")
DEFAULT_DASHBOARD_URL = "http://localhost:8501"

# ──────────────────────────────── DATA HELPERS ────────────────────────────────

def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Guarantee all required columns exist in DataFrame."""
    for col, dtype in {
        "user": "object",
        "date": "datetime64[ns]",
        "task": "object",
        "status": "object",
        "deadline": "datetime64[ns]",
    }.items():
        if col not in df.columns:
            df[col] = pd.Series(dtype=dtype)
    return df


def load_data() -> pd.DataFrame:
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE, parse_dates=["date", "deadline"])
    else:
        df = pd.DataFrame()
    return _ensure_columns(df)


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)

# ────────────────────────────── EMAIL REMINDER ────────────────────────────────

def send_daily_reminder() -> None:
    """Send an email asking the team to update tasks."""
    if not (EMAIL_SENDER and EMAIL_PASSWORD and any(RECIPIENTS)):
        print("[Reminder] Email creds or recipients missing; skip.")
        return

    subject = "Daily Task Tracker – please update your tasks"
    dashboard_url = st.secrets.get("app_url", DEFAULT_DASHBOARD_URL)
    body = (
        "Hi team,\n\n"
        "This is your automated reminder to update today's tasks.\n\n"
        f"Dashboard: {dashboard_url}\n\n"
        "Regards,\nTask Tracker Bot"
    )

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

# ───────────────────────────────── STREAMLIT UI ───────────────────────────────

def main() -> None:
    st.set_page_config(page_title="Daily Task Tracker", layout="wide")
    st.title("📋 Daily Task Tracker – Multi‑User")

    # ---------- Pick active user ----------
    with st.sidebar:
        active_user = st.selectbox("Who's updating tasks?", USERS, key="user_selector")
        st.markdown("---")
        st.markdown("**Instructions**:\n- Select your name.\n- Add or edit tasks – you'll only see yours.")

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
            mask = (
                (df["user"] == active_user)
                & (df["date"] == task_date_pd)
                & (df["task"] == task_name)
            )
            if mask.any():
                # Update existing row
                df.loc[mask, ["status", "deadline"]] = [status, deadline_pd]
            else:
                # Append new row
                df.loc[len(df)] = [active_user, task_date_pd, task_name, status, deadline_pd]
            save_data(df)
            st.success("Task saved.")

    # ---------- Display + inline edit ----------
    st.subheader(f"Tasks for **{active_user}**")
    user_df = df[df["user"] == active_user].sort_values(["date", "deadline"]).reset_index(drop=True)

    edited_df = st.data_editor(
        user_df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor",
    )
    if st.button("💾 Save changes"):
        # Overwrite only the active user's slice, keep others intact
        other_df = df[df["user"] != active_user]
        edited_df["user"] = active_user  # ensure column retained
        df_updated = pd.concat([other_df, edited_df], ignore_index=True)
        save_data(df_updated)
        st.success("Updates saved.")
        df = df_updated  # refresh in session

    st.markdown("---")
    st.caption(
        "Schedule `send_daily_reminder()` (see helper in repo) to email the whole team every morning."
    )


if __name__ == "__main__":
    main()

