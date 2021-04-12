import discord
from discord.ext import commands
from requests.utils import quote

from bot.tft_utils import get_tft_profile, get_tft_full_profile
from bot.db_utils import register_member, fetch_member


def get_user_not_found_embed(username):
    embed = discord.Embed()
    embed.add_field(
        name="**Pas de profil trouvé**",
        value=f"Je n'ai pas trouvé **{username}** sur le serveur EUW",
        inline=False,
    )
    return embed


def get_unregistered_embed():
    embed = discord.Embed()
    embed.add_field(
        name="**Pas de profil enregistré**",
        value=(
            "Vous n'avez pas enregistré votre compte TFT, "
            "pour ce faire veuillez utiliser la commande `+register` suivi de votre pseudo TFT. \n"
        ),
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
        name="**Parties classées**",
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
                f"{tft_data['activity']['last_game']['date'].strftime('Le %d/%m/%Y à %H:%M')} - "
                f"{tft_data['activity']['last_game']['game_type']} - "
                f"{tft_data['activity']['last_game']['position']}\u1D49 place"
            ),
            inline=False,
        )

    if "activity" in tft_data and "num_recent_games" in tft_data["activity"]:
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
        if not args:
            username = fetch_member(self.bot.db_conn, ctx.author.id)
        else:
            username = " ".join(args)

        if not username:
            await ctx.send(embed=get_unregistered_embed())
            return

        tft_data = get_tft_profile(username)

        if tft_data:
            embed = add_profile_footer(format_profile_embed(tft_data), username)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=get_user_not_found_embed(username))

    @commands.command()
    async def full(self, ctx, *args):
        if not args:
            username = fetch_member(self.bot.db_conn, ctx.author.id)
        else:
            username = " ".join(args)

        if not username:
            await ctx.send(embed=get_unregistered_embed())
            return

        tft_data = get_tft_full_profile(username)

        if tft_data:
            embed = add_profile_footer(format_full_profile_embed(tft_data), username)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=get_user_not_found_embed(username))

    @commands.command()
    async def register(self, ctx, *args):
        tft_username = " ".join(args)
        embed = discord.Embed()

        try:
            register_member(self.bot.db_conn, ctx.author.id, tft_username)
        except Exception:
            embed.add_field(
                name="**Erreur lors de l'enregistrement**",
                value=(
                    f"Je n'ai pas réussi à enregistrer votre compte **{tft_username}** dans la base de données. "
                    "Veuillez contacter un modérateur."
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="**Profil enregistré**",
                value=f"Votre profil TFT **{tft_username}** a bien été lié à votre compte Discord",
                inline=False,
            )
        finally:
            await ctx.send(embed=embed)
