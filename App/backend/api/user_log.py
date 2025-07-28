from fastapi import APIRouter, Request, HTTPException, Depends
from kafka import KafkaProducer
import json
from datetime import datetime, timezone
import logging

from schema.user_schema import UserLog
from dependencies import get_current_user
from models import User
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
async def log_user_event(log: UserLog, request: Request, current_user: User = Depends(get_current_user)):
    try:
        log_dict = log.dict()
        log_dict["user_id"] = current_user.id
        log_dict["username"] = current_user.username
        log_dict["timestamp"] = (log.timestamp or datetime.now(timezone.utc)).isoformat()
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
