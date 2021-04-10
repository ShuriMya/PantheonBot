import os
from dotenv import load_dotenv

from discord.ext import commands
from bot.commands import UserCommands

load_dotenv()

bot = commands.Bot(command_prefix="+")

bot.add_cog(UserCommands(bot))
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
