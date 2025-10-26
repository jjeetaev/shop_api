from celery import Celery
from celery.schedules import crontab

app = Celery('your_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-low-stock-daily': {
        'task': 'products.tasks.check_low_stock_and_cleanup',
        'schedule': crontab(hour=8, minute=0),
    },
    'send-low-stock-alerts': {
        'task': 'products.tasks.send_low_stock_alert',
        'schedule': crontab(hour=9, minute=0),
    },
    'daily-sales-report': {
        'task': 'products.tasks.send_daily_sales_report',
        'schedule': crontab(hour=18, minute=0), 
    },
}