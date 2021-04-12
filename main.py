import os
import psycopg2
import asyncio
from dotenv import load_dotenv

from discord.ext import commands
from bot.commands import UserCommands
from bot.db_utils import init_db

load_dotenv()


class DbBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=kwargs.pop("command_prefix"),
        )

        self.db_conn = kwargs.pop("db_conn")

    async def on_ready(self):
        print("Bot is now ready.\nUsername: {0}\nID: {0.id}".format(self.user))


async def run():
    db_conn = psycopg2.connect(
        f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}"
    )
    init_db(db_conn)

    bot = DbBot(command_prefix="+", db_conn=db_conn)
    bot.add_cog(UserCommands(bot))

    try:
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))
    except KeyboardInterrupt:
        await db_conn.close()
        await bot.logout()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
