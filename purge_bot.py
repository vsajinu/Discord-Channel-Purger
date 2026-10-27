"""
Purge bot - wipes every message in a specific Discord channel.

Setup is in README.md. Short version:
  1. pip install -r requirements.txt
  2. Put your token in the .env file next to this script
  3. python purge_bot.py
"""

import os
from pathlib import Path

import discord
from discord import app_commands
from dotenv import load_dotenv

# Loads .env from the same folder as this script, no matter where you run it from
load_dotenv(Path(__file__).resolve().parent / ".env")

# Lock the commands to one channel. None = works in whatever channel you run it in.
TARGET_CHANNEL_ID = None  # e.g. 123456789012345678

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def wrong_channel(interaction: discord.Interaction) -> bool:
    return TARGET_CHANNEL_ID is not None and interaction.channel_id != TARGET_CHANNEL_ID


class ConfirmView(discord.ui.View):
    """Yes/No buttons so nobody wipes a channel by accident."""

    def __init__(self, author_id: int):
        super().__init__(timeout=30)
        self.author_id = author_id
        self.confirmed = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Not your button.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Yes, delete everything", style=discord.ButtonStyle.danger)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        await interaction.response.edit_message(content="Working on it...", view=None)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Cancelled.", view=None)
        self.stop()


@tree.command(name="purge", description="Delete every message in this channel")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction):
    if wrong_channel(interaction):
        await interaction.response.send_message("This command is locked to a different channel.", ephemeral=True)
        return

    view = ConfirmView(interaction.user.id)
    await interaction.response.send_message(
        "This deletes **every message** in this channel. Sure?", view=view, ephemeral=True
    )
    await view.wait()
    if not view.confirmed:
        return

    # Messages under 14 days old get bulk deleted (fast).
    # Older ones get deleted one at a time (slow, Discord rate limits this).
    deleted = await interaction.channel.purge(limit=None, reason=f"Purge by {interaction.user}")
    await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)


@tree.command(name="nuke", description="Clone this channel and delete the original (instant full wipe)")
@app_commands.default_permissions(manage_channels=True)
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    if wrong_channel(interaction):
        await interaction.response.send_message("This command is locked to a different channel.", ephemeral=True)
        return

    view = ConfirmView(interaction.user.id)
    await interaction.response.send_message(
        "This recreates the channel empty (same name, perms, category) and deletes the old one. Sure?",
        view=view,
        ephemeral=True,
    )
    await view.wait()
    if not view.confirmed:
        return

    old = interaction.channel
    new = await old.clone(reason=f"Nuke by {interaction.user}")
    await new.edit(position=old.position)
    await old.delete(reason=f"Nuke by {interaction.user}")
    await new.send("Channel wiped.")
    # Note: the channel ID changes after a nuke, so update TARGET_CHANNEL_ID if you set it.


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        msg = "You don't have permission to do that."
    else:
        msg = f"Something went wrong: {error}"
    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user} - slash commands synced")


if __name__ == "__main__":
    if not TOKEN or TOKEN == "paste_your_token_here":
        raise SystemExit("No token found. Open the .env file next to purge_bot.py and paste your bot token in.")
    client.run(TOKEN)
