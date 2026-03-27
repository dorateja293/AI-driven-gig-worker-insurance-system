from app import create_app
from app.services.scheduler import start_scheduler
import logging

# Configure logging for demo clarity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

app = create_app()

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting InsureX Backend Server")
    logger.info("📍 Demo endpoint: POST http://localhost:5000/api/demo/run")

    # Start background scheduler for weather polling
    start_scheduler(app)

    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
