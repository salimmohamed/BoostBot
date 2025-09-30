# Discord Auto-Responder Bot

## The Problem

I play WoW and wanted to get into boosting (helping other players for gold). The boosting communities post keys in Discord channels and it's first-come-first-serve. I was missing opportunities because I couldn't respond fast enough - by the time I saw the message, someone else already claimed it.

So I built this bot to automatically reply when certain keywords are posted. Works great for boosting, but you could use it for anything really.

## What It Does

- Monitors Discord channels for keywords (like "key" or "boost")
- Automatically responds with your message
- Only works in channels you specify (so you don't spam everywhere)
- Has a GUI to set up keywords and responses
- Detects role mentions - responds when specific roles are mentioned
- Channel filtering - restrict bot to only certain channels

## Quick Setup

1. Install Python packages:
```bash
pip install -r requirements.txt
```

2. Get your Discord token (Google "how to get Discord token" - there are tutorials)

3. Run the GUI:
```bash
python gui.py
```

4. Set up your bot:
   - Put your Discord token in the Configuration tab
   - Add keywords like "key", "boost", "carry" in the Keywords tab
   - Add your response like "I can do this! DM me"
   - Add the channel IDs where boosting keys are posted
   - Click Start Bot

## How It Works

1. Bot watches the channels you specify
2. When someone posts a message with your keywords
3. Bot automatically replies with your message
4. You get notified and can DM the person

## Configuration

The bot uses `config.json` for all settings. The GUI automatically creates and manages this file.

### Configuration Structure

```json
{
    "token": "YOUR_ACTUAL_TOKEN_HERE",
    "keywords": {
        "key": "I can do this key! DM me",
        "boost": "I'm available for boosting! DM me",
        "carry": "I can carry this! DM me"
    },
    "case_sensitive": false,
    "respond_to_self": false,
    "reply_to_message": true,
    "role_mentions": {
        "123456789012345678": "This role was mentioned!"
    },
    "allowed_channels": ["123456789012345678"]
}
```

### Configuration Options

- token: Your Discord user token
- keywords: Dictionary of keyword → response pairs
- case_sensitive: Whether keyword matching is case-sensitive
- respond_to_self: Whether to respond to your own messages
- reply_to_message: Whether to reply to original message or send new one
- role_mentions: Dictionary of role ID → response pairs
- allowed_channels: List of channel IDs where bot should respond (empty = all channels)

## How to Use

### Keywords
- Add keywords and responses in the Keywords tab
- Bot will automatically detect these keywords in messages
- Supports case-sensitive or case-insensitive matching

### Role Mentions
- Get role IDs by right-clicking roles → Copy ID (requires Developer Mode)
- Add role IDs and responses in the Role Mentions tab
- Bot responds when those roles are mentioned in messages

### Channel Filtering
- Get channel IDs by right-clicking channels → Copy ID (requires Developer Mode)
- Add channel IDs in the Channels tab
- Leave empty to listen in all channels
- Bot only responds in specified channels

### Bot Control
- Use the Start/Stop buttons to control the bot
- View live logs in the Bot Control tab
- Bot automatically cleans up when stopped

## Getting IDs

### Channel ID
1. Right-click the channel name
2. Select "Copy ID" (requires Developer Mode)

### Role ID
1. Right-click the role name in the server member list
2. Select "Copy ID" (requires Developer Mode)

### Enable Developer Mode
1. User Settings → Advanced
2. Toggle "Developer Mode" on


## Important Notes

- Configuration changes: After modifying settings in the GUI, restart the bot to apply changes
- Token security: Never share your Discord token
- Channel restrictions: If no channels are specified, bot listens in ALL channels
- Process locking: Only one bot instance can run at a time

## ⚠️ Warning

This is a self-bot (uses your personal account). Discord doesn't like self-bots and could ban your account. Use at your own risk!

## Troubleshooting

### Common Issues

1. "Another bot instance is already running"
   - Check if bot is running in another terminal
   - Delete `bot.lock` file if it exists

2. "Invalid token"
   - Verify your token is correct
   - Get a fresh token using the browser method

3. Bot not responding
   - Check if channel is in allowed_channels list
   - Verify keywords are correctly configured
   - Check bot logs in the GUI

4. Python 3.13+ compatibility issues
   - Install `legacy-cgi` and `audioop-lts` packages
