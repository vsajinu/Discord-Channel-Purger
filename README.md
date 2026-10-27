# Discord Channel Purger

Discord bot for wiping a channel.

## Commands

- `/purge` - deletes every message in the channel. Messages older than 14 days are deleted one at a time, so big channels take a while.
- `/nuke` - clones the channel and deletes the original. Instant, but the channel ID changes.

Both ask for confirmation. `/purge` needs Manage Messages, `/nuke` needs Manage Channels.

## Setup

```
pip install -r requirements.txt
```

Create a `.env` file:

```
DISCORD_TOKEN=your_token_here
```

Then run `python purge_bot.py`.

Set `TARGET_CHANNEL_ID` in `purge_bot.py` to lock the commands to one channel.
