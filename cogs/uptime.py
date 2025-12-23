import guilded
from guilded.ext import commands
import time
from gil_utility.gperms import *


class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.command_count = 0


    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.command_count += 1
        # Update the total command count in the file
        with open('files/total_commands.txt', 'r+') as file:
            total_commands = int(file.read())
            total_commands += 1
            file.seek(0)
            file.write(str(total_commands))

        # Check for milestone and congratulate the user
        if total_commands % 100000 == 0:
            await ctx.send(embed=guilded.Embed(color=guilded.Color.green(), description=f"Congratulations {ctx.author.mention}! You've executed the {total_commands}th command! 🎉\nJoin us at [guilded.gg/karma](https://guilded.gg/karma) for a custom role!"))

    @commands.command()
    async def uptime(self, ctx):
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Read the total commands ever run from the file
        with open('files/total_commands.txt', 'r') as file:
            total_commands = int(file.read())

        embed = guilded.Embed(title="Bot Uptime", color=guilded.Color.blue())
        embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m {seconds}s", inline=False)
        embed.add_field(name="Commands Executed This Session", value=f"{self.command_count}", inline=False)
        embed.add_field(name="Total Commands Executed", value=f"{total_commands}", inline=False)
        embed.add_field(name="Milestone Hint",
                        value="When the total commands executed hits a milestone (e.g., 100k, 200k, etc.), there will be a surprise!",
                        inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Uptime(bot))