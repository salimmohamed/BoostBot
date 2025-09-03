import discord
import asyncio
import json
import os
import sys
import platform
import time
from discord.ext import commands

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
            "allowed_channels": []
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

print(f"Config loaded: {len(config.get('keywords', {}))} keywords, {len(config.get('role_mentions', {}))} role mentions")
if config.get("allowed_channels"):
    print(f"Listening in channels: {config['allowed_channels']}")
else:
    print("Listening in ALL channels (no channel restrictions)")

# Create bot instance
bot = commands.Bot(command_prefix='!', self_bot=True, chunk_guilds_at_startup=False)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Monitoring for keywords: {list(config["keywords"].keys())}')
    if config.get("role_mentions"):
        print(f'Monitoring for role mentions: {list(config["role_mentions"].keys())}')
    if config.get("allowed_channels"):
        print(f'Restricted to channels: {config["allowed_channels"]}')
    else:
        print('Listening in all channels')
    print('Bot is ready!')

@bot.event
async def on_message(message):
    # Don't respond to our own messages unless configured to do so
    if message.author == bot.user and not config.get("respond_to_self", False):
        return
    
    # Check if we should respond in this channel
    allowed_channels = config.get("allowed_channels", [])
    if allowed_channels and str(message.channel.id) not in allowed_channels:
        return  # Skip this message if channel is not in allowed list
    
    # Check for role mentions first
    if message.role_mentions and config.get("role_mentions"):
        for role in message.role_mentions:
            role_id = str(role.id)
            if role_id in config["role_mentions"]:
                try:
                    response = config["role_mentions"][role_id]
                    if config.get("reply_to_message", True):
                        await message.reply(response)
                        print(f'Replied to role mention "{role.name}" in channel {message.channel.name} ({message.channel.id})')
                    else:
                        await message.channel.send(response)
                        print(f'Sent message for role mention "{role.name}" in channel {message.channel.name} ({message.channel.id})')
                    # Add a small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    return  # Exit after handling role mention
                except discord.HTTPException as e:
                    print(f'Error sending role mention response: {e}')
                except Exception as e:
                    print(f'Unexpected error with role mention: {e}')
    
    # Check if message contains any of our keywords
    message_content = message.content if config.get("case_sensitive", False) else message.content.lower()
    
    for keyword, response in config["keywords"].items():
        search_keyword = keyword if config.get("case_sensitive", False) else keyword.lower()
        
        if search_keyword in message_content:
            try:
                if config.get("reply_to_message", True):
                    await message.reply(response)
                    print(f'Replied to keyword "{keyword}" in channel {message.channel.name} ({message.channel.id})')
                else:
                    await message.channel.send(response)
                    print(f'Sent message for keyword "{keyword}" in channel {message.channel.name} ({message.channel.id})')
                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)
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
    
    print("Bot lock acquired - starting bot...")
    
    if config["token"] == "YOUR_USER_TOKEN_HERE":
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
        print("Starting bot...")
        bot.run(config["token"])
    except discord.LoginFailure:
        print("ERROR: Invalid token. Please check your token in config.json")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("\nBot shutdown requested...")
    finally:
        # Clean up lock file
        try:
            os.remove(lock_file)
            print("Lock file removed")
        except:
            pass
        
        print("Bot shutdown complete")
