# Daily Task Tracker (Streamlit)

A lightweight Streamlit dashboard to log daily tasks and send automated email reminders.

## Features

* **Dashboard** – Create, update, and inline‑edit tasks (`Date | Task | Status | Deadline`).
* **Persistence** – Saves to `tasks.csv` by default (swap in SQLite/Google Sheets easily).
* **Email reminders** – `send_daily_reminder()` notifies selected recipients every morning.

## Quick start

```bash
# 1. Clone the repo
git clone https://github.com/<your‑user>/daily_task_tracker.git
cd daily_task_tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Export env vars or add them as Streamlit secrets
export EMAIL_SENDER='yourbot@gmail.com'
export EMAIL_PASSWORD='app‑password'
export RECIPIENTS='alice@example.com,bob@example.com'

# 4. Run locally
streamlit run daily_task_tracker_app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to GitHub.
2. In Streamlit, **"Deploy an app"** → point to your repo and `daily_task_tracker_app.py`.
3. In **Secrets**, add:

```toml
EMAIL_SENDER = "yourbot@gmail.com"
EMAIL_PASSWORD = "app‑password"
RECIPIENTS = "alice@example.com,bob@example.com"
app_url = "https://<app‑url>"  # optional
```
4. Because Community Cloud doesn't run long‑lived background jobs, host `scheduler.py` elsewhere
   (cron on a small VPS, GitHub Action, or Cloud Function) to hit the same email credentials.

## Folder structure

```
.
├── daily_task_tracker_app.py
├── scheduler.py
├── requirements.txt
├── README.md
└── tasks.csv              # auto‑created
```

## License

MIT
