import guilded
import asyncio
from guilded.ext import commands
import time
from gil_utility.gperms import *


class Introducing(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.nick_cache = {}

    @commands.Cog.listener()
    async def on_bot_add(self, server, member):
      defaultChannel = None
      try:
        defaultChannel = await server.fetch_default_channel()
      except:
        pass
      if defaultChannel is None:
        try:
          defaultChannel = await self.client.wait_for("message", timeout=30, check=lambda response: response.server == server)
        except asyncio.TimeoutError:
          return
      embed = guilded.Embed(color = guilded.Color.blue(),
      description = f"Hey {member.mention} :hi:\nThanks for adding me to your Server :heart_gil:\nTo get started, type `.help`\nIf you need any further help, feel free to join our Support-Server!")
      embed.add_field(name="Links", value="[Support](https://guilded.gg/karma) • [Invite](https://www.guilded.gg/b/25a00b00-e6ca-4211-b86e-1af0be2cf2a3) • [Bot-Page](https://katana.pages.dev)", inline=True)
      embed.set_image(url="https://cdn.discordapp.com/attachments/981904880514007121/1038210248755912854/FE1CE8A5-749C-46EA-A623-EC32945C937A.jpeg")
      try:
        await asyncio.sleep(0.2)
        await defaultChannel.send(embed=embed)
      except:
        return
      return
      
      
       

def setup(bot):
    bot.add_cog(Introducing(bot))