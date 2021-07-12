import time
import threading
from schemas import Subscription
from database import SessionLocal
from models import Subscription, FeedItem, ReadItem
from fastapi.exceptions import HTTPException
from utils.scraping import scrape
from dateutil.parser import *
import dramatiq


def feed_scheduler(feed_url: str, schedule_action: dramatiq.Actor, fails_until_stop: int):
    '''Takes in string feed url, dramatiq actor and number of runs thread will take until stopping the proccess'''
    attempts = 0
    while attempts != fails_until_stop:
        try:
            schedule_action.send(feed_url)
            time.sleep(60)
        except Exception as e:
            attempts += 1
            time.sleep(60)


@dramatiq.actor
def update_feed(feed_url: str):
    '''Takes in string feed url, updates feed items in the database'''
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


def get_feed_items(feed_url: str, start: int, end: int):
    '''Takes in string feed url,  int start index and int end index, returns array of feed items'''
    with SessionLocal() as session:
        feeds = session.query(FeedItem).filter(
            FeedItem.feed_url == feed_url)[start:end].all()
        return feeds


def mark_item(item_link: str, user_id: int):
    '''Takes in string feed url, int user_id, marks item as read (adds it to db of read items)'''
    with SessionLocal() as session:
        # get feed item
        item = session.query(FeedItem).filter(
            FeedItem.link == item_link).first()
        if item:
            read_item = session.query(ReadItem).filter(ReadItem.item_id == item.id,
                                                       ReadItem.reader_id == user_id).first()
            # if item is already read - remove from read items e.g. "unread" it
            if read_item:
                session.delete(read_item)
                session.commit()
            else:
                # if not read - add to read table
                read_item = ReadItem(reader_id=user_id, item_id=item.id)
                session.add(read_item)
                session.commit()


def subscribe_feed(feed_url: str, user_id: int):
    '''Takes in string feed url, int user id, adds created subscription to db'''
    with SessionLocal() as session:
        subscription = session.query(Subscription).filter(
            Subscription.subscribed_id == user_id, Subscription.feed_url == feed_url).first()
        if not subscription:
            # create subscription
            subscription = Subscription(
                feed_url=feed_url, subscribed_id=user_id)
            session.add(subscription)
            session.commit()
            # start thread that will queue task for dramatiq workers
            updator_thread = threading.Thread(
                target=feed_scheduler, args=(feed_url, get_feed_items, 5))
            updator_thread.start()
        else:
            raise HTTPException(
                status_code=400, detail="user already follows this feed")


def unsubscribe_feed(feed_url: str, user_id: int):
    '''Takes in string feed url, int user id, removes created subscription to db'''
    with SessionLocal() as session:
        subscription = session.query(Subscription).filter(
            Subscription.subscribed_id == user_id, Subscription.feed_url == feed_url).first()
        if subscription:
            session.delete(subscription)
            session.commit()
        else:
            raise HTTPException(
                status_code=400, detail="user does not follow this feed")


def list_feeds(user_id: int, start: int, end: int):
    '''Takes in int user id, number start and number end, returns array of subscribed feed url's'''
    with SessionLocal() as session:
        subscriptions = session.query(Subscription).filter(
            Subscription.subscribed_id == user_id)[start:end].all()
        if subscriptions:
            feed_links = []
            for subscription in subscriptions:
                feed_links.append(subscription.feed_url)
            return feed_links
        else:
            raise HTTPException(
                status_code=400, detail="user does not follow any feeds")
