import guilded, os, json
import asyncio
from guilded.ext import commands
import time
import checksfrfr
from gil_utility.gperms import *

intervals = (
    ('years', 86400 * 30 * 12),
    ('months', 86400 * 30),
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1))


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(str(int(value)), name))
    string_final = ""
    for i in result:
        string_final += f"{i}, "
    return string_final[:-2]


class Afk(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.nick_cache = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message is None:
            return
        if message.author is None:
            return
        if message.author.bot:
            return
        if not os.path.exists(f"Database/Afk/{message.guild.id}.json"):
            return
        else:
          try:
            with open(f"Database/Afk/{message.guild.id}.json", "r") as json_file:
                json_content = json.load(json_file)
            afk = False
            order = 0
            c = -1
            for i in range(len(json_content)):
                c += 1
                if json_content[i]["_id"] == message.author.id:
                    afk, order = True, c
            if afk:
                await message.reply(embed=guilded.Embed(
                    description=
                    f"Welcome back **{message.author.name}!** I have removed your AFK status!",
                    color=guilded.Color.dark_theme_embed()))
                json_content.pop(i)
                json_f = open(f"Database/Afk/{message.guild.id}.json", "w")
                json_f.write(json.dumps(json_content))
                json_f.close()

                # await db.AFK.delete_one({"_id": f"{message.author.id}{message.guild.id}"})
                jsn = await self.client.http.get_member(
                    message.server.id, message.author.id)
                info = jsn
                if not (info["member"].get('nickname') is None):
                    if str(f"[AFK] {message.author.name}"
                           ) == info["member"]["nickname"]:
                        try:
                            await message.author.edit(
                                nick=None  #f"{message.author.name}"
                            )
                        except Exception as e:
                            print(e)
                            pass
                    else:
                        if "[AFK] " in info["member"]["nickname"]:
                            try:
                                await message.author.edit(
                                    nick=info["member"]["nickname"].replace(
                                        "[AFK] ", ""))
                            except Exception as e:
                                print(e)
                                pass
                return
            with open(f"Database/Afk/{message.guild.id}.json", "r") as json_file:
                json_content = json.load(json_file)
            if len(message.raw_mentions) == 0 and len(message.replied_to) == 0:
                json_file.close()
                return
            else:
                replied_users = []

                for s in range(len(message.raw_mentions)):
                    id = message.raw_mentions[s]
                    if id not in replied_users:
                        for a in range(len(json_content)):
                            if json_content[a]["_id"] == id:
                                if id not in replied_users:
                                    await message.reply(embed=guilded.Embed(
                                        description=
                                        f"<@{id}> is AFK - {json_content[a]['message']} - {display_time(time.time() - json_content[a]['start'])} ago",
                                        color=guilded.Colour.blue()),
                                                        silent=True)
                                    replied_users.append(id)
                print(message.replied_to)
                for e in range(len(message.replied_to)):
                    msg = message.replied_to[e]
                    if not msg:
                        continue
                    if msg.author.id not in replied_users:
                        for v in range(len(json_content)):
                            print(json_content[v]["_id"] + " " + msg.author.id)
                            if json_content[v]["_id"] == msg.author.id:
                                if msg.author.id not in replied_users:
                                    await message.reply(embed=guilded.Embed(
                                        description=
                                        f"<@{msg.author.id}> is AFK - {json_content[v]['message']} - {display_time(time.time() - json_content[v]['start'])} ago",
                                        color=guilded.Colour.blue()),
                                                        silent=True)
                                    replied_users.append(msg.author.id)
          except Exception as e:
            print(e)

    @commands.command(name="afk")
    async def afk(self, ctx, *, message: str = "AFK"):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if (self.nick_cache.get(ctx.server.id) is None):
            self.nick_cache[ctx.server.id] = {}
        if (self.nick_cache[ctx.guild.id].get(ctx.author.id) is None):

            jsn = await self.client.http.get_member(ctx.server.id,
                                                    ctx.author.id)
            info = jsn
            if not (info["member"].get('nickname') is None):
                nick = info["member"]["nickname"]
                self.nick_cache[ctx.server.id][ctx.author.id] = {
                    "nick": nick,
                    "time": time.time()
                }
            else:
                self.nick_cache[ctx.server.id][ctx.author.id] = {
                    "nick": None,
                    "time": time.time()
                }
                nick = None
        else:
            if time.time() - self.nick_cache[ctx.server.id][
                    ctx.author.id]["time"] > 30:  # 3 * 60:
                jsn = await self.client.http.get_member(
                    ctx.server.id, ctx.author.id)
                info = jsn
                if not (info["member"].get('nickname') is None):
                    nick = info["member"]["nickname"]
                    self.nick_cache[ctx.server.id][ctx.author.id] = {
                        "nick": nick,
                        "time": time.time()
                    }
                else:
                    self.nick_cache[ctx.server.id][ctx.author.id] = {
                        "nick": None,
                        "time": time.time()
                    }
            nick = self.nick_cache[ctx.server.id][ctx.author.id]["nick"]
        if not os.path.exists(f"Database/Afk/{ctx.guild.id}.json"):
            #u = await db.AFK.find_one(
            #    {"_id": ctx.author.id}
            #)
            creating_file = open(f'Database/Afk/{ctx.guild.id}.json', "w")
            data = []
            creating_file.write(json.dumps(data))
            creating_file.close()
        json_file = open(f'Database/Afk/{ctx.guild.id}.json', "r")
        json_content = json.load(json_file)
        json_file.close()
        afk = False
        for i in range(len(json_content)):
            if json_content[i]["_id"] == ctx.message.author.id:
                afk, order = True, i
        if not afk:
            try:
                if nick is None:
                    await ctx.author.edit(nick=f"[AFK] {ctx.author.name}")
                else:
                    await ctx.author.edit(nick=f"[AFK] {nick}")
            except Exception as e:
                print(e)
                pass
            await ctx.reply(embed=guilded.Embed(
                description=f"Set your AFK status - **{message}**",
                color=guilded.Color.dark_theme_embed()))
            await asyncio.sleep(3)
            data = {
                "_id": f"{ctx.author.id}",
                "message": message,
                "start": time.time()
            }
            try:
                json_content.append(data)
                json_db = open(f'Database/Afk/{ctx.guild.id}.json', "w")
                json_db.write(json.dumps(json_content))
                json_db.close()
            except:
                pass


def setup(bot):
    bot.add_cog(Afk(bot))
