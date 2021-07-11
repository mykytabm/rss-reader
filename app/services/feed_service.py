from app.schemas import Subscription
from ..database import SessionLocal
from ..models import Subscription, FeedItem
from fastapi.exceptions import HTTPException
from ..utils.scraping import scrape
from dateutil.parser import *
# def update_feed(feed_url)


def add_feed_items(feed_url: str):
    feed_items = scrape(feed_url)
    if feed_items:
        with SessionLocal() as session:
            for feed in feed_items:
                feed_item = FeedItem(title=feed['title'],
                                     feed_url=feed_url,
                                     link=feed['link'],
                                     publication_date=parse(feed['published']))
                print(feed_item.publication_date)
                existing_feed = session.query(FeedItem).filter(
                    FeedItem.link == feed['link']).first()
                if not existing_feed:
                    session.add(feed_item)
                    session.commit()
    else:
        raise HTTPException(
            status_code=400, detail="retrieving feed items failed")


def get_feed(feed_url, user_id):
    with SessionLocal() as session:
        feeds = session.query(FeedItem).filter(
            FeedItem.feed_url == feed_url).all()
        return feeds


def subscribe_feed(feed_url: str, user_id: int):
    with SessionLocal() as session:
        subscription = session.query(Subscription).filter(
            Subscription.subscribed_id == user_id, Subscription.feed_url == feed_url).first()
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
            Subscription.subscribed_id == user_id, Subscription.feed_url == feed_url).first()
        if subscription:
            session.delete(subscription)
            session.commit()
        else:
            raise HTTPException(
                status_code=400, detail="user does not follow this feed")


def list_feeds(user_id: int):
    with SessionLocal() as session:
        subscriptions = session.query(Subscription).filter(
            Subscription.subscribed_id == user_id).all()
        if subscriptions:
            feed_links = []
            for subscription in subscriptions:
                feed_links.append(subscription.feed_url)
            return feed_links
        else:
            raise HTTPException(
                status_code=400, detail="user does not follow any feeds")


def list_feed_items(feed_url: str):
    pass
