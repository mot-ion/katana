import json
import time, os
import string, glob, re
import checksfrfr
from gil_utility.gperms import *

from guilded.ext import commands, tasks

intervals = (
    ('years', 86400 * 30 * 12),
    ('months', 86400 * 30),
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1))

def create_guild_json(guild_id):
    creating_file = open(f"./Database/Reminders/{guild_id}.json", "w")
    creating_file.write("""[]""")
    creating_file.close()

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    string_final = ""
    for i in result:
        string_final += f"{i}, "
    return string_final[:-2]



async def stop_reminder(self, g_id, i):
    try:
        #for guild in self.client.guilds:
        #  if guild.id == g_id:
        #    for ch in guild.channels:
        #      if ch.id == data["channel_id"]:
        #        channel = ch
        #print(f"Channel-ID: {data['channel_id']}")
        reminders = json.load(open(f"./Database/Reminders/{g_id}.json", "r"))
        channel = await self.client.fetch_channel(reminders[i]["channel_id"])
        author_id = reminders[i]["author_id"]
        reason = reminders[i]["reason"]
        result_embed = guilded.Embed(
            title=f"Reminder",
            color=self.color,
            description=
            f"<@{author_id}> your reminder is over!\n\nReason:\n```{reason}```"
        )
        result_embed.set_footer(
            icon_url=reminders[i]["avatar"],
            text="Reminder Ended!")
        msg = await channel.send(embed=result_embed, private=True)
        #await msg.reply(embed=guilded.Embed(color=self.color, description=f"<@{author_id}>"), private=True)
        reminders = json.load(open(f"./Database/Reminders/{g_id}.json", "r"))
        reminders[i]['finished'] = True
        clean_json = json.dump(reminders,
                               open(f"./Database/Reminders/{g_id}.json", "w"),
                               indent=4)
        return True
    except Exception as e:
        print(str(e) + " " + str(g_id))
        print(e.__class__.__name__)
        if e.__class__.__name__ in ["NotFound", "Forbidden"]:
            giveaways = json.load(open(f"./Database/Reminders/{g_id}.json", "r"))
            giveaways[i]['finished'] = True
            clean_json = json.dump(giveaways,
                                   open(f"./Database/Reminders/{g_id}.json", "w"),
                                   indent=4)
            return True


def convert(date):
    inputSplit = re.split('(\d+)', date)
    #   inputSplit looks like ['', '1', 'd', '3', 'h', '10', 'm', '1', 's']
    del inputSplit[0]
    #   inputSplit now looks like ['1', 'd', '3', 'h', '10', 'm', '1', 's']

    seconds = 0

    #  Looping through inputSplit, from first to last letter
    for i in range(1, len(inputSplit), 2):
        timeModifier = inputSplit[i]  # Modifier is the letter
        timeValue = int(inputSplit[i - 1])  # Value is number before modifier

        # Same if loop as yours. Checking modifiers and adding the value
        if timeModifier.lower() in ["day", "days", "d"]:
            seconds += 86400 * timeValue
        elif timeModifier.lower() in ["y", "year", "years"]:
            seconds += 86400 * timeValue * 30 * 12
        elif timeModifier.lower() in ["w", "week", "weeks"]:
            seconds += 604800 * timeValue
        elif timeModifier in ["M", "month", "months"]:
            seconds += 86400 * timeValue * 30
        elif timeModifier.lower() in ["h", "hour", "hours"]:
            seconds += 3600 * timeValue
        elif timeModifier in ["m", "minute", "minutes"]:
            seconds += 60 * timeValue
        elif timeModifier.lower() in ["s", "second", "seconds"]:
            seconds += timeValue * 1
    until = int(seconds)
    return (until)

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        #self.config = json.load(open("config.json", "r"))
        self.color = int("0xad13eb", 16) + 0x200
        self.reminder_task.start()

    def cog_unload(self):
        self.reminder_task.cancel()

    def find_member_named(self, team, argument: str, ctx):
        try:
            argument = argument.replace("@", "")
        except:
            pass
        mem = guilded.utils.find(
            lambda m: m.name == argument or m.nick == argument or m.id ==
            argument, team.members)
        if mem is not None:
            return mem
        if len(ctx.message.mentions) != 0:
            return ctx.message.mentions[0]
        return None

    async def user_not_found(self, ctx, member):
        color = guilded.Color.from_rgb(239, 83, 80)
        embed = guilded.Embed(
            description=
            f"Couldn\'t find a member with the name/id {member}\nTry putting in the user ID, if the mention doesn\'t work.",
            color=color)
        embed.set_author(name=ctx.author,
                         icon_url=avatar_handler(ctx.author))
        await ctx.channel.send(embed=embed, silent=True)
        return

    async def role_not_found(self, ctx, role):
        color = guilded.Color.from_rgb(239, 83, 80)
        embed = guilded.Embed(
            description=
            f"Couldn\'t find a role with the name/id {role}\nTry putting in the role ID, if the mention doesn\'t work.",
            color=color)
        embed.set_author(name=ctx.author,
                         icon_url=avatar_handler(ctx.author))
        await ctx.channel.send(embed=embed, silent=True)
        return

    def find_channel_named(self, team, argument: str):
        try:
            argument = argument.replace("#", "")
        except:
            pass
        return guilded.utils.find(
            lambda m: m.name == argument or m.id == argument, team.channels)

    def find_role_named(self, team, argument: str):
        try:
            argument = argument.replace("@", "")
        except:
            pass
        return guilded.utils.find(
            lambda m: m.name == argument or m.id == argument, team.roles)


    @tasks.loop(seconds=15)
    async def reminder_task(self):
        await asyncio.sleep(1)
        path = './Database/Reminders/'
        for filename in glob.glob(os.path.join(path, '*.json')):
            try:
                with open(os.path.join(os.getcwd(), filename), 'r') as f:
                #print(filename)
                    reminders = json.load(f)
                    dump_reminders = reminders

                if not len(reminders) == 0:
                    for i in range(len(reminders)):
                        skip = False
                        data = reminders[i]
                        if int(time.time()) > data["end_time"]:
                            if data["finished"] is True:

                                skip = True
                            if not skip:
                                await stop_reminder(self, filename[21:-5], i)
                    f.close()
                else:
                  os.remove(filename)
            except Exception as e:
                print(e, "a")

        for flnm in glob.glob(os.path.join(path, '*.json')):
            try:
                with open(os.path.join(os.getcwd(), flnm), 'r') as f:
                    reminderss = json.load(f)
                    dump_reminders = reminderss

                if not len(reminderss) == 0:
                    a = 0
                    for b in range(len(reminderss)):
                        skip = False
                        data = reminderss[a]
                        if int(time.time()) > data["end_time"]:
                            if data["finished"] is True:
                                if int(time.time()
                                       ) - data["end_time"] > 20:
                                    dump_reminders.pop(a)
                                    a -= 1
                        a += 1
                    clean_json = json.dump(
                        dump_reminders,
                        open(f"./Database/Reminders/{flnm[21:-5]}.json", "w"),
                        indent=4)
                    f.close()
            except Exception as e:
                print(e)
    @commands.command(name="create-reminder", aliases=["remind-me","remind"])
    async def create_reminder(self, ctx, dlay=None, *, reason=None):
      if reason is None:
        reason = "No reason given"
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
        return
      try:
        if dlay and dlay.isdigit():
          dlay = f'{dlay}m'
        delay = convert(dlay)
        if delay < 1:
          color = guilded.Colour.red()
          embed = guilded.Embed(
            description=
          f"Invalid `<delay>` argument given.\n\nUsage:\n`remind-me <delay> [reason]`",
          color=color)
          embed.set_author(name=ctx.author, icon_url=avatar_handler(ctx.author))
          await ctx.channel.send(embed=embed, silent=True)
          return
      except Exception as e:
        print(e)
        color = guilded.Colour.red()
        embed = guilded.Embed(
          description=
          f"Invalid `<delay>` argument given.\n\nUsage:\n`remind-me <delay> [reason]`",
        color=color)
        embed.set_author(name=ctx.author, icon_url=avatar_handler(ctx.author))
        await ctx.channel.send(embed=embed, silent=True)
        return
      reminder_id = ''.join([random.choice(string.ascii_letters + string.digits)for i in range(9)])
      embed = guilded.Embed(color=self.color, description=f"Reminding {ctx.author.mention} in {display_time(delay)}")
      now = int(time.time())
      embed.set_author(name=ctx.author, icon_url=avatar_handler(ctx.author))
      embed.set_footer(text=f"Reminder-ID: {reminder_id}")
      #await ctx.reply(embed=embed, private=True, silent=True)
      av = avatar_handler(ctx.author).url
      try:

        await ctx.message.delete()
      except:
        pass
      try:
          await ctx.channel.send(embed=embed, private=True)
      except:
          pass
      if not os.path.exists(f"./Database/Reminders/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
      reminders = json.load(
            open(f"./Database/Reminders/{ctx.message.guild.id}.json", "r"))
      data = {
            "author_id": ctx.author.id,
            "end_time": now + delay,
            "channel_id": ctx.channel.id,
            "reminder_id": reminder_id,
            "reason": reason.replace("`", "").replace("@", "@​"),
            "finished": False,
            "avatar": av
        
        }
      reminders.append(data)
      clean_json = json.dump(reminders,
                               open(f"./Database/Reminders/{ctx.message.guild.id}.json",
                                    "w"),
                               indent=4,
                               separators=(",", ": "))




def setup(client):
    client.add_cog(Reminder(client))
