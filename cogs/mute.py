import json
import time, os
import glob, re
import checksfrfr
from gil_utility.gperms import *

from guilded.ext import commands, tasks
from guilded.ext.commands.converters import (_INT_ID_REGEX, )

intervals = (
    ('years', 86400 * 30 * 12),
    ('months', 86400 * 30),
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


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


def create_guild_json(guild_id):
    creating_file = open(f"./mutes/{guild_id}.json", "w")
    creating_file.write("""{"mute_role": null, "mutes": []}""")
    creating_file.close()


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
            seconds += timeValue

    until = int(seconds)
    return (until)


async def stop_mute(self, g_id, user_id):
    #for guild in self.client.guilds:
    #  if guild.id == g_id:
    #    for ch in guild.channels:
    #      if ch.id == data["channel_id"]:
    #        channel = ch
    #print(f"Channel-ID: {data['channel_id']}")
    guild = self.client.get_server(g_id)
    if not guild:
        return
    await guild.fill_members()
    muted_users = json.load(open(f"./mutes/{g_id}.json", "r"))
    #giveaway_message = await channel.fetch_message(g_id)
    #users = await giveaway_message.reactions[0].users().flatten()
    if type(muted_users) == list:
        mute_role = None
    else:
        mute_role = muted_users['mute_role']
        muted_users = muted_users['mutes']
    users = muted_users  #[i]["users"]
    position = 0
    user_found = False
    for i in range(len(users)):
        if users[i]["user_id"] == user_id:
            position = i
            user_found = True
    if not user_found: return
    member = guilded.utils.find(lambda m: m.id == users[position]["user_id"],
                                guild.members)
    #print(member)
    if not member:
        return
    if not mute_role:
        mute_role = guilded.utils.find(lambda m: m.name == "Muted",
                                       guild.roles)
    else:
        mute_role = guilded.utils.find(lambda m: m.id == mute_role,
                                       guild.roles)
    try:
        await member.remove_roles(mute_role)
    except Exception as e:
        print(e)

    muted_users = json.load(open(f"./mutes/{g_id}.json", "r"))
    if type(muted_users) == list:
        mute_role = None
    else:
        mute_role = muted_users['mute_role']
        muted_users = muted_users['mutes']
    #ghost_ping = await channel.send(f"<@{data['host']}>")
    #await ghost_ping.delete()
    muted_users.pop(position)
    muted_users = {'mute_role': mute_role, 'mutes': muted_users}
    clean_json = json.dump(muted_users,
                           open(f"./mutes/{g_id}.json", "w"),
                           indent=4)


class TempMute(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        #self.config = json.load(open("config.json", "r"))
        self.color = int("0xad13eb", 16) + 0x200
        self.mute_task.start()



    def cog_unload(self):
        self.mute_task.cancel()


    @tasks.loop(seconds=5)
    async def mute_task(self):
        await self.client.wait_until_ready()
        path = './mutes/'
        for filename in glob.glob(os.path.join(path, '*.json')):
          try:
            with open(os.path.join(os.getcwd(), filename), 'r') as f:
                mutes = json.load(f)
            if type(mutes) == list:
                mute_role = None
            else:
                mute_role = mutes['mute_role']
                mutes = mutes['mutes']

            if not len(mutes) == 0:
                for i in range(len(mutes)):
                    data = mutes[i]
                    if int(time.time()) > data["end_time"]:
                        await stop_mute(self, filename[8:-5], data["user_id"])
                f.close()
          except Exception as e:
            print(e)
            os.remove(filename)
            
              

    @commands.command(name="mute-role",
                      alises=[])  # reminder to add to help menu
    async def set_mute_role(self, ctx, *, role=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        if role is None:
            await ctx.message.reply("You need to specify a target Role!",
                                    private=True)
        if not os.path.exists(f"./mutes/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        mutes = json.load(open(f"./mutes/{ctx.message.guild.id}.json", "r"))
        if type(mutes) == list:
            mute_role = None
        else:
            mute_role = mutes['mute_role']
            mutes = mutes['mutes']
        if mute_role:
            mute_role = guilded.utils.find(lambda m: m.id == mute_role,
                                           ctx.guild.roles)
        if mute_role:
            return await ctx.reply(
                "This Server already has a Mute-Role set! If you wish to change it still, delete it first with .del-mute-role!",
                private=True)
        mute_role =  await find_role_named(ctx.guild, role)
        if not mute_role:
            embed = guilded.Embed(
                title="Invalid Mute-Role was passed",
                description=
                "Seems like you entered a invalid Role!\nDoes the Role exist? Try .recache!",
                color=guilded.Color.from_rgb(239, 83, 80))
            await ctx.channel.send(embed=embed)
            return
        role = mute_role.id
        mutes = {"mute_role": role, "mutes": mutes}
        clean_json = json.dump(mutes,
                               open(f"./mutes/{ctx.message.guild.id}.json",
                                    "w"),
                               indent=4,
                               separators=(",", ": "))
        embed = guilded.Embed(
            title="Mute-Role Set",
            description=
            f"{mute_role.mention} has been set as the Server's Mute-Role!")
        await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name="del-mute-role",
                      alises=[])  # reminder to add to help menu
    async def del_mute_role(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        if not os.path.exists(f"./mutes/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        mutes = json.load(open(f"./mutes/{ctx.message.guild.id}.json", "r"))
        if type(mutes) == list:
            mute_role = None
        else:
            mute_role = mutes['mute_role']
            mutes = mutes['mutes']
        if mute_role:
            mute_role = guilded.utils.find(lambda m: m.id == mute_role,
                                           ctx.guild.roles)
        if not mute_role:
            return await ctx.reply(
                "This Server doesn't have a Mute-Role set! If you wish to set it, use the .mute-role command!",
                private=True)

        role = None
        mutes = {"mute_role": role, "mutes": mutes}
        clean_json = json.dump(mutes,
                               open(f"./mutes/{ctx.message.guild.id}.json",
                                    "w"),
                               indent=4,
                               separators=(",", ": "))
        embed = guilded.Embed(
            title="Mute-Role Removed",
            description=
            f"{mute_role.mention} has been removed as the Server's Mute-Role! Temp-Mutes will no longer remove this role even when they end."
        )
        await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name="tempmute", aliases=["temp-mute"])
    async def temp_mute(self, ctx, duration, *, target=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if target is None:
            await ctx.message.reply("You need to specify a target User!",
                                    private=True)
            return
        if not (await ban_users(ctx)):
            return
        converted_time = convert(duration)
        await ctx.guild.fill_members()
        user = await find_member_named(ctx.guild, target, ctx)
        if not user:
            await user_not_found(ctx, target)
            return
        if ctx.author.id == user.id:
            await ctx.channel.send("You cannot mute yourself!")
            return
        if self.client.user.id == user.id:
            await ctx.channel.send("You cannot mute me!")
            return
        bot_user = await find_member_named(ctx.guild, self.client.user.id, ctx)
        if not await is_higher(ctx, user, bot_user):
            return
        if not os.path.exists(f"./mutes/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        mutes = json.load(open(f"./mutes/{ctx.message.guild.id}.json", "r"))
        if type(mutes) == list:
            mute_role = None
        else:
            mute_role = mutes['mute_role']
            mutes = mutes['mutes']
        if mute_role:
            mute_role = guilded.utils.find(lambda m: m.id == mute_role,
                                           ctx.guild.roles)
        if not mute_role:
            embed = guilded.Embed(
                title="No Mute-Role was found",
                description=
                "Seems like this Server doesn\'t have a Mute-Role! Configure your Server\'s Mute-Role first with .mute-role and then try muting members!\nRole exists and is already set? Try .recache!",
                color=guilded.Color.from_rgb(239, 83, 80))
            await ctx.channel.send(embed=embed)
            return
        try:
            await user.add_roles(mute_role)
        except Exception as e:
            embed = guilded.Embed(title="An error has occured",
                                  description=f"**Exception:**\n`{e}`",
                                  color=guilded.Color.from_rgb(239, 83, 80))
            await ctx.channel.send(embed=embed)
            return
        duration = display_time(converted_time)
        embed = guilded.Embed(
            title="Temp-Mute",
            description=f"{user.mention} has been muted for {duration}")
        await ctx.channel.send(embed=embed, silent=True)
        now = int(time.time())
        for i in range(len(mutes)):
            if mutes[i]["user_id"] == user.id:
                mutes.pop(i)
        data = {"end_time": now + converted_time, "user_id": user.id}
        mutes.append(data)
        mutes = {"mute_role": mute_role.id, "mutes": mutes}
        clean_json = json.dump(mutes,
                               open(f"./mutes/{ctx.message.guild.id}.json",
                                    "w"),
                               indent=4,
                               separators=(",", ": "))

    @commands.command(name="mute", aliases=[])
    async def mute(self, ctx, *, target=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await ban_users(ctx)):
            return
        if target is None:
            await ctx.message.reply("You need to specify a target User!",
                                    private=True)
            return
        await ctx.guild.fill_members()
        user = await find_member_named(ctx.guild, target, ctx)
        if not user:
            await user_not_found(ctx, target)
            return
        if ctx.author.id == user.id:
            await ctx.channel.send("You cannot mute yourself!")
            return
        if self.client.user.id == user.id:
            await ctx.channel.send("You cannot mute me!")
            return
        bot_user = await find_member_named(ctx.guild, self.client.user.id, ctx)
        if not await is_higher(ctx, user, bot_user):
            return
        if not os.path.exists(f"./mutes/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        mutes = json.load(open(f"./mutes/{ctx.message.guild.id}.json", "r"))
        if type(mutes) == list:
            mute_role = None
        else:
            mute_role = mutes['mute_role']
            mutes = mutes['mutes']
        if mute_role:
            mute_role = guilded.utils.find(lambda m: m.id == mute_role,
                                           ctx.guild.roles)
        if not mute_role:
            embed = guilded.Embed(
                title="No Mute-Role was found",
                description=
                "Seems like this Server doesn\'t have a Mute-Role! Configure your Server\'s Mute-Role first with .mute-role and then try muting members!\nRole exists and is already set? Try .recache!",
                color=guilded.Color.from_rgb(239, 83, 80))
            await ctx.channel.send(embed=embed)
            return
        try:
            await user.add_roles(mute_role)
        except Exception as e:
            embed = guilded.Embed(title="An error has occured",
                                  description=f"**Exception:**\n`{e}`",
                                  color=guilded.Color.from_rgb(239, 83, 80))
            await ctx.channel.send(embed=embed)
            return
        embed = guilded.Embed(
            title="Mute",
            description=f"{user.mention} has been muted indefinitely!")
        await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name="unmute", aliases=[])
    async def unmute(self, ctx, *, target=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if target is None:
            await ctx.message.reply("You need to specify a target User!",
                                    private=True)
            return
        if not (await ban_users(ctx)):
            return
        await ctx.guild.fill_members()
        user = await find_member_named(ctx.guild, target, ctx)
        if not user:
            await user_not_found(ctx, target)
            return
            return
        if not os.path.exists(f"./mutes/{ctx.message.guild.id}.json"):
            create_guild_json(guild_id=ctx.message.guild.id)
        mutes = json.load(open(f"./mutes/{ctx.message.guild.id}.json", "r"))
        if type(mutes) == list:
            mute_role = None
        else:
            mute_role = mutes['mute_role']
            mutes = mutes['mutes']
        if mute_role:
            mute_role = guilded.utils.find(lambda m: m.id == mute_role,
                                           ctx.guild.roles)
        if not mute_role:
            embed = guilded.Embed(
                title="No Mute-Role was found",
                description=
                "Seems like this Server doesn\'t have a Mute-Role! Configure your Server\'s Mute-Role first with .mute-role and then try muting members!\nRole exists and is already set? Try .recache!",
                color=guilded.Color.from_rgb(239, 83, 80))
            await ctx.channel.send(embed=embed)
            return
        try:
            rids = await user.fetch_role_ids()
            if mute_role.id in rids:
                await user.remove_roles(mute_role)
            else:
                embed = guilded.Embed(
                    title="User not muted!",
                    description="Seems like this User isn\'t muted!",
                    color=guilded.Color.from_rgb(239, 83, 80))
                await ctx.channel.send(embed=embed)
                return
        except Exception as e:
            embed = guilded.Embed(title="An error has occured",
                                  description=f"**Exception:**\n`{e}`",
                                  color=guilded.Color.from_rgb(239, 83, 80))
            await ctx.channel.send(embed=embed)
            return
        embed = guilded.Embed(title="Unmute",
                              description=f"{user.mention} has been unmuted!")
        await ctx.channel.send(embed=embed, silent=True)


def setup(client):
    client.add_cog(TempMute(client))
