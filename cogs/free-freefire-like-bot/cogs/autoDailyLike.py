import discord
from discord.ext import commands, tasks
import aiohttp
import json
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
CONFIG_FILE = "like_channels.json"

class AutoDailyLike(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.auto_like_loop.start()

    def cog_unload(self):
        self.auto_like_loop.cancel()
        self.bot.loop.create_task(self.session.close())

    @tasks.loop(hours=24)
    async def auto_like_loop(self):
        await self.bot.wait_until_ready()
        await self.perform_auto_likes()

    async def perform_auto_likes(self):
        try:
            with open(CONFIG_FILE, "r") as file:
                data = json.load(file)
        except Exception as e:
            print(f"❌ Failed to read {CONFIG_FILE}: {e}")
            return

        servers = data.get("servers", {})

        for guild_id, guild_data in servers.items():
            like_channels = guild_data.get("like_channels", [])
            for channel_id in like_channels:
                uid = guild_data.get("uid")
                if not uid:
                    continue

                try:
                    url = f"https://free-fire-like1.p.rapidapi.com/like?uid={uid}"
                    headers = {
                        "x-rapidapi-key": RAPIDAPI_KEY,
                        "x-rapidapi-host": "free-fire-like1.p.rapidapi.com"
                    }

                    async with self.session.get(url, headers=headers) as resp:
                        if resp.status != 200:
                            print(f"❌ API Error for UID {uid}: {resp.status}")
                            continue

                        data = await resp.json()
                        channel = self.bot.get_channel(int(channel_id))
                        if not channel:
                            continue

                        embed = discord.Embed(
                            title="AUTO LIKE REPORT",
                            timestamp=datetime.now(),
                            color=0x2ECC71 if data.get("status") == 1 else 0xE74C3C
                        )

                        if data.get("status") == 1:
                            embed.description = (
                                f"👤 **PLAYER:** {data.get('player', 'Unknown')}\n"
                                f"🆔 **UID:** {uid}\n"
                                f"👍 **ADDED:** +{data.get('likes_added', 0)}\n"
                                f"📊 **BEFORE:** {data.get('likes_before')}\n"
                                f"📈 **AFTER:** {data.get('likes_after')}"
                            )
                        else:
                            embed.description = (
                                f"⚠️ UID `{uid}` has already received max likes today."
                            )

                        embed.set_footer(text="Auto Like Service • Basanta Bot")
                        await channel.send(embed=embed)
                        await asyncio.sleep(3)

                except Exception as e:
                    print(f"❌ Error for UID {uid}: {e}")

async def setup(bot):
    await bot.add_cog(AutoDailyLike(bot))
