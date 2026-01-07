# SafeFolks Telegram Bot

A Telegram bot that records trust relationships in groups. When added to a group, it records that the group owner trusts all other members.

## Bot Username

`@safefolks_bot`

## Features

- 🤖 Automatically detects group owner
- 🤝 Records trust relationships (owner → members)
- 💾 Persistent storage of trust data
- 📊 View trust status with `/status` command
- 🔍 Scan group members with `/scan` command

## How It Works

1. Add the bot to your Telegram group
2. Use `/scan` to register the group and detect the owner
3. The bot records that the owner trusts all group members
4. As members send messages or join, trust relationships are automatically recorded
5. Use `/status` to view all trust relationships in the group

## Setup

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/emranbm/safefolks.git
cd safefolks/bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration file:
```bash
cp config.example.py config.py
```

4. Edit `config.py` and add your bot token:
```python
BOT_TOKEN = "your_bot_token_here"
```

### Running the Bot

```bash
python safefolks_bot.py
```

The bot will start and listen for updates. Keep this process running to keep the bot active.

## Usage

### Commands

- `/start` - Welcome message and bot introduction
- `/help` - Show help information
- `/scan` - Scan group members and register the group
- `/status` - Show trust relationships in the group

### Adding to a Group

1. Start a chat with `@safefolks_bot`
2. Add the bot to your group
3. Make the bot an admin (required to see member list)
4. Use `/scan` to initialize the group

### Trust Relationships

The bot records **unidirectional** trust relationships:
- ✅ Owner trusts members (recorded)
- ❌ Members trust owner (NOT recorded)

Trust is recorded when:
- A member sends a message in the group
- A member joins the group
- The `/scan` command is used

## Data Storage

Trust data is stored in `trust_data.json` in the following format:

```json
{
  "groups": {
    "group_id": {
      "name": "Group Name",
      "owner_id": 123456,
      "owner_name": "Owner Name",
      "added_at": "2024-01-01T00:00:00"
    }
  },
  "trusts": [
    {
      "group_id": -1234567,
      "truster_id": 123456,
      "truster_name": "Owner Name",
      "trustee_id": 789012,
      "trustee_name": "Member Name",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

## Development

### Project Structure

```
bot/
├── safefolks_bot.py       # Main bot script
├── config.example.py      # Example configuration
├── config.py              # Your configuration (not in git)
├── requirements.txt       # Python dependencies
├── trust_data.json        # Data storage (not in git)
└── README.md             # This file
```

### Running in Production

For production deployment, consider using:
- **systemd** service on Linux
- **Docker** container
- **Screen** or **tmux** session
- **Cloud hosting** (Heroku, AWS, etc.)

Example systemd service:

```ini
[Unit]
Description=SafeFolks Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/safefolks/bot
ExecStart=/usr/bin/python3 safefolks_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

Part of the SafeFolks project.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.
