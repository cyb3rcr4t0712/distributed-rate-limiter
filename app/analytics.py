import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analytics")

def log_request(client_id: str, endpoint: str):
    # In prod, push to Kafka or directly to TimescaleDB
    logger.info(f"ALLOWED: {client_id} hit {endpoint}")

def log_violation(client_id: str, endpoint: str):
    # Alert the sysadmin
    logger.warning(f"BLOCKED: {client_id} exceeded quota on {endpoint}")