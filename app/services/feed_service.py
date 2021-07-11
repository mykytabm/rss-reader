from app.schemas import Subscription
from ..database import SessionLocal
from ..models import Subscription
from fastapi.exceptions import HTTPException


def subscribe_feed(feed_url: str, user_id: int):
    with SessionLocal() as session:
        subscription = session.query(Subscription).filter(
            Subscription.subscribed_id == user_id and Subscription.feed_url == feed_url).first()
        if not subscription:
            subscription = Subscription(
                feed_url=feed_url, subscribed_id=user_id)
            session.add(subscription)
            session.commit()
        else:
            raise HTTPException(
                status_code=400, detail="user already follows this feed")


def unsubscribe_feed(feed_url: str, user_id: int):
    with SessionLocal() as session:
        subscription = session.query(Subscription).filter(
            Subscription.subscribed_id == user_id and Subscription.feed_url == feed_url).first()
        if subscription:
            session.delete(subscription)
            session.commit()
        else:
            raise HTTPException(
                status_code=400, detail="user does not follow this feed")
