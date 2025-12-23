import json
import datetime
import time, os
import string, glob, re
import checksfrfr
from gil_utility.gperms import *

from guilded.ext import commands, tasks
from guilded.ext.commands.converters import (_INT_ID_REGEX, _UUID_REGEX, )

intervals = (
    ('years', 86400 * 30 * 12),
    ('months', 86400 * 30),
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1))


def create_guild_json(guild_id):
    creating_file = open(f"./giveaways/{guild_id}.json", "w")
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


async def stop_giveaway(self, g_id, i):
    try:
        #for guild in self.client.guilds:
        #  if guild.id == g_id:
        #    for ch in guild.channels:
        #      if ch.id == data["channel_id"]:
        #        channel = ch
        #print(f"Channel-ID: {data['channel_id']}")
        giveaways = json.load(open(f"./giveaways/{g_id}.json", "r"))
        channel = await self.client.fetch_channel(giveaways[i]["channel_id"])
        #giveaway_message = await channel.fetch_message(g_id)
        #users = await giveaway_message.reactions[0].users().flatten()
        users = giveaways[i]["users"]
        #users.pop(users.index(self.client.user))
        if len(users) < giveaways[i]["winners"]:
            winners_number = len(users)
        else:
            winners_number = giveaways[i]["winners"]

        winners = []

        for a in range(int(winners_number)):
            winner = random.choice(users)
            winners.append(winner)
            users.remove(winner)

        users_mention = []
        for user in winners:
            start = "<@"
            start += user
            start += ">"
            users_mention.append(start)
        mentions = ', '.join(users_mention)
        no_winners = False
        if len(winners) < 1:
            await channel.send(
                f"Nobody won the giveaway with the ID **{giveaways[i]['giveaway_id']}** :("
            )
            no_winners = True
        prize = giveaways[i]['prize']
        host = giveaways[i]['host']
        result_embed = guilded.Embed(
            title=f"🎉 {prize} 🎉",
            color=self.color,
            description=
            f"Congratulations {mentions} you won the giveaway!\n\nHost: <@{host}>"
        )
        result_embed.set_footer(
            icon_url=
            "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
            text="Giveaway Ended!")
        giveaways = json.load(open(f"./giveaways/{g_id}.json", "r"))
        giveaways[i]['finished'] = True
        try:
            if not no_winners:
                await channel.send(embed=result_embed)
        except Exception as e:
            print(e)
        #ghost_ping = await channel.send(f"<@{data['host']}>")
        #await ghost_ping.delete()
        #giveaways.pop(i)
        clean_json = json.dump(giveaways,
                               open(f"./giveaways/{g_id}.json", "w"),
                               indent=4)
        return True
    except Exception as e:
        try:
          print(str(e) + " " + str(g_id))
          print(e.__class__.__name__)
        except:
          print(e)
        if e.__class__.__name__ in ["NotFound", "Forbidden"]:
            giveaways = json.load(open(f"./giveaways/{g_id}.json", "r"))
            giveaways[i]['finished'] = True
            clean_json = json.dump(giveaways,
                                   open(f"./giveaways/{g_id}.json", "w"),
                                   indent=4)
            return True


async def reroll_giveaway(self, g_id, i):
    #for guild in self.client.guilds:
    #  if guild.id == g_id:
    #    for ch in guild.channels:
    #      if ch.id == data["channel_id"]:
    #        channel = ch
    #print(f"Channel-ID: {data['channel_id']}")
    giveaways = json.load(open(f"./giveaways/{g_id}.json", "r"))
    channel = await self.client.fetch_channel(giveaways[i]["channel_id"])
    #giveaway_message = await channel.fetch_message(g_id)
    #users = await giveaway_message.reactions[0].users().flatten()
    users = giveaways[i]["users"]
    #users.pop(users.index(self.client.user))
    if len(users) < giveaways[i]["winners"]:
        winners_number = len(users)
    else:
        winners_number = giveaways[i]["winners"]

    winners = []

    for a in range(int(winners_number)):
        winner = random.choice(users)
        winners.append(winner)
        users.remove(winner)

    users_mention = []
    for user in winners:
        start = "<@"
        start += user
        start += ">"
        users_mention.append(start)
    mentions = ', '.join(users_mention)
    no_winners = False
    if len(winners) < 1:
        await channel.send(
            f"Nobody won the giveaway with the ID **{giveaways[i]['giveaway_id']}** :("
        )
        no_winners = True
    prize = giveaways[i]['prize']
    host = giveaways[i]['host']
    result_embed = guilded.Embed(
        title=f"🎉 {prize}  | Reroll 🎉",
        color=self.color,
        description=
        f"Congratulations {mentions} you won the giveaway!\n\nHost: <@{host}>")
    result_embed.set_footer(
        icon_url=
        "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
        text="Giveaway Ended!")
    giveaways = json.load(open(f"./giveaways/{g_id}.json", "r"))
    giveaways[i]['finished'] = True
    try:
        if not no_winners:
            await channel.send(embed=result_embed)
    except Exception as e:
        print(e)
    #ghost_ping = await channel.send(f"<@{data['host']}>")
    #await ghost_ping.delete()
    #giveaways.pop(i)
    clean_json = json.dump(giveaways,
                           open(f"./giveaways/{g_id}.json", "w"),
                           indent=4)
    return True


async def delete_giveaway(ctx, g_id, i):
    giveaways = json.load(open(f"./giveaways/{g_id}.json", "r"))
    giveaways.pop(i)
    clean_json = json.dump(giveaways,
                           open(f"./giveaways/{g_id}.json", "w"),
                           indent=4)
    await ctx.channel.send("The giveaway has been deleted")


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        #self.config = json.load(open("config.json", "r"))
        self.color = int("0xad13eb", 16) + 0x200
        self.giveaway_task.start()

    def cog_unload(self):
        self.giveaway_task.cancel()

    @tasks.loop(seconds=15)
    async def giveaway_task(self):
        print("giveaway loop")
        await asyncio.sleep(1)
        path = './giveaways/'
        for filename in glob.glob(os.path.join(path, '*.json')):
            try:
                with open(os.path.join(os.getcwd(), filename), 'r') as f:
                #print(filename)
                    giveaways = json.load(f)
                    dump_giveaways = giveaways

                if not len(giveaways) == 0:
                    for i in range(len(giveaways)):
                        skip = False
                        data = giveaways[i]
                        if int(time.time()) > data["end_time"]:
                            if data["finished"] is True:

                                skip = True
                            if not skip:
                                print(filename[12:-5])
                                await stop_giveaway(self, filename[12:-5], i)
                    f.close()
                else:
                  os.remove(filename)
            except Exception as e:
                print(e)
                os.remove(filename)

        for flnm in glob.glob(os.path.join(path, '*.json')):
            try:
                f = open(os.path.join(os.getcwd(), flnm), 'r')
                giveawayss = json.load(f)
                dump_giveaways = giveawayss

                if not len(giveawayss) == 0:
                    a = 0
                    for b in range(len(giveawayss)):
                        skip = False
                        data = giveawayss[a]
                        if int(time.time()) > data["end_time"]:
                            if data["finished"] is True:
                                if int(time.time()
                                       ) - data["end_time"] > 604800:
                                    dump_giveaways.pop(a)
                                    a -= 1
                        a += 1
                    clean_json = json.dump(
                        dump_giveaways,
                        open(f"./giveaways/{flnm[12:-5]}.json", "w"),
                        indent=4)
                    f.close()
            except Exception as e:
                print(e)

    @commands.command(name="giveaway", aliases=["gstart", "g-start"])
    async def giveaway(self, ctx: commands.Context):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return

        init = await ctx.send(
            "🎉 New Giveaway 🎉\nPlease answer the following questions to finalize the creation of the Giveaway"
        )  #embed=discord.Embed(
        #title="🎉 New Giveaway ! 🎉",
        #description="Please answer the following questions to finalize the creation of the Giveaway",
        #color=self.color)
        #           .set_footer(icon_url="https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png", text=self.client.user.name))

        questions = [
            "What would be the prize of the giveaway?",
            "What would the giveaway channel be like? (Please mention the giveaway channel)",
            "What would be the duration of the giveaway ? Example: (1d | 1h10m | 1m | 10h50s)",
            "How many winners do you want for this Giveaway ?"
        ]

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        index = 1
        answers = []
        question_message = None
        for question in questions:
            embed = guilded.Embed(
                title="Giveaway 🎉", description=question, color=self.color
            ).set_footer(
                icon_url=
                "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                text=self.client.user.name)
            if index == 1:
                question_message = await ctx.send(embed=embed)
            else:
                #await ctx.send(question)
                try:
                    await question_message.edit(embed=embed)
                except:
                    question_message = await ctx.send(embed=embed)

            try:
                user_response = await self.client.wait_for("message",
                                                           timeout=120,
                                                           check=check)
                try:
                    await user_response.delete()
                except:
                    pass
            except asyncio.TimeoutError:
                await ctx.send("You took too long to answer the question"
                               )  #embed=guilded.Embed(
                #title="Error",
                # color=self.color,
                #description="You took too long to answer this question"
                #))
                return
            else:
                answers.append(user_response.content)
                index += 1
        try:
            #print(str(answers[1]))
            if answers[1][-1] == " ":
                ch = answers[1][:-1]
            else:
                ch = answers[1]
            channel = await find_channel_named(ctx.guild, ch)
            #ch = str(answers[1]).replace("#", "")

            #channel_id = str(answers[1][2:-1])
        except ValueError:
            await ctx.send(
                "You didn't mention the channel correctly, try putting in the ID instead"
            )  #.format(ctx.channel.mention))
            return

        try:
            winners = abs(int(answers[3]))
            if winners <= 0:
                await ctx.send("You did not enter a postive number.")
                return
        except ValueError:
            await ctx.send("You did not enter an integer.")
            return
        prize = answers[0].title()
        #channel = await self.client.fetch_channel(channel_id)
        converted_time = convert(answers[2])
        if converted_time == -1:
            await ctx.send(
                "You did not enter the correct unit of time (s|m|d|h)")
        elif converted_time == -2:
            await ctx.send("Your time value should be an integer.")
            return
        try:
            await init.delete()
            await question_message.delete()
        except:
            pass
        giveaway_id = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for i in range(9)
        ])
        giveaway_embed = guilded.Embed(
            title="🎉 {} 🎉".format(prize),
            color=self.color,
            description=
            f'» **{winners}** {"winner" if winners == 1 else "winners"}\n'
            f'» Hosted by {ctx.author.mention}\n\n'
            f'» **Type .gjoin {giveaway_id} to get into the giveaway.**\n')
        giveaway_embed.set_footer(
            icon_url=
            "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
            text="Ends at")

        giveaway_embed.timestamp = datetime.datetime.utcnow(
        ) + datetime.timedelta(seconds=converted_time)
        giveaway_message = await channel.send(embed=giveaway_embed)
        f'''**Prize:**
{prize}                                             
» **{winners}** {"winner" if winners == 1 else "winners"}
» Hosted by @{ctx.author}

» **Type .gjoin {giveaway_id} to get into the giveaway.**\n'''#)#embed=giveaway_embed)
        #await giveaway_message.add_reaction("🎉")
        now = int(time.time())
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        data = {
            "prize": prize,
            "finished": False,
            "host": ctx.author.id,
            "winners": winners,
            "end_time": now + converted_time,
            "channel_id": channel.id,
            "giveaway_id": giveaway_id,
            "message_id": giveaway_message.id,
            "message_content":
            f'» **{winners}** {"winner" if winners == 1 else "winners"}\n» Hosted by {ctx.author.mention}\n\n» **Type .gjoin {giveaway_id} to get into the giveaway.**\n',
            "users": [],
            "blocked": [],
            "locked": False,
            "whitelisted_roles": []
        }
        giveaways.append(data)
        clean_json = json.dump(giveaways,
                               open(f"./giveaways/{ctx.message.guild.id}.json",
                                    "w"),
                               indent=4,
                               separators=(",", ": "))

    @commands.command(name="gstop",
                      aliases=["gcancel", "g-stop", "g-cancel"],
                      usage="{giveaway_id}")
    async def gstop(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        #await ctx.message.delete()
        guild_id = ctx.message.guild.id
        found = False
        giveaways = json.load(open(f"./giveaways/{ctx.guild.id}.json", "r"))
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                return await stop_giveaway(self, guild_id, i)
        return await ctx.send("Couldn\'t find such a giveaway ID")
        #embed=discord.Embed(title="Error",
        #description="This giveaway ID is not found.",
        #color=self.color))

    @commands.command(name="g-delete",
                      aliases=["gdelete"],
                      usage="{giveaway_id}")
    async def delete(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        #await ctx.message.delete()
        guild_id = ctx.message.guild.id
        found = False
        giveaways = json.load(open(f"./giveaways/{ctx.guild.id}.json", "r"))
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                return await delete_giveaway(ctx, guild_id, i)
        return await ctx.send("Couldn\'t find such a giveaway ID")

    @commands.command(name="g-join", aliases=["gjoin"])
    async def join(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if giveaways[giveaway_range]["locked"]:
            white_list = False
            for role in ctx.author.roles:
                if role.id in giveaways[giveaway_range]["whitelisted_roles"]:
                    white_list = True
            if not white_list:
                await ctx.channel.send(
                    "This giveaway has been locked by a Server Admin, only whitelisted people can enter it!"
                )
                return
        if giveaways[giveaway_range]["finished"]:
            await ctx.channel.send("This giveaway has already ended!")
            return
        if ctx.message.author.id in giveaways[giveaway_range]["blocked"]:
            await ctx.channel.send(
                "You were blocked from participating at this giveaway by a Server Admin!"
            )
            return
        if ctx.message.author.id not in giveaways[giveaway_range]["users"]:
            giveaways[giveaway_range]["users"].append(ctx.message.author.id)
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully joined the giveaway with the ID: **{giveaway_id}**\n\nUse the 'show-giveaway' command to obtain more informations about the giveaway."
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                desc += f"» **Total participants:** {len(giveaways[giveaway_range]['users'])}"
                if giveaways[giveaway_range]['locked']:
                    desc += "\n:lock: This giveaway has been locked"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass

        else:
            await ctx.channel.send(
                f"You have already joined this giveaway!\n\nYou may quit it via 'g-leave {giveaway_id}'"
            )

    @commands.command(name="gleave", aliases=["gquit", "g-leave", "g-quit"])
    async def leave(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if ctx.message.author.id in giveaways[giveaway_range]["users"]:
            giveaways[giveaway_range]["users"].remove(ctx.message.author.id)
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully quitted the giveaway with the ID: **{giveaway_id}**"
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                if len(giveaways[giveaway_range]['users']) > 0:
                    desc += f"\n» **Total participants:** {len(giveaways[giveaway_range]['users'])}"
                if giveaways[giveaway_range]['locked']:
                    desc += "\n:lock: This giveaway has been locked"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass
        else:
            await ctx.channel.send(
                "You didn\'t even participate at this giveaway so I didn\'t removed you. You may join the giveaway via 'g-join %s'"
                % (giveaway_id))

    @commands.command(name="g-block", aliases=["gblock"])
    async def block(self, ctx: commands.Context, giveaway_id, *, target):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        member = await find_member_named(ctx.guild, target, ctx)
        if not member:
            await user_not_found(ctx, target)
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if member.id not in giveaways[giveaway_range]["blocked"]:
            if member.id in giveaways[giveaway_range]["users"]:
                giveaways[giveaway_range]["users"].remove(member.id)
            giveaways[giveaway_range]["blocked"].append(member.id)
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully blocked {member} from the giveaway with the ID: **{giveaway_id}**"
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                desc += f"» **Total participants:** {len(giveaways[giveaway_range]['users'])}"
                if giveaways[giveaway_range]["locked"]:
                    desc += "\n:lock: This giveaway has been locked"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass

        else:
            await ctx.channel.send(
                f"{member} is already blocked from that giveaway, you may unblock him via 'g-unblock {giveaway_id} {member.id}'"
            )

    @commands.command(name="g-unblock", aliases=["gunblock"])
    async def unblock(self, ctx: commands.Context, giveaway_id, *, target):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        member = await find_member_named(ctx.guild, target, ctx)
        if not member:
            await user_not_found(ctx, target)
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if member.id in giveaways[giveaway_range]["blocked"]:
            giveaways[giveaway_range]["blocked"].remove(member.id)
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully unblocked {member} from the giveaway with the ID: **{giveaway_id}**"
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                desc += f"» **Total participants:** {len(giveaways[giveaway_range]['users'])}"
                if giveaways[giveaway_range]["locked"]:
                    desc += "\n:lock: This giveaway has been locked"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass

        else:
            await ctx.channel.send(
                f"{member} wasn\'t even blocked from that giveaway, you may block him via 'g-block {giveaway_id} {member.id}'"
            )

    @commands.command(name="show-giveaway", aliases=["giveaway-info"])
    async def show_giveaway(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        embed_desc = ""
        if not giveaways[giveaway_range]["finished"]:
            duration = display_time(
                seconds=giveaways[giveaway_range]["end_time"] -
                int(time.time()))
            embed_desc += f"This giveaway ends in {duration}\n"
        else:
            embed_desc += "This giveaway has already ended\n"
        embed_desc += f"Total winners: {giveaways[giveaway_range]['winners']}\nPrize: {giveaways[giveaway_range]['prize']}\nHost: <@{giveaways[giveaway_range]['host']}>\nTotal participants: {len(giveaways[giveaway_range]['users'])}\nTotal blocked users: {len(giveaways[giveaway_range]['blocked'])}\nTotal Roles whitelisted: {len(giveaways[giveaway_range]['whitelisted_roles'])}\n"
        if giveaways[giveaway_range]['locked']:
            embed_desc += "Giveaway is locked :lock:"
        else:
            embed_desc += "Giveaway isn\'t locked :unlock:"

        giveaway_embed = guilded.Embed(
            title=f"🎉 Information about Giveaway: {giveaway_id} 🎉",
            color=self.color,
            description=embed_desc)
        giveaway_embed.set_footer(
            icon_url=
            "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
            text="Ends at")

        giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
            giveaways[giveaway_range]['end_time'])
        await ctx.channel.send(embed=giveaway_embed, silent=True)

    @commands.command(name="g-lock", aliases=["glock"])
    async def lock(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if not giveaways[giveaway_range]["locked"]:
            giveaways[giveaway_range]["locked"] = True
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully locked the giveaway with the ID: **{giveaway_id}**"
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                desc += f"» **Total participants:** {len(giveaways[giveaway_range]['users'])}\n:lock: This giveaway has been locked"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass

        else:
            await ctx.channel.send(
                f"This giveaway was already locked, you may unlock it via 'g-unlock {giveaway_id}'"
            )

    @commands.command(name="g-unlock", aliases=["gunlock"])
    async def unlock(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if giveaways[giveaway_range]["locked"]:
            giveaways[giveaway_range]["locked"] = False
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully unlocked the giveaway with the ID: **{giveaway_id}**"
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                desc += f"» **Total participants:** {len(giveaways[giveaway_range]['users'])}"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass

        else:
            await ctx.channel.send(
                f"This giveaway wasn\'t even locked, you may lock it via 'g-lock {giveaway_id}'"
            )

    @commands.command(name="g-whitelist", aliases=["gwhitelist"])
    async def whitelist(self, ctx: commands.Context, giveaway_id, *, target):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        role = await find_role_named(ctx.guild, target)
        if not role:
            await role_not_found(ctx, target)
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if role.id not in giveaways[giveaway_range]["whitelisted_roles"]:
            if not giveaways[giveaway_range]["locked"]:
                giveaways[giveaway_range]["locked"] = True
            giveaways[giveaway_range]["whitelisted_roles"].append(role.id)
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully whitelisted the role {role} for the giveaway with the ID: **{giveaway_id}**"
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                desc += f"» **Total participants:** {len(giveaways[giveaway_range]['users'])}\n:lock: This giveaway has been locked"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass

        else:
            await ctx.channel.send(
                f"{role} was already whitelisted for that giveaway, you may unwhitelist it via 'g-unwhitelist {giveaway_id} {role.id}'"
            )

    @commands.command(name="g-unwhitelist", aliases=["gunwhitelist"])
    async def unwhitelist(self, ctx: commands.Context, giveaway_id, *, target):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        role = await find_role_named(ctx.guild, target)
        if not role:
            await role_not_found(ctx, target)
            return
        if not os.path.exists(f"./giveaways/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        giveaways = json.load(
            open(f"./giveaways/{ctx.message.guild.id}.json", "r"))
        giveaway_found = False
        giveaway_range = None
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                giveaway_range = i
                giveaway_found = True
        if not giveaway_found:
            await ctx.channel.send("Couldn\'t find a giveaway with such an ID")
            return
        if role.id in giveaways[giveaway_range]["whitelisted_roles"]:
            #if not giveaways[giveaway_range]["locked"]:
            #giveaways[giveaway_range]["locked"] = True
            giveaways[giveaway_range]["whitelisted_roles"].remove(role.id)
            if len(giveaways[giveaway_range]["whitelisted_roles"]) == 0:
                giveaways[giveaway_range]["locked"] = False
            clean_json = json.dumps(giveaways,
                                    indent=4,
                                    separators=(",", ": "))
            file = open(f"./giveaways/{ctx.message.guild.id}.json", "w")
            file.write(clean_json)
            file.close()
            await ctx.channel.send(
                f"You have successfully unwhitelisted the role {role} for the giveaway with the ID: **{giveaway_id}**"
            )
            try:
                channel = await self.client.fetch_channel(
                    giveaways[i]["channel_id"])
                desc = giveaways[i]["message_content"]
                desc += f"» **Total participants:** {len(giveaways[giveaway_range]['users'])}"
                if giveaways[giveaway_range]["locked"]:
                    desc += "\n:lock: This giveaway has been locked"
                message = await channel.fetch_message(
                    giveaways[i]["message_id"])
                giveaway_embed = guilded.Embed(title="🎉 {} 🎉".format(
                    giveaways[i]["prize"]),
                                               color=self.color,
                                               description=desc)
                giveaway_embed.set_footer(
                    icon_url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/984846774801948722/katana.png",
                    text="Ends at")

                giveaway_embed.timestamp = datetime.datetime.fromtimestamp(
                    giveaways[i]["end_time"])
                await message.edit(embed=giveaway_embed)
            except Exception as e:
                print(e)
                pass

        else:
            await ctx.channel.send(
                f"{role} wasn\'t even whitelisted, you may whitelist it via 'g-whitelist {giveaway_id} {role.id}'"
            )

    @commands.command(name="greroll",
                      aliases=["g-reroll"],
                      usage="{giveaway_id}")
    async def greroll(self, ctx: commands.Context, giveaway_id):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        #await ctx.message.delete()
        guild_id = ctx.message.guild.id
        found = False
        giveaways = json.load(open(f"./giveaways/{ctx.guild.id}.json", "r"))
        for i in range(len(giveaways)):
            if giveaways[i]["giveaway_id"] == giveaway_id:
                if giveaways[i]["finished"]:
                    return await reroll_giveaway(self, guild_id, i)
                else:
                    return await ctx.send(
                        f"This giveaway hasn\'t ended yet, you may end it via 'gstop **{giveaway_id}**'"
                    )
        return await ctx.send("Couldn\'t find such a giveaway ID'")


def setup(client):
    client.add_cog(Giveaways(client))
