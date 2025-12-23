import guilded, asyncio, random, json, os, datetime, glob
from guilded.ext import commands, tasks
import checksfrfr
from gil_utility.gperms import *


async def GetListOfSubstrings(stringSubject, string1, string2):
    MyList = []
    intstart = 0
    strlength = len(stringSubject)
    continueloop = 1

    while (intstart < strlength and continueloop == 1):
        intindex1 = stringSubject.find(string1, intstart)
        if (intindex1 != -1):  #The substring was found, lets proceed
            intindex1 = intindex1 + len(string1)
            intindex2 = stringSubject.find(string2, intindex1)
            if (intindex2 != -1):
                subsequence = stringSubject[intindex1:intindex2]
                MyList.append(subsequence)
                intstart = intindex2 + len(string2)
            else:
                continueloop = 0
        else:
            continueloop = 0
    return MyList


class Snipe(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.sniped_edits = {}
        self.client.sniped_messages = {}
        client.sniped_images = {}
        self.clear_snipes.start()

    def cog_unload(self):
        self.clear_snipes.cancel()

    @tasks.loop(seconds=60*60*2)
    async def clear_snipes(self):
      print("clearing snipes")
      path = './snipe/'
      for filename in  glob.glob(os.path.join(path, '*.json')):
        os.remove(filename)
      print("done")
            
      

    async def missing_perms(self, ctx):
        color = guilded.Color.from_rgb(239, 83, 80)
        embed = guilded.Embed(
            description=
            f"🔒 Only moderators can snipe messages from another moderator.",
            color=color)
        embed.set_author(name=ctx.author,
                         icon_url=avatar_handler(ctx.author))
        await ctx.channel.send(embed=embed)
        return

    def devperms(self, user: guilded.User):
        if user.id in self.client.devids:
            return True
        return False

    def guild_owner(self, user, guild):
        if user.id == guild.owner_id:
            return True
        if self.devperms(user):
            return True
        return False

    def administrator(self, user, guild):
        for role in user.roles:
            if role.permissions.administrator:
                return True

    def admin_owner_check(self, user, guild):
        if self.guild_owner(user, guild):
            return True
        if self.administrator(user, guild):
            return True
        return False

    def manage_messages(self, user, guild):
        if self.admin_owner_check(user, guild):
            return True
        for role in user.roles:
            if role.permissions.manage_messages:
                return True

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
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)
        return

    def overwrite_json(self, content, guild_id):
        self.json_db = open(f"snipe/{guild_id}.json", "w")
        self.clean_json = json.dumps(content, indent=4, separators=(",", ": "))
        self.json_db.write(self.clean_json)
        self.json_db.close()

    def create_guild_json(self, guild_id):
        creating_file = open(f"snipe/{guild_id}.json", "w")
        # adding default json config into the file if creating new
        # all the users will get created automatically in the function self.find_index_in_db()
        # but for the different jobs etc the program needs configs for variables and symbols
        creating_file.write("""{\n\t
            "users": [],
            "delete_history": [],
            "edit_history": []
        \n}""")
        creating_file.close()

    def find_index_in_db(self,
                         data_to_search,
                         user_to_find,
                         delete_or_edit,
                         fail_safe=False):
        #print(data_to_search)
        user_to_find = str(user_to_find)
        for i in range(len(data_to_search)):
            if data_to_search[i]["user_id"] == user_to_find:
                return int(i), "none"
        delete, edit = [], []
        if fail_safe:
            return 0, "error"
        data_to_search.append({
            "user_id": str(user_to_find),
            "delete_history": [],
            "edit_history": []
        })

        for i in range(len(data_to_search)):
            if data_to_search[i]["user_id"] == user_to_find:
                return i, data_to_search

    def snipe_json_handler(self, guild_id, author_id, delete_or_edit,
                           snipe_json):
        if not os.path.exists(f"snipe/{guild_id}.json"):
            self.create_guild_json(guild_id=guild_id)
        with open(f"snipe/{guild_id}.json", "r") as json_file:
            try:
                json_content = json.load(json_file)
            except:
                return os.remove(f"snipe/{guild_id}.json")
        edits = json_content["edit_history"]
        deletes = json_content["delete_history"]
        user_index, new_data = self.find_index_in_db(json_content["users"],
                                                     author_id, delete_or_edit)

        if new_data != "none":
            json_content["users"] = new_data

        json_user_content = json_content["users"][user_index]
        if delete_or_edit == "edit":
            if len(json_user_content["edit_history"]) == 3:
                json_user_content["edit_history"].pop(2)
            json_user_content["edit_history"].insert(0, snipe_json)
            if len(edits) == 5:
                edits.pop(4)
            edits.insert(0, snipe_json)
            json_content["edit_history"] = edits
        if delete_or_edit == "delete":
            if len(json_user_content["delete_history"]) == 3:
                json_user_content["delete_history"].pop(2)
            json_user_content["delete_history"].insert(0, snipe_json)
            if len(deletes) == 5:
                deletes.pop(4)
            deletes.insert(0, snipe_json)
            json_content["delete_history"] = deletes

        json_content["users"][user_index] = json_user_content
        self.overwrite_json(json_content, guild_id=guild_id)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
      sleep = random.randint(1, 11) /10
      await asyncio.sleep(sleep)
      try:
        if not message.author.bot:
            moderator = self.manage_messages(message.author, message.guild)
            all_files = []
            url = f"https://guilded.gg/teams/{message.guild.id}/channels/{message.channel.id}/chat?messageId={message.id}"
            if message.attachments:
                print("files found")
                for attachment in message.attachments:
                    all_files.append(attachment.proxy_url)
                    self.client.sniped_messages[message.guild.id] = (
                        all_files, message.content, message.author,
                        message.channel, message.created_at, url)
            else:
                self.client.sniped_messages[message.guild.id] = (
                    all_files, message.content, message.author,
                    message.channel, message.created_at, url)
            snipe_json = {
                "all_files":
                all_files,
                "content":
                str(message.content),
                "author":
                str(message.author.name),
                "av":
                str(avatar_handler(message.author)).replace(
                    "https://img.guildedcdn.com",
                    "https://s3-us-west-2.amazonaws.com/www.guilded.gg"),
                "channel":
                str(message.channel.name),
                "created":
                str(message.created_at),
                "url":
                str(url),
                "moderator":
                moderator
            }
            self.snipe_json_handler(message.guild.id, message.author.id,
                                    "delete", snipe_json)
      except:
        pass

    @commands.command()
    async def snipe(self, ctx, history=1):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        moderator = self.manage_messages(ctx.author, ctx.guild)
        if history < 1: return await ctx.channel.send("Only positive values!")
        else:
            guild_id = ctx.guild.id
            if not os.path.exists(f"snipe/{guild_id}.json"):
                self.create_guild_json(guild_id=guild_id)
            try:
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            except:
                os.remove(f"snipe/{guild_id}.json")
                self.create_guild_json(guild_id=guild_id)
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            deletes = json_content["delete_history"]
            if len(deletes) == 0:
                return await ctx.channel.send("There's nothing to snipe!")
            else:
                try:
                    snipe_content = deletes[history - 1]
                except:
                    return await ctx.channel.send("There's nothing to snipe!")
                if snipe_content["moderator"] is True:
                    if not moderator:
                        return await self.missing_perms(ctx)
                contents = snipe_content["content"]
                message = snipe_content["content"]
                channel = snipe_content["channel"]
                url = snipe_content["url"]
                author = snipe_content["author"]
                av = snipe_content["av"]
                time = snipe_content["created"]
                List = await GetListOfSubstrings(contents, "![](", ")")
                index = 0
                full_list = ""
                for x in range(0, len(List)):
                    index += 1
                    full_list += f"[File {index}]({List[x]})\n"
                    message = message.replace(f"![]({List[x]})\n", "")
                    message = message.replace(f"![]({List[x]})", "")
                    print(List[x])
            #for file in all_files:
            #index += 1
            #full_list += f"[File {index}({file})"
                embed = guilded.Embed(description=message,
                                      color=guilded.Color.blue(),
                                      timestamp=datetime.datetime.strptime(
                                          time, '%Y-%m-%d %H:%M:%S.%f'))
                embed.add_field(name="Channel", value=f"[`#{channel}`]({url})")

                if index != 0:
                    embed.add_field(name="Files", value=full_list)
                embed.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/993941829315735653/Design_ohne_Titel_2-fococlipping-standard.png"
                )

                embed.set_author(name=f"{author}", icon_url=av)

                #embed.set_footer()

                await ctx.channel.send(embed=embed, silent=True)

    #@commands.command(name="media-snipe", aliases=["msnipe", "mediasnipe"])
    async def mediasnipe(self, ctx):
        try:
            all_files, contents, author, channel, time, url = self.client.sniped_messages[
                ctx.guild.id]

        except:
            await ctx.channel.send("There's nothing to snipe!")
            return
        List = await GetListOfSubstrings(contents, "![](", ")")
        index = 0
        full_list = ""
        for x in range(0, len(List)):
            index += 1
            full_list += f"[File {index}]({List[x]})\n"
            print(List[x])
        for file in all_files:
            index += 1
            full_list += f"[File {index}({file})"

        if index == 0:
            await ctx.channel.send("There's nothing to snipe!")
            return

        embed = guilded.Embed(description=full_list,
                              color=guilded.Color.blue(),
                              timestamp=time)
        embed.set_author(name=f"{author}",
                         icon_url=avatar_handler(author))
        embed.add_field(name="Channel", value=f"[`#{channel}`]({url})")
        embed.set_image(
            url=
            "https://cdn.discordapp.com/attachments/981904880514007121/993941829315735653/Design_ohne_Titel_2-fococlipping-standard.png"
        )
        #embed.set_footer()

        await ctx.channel.send(embed=embed)

    #@commands.command()
    async def imagesnipe(self, ctx):
        try:
            bob_proxy_url, contents, author, channel, time = self.client.sniped_messages[
                ctx.guild.id]
        except:
            ctx.send("There's nothing to snipe!")
        try:
            embed = guilded.Embed(description=contents,
                                  color=guilded.Color.blue(),
                                  timestamp=time)
            embed.set_image(url=bob_proxy_url)
            embed.add_field(name="Channel", value=f"`#{channel}`"),
            embed.set_author(name=f"{author.name}",
                             icon_url=avatar_handler(author))
            #embed.set_footer()
            await ctx.channel.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.channel.send("There's nothing to snipe!")
            # embed = guilded.Embed(description=contents , color=guilded.Color.purple(), timestamp=time)
            # embed.set_author(name=f"{author.name}#{author.discriminator}", icon_url=avatar_handler(author))
            # embed.set_image(url=bob_proxy_url)
            # embed.add_field(name="Tatort", value=f"<#{channel}>")
            # embed.set_footer(text='made by karma.meme#8811',
            # icon_url=
            # 'https://images-ext-1.guildedapp.net/external/hJ5Q6Win_W60oWk0dLy4W3tNlucrx9bgWTQhadGrugM/%3Fsize%3D1024/https/cdn.guildedapp.com/avatars/784122369416364082/a_b562e0c0d3be255f4365a1ef74e17703.gif')
            # await ctx.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
      sleep = random.randint(1, 11)
      await asyncio.sleep(sleep)
      try:
        if not message_before.author.bot:
            moderator = self.manage_messages(message_after.author,
                                             message_after.guild)
            url = url = f"https://guilded.gg/teams/{message_after.guild.id}/channels/{message_after.channel.id}/chat?messageId={message_after.id}"
            self.client.sniped_edits[message_before.guild.id] = (
                message_before.content, message_before.author,
                message_after.content, message_before.channel,
                message_before.created_at, url)
            snipe_json = {
                "before_content":
                str(message_before.content),
                "after_content":
                str(message_after.content),
                "author":
                str(message_before.author.name),
                "av":
                str(avatar_handler(message_before.author)).replace(
                    "https://img.guildedcdn.com",
                    "https://s3-us-west-2.amazonaws.com/www.guilded.gg"),
                "channel":
                str(message_before.channel.name),
                "created":
                str(message_before.created_at),
                "url":
                str(url),
                "moderator":
                moderator
            }
            self.snipe_json_handler(message_before.guild.id,
                                    message_before.author.id, "edit",
                                    snipe_json)
      except:
        pass

    @commands.command(name="editsnipe",
                      aliases=["edit-snipe", "esnipe", "e-snipe"])
    async def editsnipe(self, ctx, history=1):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        moderator = self.manage_messages(ctx.author, ctx.guild)
        if history < 1: return await ctx.channel.send("Only positive values!")
        else:
            guild_id = ctx.guild.id
            if not os.path.exists(f"snipe/{guild_id}.json"):
                self.create_guild_json(guild_id=guild_id)
            try:
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            except:
                os.remove(f"snipe/{guild_id}.json")
                self.create_guild_json(guild_id=guild_id)
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            edits = json_content["edit_history"]
            if len(edits) == 0:
                return await ctx.channel.send("There's nothing to snipe!")
            else:
                try:
                    snipe_content = edits[history - 1]
                except:
                    return await ctx.channel.send("There's nothing to snipe!")
                if snipe_content["moderator"] is True:
                    if not moderator:
                        return await self.missing_perms(ctx)
                content = snipe_content["before_content"]
                after_content = snipe_content["after_content"]
                channel = snipe_content["channel"]
                url = snipe_content["url"]
                author = snipe_content["author"]
                av = snipe_content["av"]
                time = snipe_content["created"]

                embed = guilded.Embed(color=guilded.Color.blue(),
                                      timestamp=datetime.datetime.strptime(
                                          time, '%Y-%m-%d %H:%M:%S.%f'))
                embed.set_author(name=f"{author}", icon_url=av)
                embed.add_field(name="Before", value=content, inline=True)
                embed.add_field(name="After", value=after_content)
                embed.add_field(name="Channel", value=f"[`#{channel}`]({url})")
                embed.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/993941829315735653/Design_ohne_Titel_2-fococlipping-standard.png"
                )
                #embed.set_footer()
                try:
                    await ctx.channel.send(embed=embed, silent=True)
                except Exception as e:
                    print(e)
                    await ctx.channel.send("There's nothing to snipe!")

    @commands.command(name="user-snipe",
                      aliases=["u-snipe", "usnipe", "usersnipe"])
    async def usnipe(self, ctx, history=1, *, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if user is None:
            return await ctx.channel.send(
                "Please provide a target User\nExample: .usnipe 1 @hoemotion")
        member = self.find_member_named(ctx.server, user, ctx)
        moderator = self.manage_messages(ctx.author, ctx.guild)
        if member is None:
            return await self.user_not_found(ctx, user)
        if history < 1: return await ctx.channel.send("Only positive values!")
        else:
            guild_id = ctx.guild.id
            if not os.path.exists(f"snipe/{guild_id}.json"):
                self.create_guild_json(guild_id=guild_id)
            try:
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            except:
                os.remove(f"snipe/{guild_id}.json")
                self.create_guild_json(guild_id=guild_id)
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            user_index, new_data = self.find_index_in_db(
                json_content["users"], member.id, "delete")

            if new_data != "none":
                json_content["users"] = new_data
            json_user_content = json_content["users"][user_index]
            deletes = json_user_content["delete_history"]
            if len(deletes) == 0:
                return await ctx.channel.send("There's nothing to snipe!")
            else:
                try:
                    snipe_content = deletes[history - 1]
                except:
                    return await ctx.channel.send("There's nothing to snipe!")
                if snipe_content["moderator"] is True:
                    if not moderator:
                        return await self.missing_perms(ctx)
                contents = snipe_content["content"]
                message = snipe_content["content"]
                channel = snipe_content["channel"]
                url = snipe_content["url"]
                author = snipe_content["author"]
                av = snipe_content["av"]
                time = snipe_content["created"]
                List = await GetListOfSubstrings(contents, "![](", ")")
                index = 0
                full_list = ""
                for x in range(0, len(List)):
                    index += 1
                    full_list += f"[File {index}]({List[x]})\n"
                    message = message.replace(f"![]({List[x]})\n", "")
                    message = message.replace(f"![]({List[x]})", "")
                    print(List[x])
            #for file in all_files:
            #index += 1
            #full_list += f"[File {index}({file})"
                embed = guilded.Embed(description=message,
                                      color=guilded.Color.blue(),
                                      timestamp=datetime.datetime.strptime(
                                          time, '%Y-%m-%d %H:%M:%S.%f'))
                embed.add_field(name="Channel", value=f"[`#{channel}`]({url})")

                if index != 0:
                    embed.add_field(name="Files", value=full_list)
                embed.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/993941829315735653/Design_ohne_Titel_2-fococlipping-standard.png"
                )

                embed.set_author(name=f"{author}", icon_url=av)

                #embed.set_footer()

                await ctx.channel.send(embed=embed,silent=True)

    @commands.command(name="usereditsnipe",
                      aliases=["user-edit-snipe", "uesnipe", "ue-snipe"])
    async def usereditsnipe(self, ctx, history=1, *, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if user is None:
            return await ctx.channel.send(
                "Please provide a target User\nExample: .uesnipe 1 @hoemotion")
        moderator = self.manage_messages(ctx.author, ctx.guild)
        member = self.find_member_named(ctx.server, user, ctx)
        if member is None:
            return await self.user_not_found(ctx, user)
        if history < 1: return await ctx.channel.send("Only positive values!")
        else:
            guild_id = ctx.guild.id
            if not os.path.exists(f"snipe/{guild_id}.json"):
                self.create_guild_json(guild_id=guild_id)
            try:
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            except:
                os.remove(f"snipe/{guild_id}.json")
                self.create_guild_json(guild_id=guild_id)
                with open(f"snipe/{guild_id}.json", "r") as json_file:
                    json_content = json.load(json_file)
            user_index, new_data = self.find_index_in_db(
                json_content["users"], member.id, "edit")

            if new_data != "none":
                json_content["users"] = new_data
            json_user_content = json_content["users"][user_index]
            edits = json_user_content["edit_history"]
            if len(edits) == 0:
                return await ctx.channel.send("There's nothing to snipe!")
            else:
                try:
                    snipe_content = edits[history - 1]
                except:
                    return await ctx.channel.send("There's nothing to snipe!")
                if snipe_content["moderator"] is True:
                    if not moderator:
                        return await self.missing_perms(ctx)
                content = snipe_content["before_content"]
                after_content = snipe_content["after_content"]
                channel = snipe_content["channel"]
                url = snipe_content["url"]
                author = snipe_content["author"]
                av = snipe_content["av"]
                time = snipe_content["created"]

                embed = guilded.Embed(color=guilded.Color.blue(),
                                      timestamp=datetime.datetime.strptime(
                                          time, '%Y-%m-%d %H:%M:%S.%f'))
                embed.set_author(name=f"{author}", icon_url=av)
                embed.add_field(name="Before", value=content, inline=True)
                embed.add_field(name="After", value=after_content)
                embed.add_field(name="Channel", value=f"[`#{channel}`]({url})")
                embed.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/981904880514007121/993941829315735653/Design_ohne_Titel_2-fococlipping-standard.png"
                )
                #embed.set_footer()
                try:
                    await ctx.channel.send(embed=embed, silent=True)
                except Exception as e:
                    print(e)
                    await ctx.channel.send("There's nothing to snipe!")

    @commands.command(name="clean-snipe-json")
    async def clean_snipe_json(self, ctx):
        if ctx.author.id != "dzOn13bm":
            return
        path = './snipe/'
        for filename in glob.glob(os.path.join(path, '*.json')):
            f = open(os.path.join(os.getcwd(), filename), 'r')
            try:
                json.load(f)
                f.close()
            except:
                f.close()
                os.remove(os.path.join(os.getcwd(), filename))


def setup(client):
    client.add_cog(Snipe(client))
