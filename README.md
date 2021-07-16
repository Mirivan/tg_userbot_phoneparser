# 💣 Universal phone parser for Telegram 👑
### Based on SQL Alchemy and Telethon

## Installing:
1) Clone repository
2) Setup DB_URI, session name, api_id and api_hash into parser_m.py
3) Let's parse!

## Usage:
- `.parse` chat_id/this chat - parse all participants in the chat and add to the database. (If id or phone changes - only they are updated)
- `.uid` user_id - check user id from reply message and his state existing in the databse.
- `.index` user_id - show user parsed info from the database.
