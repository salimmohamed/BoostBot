import discord
import asyncio
import json
import os
from discord.ext import commands

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
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
            "reply_to_message": True
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

# Load configuration
config = load_config()
print(f"Config loaded: {config}")

# Create bot instance
bot = commands.Bot(command_prefix='!', self_bot=True, chunk_guilds_at_startup=False)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Monitoring for keywords: {list(config["keywords"].keys())}')
    print('Bot is ready!')

@bot.event
async def on_message(message):
    # Don't respond to our own messages unless configured to do so
    if message.author == bot.user and not config.get("respond_to_self", False):
        return
    
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

# No commands - this bot only reads and replies based on config.json
# All configuration must be done by editing config.json directly

if __name__ == "__main__":
    if config["token"] == "YOUR_USER_TOKEN_HERE":
        print("ERROR: Please set your Discord user token in config.json")
        print("Easy method to get your token:")
        print("1. Open Discord in your browser")
        print("2. Press F12 to open Developer Tools")
        print("3. Press Ctrl + Shift + M to enable mobile device emulation")
        print("4. Go to Application tab → Local Storage → https://discord.com/")
        print("5. Find the 'token' key and copy its value")
        print("6. Replace 'YOUR_USER_TOKEN_HERE' in config.json")
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
