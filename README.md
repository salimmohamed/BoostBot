# Discord Self-Bot - Keyword Auto-Responder

⚠️ **CRITICAL WARNING**: This bot violates Discord's Terms of Service and can result in **permanent account termination**. Use at your own risk!

## What This Bot Does

This Discord self-bot monitors messages and automatically responds when certain keywords are detected or specific roles are mentioned. It operates using your user account (not a bot account) and can be controlled through a modern GUI interface.

## Features

- **Keyword Detection**: Automatically detects specified keywords in messages
- **Role Mention Detection**: Responds when specific roles are mentioned
- **Channel Filtering**: Restrict bot responses to specific channels only
- **Customizable Responses**: Set custom responses for each keyword and role
- **Case Sensitivity**: Toggle case-sensitive keyword matching
- **Self-Response Control**: Choose whether to respond to your own messages
- **Reply Mode**: Choose between replying to messages or sending new ones
- **Modern GUI Interface**: Easy-to-use CustomTkinter interface for configuration
- **Process Management**: Start/stop bot with proper cleanup and logging
- **Rate Limiting**: Built-in delays to avoid Discord rate limits
- **Multi-Instance Protection**: Prevents multiple bot instances from running

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you're using Python 3.13+, you may need to install additional packages:
```bash
pip install legacy-cgi audioop-lts
```

### 2. Get Your Discord User Token

**Easy Method:**
1. Open Discord in your browser
2. Press **F12** to open Developer Tools
3. Press **Ctrl + Shift + M** to enable mobile device emulation
4. Go to **Application** tab → **Local Storage** → **https://discord.com/**
5. Find the **token** key and copy its value
6. Replace `YOUR_ACTUAL_TOKEN_HERE` in your `config.json`

**Alternative Console Method:**
1. Open Discord in your browser
2. Press **F12** to open Developer Tools
3. Press **Ctrl + Shift + M** to enable mobile device emulation
4. Paste this code in the console and press Enter:
```javascript
const iframe = document.createElement('iframe');
console.log(
  'Token: %c%s',
  'font-size:16px;',
  JSON.parse(document.body.appendChild(iframe).contentWindow.localStorage.token)
);
iframe.remove();
```

### 3. Run the Bot

#### Option A: GUI Interface (Recommended)
```bash
python gui.py
```

The GUI provides:
- **Configuration Tab**: Set token and bot settings
- **Keywords Tab**: Add/remove keyword-response pairs
- **Role Mentions Tab**: Configure role mention responses
- **Channels Tab**: Restrict bot to specific channels
- **Bot Control Tab**: Start/stop bot with live logs

#### Option B: Command Line
```bash
python bot.py
```

## Configuration

The bot uses `config.json` for all settings. The GUI automatically creates and manages this file.

### Configuration Structure

```json
{
    "token": "YOUR_ACTUAL_TOKEN_HERE",
    "keywords": {
        "hello": "Hi there! How can I help you?",
        "help": "I'm here to assist you!",
        "test": "This is an automated response!"
    },
    "case_sensitive": false,
    "respond_to_self": false,
    "reply_to_message": true,
    "role_mentions": {
        "123456789012345678": "This role was mentioned!",
        "987654321098765432": "Another role response!"
    },
    "allowed_channels": ["123456789012345678", "987654321098765432"]
}
```

### Configuration Options

- **token**: Your Discord user token
- **keywords**: Dictionary of keyword → response pairs
- **case_sensitive**: Whether keyword matching is case-sensitive
- **respond_to_self**: Whether to respond to your own messages
- **reply_to_message**: Whether to reply to original message or send new one
- **role_mentions**: Dictionary of role ID → response pairs
- **allowed_channels**: List of channel IDs where bot should respond (empty = all channels)

## How to Use

### 1. Keywords
- Add keywords and responses in the Keywords tab
- Bot will automatically detect these keywords in messages
- Supports case-sensitive or case-insensitive matching

### 2. Role Mentions
- Get role IDs by right-clicking roles → Copy ID (requires Developer Mode)
- Add role IDs and responses in the Role Mentions tab
- Bot responds when those roles are mentioned in messages

### 3. Channel Filtering
- Get channel IDs by right-clicking channels → Copy ID (requires Developer Mode)
- Add channel IDs in the Channels tab
- Leave empty to listen in all channels
- Bot only responds in specified channels

### 4. Bot Control
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

## Safety Features

- **Rate Limiting**: Built-in delays to avoid Discord detection
- **Error Handling**: Comprehensive error handling for network issues
- **Configuration Validation**: Automatic validation of all settings
- **Process Management**: Proper cleanup and lock file management
- **Channel Restrictions**: Limit bot activity to specific channels

## Important Notes

- **Configuration Changes**: After modifying settings in the GUI, restart the bot to apply changes
- **Token Security**: Never share your Discord token
- **Channel Restrictions**: If no channels are specified, bot listens in ALL channels
- **Process Locking**: Only one bot instance can run at a time

## Risks and Disclaimers

- **Account Termination**: Discord actively bans self-bots
- **Detection**: Discord may detect automated behavior
- **Terms of Service**: This violates Discord's ToS
- **No Support**: Use at your own risk

## Alternative Recommendation

Consider using a legitimate Discord bot instead:
1. Create a bot application at https://discord.com/developers/applications
2. Use regular `discord.py` (not `discord.py-self`)
3. Invite the bot to your server
4. Much safer and legal approach

## Troubleshooting

### Common Issues

1. **"Another bot instance is already running"**
   - Check if bot is running in another terminal
   - Delete `bot.lock` file if it exists

2. **"Invalid token"**
   - Verify your token is correct
   - Get a fresh token using the browser method

3. **Bot not responding**
   - Check if channel is in allowed_channels list
   - Verify keywords are correctly configured
   - Check bot logs in the GUI

4. **Python 3.13+ compatibility issues**
   - Install `legacy-cgi` and `audioop-lts` packages

## License

This project is for educational purposes only. Use responsibly and at your own risk.
