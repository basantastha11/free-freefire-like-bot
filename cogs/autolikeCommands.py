import discord
from discord.ext import commands
from discord import app_commands
import os
import json

CONFIG_FILE = "like_channels.json"

class AutoLikeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="autolike", description="Add a UID to the auto-like list.")
    @app_commands.describe(uid="Free Fire UID", owner="Owner of the UID (optional)")
    async def autolike(self, ctx: commands.Context, uid: str, owner: str = "Unknown"):
        if not uid.isdigit():
            await ctx.reply("❌ UID must be a number.", ephemeral=True)
            return

        guild_id = str(ctx.guild.id)
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"servers": {}}

        server = data["servers"].setdefault(guild_id, {})
        uids = server.setdefault("uids", [])
        owners = server.setdefault("owners", {})

        if uid in uids:
            await ctx.send(f"⚠️ UID `{uid}` is already added.", ephemeral=True)
            return

        uids.append(uid)
        owners[uid] = owner

        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

        await ctx.send(
            f"✅ UID `{uid}` has been added to the auto-like list for this server.\nOwned by **{owner}**.",
            ephemeral=False
        )

async def setup(bot):
    await bot.add_cog(AutoLikeCommands(bot))
