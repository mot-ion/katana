import sys, subprocess, base64
import guilded
from guilded.ext import commands, tasks
import os, io
import random
import asyncio
from PIL import Image
import ghookfile
from gil_utility.gperms import *
IDS = {}

EMOTES = {'90003217': 0, '90002056': 1, '90002009': 2}

class Test(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ids = []
    def find_member_named(self, team, argument: str, ctx):
        try:
            argument = argument.replace("@", "")
        except:
            pass
        mem = guilded.utils.find(lambda m: m.name == argument or m.nick == argument or m.id == argument, team.members)
        if mem is not None:
          return mem
        if len(ctx.message.mentions) != 0:
          return ctx.message.mentions[0]
        return None
      

    def avatar_handler(self, member: guilded.Member):
        #avatar = str(member.avatar)[:-3]
        #webp = avatar + "webp"
        #png = avatar + "png"
        #if member.bot:
        #  av = webp
        #else:
        #  av = png
        #print(av)
        #print(member.avatar)
        if member.avatar == "None" or member.avatar is None:
          return f"https://www.guilded.gg/asset/DefaultUserAvatars/profile_{random.randint(1, 5)}.png"
        return member.avatar 
    @commands.command(name="betaimage")
    async def betaimage(self,ctx):
      await ctx.send("testing..")
      #file = guilded.File("./images/heart.png")
      file_data = open("./images/heart.png", 'rb')
      attachment = file_data.read()
      await ghookfile.upload_file(attachment)
      #file.set_media_type(guilded.enums.FileType.image)
      #file.set_media_type(guilded.enums.MediaType.content_media)
      
      #img = await file._upload(self.client.http)
      #print(new_file.url)
      #embed = guilded.Embed()
      #embed.set_image(url=img.url)
      #await ctx.channel.send(embed=embed)


    def _calculate_rating(self, user1, user2):
        if user1 == user2:
            index = _seed % 2
            return _ShipScore(index * 100, _self_ratings[index].format(user=user1))

        score = ((_user_score(user1) + _user_score(user2)) * _OFFSET + _seed) % 100
        return _ShipScore(score)



    def __unload(self):
        self._mask.close()
        self._future.cancel()

    async def _load_user_avatar(self, user):
        async with ClientSession() as session:
            url = user.avatar_url_as(format='png', size=512)
            async with session.get(
                    str(url)
            ) as af:
                # if 300 > af.status >= 200:
                return await af.read()

    def _create_ship_image(self, score, avatar1, avatar2):
        ava_im1 = Image.open(avatar1).convert('RGBA')
        ava_im2 = Image.open(avatar2).convert('RGBA')

        # Assume the two images are square
        size = min(ava_im1.size, ava_im2.size)
        offset = round(_scale(0, 100, size[0], 0, score))

        ava_im1.thumbnail(size)
        ava_im2.thumbnail(size)

        # paste img1 on top of img2
        newimg1 = Image.new('RGBA', size=size, color=(0, 0, 0, 0))
        newimg1.paste(ava_im2, (-offset, 0))
        newimg1.paste(ava_im1, (offset, 0))

        # paste img2 on top of img1
        newimg2 = Image.new('RGBA', size=size, color=(0, 0, 0, 0))
        newimg2.paste(ava_im1, (offset, 0))
        newimg2.paste(ava_im2, (-offset, 0))

        # blend with alpha=0.5
        im = Image.blend(newimg1, newimg2, alpha=0.6)

        mask = Image.open(self._mask).convert('L')
        mask = mask.resize(ava_im1.size, resample=Image.BILINEAR)
        im.putalpha(mask)

        f = io.BytesIO()
        im.save(f, 'png')
        f.seek(0)
        return base64.b64encode(f.read())#guilded.File(f, filename='ship.png')

    async def _ship_image(self, score, user1, user2):
        user_avatar_data1 = io.BytesIO(await self._load_user_avatar(user1))
        user_avatar_data2 = io.BytesIO(await self._load_user_avatar(user2))
        return await self.client.loop.run_in_executor(None, self._create_ship_image, score,
                                                      user_avatar_data1, user_avatar_data2)

    #@commands.command()
    async def ship(self, ctx, user1: guilded.Member = None, user2: guilded.Member = None):
        """Ships two users together, and scores accordingly.
        Myst was here <3.
        Also Myst is mine pls no touching kthx. <3
        """
        if user1 is None:
            user1 = ctx.author
            members = ctx.guild.members
            members.remove(user1)
            user2 = random.choice(members)

        if user2 is None and user1 is not None:
            user1, user2 = ctx.author, user1

        score, comment = self._calculate_rating(user1, user2)
        if user1.id + user2.id == 829071554393931847 + 814073265223761951 or user1.id + user2.id == 819961733229314079 + 814073265223761951:
            score = 100
            comment = "Worauf wartet ihr noch?!"
        file = await self._ship_image(score, user1, user2)
        colour = guilded.Colour.from_rgb(*_lerp_pink(score / 100))

        embed = (guilded.Embed(colour=colour, description=f"{user1.mention} x {user2.mention}")
                 .set_author(name='Shipping')
                 .add_field(name='Score', value=f'{score}/100')
                 .add_field(name='\u200b', value=f'*{comment}*', inline=False)
                 .set_footer(text=f"{user1} x {user2}")
                 .set_image(url='attachment://ship.png')

                 )
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def allcmds(self,ctx):
       cmds = "["
       for c in self.client.commands:
         cmds += f'"{c.name}"' + ", "
       cmds = cmds[:-2]
       cmds += "]"
       await ctx.channel.send(cmds)
    @commands.command(name="reaction-test")
    async def reaction_test(self, ctx):
      message =await ctx.channel.send("abc")
      await message.add_reaction('90002199')
      self.ids.append(message.id)
      await asyncio.sleep(10)
      try: 
        self.ids.remove(message.id)
      except:
        pass
    @commands.command(name="fetch-servers")
    async def fetch_servers(self, ctx):
      try:
        servers = await self.client.fetch_servers()
        await ctx.channel.send(len(servers))
      except Exception as e:
        await ctx.channel.send(e)
    @commands.command(name="emoji-list")
    async def emoji_list(self, ctx):
      emojis = ""
      for emoji in ctx.guild.emotes:
        emojis += f"{emoji} - {emoji.id}\n"
      await ctx.channel.send(embed=guilded.Embed(description=emojis))
    @commands.command(name="testdel")
    async def test_del(self, ctx):
      await ctx.message.delete()
      
    #@commands.Cog.listener()
    async def on_message_reaction_add(self, reaction):# -> None:
        #print(dir(reaction))
        #print(reaction._user_id)
        ctx = None
        user = self.find_member_named(reaction.message.guild, reaction._user_id, ctx)
        """
        Check which reaction role was pressed and changes the board accordingly.
        """
        # If reaction is in a channel where no one is playing, or if the person
        # adding the reactions is the bot, do nothing.
        if reaction.message.id not in self.ids or \
                user.id == self.client.user.id:
            return None
        else:
          if str(reaction.emoji.id) == "90002199":
            await reaction.message.remove_reaction("90002199", user)
            self.ids.remove(reaction.message.id)

        #embed.add_field(name="Roles", value=", ".join(role.mentions for role in member.roles if role is not None), inline=False)
        #embed.add_field(name="Permissions", value=", ".join(permissions), inline=False)

    def get_top_role(self, member: guilded.Member):
        top_role = 0
        for role in member.roles:
            if role.position > top_role:
                top_role = role.position
        return top_role

    @commands.command(name="rolepos")
    async def rolepos(self, ctx, *, user=None):
        #check = await checksfrfr.enabled(ctx, ctx.command.name)
        #if not check:
        #    return
        member = ctx.author if not user else user
        if user:
            member = self.find_member_named(ctx.guild, user, ctx)
            if not member:
                #await self.user_not_found(ctx, user)
                return
        await ctx.send(self.get_top_role(member))


            

      
def setup(client):
    client.add_cog(Test(client))