# Discord Self-Bot - Keyword Auto-Responder

⚠️ **CRITICAL WARNING**: This bot violates Discord's Terms of Service and can result in **permanent account termination**. Use at your own risk!

## What This Bot Does

This bot monitors Discord messages and automatically responds when certain keywords are detected. It operates using your user account (not a bot account).

## Features

- **Keyword Detection**: Automatically detects specified keywords in messages
- **Customizable Responses**: Set custom responses for each keyword
- **Case Sensitivity**: Toggle case-sensitive matching
- **Self-Response Control**: Choose whether to respond to your own messages
- **Live Configuration**: Add/remove keywords without restarting
- **Rate Limiting**: Built-in delays to avoid Discord rate limits

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
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
5. Copy the token from the console output



### 3. Configure the Bot

Create a `config.json` file with your Discord token. In the `keywords` section, each entry is a pair: the text on the left is the message to look for, and the text on the right (in quotes) is the reply the bot will send.

```json
{
    "token": "YOUR_ACTUAL_TOKEN_HERE",
    "keywords": {
        "hello": "Hi there! How can I help you?",
        "help": "I'm here to assist you!",
        "test": "This is an automated response!",
        "good morning": "Good morning! Have a great day!",
        "good night": "Good night! Sleep well!"
    },
    "case_sensitive": false,
    "respond_to_self": false
}
```

### 4. Run the Bot

```bash
python bot.py
```

## Configuration

The bot only reads and replies based on your `config.json` file. To modify keywords or settings:

1. **Stop the bot** (Ctrl+C)
2. **Edit `config.json`** with your changes
3. **Restart the bot** to load the new configuration

## Configuration Options

- **token**: Your Discord user token
- **keywords**: Dictionary of keyword → response pairs
- **case_sensitive**: Whether keyword matching is case-sensitive
- **respond_to_self**: Whether to respond to your own messages

## Safety Features

- Rate limiting to avoid Discord detection
- Error handling for network issues
- Configuration validation
- Safe token handling

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

## License

This project is for educational purposes only. Use responsibly and at your own risk.
