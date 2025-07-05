
"""Simple daily scheduler for send_daily_reminder(). Run as a background process."""
import time
from schedule import every, run_pending
from daily_task_tracker_app import send_daily_reminder

# Schedule at 09:00 (server local time). Adjust as needed.
every().day.at("09:00").do(send_daily_reminder)

while True:
    run_pending()
    time.sleep(60)
