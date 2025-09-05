import discord
import asyncio
import json
import os
import sys
import platform
import time
import logging
from discord.ext import commands

# Completely disable Discord.py logging
logging.getLogger('discord').disabled = True
logging.getLogger('discord.client').disabled = True
logging.getLogger('discord.gateway').disabled = True
logging.getLogger('discord.http').disabled = True
logging.getLogger('discord.voice_client').disabled = True
logging.getLogger('discord.player').disabled = True
logging.getLogger('discord.opus').disabled = True

# Also disable root logger for discord modules
logging.getLogger().setLevel(logging.CRITICAL)

# Redirect Discord's logging to devnull
import io
discord_log_handler = logging.StreamHandler(io.StringIO())
discord_log_handler.setLevel(logging.CRITICAL)
for logger_name in ['discord', 'discord.client', 'discord.gateway', 'discord.http']:
    logger = logging.getLogger(logger_name)
    logger.addHandler(discord_log_handler)
    logger.propagate = False

# Custom logging function for bot messages
def bot_log(message):
    """Custom logging function with timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    # Force flush to ensure output appears immediately
    sys.stdout.flush()

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        if "token" not in config:
            raise ValueError("Missing 'token' in config.json")
        if "keywords" not in config:
            raise ValueError("Missing 'keywords' in config.json")
        if "case_sensitive" not in config:
            config["case_sensitive"] = False
        if "respond_to_self" not in config:
            config["respond_to_self"] = False
        if "reply_to_message" not in config:
            config["reply_to_message"] = True
        if "role_mentions" not in config:
            config["role_mentions"] = {}
        if "allowed_channels" not in config:
            config["allowed_channels"] = []
        if "message_delay_minutes" not in config:
            config["message_delay_minutes"] = 5
            
        return config
        
    except FileNotFoundError:
        # Create default config if it doesn't exist
        default_config = {
            "token": "YOUR_USER_TOKEN_HERE",
            "keywords": {
                "hello": "Hi there! How can I help you?",
                "help": "I'm here to assist you!",
                "test": "This is an automated response!"
            },
            "case_sensitive": False,
            "respond_to_self": False,
            "reply_to_message": True,
            "role_mentions": {},
            "allowed_channels": [],
            "message_delay_minutes": 5
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config.json: {e}")
        return None
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return None

# Load configuration
config = load_config()
if not config:
    print("ERROR: Failed to load configuration")
    exit(1)

bot_log("=== Discord Self-Bot Starting ===")
bot_log(f"Config loaded: {len(config.get('keywords', {}))} keywords, {len(config.get('role_mentions', {}))} role mentions")
bot_log("Creating bot instance...")
if config.get("allowed_channels"):
    bot_log(f"Listening in {len(config['allowed_channels'])} channels")
else:
    bot_log("Listening in ALL channels (no channel restrictions)")

# Create bot instance with logging disabled
try:
    bot_log("Initializing Discord bot...")
    bot = commands.Bot(command_prefix='!', self_bot=True, chunk_guilds_at_startup=False)
    bot_log("Bot instance created successfully")
except Exception as e:
    bot_log(f"ERROR creating bot instance: {e}")
    print(f"ERROR creating bot instance: {e}")
    exit(1)

# Disable Discord client logging
try:
    bot._connection._logger.disabled = True
    bot_log("Discord logging disabled")
except Exception as e:
    bot_log(f"Warning: Could not disable Discord logging: {e}")

# Global timer for message delays
last_message_time = 0

# Background task for handling name resolution requests
async def monitor_name_requests():
    """Monitor for name resolution request files"""
    bot_log("Name request monitor started - checking for requests every 0.5 seconds")
    while True:
        try:
            # Check for role name request
            if os.path.exists("get_role_names"):
                bot_log("Role name request detected!")
                os.remove("get_role_names")
                await dump_role_info_with_names()
            
            # Check for channel name request
            if os.path.exists("get_channel_names"):
                bot_log("Channel name request detected!")
                os.remove("get_channel_names")
                await dump_channel_info_with_names()
            
            # Check for test connection request (commented out - uncomment if needed for debugging)
            # if os.path.exists("test_bot_connection"):
            #     bot_log("Bot connection test detected!")
            #     os.remove("test_bot_connection")
            #     bot_log("Bot is running and monitoring files correctly!")
            
                
        except Exception as e:
            bot_log(f"Error in name request monitor: {e}")
        
        await asyncio.sleep(0.5)  # Check every half second

# Start the background task immediately when the module loads
import asyncio
import threading

def start_background_task():
    """Start the background task in a separate thread"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(monitor_name_requests())
    except Exception as e:
        bot_log(f"Failed to start background task: {e}")

# Start the background task in a separate thread
background_thread = threading.Thread(target=start_background_task, daemon=True)
background_thread.start()
bot_log("Background task started in separate thread")

async def dump_role_info_with_names():
    """Dump role information with resolved names"""
    bot_log("=== ROLE INFORMATION DUMP ===")
    role_mentions = config.get("role_mentions", {})
    
    if not role_mentions:
        bot_log("No role mentions configured")
    else:
        bot_log(f"Found {len(role_mentions)} role mentions:")
        for role_id, response in role_mentions.items():
            try:
                # Try to find role in bot's guild cache
                role_found = False
                for guild in bot.guilds:
                    role = guild.get_role(int(role_id))
                    if role:
                        bot_log(f"Role: {role.name} in {guild.name} | Response: '{response}'")
                        role_found = True
                        break
                
                if not role_found:
                    bot_log(f"Role ID: {role_id} (not found in any guild) | Response: '{response}'")
            except AttributeError as e:
                # Bot doesn't have guilds attribute yet
                bot_log(f"Role ID: {role_id} (bot not ready - AttributeError: {e}) | Response: '{response}'")
            except Exception as e:
                bot_log(f"Role ID: {role_id} (error: {e}) | Response: '{response}'")
    bot_log("=== END ROLE DUMP ===")

async def dump_channel_info_with_names():
    """Dump channel information with resolved names"""
    bot_log("=== CHANNEL INFORMATION DUMP ===")
    allowed_channels = config.get("allowed_channels", [])
    
    if not allowed_channels:
        bot_log("No channel restrictions - listening in ALL channels")
    else:
        bot_log(f"Found {len(allowed_channels)} allowed channels:")
        
        
        for channel_id in allowed_channels:
            try:
                # Try to get channel directly - if it works, the bot is ready
                channel = bot.get_channel(int(channel_id))
                if channel:
                    # Handle emoji characters in channel names
                    try:
                        channel_name = channel.name
                        guild_name = channel.guild.name
                        bot_log(f"Channel: #{channel_name} in {guild_name}")
                    except UnicodeEncodeError:
                        # Remove emoji characters and show clean name
                        import re
                        clean_name = re.sub(r'[^\w\s-]', '', channel.name)
                        if clean_name.strip():
                            bot_log(f"Channel: #{clean_name.strip()} in {channel.guild.name}")
                        else:
                            bot_log(f"Channel: #{channel_id} in {channel.guild.name} (name contains only emojis)")
                else:
                    bot_log(f"Channel ID: {channel_id} (not found)")
            except AttributeError:
                # Bot doesn't have get_channel method yet
                bot_log(f"Channel ID: {channel_id} (bot not ready)")
            except Exception as e:
                bot_log(f"Channel ID: {channel_id} (error: {e})")
    bot_log("=== END CHANNEL DUMP ===")

def can_send_message():
    """Check if enough time has passed since last message"""
    global last_message_time
    delay_minutes = config.get("message_delay_minutes", 5)
    
    # If delay is 0, always allow sending messages
    if delay_minutes == 0:
        return True
    
    current_time = time.time()
    delay_seconds = delay_minutes * 60
    
    if current_time - last_message_time >= delay_seconds:
        last_message_time = current_time
        return True
    return False

def get_remaining_delay():
    """Get remaining delay time in seconds"""
    global last_message_time
    delay_minutes = config.get("message_delay_minutes", 5)
    
    # If delay is 0, no remaining delay
    if delay_minutes == 0:
        return 0
    
    current_time = time.time()
    delay_seconds = delay_minutes * 60
    elapsed = current_time - last_message_time
    remaining = delay_seconds - elapsed
    return max(0, remaining)

@bot.event
async def on_ready():
    try:
        bot_log(f'Logged in as {bot.user} (ID: {bot.user.id})')
        bot_log(f'Monitoring for keywords: {list(config["keywords"].keys())}')
        
        # Show role mentions count (simplified for now)
        if config.get("role_mentions"):
            bot_log(f'Monitoring for role mentions: {len(config["role_mentions"])} roles configured')
        
        # Show channels count (simplified for now)
        if config.get("allowed_channels"):
            bot_log(f'Restricted to channels: {len(config["allowed_channels"])} channels configured')
        else:
            bot_log('Listening in all channels')
        
        delay_minutes = config.get("message_delay_minutes", 5)
        if delay_minutes == 0:
            bot_log('Message delay: No delay (instant responses)')
        else:
            bot_log(f'Message delay: {delay_minutes} minutes between responses')
        bot_log('Bot is ready!')
        
        # Background task is already running in separate thread
        bot_log("Bot is fully ready and monitoring for name requests!")
    except Exception as e:
        bot_log(f'ERROR in on_ready: {e}')
        print(f'ERROR in on_ready: {e}')
        import traceback
        traceback.print_exc()

@bot.event
async def on_message(message):
    # Don't respond to our own messages unless configured to do so
    if message.author == bot.user and not config.get("respond_to_self", False):
        return
    
    # Check if we should respond in this channel
    allowed_channels = config.get("allowed_channels", [])
    if allowed_channels and str(message.channel.id) not in allowed_channels:
        return  # Skip this message if channel is not in allowed list
    
    # Check if we have any triggers to respond to first
    has_role_mention = False
    has_keyword = False
    
    # Check for role mentions
    if message.role_mentions and config.get("role_mentions"):
        for role in message.role_mentions:
            role_id = str(role.id)
            if role_id in config["role_mentions"]:
                has_role_mention = True
                break
    
    # Check for keywords
    if not has_role_mention and config.get("keywords"):
        message_content = message.content if config.get("case_sensitive", False) else message.content.lower()
        for keyword in config["keywords"].keys():
            search_keyword = keyword if config.get("case_sensitive", False) else keyword.lower()
            if search_keyword in message_content:
                has_keyword = True
                break
    
    # Only check timer if we actually have something to respond to
    if not has_role_mention and not has_keyword:
        return  # No triggers, exit early without checking timer
    
    # Now check global timer - only if we're about to respond
    if not can_send_message():
        remaining = get_remaining_delay()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        bot_log(f'[TIMER] Skipping response - {minutes}m {seconds}s remaining until next message allowed')
        return
    
    # Handle role mentions (we already confirmed there's a trigger)
    if has_role_mention:
        for role in message.role_mentions:
            role_id = str(role.id)
            if role_id in config["role_mentions"]:
                try:
                    response = config["role_mentions"][role_id]
                    if config.get("reply_to_message", True):
                        await message.reply(response)
                        server_name = message.guild.name if message.guild else "DM"
                        bot_log(f'[ROLE MENTION] Replied to "{role.name}" in #{message.channel.name} | Server: {server_name}')
                    else:
                        await message.channel.send(response)
                        server_name = message.guild.name if message.guild else "DM"
                        bot_log(f'[ROLE MENTION] Sent message for "{role.name}" in #{message.channel.name} | Server: {server_name}')
                    return  # Exit after handling role mention
                except discord.HTTPException as e:
                    print(f'Error sending role mention response: {e}')
                except Exception as e:
                    print(f'Unexpected error with role mention: {e}')
    
    # Handle keywords (we already confirmed there's a trigger)
    elif has_keyword:
        message_content = message.content if config.get("case_sensitive", False) else message.content.lower()
        for keyword, response in config["keywords"].items():
            search_keyword = keyword if config.get("case_sensitive", False) else keyword.lower()
            
            if search_keyword in message_content:
                try:
                    if config.get("reply_to_message", True):
                        await message.reply(response)
                        server_name = message.guild.name if message.guild else "DM"
                        bot_log(f'[KEYWORD] Replied to "{keyword}" in #{message.channel.name} | Server: {server_name}')
                    else:
                        await message.channel.send(response)
                        server_name = message.guild.name if message.guild else "DM"
                        bot_log(f'[KEYWORD] Sent message for "{keyword}" in #{message.channel.name} | Server: {server_name}')
                    break  # Only respond to the first matching keyword
                except discord.HTTPException as e:
                    print(f'Error sending response: {e}')
                except Exception as e:
                    print(f'Unexpected error: {e}')

if __name__ == "__main__":
    # Check for existing bot instance
    lock_file = "bot.lock"
    
    def check_lock():
        """Check if another bot instance is running"""
        if os.path.exists(lock_file):
            try:
                with open(lock_file, 'r') as f:
                    pid = f.read().strip()
                # Check if the process is still running
                if platform.system() == "Windows":
                    try:
                        os.kill(int(pid), 0)  # Check if process exists
                        return True  # Process is running
                    except (OSError, ValueError):
                        # Process not running, remove stale lock file
                        os.remove(lock_file)
                        return False
                else:
                    # Unix-like systems
                    try:
                        os.kill(int(pid), 0)
                        return True
                    except (OSError, ValueError):
                        os.remove(lock_file)
                        return False
            except:
                # Corrupted lock file, remove it
                try:
                    os.remove(lock_file)
                except:
                    pass
                return False
        return False
    
    def create_lock():
        """Create a lock file"""
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except:
            return False
    
    # Check if another instance is running
    if check_lock():
        print("ERROR: Another bot instance is already running!")
        print("Please stop the existing bot before starting a new one.")
        print("If you're using the GUI, click 'Stop Bot' first.")
        exit(1)
    
    # Create lock file
    if not create_lock():
        print("ERROR: Could not create lock file. Check file permissions.")
        exit(1)
    
    bot_log("Bot lock acquired - starting bot...")
    
    if config["token"] == "YOUR_USER_TOKEN_HERE":
        bot_log("ERROR: Please set your Discord user token in config.json")
        print("ERROR: Please set your Discord user token in config.json")
        print("Easy method to get your token:")
        print("1. Open Discord in your browser")
        print("2. Press F12 to open Developer Tools")
        print("3. Press Ctrl + Shift + M to enable mobile device emulation")
        print("4. Go to Application tab → Local Storage → https://discord.com/")
        print("5. Find the 'token' key and copy its value")
        print("6. Replace 'YOUR_USER_TOKEN_HERE' in config.json")
        try:
            os.remove(lock_file)
        except:
            pass
        exit(1)
    
    try:
        bot_log("Starting bot...")
        bot_log(f"Token length: {len(config['token'])} characters")
        bot_log("Attempting to connect to Discord...")
        bot.run(config["token"])
    except discord.LoginFailure:
        print("ERROR: Invalid token. Please check your token in config.json")
        bot_log("ERROR: Invalid token. Please check your token in config.json")
    except Exception as e:
        print(f"ERROR: {e}")
        bot_log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        bot_log("Bot shutdown requested...")
    finally:
        # Clean up lock file
        try:
            os.remove(lock_file)
            bot_log("Lock file removed")
        except:
            pass
        
        bot_log("Bot shutdown complete")
