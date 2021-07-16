#!/usr/bin/python3

""" Universal phone parser for Telegram """

from telethon import TelegramClient, events
import io

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Integer, String

DB_URI = ''
session = ''
api_id = 
api_hash = ''

def start() -> scoped_session:
    engine = create_engine(DB_URI)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('telethon').setLevel(level=logging.WARNING)

try:
    BASE = declarative_base()
    SESSION = start()
except AttributeError as e:
    print(
        "DB_URI is not configured. Features depending on the database have issues."
    )
    print(str(e))

client = TelegramClient(session, api_id, api_hash)
me = client.get_me()

def newMsg(**args):
    only_me = args.get("only_me", False)
    if only_me:
        args["from_users"] = 'me'
        del args["only_me"]
    return events.NewMessage(**args)

class Database(BASE):
    __tablename__ = "Database"
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    phone = Column(Integer)

    def __init__(self, user_id, username, phone):
        self.user_id = user_id
        self.username = username
        self.phone = phone

Database.__table__.create(checkfirst=True)

def get_state(user_id):
    try:
        return SESSION.query(Database).get(user_id)
    finally:
        SESSION.close()

def addnew(user_id, username, phone):
    adder = Database(user_id, username, phone)
    SESSION.add(adder)
    SESSION.commit()

def updun(user_id, username):
    upd = SESSION.query(Database).get(user_id)
    upd.username = username
    SESSION.commit()

def updph(user_id, phone):
    upd = SESSION.query(Database).get(user_id)
    upd.phone = phone
    SESSION.commit()

@client.on(newMsg(pattern='\.parse ?(.*)', only_me=True))
async def putparsed(msg):
    target = msg.pattern_match.group(1)
    if target:
        try:
            chat = await msg.client.get_entity(target)
        except Exception as e:
            return print(str(e))
    else:
        if not msg.is_group:
            return await msg.edit("`are you sure this is a group?`")
    await msg.edit("`processing...`")
    if target:
      chato = chat.id
    else:
        chato = msg.chat_id
    async for user in msg.client.iter_participants(chato):
        if not user.deleted:
            username = user.username if user.username else None
            phone = user.phone if user.phone else None
            if not user.id in get_state(user.id):
                addnew(user.id, username, phone)
            else:
                if username != get_state(user.id).username:
                    updun(user.id, username)
                if phone and phone != get_state(user.id).phone:
                    updph(user.id, phone)
    await msg.edit('`parsed`')

@client.on(newMsg(pattern='\.uid', only_me=True))
async def check_user(msg):
    if msg.is_reply:
        reply = await msg.get_reply_message()
        sender = await reply.get_sender()
        id = sender.id
        state = get_state(id)
        if state:
            db = "\nUser in the database"
        await msg.edit(f'User ID is equal: `{id}`{db}')

@client.on(newMsg(pattern='\.index ?(.*)', only_me=True))
async def index(msg):
    i = msg.pattern_match.group(1)
    if i: id = i
    elif msg.is_reply:
        reply = await msg.get_reply_message()
        sender = await reply.get_sender()
        id = sender.id
    else:
        return await msg.delete()
    mention = "Indexed:\n\n"
    state = get_state(id)
    if state:
        mention += f"ID: `{state.user_id}`\n"
        mention += f"Username: `{state.username}`\n"
        mention += f"Phone: `{state.phone}`\n"
    else:
        return await msg.edit("None indexed")
    await msg.edit(mention)

client.start()
client.run_until_disconnected()