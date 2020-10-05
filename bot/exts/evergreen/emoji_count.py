import datetime
import logging
import random
from collections import defaultdict

import discord
from discord.ext import commands

from bot.constants import Colours, ERROR_REPLIES
from bot.utils.pagination import LinePaginator

log = logging.getLogger(__name__)


class EmojiCount(commands.Cog):
    """Command that give random emoji based on category."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def embed_builder(self, emoji: dict) -> [discord.Embed, str]:
        """Generates an embed with the emoji names and count."""
        embed = discord.Embed(
            color=Colours.orange,
            title="Emoji Count",
            timestamp=datetime.datetime.utcnow()
        )
        msg = []

        if len(emoji) == 1:
            for key, value in emoji.items():
                msg.append(f"There are **{len(value)}** emojis in the **{key}** category")
                embed.set_thumbnail(url=random.choice(value).url)

        else:
            for key, value in emoji.items():
                emoji_choice = random.choice(value)
                emoji_info = f'There are **{len(value)}** emojis in the **{key}** category\n'
                if emoji_choice.animated:
                    msg.append(f'<a:{emoji_choice.name}:{emoji_choice.id}> {emoji_info}')
                else:
                    msg.append(f'<:{emoji_choice.name}:{emoji_choice.id}> {emoji_info}')
        return embed, msg

    @staticmethod
    def generate_invalid_embed(ctx: commands.Context) -> [discord.Embed, str]:
        """Genrates error embed."""
        embed = discord.Embed(
            color=Colours.soft_red,
            title=random.choice(ERROR_REPLIES)
        )
        msg = []

        emoji_dict = defaultdict(list)
        for emoji in ctx.guild.emojis:
            emoji_dict[emoji.name.split("_")[0]].append(emoji)

        error_comp = ', '.join(key for key in emoji_dict.keys())
        msg.append(f"These are the valid categories\n```{error_comp}```")
        return embed, msg

    @commands.command(name="emoji_count", aliases=["ec"])
    async def emoji_count(self, ctx: commands.Context, *, emoji_category: str = None) -> None:
        """Returns embed with emoji category and info given by the user."""
        emoji_dict = defaultdict(list)

        for emoji in ctx.guild.emojis:
            if emoji_category is None:
                log.trace("Emoji Category not provided by the user")
                emoji_dict[emoji.name.split("_")[0]].append(emoji)
            elif emoji.name.split("_")[0] in emoji_category:
                log.trace("Emoji Category provided by the user")
                emoji_dict[emoji.name.split("_")[0]].append(emoji)

        if len(emoji_dict) == 0:
            embed, msg = self.generate_invalid_embed(ctx)
        else:
            embed, msg = self.embed_builder(emoji_dict)
        await LinePaginator.paginate(lines=msg, ctx=ctx, embed=embed)


def setup(bot: commands.Bot) -> None:
    """Emoji Count Cog load."""
    bot.add_cog(EmojiCount(bot))
