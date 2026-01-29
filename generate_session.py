"""
Session String Generator for Koyeb Deployment

Run this script ONCE locally to convert your existing .session files
to StringSession format for use as environment variables on Koyeb.

Usage:
    python generate_session.py
"""

import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PHONE_NUMBER = os.getenv("phone_number", "")

if not API_ID or not API_HASH:
    print("Error: API_ID and API_HASH must be set in .env file")
    sys.exit(1)


async def export_user_session():
    print("\n" + "="*60)
    print("EXPORTING USER SESSION")
    print("="*60)
    
    if os.path.exists("user_session.session"):
        print("Found existing user_session.session file.")
        file_client = TelegramClient("user_session", API_ID, API_HASH)
        await file_client.connect()
        
        if await file_client.is_user_authorized():
            session_string = StringSession.save(file_client.session)
            await file_client.disconnect()
            return session_string
        else:
            print("Session not authorized. Creating new session...")
            await file_client.disconnect()
    
    print("Creating new user session...")
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    
    if not PHONE_NUMBER:
        print("Error: phone_number must be set in .env file")
        sys.exit(1)
    
    await client.start(phone=PHONE_NUMBER)
    session_string = client.session.save()
    await client.disconnect()
    return session_string


async def export_bot_session():
    print("\n" + "="*60)
    print("EXPORTING BOT SESSION")
    print("="*60)
    
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN must be set in .env file")
        sys.exit(1)
    
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    session_string = client.session.save()
    await client.disconnect()
    return session_string


async def main():
    print("="*60)
    print("KOYEB SESSION STRING GENERATOR")
    print("="*60)
    
    user_session = await export_user_session()
    bot_session = await export_bot_session()
    
    print("\n" + "="*60)
    print("SUCCESS! Copy these to Koyeb environment variables:")
    print("="*60)
    print("\nUSER_SESSION_STRING:")
    print(user_session)
    print("\nBOT_SESSION_STRING:")
    print(bot_session)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
