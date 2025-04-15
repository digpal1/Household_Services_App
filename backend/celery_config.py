from celery import Celery
from celery.schedules import crontab


def make_celery(app_name):
    """Create and configure a Celery instance."""
    return Celery(app_name, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

celery = make_celery(__name__)

# Import tasks to make sure Celery can discover them
import tasks


# 1. Celery beat configuration to run every 10 seconds to generate monthly report
# 2. Celery beat configuration to run daily at 18:00
# 3. Both will run at server startup time from task.py
# During viva demonstration notes
    # All schedules will run at server startup time with part of task.py defined functions
    # Which are contained information of household and users daily activity tasks
    # For demonstration purposes use replace crontab(day_of_month=1) as time 10.0 => 10 seconds
    # crontab(hour=18) => 18:00 means daily at 18:00pm schedule task will execute
    # crontab(day_of_month=12) => 1st day of month means monthly task will execute


# Define the Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    'generate_monthly_report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1),                      #crontab(day_of_month=1),  # Adjust to run monthly set 10.0
    },
    'generate_daily_report': {
        'task': 'tasks.generate_daily_report',
        'schedule': 10.0 #crontab(hour=0, minute=0),                    #crontab(hour=0, minute=0),  # Runs daily at midnight
    },
    'daily_reminder': {
        'task': 'tasks.daily_reminders',
        'schedule': crontab(hour=18),                    #crontab(hour=18),  # Runs daily at 18:00
    },
}

celery.conf.beat_schedule = CELERY_BEAT_SCHEDULE