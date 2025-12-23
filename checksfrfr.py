import guilded
from guilded.ext import commands
#import dtbs as db
import asyncio
import json, os


async def enabled(ctx, command):
    u = os.path.exists(f"Database/Disabled/{ctx.guild.id}.json")
    if u is False:
        return True
    else:
        json_file = open(f"Database/Disabled/{ctx.guild.id}.json", "r")
        json_content = json.load(json_file)
    if command in json_content["disabled"]:

        def devperms(user: guilded.User, ctx):
            if user.id in ctx.bot.devids:
                return True
            return False

        json_file.close()
        await ctx.reply(f"The command {command} was disabled in this Server",
                        private=True)
        if not devperms(ctx.author, ctx):
            return False
        else:

            def check(message):
                return (message.author.id == ctx.author.id
                        and message.content.lower() == 'bypass')

            try:
                message = await ctx.bot.wait_for('message',
                                                 timeout=20,
                                                 check=check)
                await message.add_reaction(90002171)
            except asyncio.TimeoutError:
                return False
        return True
    json_file.close()
    return True
