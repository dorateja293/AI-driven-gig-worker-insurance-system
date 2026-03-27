from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import atexit

scheduler = None

def start_scheduler(app):
    """
    Start the background scheduler for periodic tasks
    """
    global scheduler

    if scheduler is not None:
        return

    scheduler = BackgroundScheduler()

    # Add weather polling job (every 60 minutes)
    def weather_polling_job():
        with app.app_context():
            from app.services.weather_poller import poll_weather
            poll_weather()

    # Add claim processing job (every 5 minutes)
    def claim_processing_job():
        with app.app_context():
            from app.services.queue_service import pop_event_from_queue
            from app.services.claim_processor import process_claim_for_event

            # Process events from queue
            while True:
                event_data = pop_event_from_queue()
                if not event_data:
                    break

                event_id = event_data.get('event_id')
                if event_id:
                    print(f"Processing event {event_id} from queue")
                    try:
                        process_claim_for_event(event_id)
                    except Exception as e:
                        print(f"Error processing event {event_id}: {e}")

    # Schedule weather polling every 60 minutes
    scheduler.add_job(
        func=weather_polling_job,
        trigger=IntervalTrigger(minutes=60),
        id='weather_polling_job',
        name='Poll weather data every 60 minutes',
        replace_existing=True
    )

    # Schedule claim processing every 5 minutes
    scheduler.add_job(
        func=claim_processing_job,
        trigger=IntervalTrigger(minutes=5),
        id='claim_processing_job',
        name='Process claims from queue every 5 minutes',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    print("Background scheduler started")

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
