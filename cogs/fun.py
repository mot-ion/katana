import sys, subprocess, base64, ghookfile
import guilded
from aiohttp import ClientSession
from guilded.ext import commands, tasks
import os, io
import random
from PIL import Image
import asyncio, functools, collections
import checksfrfr
from gil_utility.gperms import *

_OFFSET = 2**3217 - 1
ship_cooldown = {}


def _lerp(v0, v1, t):
    return v0 + t * (v1 - v0)


def _lerp_color(c1, c2, t, *, type=round):
    return tuple(round(_lerp(v1, v2, t)) for v1, v2 in zip(c1, c2))


_lerp_pink = functools.partial(
    _lerp_color, (0, 0, 0), (255, 105, 180)
)  # This seed is used to change the result of ->ship without having to do a
# complicated cache
_seed = 0


def _scale(old_min, old_max, new_min, new_max, value):
    return ((value - old_min) /
            (old_max - old_min)) * (new_max - new_min) + new_min


def _user_score(user):
    return (sum(ord(c) * 0x10FFFF * i for i, c in enumerate(user.id)) +
            sum(ord(c) * 0x10FFFF * i for i, c in enumerate(str(user.avatar)))
            # 0x10FFFF is the highest Unicode can go.
            + sum(ord(c) * 0x10FFFF * i for i, c in enumerate(user.name)))


_default_rating_comments = (
    'There is no chance for this to happen.',
    'Hell nah...',
    'No way, not happening.',
    'Nope.',
    'Perhaps.',
    'Woah this actually might happen.',
    'Sheesh what\'s this',
    'You\'ve got a chance!',
    'Definitely.',
    'What are you waiting for?!',
)
_self_ratings = [
    "Rip {user}, they're forever alone...",
    "Selfcest is bestest.",
]

_value_to_index = functools.partial(_scale, 0, 100, 0,
                                    len(_default_rating_comments) - 1)


class _ShipScore(collections.namedtuple('_ShipRating', 'score comment')):
    __slots__ = ()

    def __new__(cls, score, comment=None):
        if comment is None:
            index = round(_value_to_index(score))
            print(index)
            comment = _default_rating_comments[index]
        return super().__new__(cls, score, comment)


class FUN(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._mask = open('./images/heart.png', 'rb')
        self.possible = [
            "Yes", "No", "Maybe", "Perhaps", "Sure", "Probably", "Nope", "Nah",
            "Absolutely", "Nah", "Yeah"
        ]

    async def _load_user_avatar(self, user):
        async with ClientSession() as session:
            url = str(avatar_handler(user))  #.replace(".webp", ".png")
            if str(url).replace(".webp", "") != str(url):
                webp = True
            else:
                webp = False
            async with session.get(str(url)) as af:
                f = io.BytesIO()
                # if 300 > af.status >= 200:
                b = await af.read()
                image = Image.open(io.BytesIO(b))
                image = image.convert('RGB')
                image = image.resize(size=(500, 500))

                # 3. Save The Image:

                with io.BytesIO() as output:
                    image.save(output, format="png")
                    contents = output.getvalue()
                return contents

    def _calculate_rating(self, user1, user2):
        if user1 == user2:
            index = _seed % 2
            return _ShipScore(index * 100,
                              _self_ratings[index].format(user=user1))

        score = (
            (_user_score(user1) + _user_score(user2)) * _OFFSET + _seed) % 100
        return _ShipScore(score)

    async def find_member_named(self, team, argument: str, ctx, range=0):
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
            try:
                return ctx.message.mentions[range]
            except:
                return None
        return None

    async def _ship_image(self, score, user1, user2):
        u1 = await self._load_user_avatar(user1)
        u2 = await self._load_user_avatar(user2)
        user_avatar_data1 = io.BytesIO(u1)
        user_avatar_data2 = io.BytesIO(u2)
        img = await self._create_ship_image(score, user_avatar_data1,
                                            user_avatar_data2)
        #img = await self.client.loop.run_in_executor(None, self._create_ship_image, score, user_avatar_data1, user_avatar_data2)#await self._create_ship_image(score, user_avatar_data1, user_avatar_data2)
        return img  #await self.client.loop.run_in_executor(None, self._create_ship_image, score,

    async def _create_ship_image(self, score, avatar1, avatar2):
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
        # file =guilded.File(f)
        #file.set_media_type(guilded.enums.FileType.image)
        #file.set_media_type(guilded.enums.MediaType.content_media)
        #  img = await file._upload(self.client.http)
        #print(new_file.url)

        return f  #guilded.File(f, filename='ship.png')#img.url



    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, question=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if question is None:
            await ctx.channel.send(
                "You need to provide a question.\nExample: .8ball will i become rich?"
            )
            return
        choice = random.choice(self.possible)
        if "is guilded better than" in question.lower():
            choice = self.possible[8]
        if "is discord better than" in question.lower():
            choice = self.possible[1]

        # Doesn't start if no one or a bot is mentioned

        # Prints starting board
        embed = guilded.Embed(title=question,
                              description=choice,
                              color=guilded.Colour.dark_theme_embed())
        embed.set_author(name=ctx.author.name,
                         icon_url=avatar_handler(ctx.author))
        message = await ctx.send(embed=embed)
        #sum(ord(c) * 0x10FFFF * i for i, c in enumerate(user.name))
    @commands.command(name="rate")
    async def rate(self, ctx, *, question=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if question is None:
            await ctx.channel.send(
                "You need to provide a topic.\nExample: .rate soccer")
            return
        if len(question) < 2:
            await ctx.channel.send(
                "Topic mustn't be shorter than 2 characters.")
            return
        rt = sum(ord(c) * 0x10FFFF * i for i, c in enumerate(question))
        score = (rt * _OFFSET + _seed) % 100
        scr = round(score / 10)
        good_things = ["katana", "cashey", "hoemotion"]
        for i in range(len(good_things)):
            if good_things[i] in question.lower():
                scr = 10
        embed = guilded.Embed(title=f"Rating {question}",
                              description=f"I give **{question}** a {scr}/10",
                              color=guilded.Colour.dark_theme_embed())
        embed.set_author(name=ctx.author.name,
                         icon_url=avatar_handler(ctx.author))
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def ship(self, ctx, user1=None, user2=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        global ship_cooldown
        """try:
            cooldown, executing = ship_cooldown[ctx.guild.id][
                "cooldown"], ship_cooldown[ctx.guild.id]["executing"]
            try:
                if executing is True:
                    return
            except:
                pass
            print(cooldown)
            if cooldown > 0:
                await ctx.channel.send(
                    f"Command is on cooldown for {cooldown} seconds")
                await asyncio.sleep(cooldown)
                try:
                  cd = ship_cooldown[ctx.guild.id][
                "cooldown"]
                  if cd == cooldown:
                    del ship_cooldown[ctx.guild.id]
                except:
                  pass
                    
                
                return
        except Exception as e:
            print(e)
            ship_cooldown[ctx.guild.id] = {}
            #purge_cooldown[ctx.guild.id] = (int(limit), True)
            ship_cooldown[ctx.guild.id]["cooldown"], ship_cooldown[
                ctx.guild.id]["executing"] = 5, True """

        if len(ctx.message.raw_mentions) == 1:
            user1 = await self.find_member_named(ctx.message.guild,
                                           ctx.message.raw_mentions[0],
                                           ctx,
                                           range=1)
            user2 = ctx.author
        elif len(ctx.message.raw_mentions) == 2:
            user1 = await self.find_member_named(ctx.message.guild,
                                           ctx.message.raw_mentions[0],
                                           ctx,
                                           range=1)
            user2 = await self.find_member_named(ctx.message.guild,
                                           ctx.message.raw_mentions[1],
                                           ctx,
                                           range=1)
        else:
            if user2 is not None:
                user2 = await self.find_member_named(ctx.message.guild, user2, ctx)
                user1 = await self.find_member_named(ctx.message.guild,
                                               user1,
                                               ctx,
                                               range=1)
            if user2 is None and user1 is not None:
                nn = await self.find_member_named(ctx.message.guild, user1, ctx)
                user1, user2 = ctx.author, nn

            if user1 is None:
                user1 = ctx.author
                members = ctx.guild.members
                members.remove(user1)
                user2 = random.choice(members)


        score, comment = self._calculate_rating(user1, user2)
        #file = await self._ship_image(score, user1, user2)
        colour = guilded.Colour.from_rgb(*_lerp_pink(score / 100))
        file = await self._ship_image(score, user1, user2)
        url = await ghookfile.upload_file(file)

        embed = (
            guilded.Embed(
                colour=colour,
                description=f"{user1.mention} x {user2.mention}").set_author(
                    name='Shipping').add_field(
                        name='Score', value=f'{score}/100').add_field(
                            name='\u200b', value=f'*{comment}*',
                            inline=False).set_footer(text=f"{user1} x {user2}")
            #.set_image(url='attachment://ship.png')
            .set_image(url=url))
        await ctx.send(embed=embed, silent=True)
        """ship_cooldown[ctx.guild.id]["executing"] = False
        for i in range(5):
            await asyncio.sleep(1)
            ship_cooldown[ctx.guild.id]["cooldown"] = ship_cooldown[
                ctx.guild.id]["cooldown"] - 1
        del ship_cooldown[ctx.guild.id]"""


def setup(client):
    client.add_cog(FUN(client))
