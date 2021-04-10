import discord
from discord.ext import commands
from requests.utils import quote

from bot.tft_utils import get_tft_profile, get_tft_full_profile


def get_user_not_found_embed(username):
    embed = discord.Embed()
    embed.add_field(
        name="**Pas de profil trouvé**",
        value=f"Je n'ai pas trouvé **{username}** sur le serveur EUW",
        inline=False,
    )
    return embed


def add_profile_footer(embed, username):
    return embed.add_field(
        name="\u200B",
        value=f"[Aller sur le profil lolchess](http://lolchess.gg/profile/euw/{quote(username)})",
        inline=False,
    )


def format_profile_embed(tft_data):
    embed = discord.Embed(title=f"Profil de {tft_data['summoner_name']}")
    embed.add_field(
        name="**Classement**",
        value=f"{tft_data['rank']} - {tft_data['lp']} LP",
        inline=False,
    )
    embed.add_field(
        name="**Parties**",
        value=f"{tft_data['games']}",
    )
    embed.add_field(
        name="**Tops 1**",
        value=f"{tft_data['wins']} ({100 * tft_data['winrate']:.2f} %)",
    )
    return embed


def format_full_profile_embed(tft_data):
    embed = format_profile_embed(tft_data)

    if "activity" in tft_data and "last_game" in tft_data["activity"]:
        embed.add_field(
            name="**Dernière game**",
            value=(
                f"Le {tft_data['activity']['last_game']['date'].isoformat()}\n"
                f"{tft_data['activity']['last_game']['game_type']}\n"
                f"Résultat: {tft_data['activity']['last_game']['position']}\u1D49 position"
            ),
            inline=False,
        )

    if "activity" in tft_data and "last_game" in tft_data["num_recent_games"]:
        embed.add_field(
            name="**Activité**",
            value=(
                f"{'Plus de ' if tft_data['activity']['num_recent_games'] >= 50 else ''}"
                f"{tft_data['activity']['num_recent_games']} partie"
                f"{'s' if tft_data['activity']['num_recent_games'] > 1 else ''} "
                f"ces 2 dernières semaines"
            ),
            inline=False,
        )
    return embed


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, *args):
        username = " ".join(args)
        tft_data = get_tft_profile(username)

        if tft_data:
            embed = add_profile_footer(format_profile_embed(tft_data), username)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=get_user_not_found_embed(username))

    @commands.command()
    async def full(self, ctx, *args):
        username = " ".join(args)
        tft_data = get_tft_full_profile(username)

        if tft_data:
            embed = add_profile_footer(format_full_profile_embed(tft_data), username)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=get_user_not_found_embed(username))
