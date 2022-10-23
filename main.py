# -------------
# Copyright (c) 2022, https://github.com/BabyEntchen/
# All rights reserved.
# -------------


import discord
from discord.ext import commands
from discord.commands import *
import sqlite3


# ------------- Database Handler -------------
async def add_entry(channel_id: int, guild_id: int):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    if await get_channel(guild_id) is None:
        c.execute("INSERT INTO temp_channels VALUES (?, ?)", (channel_id, guild_id))
    else:
        c.execute("UPDATE temp_channels SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))
    conn.commit()
    conn.close()
    return True


async def create_db():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS temp_channels (channel_id INTEGER, guild_id INTEGER)")
    con.commit()
    con.close()


async def remove_entry(guild_id: int):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("DELETE FROM temp_channels WHERE guild_id = ?", (guild_id,))
    conn.commit()
    conn.close()
    return True


async def get_channel(guild_id: int):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT channel_id FROM temp_channels WHERE guild_id = ?", (guild_id,))
    channel = c.fetchone()
    conn.close()
    return int(channel[0]) if channel is not None else None

# ------------- Bot -------------
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())  # You have to activate the intents in the developer portal (https://discord.com/developers/applications/your_app_id/bot)
temp_channels = []  # This is a list of all the temporary channels


@bot.event
async def on_ready():
    await create_db()  # Creates the database (if it doesn't exist)
    print(f'Logged in as {bot.user.name}')


@bot.slash_command(name="set", permissions=["manage_channels"])
@option("channel", description="The channel to set")
async def _set(ctx, channel: discord.VoiceChannel):
    """Set the channel to be used for temporary channels"""
    await add_entry(channel.id, ctx.guild.id)  # Adds the channel to the database
    await ctx.respond(f"Set the Tempchannel to {channel.mention}", ephemeral=True)


@bot.slash_command(name="reset")
async def _reset(ctx):
    """Reset the channel to be used for temporary channels"""
    await remove_entry(ctx.guild.id)  # Removes the channel from the database
    await ctx.respond(f"Set the channel to None", ephemeral=True)


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and await get_channel(after.channel.guild.id) == after.channel.id:  # Checks if the channel is the one set in the database
        channel = await after.channel.clone(name=f"{member.name}'s channel")  # Clones the Tempchannel
        await member.move_to(channel)  # Moves the member to the new channel
        temp_channels.append(channel.id)  # Adds the channel to the list of temporary channels

    if before.channel and before.channel.id in temp_channels:  # Checks if the channel is a temporary channel
        if len(before.channel.members) == 0:  # Checks if the member is in the channel after the event was triggered
            await before.channel.delete()  # Deletes the channel
            temp_channels.remove(before.channel.id)  # Removes the channel from the list of temporary channels



if __name__ == "__main__":
    print("Copyright (c) https://github.com/BabyEntchen/reeeaaally-simple-tempchannels/")
    bot.run("your_token_here")
