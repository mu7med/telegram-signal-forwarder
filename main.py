"""
Telegram Signal Forwarder - Koyeb Edition

Listens for messages in a source channel (via user account) and
forwards them to a target channel (via bot account).

Optimized for Koyeb deployment with StringSession support.
"""

import asyncio
import logging
import signal
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import config

# Logging Setup (stdout for Koyeb)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Shutdown flag
shutdown_event = asyncio.Event()


def get_session(session_string: str, fallback_name: str):
    """
    Returns StringSession if available, otherwise falls back to file session.
    StringSession is required for Koyeb (ephemeral storage).
    """
    if session_string:
        logger.info(f"Using StringSession for {fallback_name}")
        return StringSession(session_string)
    else:
        logger.warning(f"No StringSession for {fallback_name}, using file session (local dev only)")
        return fallback_name


# Initialize Clients with StringSession support
user_client = TelegramClient(
    get_session(config.USER_SESSION_STRING, 'user_session'),
    config.API_ID,
    config.API_HASH
)

bot_client = TelegramClient(
    get_session(config.BOT_SESSION_STRING, 'bot_session'),
    config.API_ID,
    config.API_HASH
)


@user_client.on(events.NewMessage(chats=config.SOURCE_CHANNEL_ID))
async def handler(event):
    """
    Listens for new messages in the Source Channel.
    """
    try:
        raw_text = event.message.message
        if not raw_text:
            return

        logger.info(f"Received message from source: {raw_text[:50]}...")

        # Forward message directly (no filtering)
        try:
            await bot_client.send_message(config.TARGET_CHANNEL_ID, raw_text)
            logger.info("Broadcast successful.")
        except FloodWaitError as e:
            logger.warning(f"FloodWaitError: Sleeping for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
            await bot_client.send_message(config.TARGET_CHANNEL_ID, raw_text)
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    except Exception as e:
        logger.error(f"Error processing event: {e}")


async def keepalive():
    """
    Periodic heartbeat to prevent Koyeb from marking service as idle.
    Also helps with monitoring via logs.
    """
    while not shutdown_event.is_set():
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=300)
        except asyncio.TimeoutError:
            logger.info("Heartbeat: Service running normally")


async def shutdown(sig=None):
    """Graceful shutdown handler."""
    if sig:
        logger.info(f"Received signal {sig.name}, shutting down gracefully...")
    else:
        logger.info("Shutting down...")
    
    shutdown_event.set()
    
    # Disconnect clients
    if user_client.is_connected():
        await user_client.disconnect()
        logger.info("User client disconnected")
    
    if bot_client.is_connected():
        await bot_client.disconnect()
        logger.info("Bot client disconnected")


async def main():
    logger.info("Starting Signal Forwarder (Koyeb Edition)...")
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s))
        )
    
    # Start Bot Client
    logger.info("Connecting Bot...")
    await bot_client.start(bot_token=config.BOT_TOKEN)
    
    # Start User Client
    logger.info("Connecting User...")
    if config.USER_SESSION_STRING:
        # StringSession mode - no phone prompt needed
        await user_client.start()
    else:
        # File session mode (local dev) - may prompt for phone
        await user_client.start(phone=config.PHONE_NUMBER)

    # Pre-resolve the target channel entity for the bot
    logger.info("Resolving target channel...")
    try:
        target_entity = await bot_client.get_entity(config.TARGET_CHANNEL_ID)
        logger.info(f"Target channel resolved: {target_entity.title if hasattr(target_entity, 'title') else target_entity}")
    except Exception as e:
        logger.error(f"Failed to resolve target channel. Make sure your bot is an ADMIN in the target channel! Error: {e}")
        await shutdown()
        return

    logger.info("Listening for signals...")
    
    # Run both the event listener and keepalive concurrently
    await asyncio.gather(
        user_client.run_until_disconnected(),
        keepalive()
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
