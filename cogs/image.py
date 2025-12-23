"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from io import BytesIO

import guilded
from guilded.ext import commands
import random
import ghookfile
import aiohttp
import checksfrfr
from gil_utility.gperms import *




class Image(commands.Cog):
    """Image manipulation cog."""

    icon = "🖼️"

    def __init__(self, bot):
        self.bot = bot
        self.bot.internalApiHost = "localhost:7050/api/v1/image"
        # Source: https://github.com/ZiRO-Bot/RandomAPI
        self.imageManipUrl = f"http://{self.bot.internalApiHost}"
    async def member_or_auth(self, memberOrUser, ctx):
        if memberOrUser is None:
            memberOrUser = ctx.author
        else:
            memberOrUser = await find_member_named(ctx.server, memberOrUser, ctx)
        if memberOrUser is None:
            memberOrUser = ctx.author
        return memberOrUser



    # TODO: Slash
    async def doImageFilter(self, ctx, _user, type: str, format: str = "png",) -> guilded.Message:
        user = _user   # type: ignore
        userAv = avatar_handler(user)
        embed_vars = {
            "triggered": {"desc": f"{user.mention} pls calm down", "color": guilded.Color.dark_magenta()},
            "blur": {"desc": f"{user.mention}\'s Avatar (blurred)", "color": guilded.Color.dark_magenta()},
            "polaroid": {"desc": f"{user.mention}\'s Avatar (polaroid style)", "color": guilded.Color.lighter_gray()},
            "rip": {"desc": f"R.I.P {user.mention} 🪦\nFly high 🕊️", "color": guilded.Color.black()},
            "invert": {"desc": f"{user.mention}\'s Avatar (inverted colors)", "color": guilded.Color.lighter_gray()},
            "mirror": {"desc": f"{user.mention}\'s Avatar (mirrored)", "color": guilded.Color.gold()},
            "sad": {"desc": f"{user.mention}\'s Avatar (very sad)", "color": guilded.Color.dark_theme()},
            "jail": {"desc": f"Free {user.mention} 🕊️", "color": guilded.Color.dark_theme()},
            "flip": {"desc": f"{user.mention}\'s Avatar (flipped)", "color": guilded.Color.gold()},
            "grayscale": {"desc": f"{user.mention}\'s Avatar (grayscaled)", "color": guilded.Color.light_gray()}
                      }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.imageManipUrl}/{type}?url={userAv}") as req:
                if str(req.content_type).startswith("image/"):
                    filename = f"{type}.{format}"
                    imgBytes = await req.read()
                    if type != "triggered":
                        img = await ghookfile.upload_file(BytesIO(imgBytes))#guilded.File(fp=BytesIO(imgBytes), filename=filename)
                    else:
                        img = await ghookfile.upload_file(BytesIO(imgBytes), "image.gif")
                    e = guilded.Embed(title=str(ctx.command.name).capitalize(), description=embed_vars[type]["desc"], color=embed_vars[type]["color"])
                    e.set_image(url=f"{img}")
                    return await ctx.reply(embed=e, silent=True)
                else:
                    return await ctx.error("Error.")

    """@commands.command()
    async def blurplify(self, ctx, * ,memberOrUser = None):
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        await self.doImageFilter(ctx, memberOrUser, "blurplify")"""

    @commands.command(name="triggered")
    async def triggered(self, ctx, * ,memberOrUser = None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        await self.doImageFilter(ctx, memberOrUser, "triggered", "gif")

    #@commands.command()
    """async def redify(self, ctx, *, memberOrUser=None):
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        await self.doImageFilter(ctx, memberOrUser, "red")"""

    @commands.command(name="polaroid")
    async def polaroid(self, ctx, * ,memberOrUser = None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "polaroid")

    @commands.command(name="rip")
    async def rip(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "rip")

    @commands.command(name="invert")
    async def invert(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "invert")

    @commands.command(name="mirror")
    async def mirror(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        await self.doImageFilter(ctx, memberOrUser, "mirror")

    @commands.command(name="sadify")
    async def sadify(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "sad")

    @commands.command(name="blur")
    async def blur(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "blur")

    @commands.command(name="jail", aliases=["prison"])
    async def jail(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "jail")

    @commands.command(name="grayscale")
    async def grayscale(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "grayscale")

    @commands.command(name="flip")
    async def flip(self, ctx, *, memberOrUser=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        memberOrUser = await self.member_or_auth(memberOrUser, ctx)
        # Currently kinda broken
        await self.doImageFilter(ctx, memberOrUser, "flip")

def setup(bot):
    bot.add_cog(Image(bot))