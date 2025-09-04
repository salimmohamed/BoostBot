#!/usr/bin/env python3

import discord
from discord.ext import commands
import json
import logging

# Disable all Discord logging
logging.getLogger('discord').disabled = True
logging.getLogger('discord.client').disabled = True
logging.getLogger('discord.gateway').disabled = True
logging.getLogger('discord.http').disabled = True

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return None

def main():
    print("=== Test Bot Starting ===")
    
    config = load_config()
    if not config:
        print("ERROR: Failed to load config")
        return
    
    print(f"Config loaded: {len(config.get('keywords', {}))} keywords")
    print(f"Token length: {len(config.get('token', ''))} characters")
    
    if not config.get("token") or config["token"] == "YOUR_USER_TOKEN_HERE":
        print("ERROR: No valid token found")
        return
    
    print("Creating bot instance...")
    try:
        bot = commands.Bot(command_prefix='!', self_bot=True, chunk_guilds_at_startup=False)
        print("Bot instance created successfully")
    except Exception as e:
        print(f"ERROR creating bot: {e}")
        return
    
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        print('Bot is ready!')
    
    print("Starting bot...")
    try:
        bot.run(config["token"])
    except Exception as e:
        print(f"ERROR running bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
