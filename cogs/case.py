import guilded, random
from guilded.ext import commands
import asyncio
import re, os, json
import checksfrfr
import constants as var
async def guild_prefix(_bot, message):
    if not message.guild:
        #return commands.when_mentioned_or(var.DEFAULT_PREFIX)(_bot, message)
        return [
             "<@4ZRw5qp4> ", "<@4ZRw5qp4>", "@Katana ", "@Katana", f"{var.DEFAULT_PREFIX} ", var.DEFAULT_PREFIX
        ]


# prefix_doc = await db.PREFIXES.find_one({"_id": message.guild.id})
    prefix = os.path.exists(f"Database/Prefixes/{message.guild.id}.json")

    if prefix is True:
        json_file = open(f"Database/Prefixes/{message.guild.id}.json", "r")
        json_content = json.load(json_file)
        json_file.close()
    if not prefix:
        #return commands.when_mentioned_or(var.DEFAULT_PREFIX)(_bot, message)
        return [
            "<@4ZRw5qp4> ", "<@4ZRw5qp4>", "@Katana ", "@Katana", f"{var.DEFAULT_PREFIX} ", var.DEFAULT_PREFIX
        ]

    #return commands.when_mentioned_or(prefix_doc["prefix"])(_bot, message)
    return [
        "<@4ZRw5qp4> ", "<@4ZRw5qp4>", "@Katana ", "@Katana", f'{json_content["prefix"]} ',
        f'{json_content["prefix"]}'
    ]


class Case(commands.Cog):
    def __init__(self, bot):
        #super().__init__()
        self.bot = bot
        self.case_insensitive = True

    @commands.Cog.listener()
    async def on_message(self, message):
      if message.author.id not in self.bot.devids:
        return
      prefixes = await guild_prefix(self.bot, message)
      notsame = False
      for prefix in prefixes:
                if message.content.startswith(prefix):
                    msg = message.content
                    # Extrahiere den Befehlsteil der Nachricht
                    command_part = message.content[len(prefix):].split()[0].lower()
                    # Ersetze den Befehlsteil der Nachricht durch die Kleinbuchstaben-Version
                    new_msg = prefix + command_part + message.content[len(prefix) + len(command_part):]
                    if new_msg != msg:
                      message.content = prefix + command_part + message.content[len(prefix) + len(command_part):]
                      notsame = True
                      break
      if notsame:
        await self.bot.process_commands(message)

        
def setup(bot):
    bot.add_cog(Case(bot))