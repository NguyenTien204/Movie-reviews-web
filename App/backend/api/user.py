from fastapi import APIRouter, Request, HTTPException
from kafka import KafkaProducer
import json
from datetime import datetime
import logging

from schema.user_schema import UserLog
KAFKA_TOPICS = {
    "click": "userlog_click",
    "rating": "userlog_rating",
    "trailer": "userlog_trailer",
    "search": "userlog_search",
    "dwelltime": "userlog_dwelltime"
}
router = APIRouter()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@router.post("/log/user_event")
async def log_user_event(log: UserLog, request: Request):
    try:
        log_dict = log.dict()
        log_dict["timestamp"] = (log.timestamp or datetime.utcnow()).isoformat()
        log_dict["ip"] = request.client.host

        topic = KAFKA_TOPICS.get(log.action_type)
        print(f"[DEBUG] Topic resolved: {topic}")

        if not topic:
            raise HTTPException(status_code=400, detail="Invalid action_type")

        producer.send(topic, log_dict)
        producer.flush()

        return {"status": "logged", "topic": topic}
    except Exception as e:
        logging.exception("Kafka logging error")
        raise HTTPException(status_code=500, detail=str(e))
