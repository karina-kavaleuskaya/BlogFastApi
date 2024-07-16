from repository.topic import create_topic_db, update_topic_db, delete_topic_db, get_topics_db


async def create_new_topic(topic, db, current_user):
    topic = await create_topic_db(topic, db, current_user)
    return topic


async def update_topic_serv(topic_id, title, db, user):
    topic = await update_topic_db(topic_id, title, db, user)
    return topic


async def delete_topic_serv(topic_id, db, current_user):
    topic = await delete_topic_db(topic_id, db, current_user)



async def get_topics(db):
    topics = await get_topics_db(db)
    return topics