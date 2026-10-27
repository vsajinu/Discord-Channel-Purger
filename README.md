# Discord Channel Purger

A small Discord bot that wipes every message in a channel.

## Commands

- `/purge` deletes every message in the channel. Anything newer than 14 days goes fast. Older messages get deleted one by one, so a big channel can take a while.
- `/nuke` clones the channel and deletes the original. It's instant, but the channel gets a new ID.

Both commands ask you to confirm first. `/purge` needs Manage Messages and `/nuke` needs Manage Channels.

## Setup

1. `pip install -r requirements.txt`
2. Open `.env` and replace `paste_your_token_here` with your bot token (Developer Portal > Bot > Reset Token)
3. `python purge_bot.py`

To lock the bot to one channel, set `TARGET_CHANNEL_ID` in `purge_bot.py`.

`.env` is in `.gitignore`, so your token won't get committed. `.env.example` is the copy that's safe to commit.
