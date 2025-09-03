import discord
import asyncio
import json
import os
import sys
import platform
import time
from discord.ext import commands

# Global config and file monitoring
config = None
config_file_mtime = 0
config_reload_cooldown = 0

def load_config():
    """Load configuration from config.json"""
    global config, config_file_mtime
    
    try:
        # Get file modification time
        current_mtime = os.path.getmtime('config.json')
        
        with open('config.json', 'r') as f:
            new_config = json.load(f)
        
        # Update modification time
        config_file_mtime = current_mtime
        
        # Validate required fields
        if "token" not in new_config:
            raise ValueError("Missing 'token' in config.json")
        if "keywords" not in new_config:
            raise ValueError("Missing 'keywords' in config.json")
        if "case_sensitive" not in new_config:
            new_config["case_sensitive"] = False
        if "respond_to_self" not in new_config:
            new_config["respond_to_self"] = False
        if "reply_to_message" not in new_config:
            new_config["reply_to_message"] = True
        if "role_mentions" not in new_config:
            new_config["role_mentions"] = {}
            
        return new_config
        
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
            "role_mentions": {}
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        
        config_file_mtime = os.path.getmtime('config.json')
        return default_config
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config.json: {e}")
        return config if config else default_config
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return config if config else default_config

def check_config_reload():
    """Check if config.json has been modified and reload if needed"""
    global config, config_reload_cooldown
    
    try:
        # Check if file has been modified
        current_mtime = os.path.getmtime('config.json')
        
        # Add cooldown to prevent excessive reloading
        if time.time() - config_reload_cooldown < 1.0:  # 1 second cooldown
            return
            
        if current_mtime != config_file_mtime:
            print("🔄 Config file modified - reloading configuration...")
            
            old_config = config
            new_config = load_config()
            
            if new_config and new_config != old_config:
                config = new_config
                config_reload_cooldown = time.time()
                
                # Print what changed
                if old_config:
                    if old_config.get("keywords") != new_config.get("keywords"):
                        print(f"📝 Keywords updated: {list(new_config['keywords'].keys())}")
                    if old_config.get("role_mentions") != new_config.get("role_mentions"):
                        print(f"🎭 Role mentions updated: {list(new_config['role_mentions'].keys())}")
                    if old_config.get("case_sensitive") != new_config.get("case_sensitive"):
                        print(f"🔍 Case sensitivity: {new_config['case_sensitive']}")
                    if old_config.get("reply_to_message") != new_config.get("reply_to_message"):
                        print(f"💬 Reply mode: {'Reply' if new_config['reply_to_message'] else 'Send new message'}")
                
                print("✅ Configuration reloaded successfully!")
            else:
                print("⚠️  Config file changed but content is identical")
                
    except Exception as e:
        print(f"⚠️  Error checking config reload: {e}")

# Initial config load
config = load_config()
print(f"Config loaded: {config}")

# Create bot instance
bot = commands.Bot(command_prefix='!', self_bot=True, chunk_guilds_at_startup=False)

# Shutdown handler
async def shutdown_bot():
    """Properly shutdown the bot"""
    print("🔄 Shutting down bot...")
    
    # Stop config monitoring
    if hasattr(bot, '_config_monitor_task'):
        bot._config_monitor_task.cancel()
    
    # Close bot connection
    if not bot.is_closed():
        await bot.close()
    
    print("✅ Bot shutdown complete")

# Handle graceful shutdown
import signal
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}, shutting down...")
    try:
        # Schedule shutdown in the event loop
        if bot.loop and not bot.loop.is_closed():
            bot.loop.create_task(shutdown_bot())
    except:
        pass
    sys.exit(0)

# Register signal handlers (Unix-like systems)
if platform.system() != "Windows":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
else:
    # Windows-specific shutdown handling
    import atexit
    import ctypes
    
    def windows_shutdown_handler():
        """Handle Windows process termination"""
        print("🛑 Windows process termination detected")
        try:
            # Clean up lock file
            if os.path.exists("bot.lock"):
                os.remove("bot.lock")
                print("🗑️  Lock file removed during Windows shutdown")
        except:
            pass
    
    # Register Windows shutdown handlers
    atexit.register(windows_shutdown_handler)
    
    # Handle Windows console close events
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCtrlHandler(lambda x: windows_shutdown_handler(), True)
    except:
        pass

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Monitoring for keywords: {list(config["keywords"].keys())}')
    if config.get("role_mentions"):
        print(f'Monitoring for role mentions: {list(config["role_mentions"].keys())}')
    print('Bot is ready!')
    
    # Start config monitoring task
    bot._config_monitor_task = bot.loop.create_task(config_monitor_task())

async def config_monitor_task():
    """Background task to monitor config.json for changes"""
    print("🔍 Config monitoring started - changes will be auto-reloaded")
    
    while not bot.is_closed():
        try:
            # Check for config changes
            check_config_reload()
            
            # Wait 2 seconds before next check
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"⚠️  Error in config monitor: {e}")
            await asyncio.sleep(5)  # Wait longer on error

@bot.event
async def on_message(message):
    # Don't respond to our own messages unless configured to do so
    if message.author == bot.user and not config.get("respond_to_self", False):
        return
    
    # Check for role mentions first
    if message.role_mentions and config.get("role_mentions"):
        for role in message.role_mentions:
            role_id = str(role.id)
            if role_id in config["role_mentions"]:
                try:
                    response = config["role_mentions"][role_id]
                    if config.get("reply_to_message", True):
                        await message.reply(response)
                        print(f'Replied to role mention "{role.name}" in channel {message.channel}')
                    else:
                        await message.channel.send(response)
                        print(f'Sent message for role mention "{role.name}" in channel {message.channel}')
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
                    print(f'Replied to keyword "{keyword}" in channel {message.channel}')
                else:
                    await message.channel.send(response)
                    print(f'Sent message for keyword "{keyword}" in channel {message.channel}')
                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)
                break  # Only respond to the first matching keyword
            except discord.HTTPException as e:
                print(f'Error sending response: {e}')
            except Exception as e:
                print(f'Unexpected error: {e}')

# Manual reload command for immediate configuration updates
@bot.command(name='reload', hidden=True)
async def reload_config_command(ctx):
    """Manually reload configuration (only works for the bot owner)"""
    if ctx.author.id == bot.user.id:
        try:
            print("🔄 Manual config reload requested...")
            old_config = config.copy()
            
            # Force reload
            global config_file_mtime
            config_file_mtime = 0  # Reset modification time to force reload
            
            new_config = load_config()
            if new_config and new_config != old_config:
                print("✅ Manual configuration reload successful!")
                await ctx.send("✅ Configuration reloaded successfully!")
            else:
                print("⚠️  Manual reload: No changes detected")
                await ctx.send("⚠️  No configuration changes detected")
                
        except Exception as e:
            error_msg = f"❌ Error reloading config: {e}"
            print(error_msg)
            await ctx.send(error_msg)

# Note: This bot primarily reads and replies based on config.json
# All configuration should be done by editing config.json directly
# Use !reload to manually reload configuration if needed

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
        print("\n🛑 Bot shutdown requested...")
    finally:
        # Clean up lock file
        try:
            os.remove(lock_file)
            print("🗑️  Lock file removed")
        except:
            pass
        
        # Ensure bot is properly closed
        try:
            if not bot.is_closed():
                print("🔄 Closing bot connection...")
                bot.loop.run_until_complete(bot.close())
                print("✅ Bot connection closed")
        except:
            pass
        
        print("✅ Bot shutdown complete")
