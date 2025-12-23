import time
from datetime import datetime
import checksfrfr
#import chat_exporter
from aiohttp import ClientSession
from gil_utility.gperms import *

tz_info = 'Europe/Berlin'
purge_cooldown = {}

nukes = [
    "https://cdn.discordapp.net/attachments/981904880514007121/983153821909925918/911.gif",
    "https://cdn.discordapp.com/attachments/858341599972818944/858342025765847090/boom.gif",
    "https://cdn.discordapp.net/attachments/981904880514007121/983155402097192980/ataturk-dertli.gif",
    "https://cdn.discordapp.net/attachments/981904880514007121/983155875801862184/q-we.gif"
]


# You can change 'Moderation' to anything.
class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.banner_cache = {}

    def find_role_named(self, team, argument: str):
        try:
            argument = argument.replace("@", "")
        except:
            pass
        # Guilded doesn't really have a query-members-through-gateway ability,
        # so instead we just search the internal cache.
        return guilded.utils.find(
            lambda m: m.name == argument or str(m.id) == argument, team.roles)

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


    def ban_users_bot(self, bot):
        for role in bot.roles:
            if role.permissions.ban_members:
                return True
        return False

    async def user_not_found(self, ctx, member):
        color = guilded.Color.from_rgb(239, 83, 80)
        embed = guilded.Embed(
            description=
            f"Couldn\'t find a member with the name/id {member}\nTry putting in the user ID, if the mention doesn\'t work.",
            color=color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)
        return

    @commands.command()
    #@commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member=None, *, reason=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await ban_users(ctx)):
            return
        if member is None:
            await ctx.message.reply("You need to specify a target User!",
                                    private=True)
            return
        user = await find_member_named(ctx.guild, member, ctx)
        if not user:
            await user_not_found(ctx, member)
            return
        if ctx.author.id == user.id:
            await ctx.channel.send("You cannot kick yourself!")
            return
        if self.client.user.id == user.id:
            await ctx.channel.send("You cannot kick me!")
            return
        bot_user = await find_member_named(ctx.guild, self.client.user.id, ctx)
        if not await is_higher(ctx, user, bot_user):
            return
        #if top_role(ctx, ctx.message.author) > top_role(ctx, user):
        if 1 == 1:
            await user.kick()
            embed = guilded.Embed(
                title="Kick",
                description=
                f'[{user}](https://guilded.gg/profile/{user.id}) has been kicked from the server\nReason: {reason}',
                color=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author,
                             icon_url=ctx.author.avatar)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Your role is too low to do that")

    #@kick.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the perms to kick somebody")

    @commands.command()
    #@commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member=None, *, reason=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await ban_users(ctx)):
            return
        if member is None:
            await ctx.message.reply("You need to specify a target User!",
                                    private=True)
            return
        user = await find_member_named(ctx.guild, member, ctx)
        if not user:
            await user_not_found(ctx, member)
            return
        #if ctx.message.author.top_role > user.top_role:
        if ctx.author.id == user.id:
            await ctx.channel.send("You cannot ban yourself!")
            return
        if self.client.user.id == user.id:
            await ctx.channel.send("You cannot ban me!")
            return
        bot_user = await find_member_named(ctx.guild, self.client.user.id, ctx)
        if not await is_higher(ctx, user, bot_user):
            return
        if 1 == 1:
            await user.ban()  #(reason=reason, delete_message_days=0)
            embed = guilded.Embed(
                title="Ban",
                description=
                f'[{user}](https://guilded.gg/profile/{user.id}) has been banned from the server\nReason: {reason}',
                color=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author,
                             icon_url=ctx.author.avatar)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Your role is too low")

    @commands.command()
    #@commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await ban_users(ctx)):
            return
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user

            if user.name == member or user.id == member:
                await ctx.guild.unban(user)
                embed = guilded.Embed(
                    title="Unban",
                    description=
                    f'[{user}](https://guilded.gg/profile/{user.id}) has been unbanned',
                    color=guilded.Colour.blue())
                embed.set_author(name=ctx.message.author,
                                 icon_url=ctx.author.avatar)
                await ctx.send(embed=embed)
                return
        await user_not_found(ctx, member)

        #if ctx.message.author.top_role > user.top_role:




    @commands.command()
    async def about(self, ctx):
        embed = guilded.Embed(
            Title="About:",
            description=
            f"Hello {ctx.author.mention},\nmy prefix is .\nI am Katana, a WIP multi-purpose bot, which will have a lot of more commands and minigames in future",
            color=guilded.Colour.blue())

        embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar)

        embed.add_field(name="Version:", value="Alpha V. 0.0.3", inline=False)
        embed.add_field(
            name="Invite",
            value=
            "[Invite-Link](https://www.guilded.gg/b/25a00b00-e6ca-4211-b86e-1af0be2cf2a3)"
        )

        embed.add_field(name="Do you need help?",
                        value="[Support-Server](https://guilded.gg/karma)",
                        inline=False)

        embed.add_field(
            name="Creator",
            value=
            "[hoemotion](https://guilded.gg/u/karma) (Same creator of the economy Bot [Cashey](https://www.guilded.gg/b/15139441-f6ee-4b12-9424-4ccb48e8c50d))",
            inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="purge", aliases=["clear"], pass_context=True)
    async def purge(self, ctx, limit: int):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_messages(ctx)):
            return

        try:
            limit = int(limit)
        except ValueError:
            return

        # Initialize the cooldown dictionary for the server if it doesn't exist
        if ctx.server.id not in purge_cooldown:
            purge_cooldown[ctx.server.id] = {"cooldown": 0, "executing": False}

        server_cooldown = purge_cooldown[ctx.server.id]

        if server_cooldown["executing"]:
            return

        if server_cooldown["cooldown"] > 0:
            await ctx.channel.send(f"Command is on cooldown for {server_cooldown['cooldown']} seconds")
            return

        if limit > 75:
            await ctx.channel.send("75 messages is the maximum limit")
            return

        try:
            await ctx.message.delete()
        except guilded.NotFound:
            pass

        server_cooldown["cooldown"], server_cooldown["executing"] = 5, True

        messages = await ctx.channel.history(limit=limit)
        for message in messages:
            try:
                await message.delete()
            except Exception as e:
                print(e)

        embed = guilded.Embed(
            title="Purge",
            description=f'{ctx.author.mention} has purged {limit} messages',
            color=guilded.Colour.blue()
        )
        embed.set_author(name=ctx.author.name, icon_url=avatar_handler(ctx.author))

        server_cooldown["executing"] = False
        await ctx.send(embed=embed, delete_after=5)

        for _ in range(5):
            await asyncio.sleep(1)
            server_cooldown["cooldown"] -= 1

        server_cooldown["cooldown"] = 0

    @commands.command()
    async def ping(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        start_time = time.time()
        first_embed = guilded.Embed(title="Ping! 🏓",
                                    description="Testing the Ping...",
                                    colour=guilded.Colour.green())

        msg = await ctx.reply(embed=first_embed, silent=True)
        second_embed = guilded.Embed(title="Pong! 🏓",
                                     colour=guilded.Colour.green())
        second_embed.set_author(name=f"{ctx.author}",
                                icon_url=ctx.author.avatar),
        second_embed.add_field(name="Bot Latency",
                               value=f"{round (self.client.latency * 1000)}ms",
                               inline=True),
        second_embed.add_field(
            name="API Latency",
            value=f"{round((time.time() - start_time) * 1000)}ms",
            inline=True)
        await msg.edit(embed=second_embed)




    @commands.command()
    async def invite(self, ctx):
        embed = guilded.Embed(
            title=f"Invite me to your Server!",
            url=
            f"https://www.guilded.gg/b/25a00b00-e6ca-4211-b86e-1af0be2cf2a3",
            description=
            f"Hey {ctx.author.mention}, thanks for inviting me to your server",
            color=guilded.Colour.blue())

        embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar)

        embed.add_field(
            name="Invite-Link",
            value=
            f"Just click [here](https://www.guilded.gg/b/25a00b00-e6ca-4211-b86e-1af0be2cf2a3) or at the title of this message",
            inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="server", aliases=["server-info", "serverinfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        name = str(ctx.guild.name)

        owner = f"<@{ctx.guild.owner_id}>"
        id = str(ctx.guild.id)
        #region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)
        bots = []
        for role in ctx.server.roles:
            if role.is_bot_managed():
                bots.append(role.bot_member)
        botCount = len(bots)
        icon = str(ctx.guild.icon)
        roles = str(len(ctx.guild.roles))
        #textchannels = len(ctx.guild.text_channels)
        #voicechannels = len(ctx.guild.voice_channels)
        if self.ban_users_bot(ctx.author):
            try:
                bans = str(len(await ctx.guild.bans()))
            except Exception as e:
                print(e)
                bans = None
        else:
            bans = None

        embed = guilded.Embed(title=name + " Server Information",
                              color=guilded.Colour.blue())
        if icon != "None":
            #print(icon + " is not None")
            embed.set_thumbnail(url=icon)
        embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar)

        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Server ID", value=id, inline=True)
        #embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(name="Member Count", value=memberCount, inline=True)
        embed.add_field(name="Bot Count", value=botCount, inline=True)
        embed.add_field(name="Role Count", value=roles, inline=True)
        created = ctx.guild.created_at.__format__('%A, %d. %B %Y at %H:%M:%S')
        embed.add_field(name='Created At', value=f"`{created}`", inline=False)
        #embed.add_field(name="Channels",
        #value=f"Text:{textchannels} Voice:{voicechannels}")
        if bans is not None:
            embed.add_field(name="Bans", value=f"{bans}")
        await ctx.send(embed=embed, silent=True)

    @commands.command(name="whois", aliases=["user-info", "user", "userinfo"])
    @commands.guild_only()
    async def userinfo(self, ctx, *, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        userperms = []
        member = ctx.author if not user else user
        if user:
            member = await find_member_named(ctx.guild, user, ctx)
            if not member:
                await user_not_found(ctx, user)
                return
        embed = guilded.Embed(title=f"{member}'s User Information",
                              color=guilded.Colour.blue())
        embed.set_thumbnail(url=avatar_handler(member))
        embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar)

        embed.add_field(name="Name", value=f"<@{member.id}>", inline=True)
        embed.add_field(name="User ID", value=member.id, inline=False)
        user_data = await self.client.http.get_member(
                    ctx.server.id, member.id)
        if member.id in self.client.devids:
            print(user_data)

        user = user_data['member']['user']

        joined_at = datetime.fromisoformat(user_data['member']['joinedAt'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
        embed.add_field(name="Joined at", value=f"`{joined_at}`", inline=False)
        embed.add_field(name="Created at", value=f"`{created_at}`", inline=False)
        roleslist = ""
        for role in member.roles:
            roleslist += f"{role.mention}, "
        if len(member.roles) != 0:
            roles = roleslist[:-2]
        else:
            roles = "No Roles"

        embed.add_field(name="User Roles", value=roles)
        embed.set_thumbnail(url=avatar_handler(member))
        banner = user.get('banner', False)
        if banner:
            embed.set_image(url=user['banner'])

        await ctx.send(embed=embed, silent=True)


    #@userinfo.error

    async def userinfo_error(self, ctx, error):
        if isinstance():
            embed = guilded.Embed(
                title=f"{guilded.User}'s User Information",
                description="Wer braucht überhaupt solche Infos",
                color=guilded.Colour.blue())
            embed.set_thumbnail(url=guilded.User.avatar)
            embed.set_author(name=ctx.message.author,
                             icon_url=ctx.author.avatar)

            embed.add_field(name="Name",
                            value=f"<@{guilded.User.id}>",
                            inline=True)
            embed.add_field(name="User ID", value=guilded.User.id, inline=True)
            embed.add_field(name='Created At',
                            value=guilded.User.created_at.__format__(
                                '%A, %d. %B %Y at %H:%M:%S'),
                            inline=False)
            await ctx.send(embed=embed, silent=True)

    @commands.command(name="av", aliases=["avatar", "pfp"])
    async def avatar(self, ctx, *, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        member = ctx.author if not user else user
        if user:
            member = await find_member_named(ctx.guild, user, ctx)
            if not member:
                await user_not_found(ctx, user)
                return
        avatar = str(avatar_handler(member)).replace(".webp", "").replace(
            ".png", "")  #[:-3]
        print(avatar_handler(member))
        webp = avatar + ".webp"
        png = avatar + ".png"
        embed = guilded.Embed(
            title=f"{member}'s avatar",
            color=guilded.Colour.blue(),  #member.color,
            description=f"[webp]({webp}) | [png]({png})")
        av = str(avatar_handler(member))
        embed.set_image(url=av)
        embed.set_author(name=ctx.message.author,
                         icon_url=ctx.message.author.avatar)
        await ctx.send(embed=embed, silent=True)

    @commands.command()
    async def categoryid(self, ctx):
        color = guilded.Color.from_rgb(239, 83, 80)
        embed = guilded.Embed(description=ctx.channel.category_id, color=color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)
        return



    @commands.command(name="recache")
    async def recache(self, ctx):
        if not (await manage_guild(ctx)):
            return
        #guild_id = ctx.guild.id
        del self.client.http._servers[ctx.guild.id]
        await ctx.message.add_reaction(90002171)
        return

# @commands.command()
#@commands.has_permissions(administrator=True)

    async def nuke(self, ctx, limit=None):
        #await ctx.channel.send("Ein Backup vom Channel wird vor dem Nuke erstellt, dies kann einige Minuten dauern, für einen sofortigen Nuke, nutze <gg instant-nuke>")
        if limit:
            limit = int(limit)
        channel = ctx.channel
        #transcript = await chat_exporter.export(channel, limit, tz_info)
        #  transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{channel.name}.html")
        embed = guilded.Embed(
            colour=guilded.Colour.blue(),
            title=f":boom: Nuke :boom:",
            description=f"Channel was nuked by <@{ctx.message.author.id}>")
        embed.set_author(name=f"{ctx.message.author}",
                         icon_url=ctx.author.avatar)
        embed.set_image(url=random.choice(nukes))
        channel = ctx.channel
        channel_position = channel.position
        await ctx.channel.delete(reason="nuke")
        new_channel = await ctx.guild.create_chat_channel(
            name=channel.name, topic=channel.topic, puplic=channel.public)
        await new_channel.edit(position=channel_position,
                               sync_permissions=True)
        await new_channel.send(embed=embed,
                               silent=True)  #, file=transcript_file)




    #@commands.command()
    #@commands.has_permissions(ban_members=True)
    async def toggle(self, ctx, user, *reason):
        if not (await manage_channels(ctx)):
            return

        member = await find_member_named(ctx.guild, user)
        if not member:
            await user_not_found(ctx, user)
            return
        if 1 > 1:  #not ctx.message.author.top_role > member.top_role:
            await ctx.channel.send("Your role is too low")
            return
        await ctx.channel.set_permissions(member,
                                          send_messages=False,
                                          add_reactions=False,
                                          read_messages=False)
        if reason:
            rsn = ""
            for i in reason:
                rsn += f"{i}"
        else:
            rsn = "No reason given"
        embed = guilded.Embed(
            colour=guilded.Colour.red(),
            title=f":lock: Toggle :lock:",
            description=
            f"{member.mention} can't send any messages in this channel anymore\nReason: {rsn}"
        )
        embed.set_author(name=f"{ctx.message.author}",
                         icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)

    #@commands.command()
    #@commands.has_permissions(ban_members=True)
    async def untoggle(self, ctx, user):
        if not (await manage_channels(ctx)):
            return
        member = await find_member_named(ctx.guild, user)
        if not member:
            await user_not_found(ctx, user)
            return
        await ctx.channel.set_permissions(member,
                                          send_messages=None,
                                          add_reactions=None,
                                          read_messages=None)
        embed = guilded.Embed(
            colour=guilded.Colour.green(),
            title=f":unlock: Untoggle :unlock:",
            description=
            f"{member.mention} can send messages in this channel again")
        embed.set_author(name=f"{ctx.message.author}",
                         icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name="banner")
    async def banner(self, ctx, *, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        member = ctx.author if not user else user
        if user:
            member = await find_member_named(ctx.guild, user, ctx)
            if not member:
                await user_not_found(ctx, user)
                return
        banner = None
        if member.banner is None:
            if (self.banner_cache.get(member.id) is None):

                jsn = await self.client.http.get_member(
                    ctx.server.id, member.id)
                info = jsn
                if not (info["member"]["user"].get('banner') is None):
                    banner = info["member"]["user"]["banner"]
                    self.banner_cache[member.id] = {
                        "banner": banner,
                        "time": time.time()
                    }
                else:
                    self.banner_cache[member.id] = {
                        "banner": None,
                        "time": time.time()
                    }
            else:
                if time.time() - self.banner_cache[
                        member.id]["time"] > 10 * 60:
                    jsn = await self.client.http.get_member(
                        ctx.server.id, member.id)
                    info = jsn
                    if not (info["member"]["user"].get('banner') is None):
                        banner = info["member"]["user"]["banner"]
                        self.banner_cache[member.id] = {
                            "banner": banner,
                            "time": time.time()
                        }
                banner = self.banner_cache[member.id]["banner"]

        if banner is None:
            return await ctx.reply(content=f"{member} has no banner!",
                                   silent=True)
        embed = guilded.Embed(
            title=f"{member}'s banner",
            color=guilded.Colour.blue(),  #member.color,
            description=f"[Banner-URL]({banner})")
        embed.set_image(url=banner)
        # embed.set_thumbnail(url=avatar_handler(member))

        embed.set_author(name=ctx.message.author,
                         icon_url=avatar_handler(ctx.author))
        await ctx.reply(embed=embed, silent=True)

    #     else:
    #  color = req["banner_color"]
    #       if color:
#             hex = color.replace("#", "")
# https://singlecolorimage.com/get/0a4850/1024x400.png
#                banner_url = f"https://singlecolorimage.com/get/{hex}/1024x500.png"
#            embed = discord.Embed(title=f"{member}'s banner", color=member.color)
#           embed.set_image(url=banner_url)
#             embed.set_thumbnail(url=avatar_handler(member))
#             embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar)
#              embed.set_footer(text=f"Hex-Code: {color}")
#               await ctx.message.reply(embed=embed)
#            else:
#               await ctx.message.reply(f"{member} benutzt seinen default Banner!")

    @commands.command(name="award-xp")
    async def award_xp(self, ctx, limit: int, *, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_xp(ctx)):
            return
        if limit > 1000:
            return await ctx.send("The maximum xp-limit is 1000.")
        if limit < -1000:
            return await ctx.send("The minimum xp-limit is -1000.")
        member = ctx.author if not user else user
        if user:
            member = await find_member_named(ctx.guild, user, ctx)
            if not member:
                await user_not_found(ctx, user)
                return
        await member.award_xp(limit)
        embed = guilded.Embed(
            description=f"✅ {member.mention} has received {(limit)} xp",
            color=guilded.Color.blue())
        embed.set_author(name=ctx.author,
                         icon_url=avatar_handler(ctx.author))
        await ctx.send(embed=embed, silent=True)

#  @commands.command(name="test", aliases=["guild-avatar", "server avatar", "server-avatar"])

    async def guild_avatar(self, ctx, *, member: guilded.User = None):
        member = ctx.author if not member else member
        req = await self.client.http.request(
            guilded.http.Route("GET",
                               "/guilds/{guild_id}/members/{uid}",
                               guild_id=ctx.message.guild.id,
                               uid=member.id))
        avatar_id = req["avatar"]
        print(req)
        # If statement because the user may not have a banner
        if avatar_id:
            banner_url = f"https://cdn.discordapp.com/guilds/{ctx.message.guild.id}/users/{member.id}/avatars/{avatar_id}.gif?size=4096"
            async with ClientSession() as nono:
                async with nono.get(banner_url) as respp:
                    if not 300 >= respp.status >= 200:
                        banner_url = f"https://cdn.discordapp.com/guilds/{ctx.message.guild.id}/users/{member.id}/avatars/{avatar_id}.png?size=4096"

            embed = guilded.Embed(title=f"{member}'s server avatar",
                                  color=member.color)
            embed.set_image(url=banner_url)
            embed.set_thumbnail(url=avatar_handler(member))
            embed.set_author(name=ctx.message.author,
                             icon_url=ctx.author.avatar)
            await ctx.message.reply(embed=embed)
        else:
            embed = guilded.Embed(title=f"{member}'s avatar",
                                  color=member.color)
            embed.set_image(url=avatar_handler(member))
            embed.set_author(name=ctx.message.author,
                             icon_url=ctx.author.avatar)
            embed.set_footer(text=f"{member} hat keinen Server-Avatar!")
            await ctx.message.reply(embed=embed)

    #@commands.command()
    #@commands.has_permissions(ban_members=True)
    async def copych(self, ctx, channel: guilded.TextChannel = None):
        return
        if channel is None:
            channel = ctx.channel
        channel_position = channel.position

        new_channel = await channel.clone(reason="clone")
        await new_channel.edit(position=channel_position,
                               sync_permissions=True)
        await new_channel.send("Channel cloned")

    #@commands.command(name="get-raw-embed")
    async def get_raw_embed(self,
                            ctx,
                            embed: int,
                            channel: guilded.TextChannel = None):
        if not channel:
            channel = ctx.message.channel
        msg = await channel.fetch_message(embed)
        embeds = msg.embeds
        for embed in embeds:
            embd = guilded.Embed(
                description=f"```json\n{embed.to_dict()}\n```")
            await ctx.send(embed=embd)

    #@commands.command(name="get-embed")
    async def get_embed(self,
                        ctx,
                        embed: int,
                        channel: guilded.TextChannel = None):
        return
        if not channel:
            channel = ctx.message.channel
        msg = await channel.fetch_message(embed)
        embeds = msg.embeds
        for embed in embeds:
            embd = guilded.Embed(description=embed.to_dict())
            await ctx.send(embed=embd)

    #@commands.command(name="get-message")
    async def get_message(self,
                          ctx,
                          embed: int,
                          channel: guilded.TextChannel = None):
        return
        if not channel:
            channel = ctx.message.channel
        msg = await channel.fetch_message(embed)
        embeds = msg.content
        await ctx.send("```%s\n```" % (embeds))

    #@commands.command(name="mention-all")
    #@commands.has_permissions(administrator=True)
    async def mention_all(self, ctx):
        if not (await mention_everyone(ctx)):
            return
        userlist = ""
        count = 0
        for member in ctx.guild.members:
            count += 1
            userlist += member.mention
            if count == 50:
                count = 0
                embed = guilded.Embed(description=userlist)
                await ctx.message.channel.send(embed=embed)
                await asyncio.sleep(0.1)
                userlist = ""
        if len(userlist) != 0:
            embed = guilded.Embed(description=userlist)
            await ctx.message.channel.send(embed=embed)

    #@commands.command()
    #@commands.is_owner()
    async def forceban(self, ctx, user: guilded.Member, *, reason=None):
        await ctx.message.delete()
        await user.ban(delete_message_days=0)


# @commands.command(name="search-discriminator")

    async def search_discriminator(self, ctx, discriminator):
        users = ""
        count = 0
        for user in self.client.users:
            len(user.discriminator)
            if int(user.discriminator) == int(discriminator):
                users += "%s\n" % user
                count += 1
        await ctx.send(
            f"Ich habe **{count}** Nutzer mit dem Tag **#{discriminator}** gefunden\n{users}"
        )

    #@commands.command(name="clone-message")
    async def get_message(self,
                          ctx,
                          embed: int,
                          channel: guilded.TextChannel = None):
        return
        if not channel:
            channel = ctx.message.channel
        msg = await channel.fetch_message(embed)
        embeds = msg.content
        embd = guilded.Embed(description=embeds)
        embd.set_author(name=msg.author, icon_url=msg.author.avatar)
        await ctx.send(embed=embd)

    @commands.command()
    async def roles(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        roleslist = ""
        count = 0
        for role in ctx.guild.roles:
            count += 1
            roleslist += f"<@{role.id}>\n"
            if count == 30:
                count = 0
                embed = guilded.Embed(description=roleslist)
                await ctx.message.channel.send(embed=embed, silent=True)
                await asyncio.sleep(0.1)
                roleslist = ""
        if len(roleslist) != 0:
            embed = guilded.Embed(description=roleslist,
                                  color=guilded.Colour.dark_theme_embed())
            await ctx.message.channel.send(embed=embed, silent=True)
    @commands.command(name="permcheck")
    async def permcheck(self, ctx, *, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        member = ctx.author if not user else user
        if user:
            member = await find_member_named(ctx.guild, user, ctx)
            if not member:
                await user_not_found(ctx, user)
                return

        dangerous_permissions = [
        "CanUpdateServer",
        "CanDeleteDocs",
        "CanMuteMembers",
        "CanDeleteListItems",
        "CanManageAnnouncements",
        "CanManageEmotes",
        "CanEditApplicationForm",
        "CanPrioritizeVoice",
        "CanEditEvents",
        "CanMentionEveryone",
        "CanDeleteMedia",
        "CanDeleteEvents",
        "CanManageRoles",
        "CanManageNicknames",
        "CanManageChannels",
        "CanDeleteSchedule",
        "CanManageGroups",
        "CanCompleteListItems",
        "CanApproveApplications",
        "CanStickyTopics",
        "CanManageThreads",
        "CanManageServerXp",
        "CanModifyLfmStatus",
        "CanUpdateListItems",
        "CanLockTopics",
        "CanEditEventRsvps",
        "CanDeafenMembers",
        "CanViewFormResponses",
        "CanCreateDocs",
        "CanEditDocs",
        "CanManageVoiceGroups",
        "CanManageChats",
        "CanManageWebhooks",
        "CanDeleteTopics",
        "CanCreateListItems",
        "CanCreateAnnouncements",
        "CanKickMembers",
        "CanBypassSlowMode",
        "CanCreateEvents",
        "CanModerateChannels",
        "CanCreateSchedule",
        "CanReportScores",
        "CanDisconnectUsers",
        "CanIndicateLfmInterest",
        "CanManageBots",
        "CanReadApplications",
        "CanReorderListItems"
        ]


        dangerous_roles = []
        permissions = set()
        
        for role in member.roles:
            if role is not None:
                role_permissions = set(role._permissions)
                permissions.update(role_permissions)
                
                for permission in role_permissions:
                    if permission in dangerous_permissions:
                        # Check if role is already in dangerous_roles
                        existing_role = next((item for item in dangerous_roles if item[0] == role), None)
                        if existing_role:
                            existing_role[1].append(permission)
                        else:
                            dangerous_roles.append([role, [permission]])
    


        embed = guilded.Embed(title=f"Permission Check for {member}")
        if len(dangerous_roles) == 0:
           embed.description="No dangerous permissions found."
        else:
          count = 0
          roles = ""
          for data in dangerous_roles:
              count += 1
              temp_roles = roles
              roles += f"{data[0].mention}: {', '.join(data[1])}\n"
              if count == 15 or len(roles) > 1500:
                t = False
                if len(roles) > 2000:
                    roles = temp_roles
                    t = True
                count = 0
                embed.description = roles
                await ctx.message.channel.send(embed=embed, silent=True)
                await asyncio.sleep(0.1)
                if not t:
                    roles = ""
                else:
                    roles = f"{data[0].mention}: {', '.join(data[1])}\n"
          if len(roles) != 0:
            embed.description = roles
            await ctx.message.channel.send(embed=embed, silent=True)

    @commands.command(name="securitycheck")
    async def securitycheck(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return


        dangerous_permissions = [
        "CanUpdateServer",
        "CanDeleteDocs",
        "CanMuteMembers",
        "CanDeleteListItems",
        "CanManageAnnouncements",
        "CanManageEmotes",
        "CanEditApplicationForm",
        "CanPrioritizeVoice",
        "CanEditEvents",
        "CanMentionEveryone",
        "CanDeleteMedia",
        "CanDeleteEvents",
        "CanManageRoles",
        "CanManageNicknames",
        "CanManageChannels",
        "CanDeleteSchedule",
        "CanManageGroups",
        "CanCompleteListItems",
        "CanApproveApplications",
        "CanStickyTopics",
        "CanManageThreads",
        "CanManageServerXp",
        "CanModifyLfmStatus",
        "CanUpdateListItems",
        "CanLockTopics",
        "CanEditEventRsvps",
        "CanDeafenMembers",
        "CanViewFormResponses",
        "CanCreateDocs",
        "CanEditDocs",
        "CanManageVoiceGroups",
        "CanManageChats",
        "CanManageWebhooks",
        "CanDeleteTopics",
        "CanCreateListItems",
        "CanCreateAnnouncements",
        "CanKickMembers",
        "CanBypassSlowMode",
        "CanCreateEvents",
        "CanModerateChannels",
        "CanCreateSchedule",
        "CanReportScores",
        "CanDisconnectUsers",
        "CanIndicateLfmInterest",
        "CanManageBots",
        "CanReadApplications",
        "CanReorderListItems"
        ]


        dangerous_roles = []
        permissions = set()
        
        for role in ctx.server.roles:
            if role is not None:
                role_permissions = set(role._permissions)
                permissions.update(role_permissions)
                
                for permission in role_permissions:
                    if permission in dangerous_permissions:
                        # Check if role is already in dangerous_roles
                        existing_role = next((item for item in dangerous_roles if item[0] == role), None)
                        if existing_role:
                            existing_role[1].append(permission)
                        else:
                            dangerous_roles.append([role, [permission]])
    


        embed = guilded.Embed(title=f"Security Check for {ctx.server}")
        if len(dangerous_roles) == 0:
           embed.description="No dangerous permissions found."
        else:
          count = 0
          roles = ""
          for data in dangerous_roles:
              count += 1
              temp_roles = roles
              roles += f"{data[0].mention}: {', '.join(data[1])}\n"
              if count == 15 or len(roles) > 1500:
                t = False
                if len(roles) > 2000:
                    roles = temp_roles
                    t = True
                count = 0
                embed.description = roles
                await ctx.message.channel.send(embed=embed, silent=True)
                await asyncio.sleep(0.1)
                if not t:
                    roles = ""
                else:
                    roles = f"{data[0].mention}: {', '.join(data[1])}\n"
          if len(roles) != 0:
            embed.description = roles
            await ctx.message.channel.send(embed=embed, silent=True)

    #@commands.command()
    async def emojis(self, ctx):
        # print("ok")
        #    print(len(ctx.guild.emojis))
        emojislist = ""
        count = 0
        for emoji in ctx.guild.emojis:
            count += 1
            emojislist += f":{emoji.name}: - `:{emoji.name}:` - ID: {emoji.id}\n"
            if count == 20:
                count = 0
                embed = guilded.Embed(description=emojislist)
                await ctx.message.channel.send(embed=embed, silent=True)
                await asyncio.sleep(0.1)
                emojislist = ""
        if len(emojislist) != 0:
            embed = guilded.Embed(description=emojislist)
            await ctx.message.channel.send(embed=embed, silent=True)


def setup(client):
    client.add_cog(Moderation(
        client))  # Remember based on which name you assigned your class for,
    # It should be used at the end of the setup function right.
    # eg:- client.add_cog(x(client)), client.add_cog(y(client)), client.add_cog(z(client))
