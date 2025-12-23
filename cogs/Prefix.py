from guilded.ext import commands
import constants as var
#import dtbs as db
from functions import get_prefix
import os, json
from gil_utility.gperms import *


class Prefix(commands.Cog):
    """
    class of Prefix commands.
    Attributes:
        bot(commands.Bot): bot reference
        prefix(dict): dictionary contains the custom prefix setting for servers
        db: database connection "custom_prefix"
    """
    def __init__(self, client: commands.Bot):
        """
        Constructor for Prefix class.
        Args:
            bot(commands.Bot): pass in bot reference
        """
        self.client = client

    def avatar_handler(self, member: guilded.Member):
        #avatar = str(member.avatar)[:-3]
        #webp = avatar + "webp"
        #png = avatar + "png"
        #if member.bot:
        #  av = webp
        #else:
        #  av = png
        #print(av)
        #print(member.avatar)
        if member.avatar == "None" or member.avatar is None:
            return f"https://www.guilded.gg/asset/DefaultUserAvatars/profile_{random.randint(1, 5)}.png"
        return member.avatar  #av

    @commands.command()
    # @user_or_admin(791950104680071188)  # This me
    async def prefix(self, ctx):
        embed = guilded.Embed(
            title="Prefix",
            description=(f"The prefix for this server is\n"
                         f"```{await get_prefix(ctx)}```\n"
                         f"Wanna change it? Use set-prefix!"),
            color=var.C_MAIN)
        await ctx.channel.send(embed=embed)

    @commands.command(name="set-prefix")
    # @user_or_admin(791950104680071188)  # This me
    async def set_prefix(self, ctx):
        if not (await administrator_check(ctx)):
            return
        await ctx.send(embed=guilded.Embed(
            description=(
                "Next message which you will send will become the prefix "
                ":eyes:\nTo cancel it enter\n"
                f"```{await get_prefix(ctx)}cancel```"),
            color=var.C_ORANGE).set_footer(
                text="Automatic cancellation after 1 minute"))

        #try:
        #await bot_msg.clear_reactions()

        #except disnake.Forbidden:
        #pass

        def message_check(message):
            return (message.author == ctx.author
                    and message.channel.id == ctx.channel.id)

        try:
            user_msg = await self.client.wait_for('message',
                                                  check=message_check,
                                                  timeout=60.0)

            # Cancel
            if user_msg.content == await get_prefix(ctx) + "cancel":
                await ctx.send("Cancelled prefix change.")

            # Same prefixes so deleting the doc
            elif user_msg.content == var.DEFAULT_PREFIX:
                os.remove(f"Database/Prefixes/{ctx.guild.id}.json")
                # await db.PREFIXES.delete_one({"_id": ctx.guild.id})
                await ctx.send(embed=guilded.Embed(
                    description="Changed your prefix to the default one\n"
                    f"```{var.DEFAULT_PREFIX}```"))

            # If current prefix is default then insert new
            elif await get_prefix(ctx) == var.DEFAULT_PREFIX:
                json_db = open(f"Database/Prefixes/{ctx.guild.id}.json", "w")

                json_db.write(json.dumps({"prefix": user_msg.content}))
                json_db.close()

                await ctx.send(embed=guilded.Embed(
                    description=
                    f"Updated your new prefix, it's\n```{user_msg.content}```")
                               )

            else:  # Exists so just update it
                #guild_doc = await db.PREFIXES.find_one(
                #    {"_id": user_msg.guild.id}
                #)

                #   new_data = {
                #         "$set": {
                #              "prefix": user_msg.content
                # }
                #       }

                #       await db.PREFIXES.update_one(guild_doc, new_data)
                json_db = open(f"Database/Prefixes/{ctx.guild.id}.json", "w")

                json_db.write(json.dumps({"prefix": user_msg.content}))
                json_db.close()
                await ctx.send(embed=guilded.Embed(
                    description=
                    f"Updated your new prefix, it's\n```{user_msg.content}```")
                               )

        except asyncio.TimeoutError:
            await ctx.send(embed=guilded.Embed(
                description="You took too long to enter your "
                f"new prefix {ctx.author.mention}"))


def setup(client: commands.Bot):
    """
    Necessary function for a cog that initialize the Prefix class.
    Args:
        bot (commands.Bot): passing in bot for class initialization
    Returns:
        None
    """
    client.add_cog(Prefix(client))
    print("Loaded Cog: Prefix")


def teardown(client: commands.Bot):
    """
    Function to be called upon Cog unload, in this case, it will print message in CMD.
    Args:
        bot (commands.Bot): passing in bot reference for unload.
    Returns:
        None
    """
    client.remove_cog("Prefix")
    print("Unloaded Cog: Prefix")
