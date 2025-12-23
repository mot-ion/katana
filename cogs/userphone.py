import guilded, random
from guilded.ext import commands
import asyncio
import re
import checksfrfr
from gil_utility.gperms import *

class Userphone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_calls = {}
        self.call_channels = {}
        self.looking_for_userphone = None
        self.image_regex = re.compile(r"!\[\]\((https:\/\/[^\s]+)\)")

    @commands.command(name="userphone")
    async def userphone(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        """Starts a userphone call."""
        if ctx.author.id in self.active_calls:
            await ctx.send(embed=guilded.Embed(description="You are already in a call.", color=guilded.Color.red()))
            return

        if self.looking_for_userphone is None:
            self.looking_for_userphone = ctx.author.id
            self.call_channels[ctx.author.id] = ctx.channel.id
            await ctx.send(
                embed=guilded.Embed(description="Looking for another userphone user...", color=guilded.Color.blue()))

            async def timeout_check():
                for _ in range(360):  # 180 Sekunden prüfen
                    await asyncio.sleep(0.5)
                    if self.looking_for_userphone != ctx.author.id:
                        return False  # Verbindung hergestellt
                if self.looking_for_userphone == ctx.author.id:
                    self.looking_for_userphone = None
                    del self.call_channels[ctx.author.id]
                    await ctx.send(
                        embed=guilded.Embed(description="No connection made. Timeout occurred. Connection ended.",
                                            color=guilded.Color.red()))
                    return True  # Signalisiere, dass der Timeout eingetreten ist
                return False

            self.timeout_task = self.bot.loop.create_task(timeout_check())

            # Warte, bis die Verbindung hergestellt wurde oder der Timeout eintritt
            while not self.timeout_task.done():
                await asyncio.sleep(0.5)
            if await self.timeout_task:
                return

        else:
            other_id = self.looking_for_userphone
            other_channel = self.bot.get_channel(self.call_channels[other_id])
            self.active_calls[ctx.author.id] = other_id
            self.active_calls[other_id] = ctx.author.id
            self.call_channels[ctx.author.id] = ctx.channel.id

            other_user = self.bot.get_user(other_id)
            embed = guilded.Embed(description=f"Connected with <@{other_id}>!", color=guilded.Color.green())
            embed.set_author(name=str(other_user), icon_url=avatar_handler(other_user))
            await ctx.send(embed=embed)

            embed = guilded.Embed(description=f"Connected with {ctx.author.mention}!", color=guilded.Color.green())
            embed.set_author(name=str(ctx.author), icon_url=avatar_handler(ctx.author))
            await other_channel.send(embed=embed)

            self.looking_for_userphone = None

        def msg_check(m):
            return m.author.id in self.active_calls and m.channel == ctx.channel
        def sign_all_content_attachments(message: guilded.Message) -> str:

            # Replace image links

            message_content = message.content
            matches = self.image_regex.findall(message_content)
            replacement_counter = 1
            for url in matches:
                replacement = f"[Media {replacement_counter}]({guilded.Asset(message._state, url=url, key=guilded.asset.strip_cdn_url(url)).url})"
                message_content = message_content.replace(f"![]({url})", replacement, 1)
                replacement_counter += 1
            return message_content

        while True:
            try:
                msg = await self.bot.wait_for('message', check=msg_check, timeout=180)
                if msg.content in [f'{ctx.prefix}hangup', f'{ctx.prefix} hangup']:
                    break

                other_id = self.active_calls[msg.author.id]
                other_channel = self.bot.get_channel(self.call_channels[other_id])
                embed = guilded.Embed(color=guilded.Color.blue())
                embed.set_author(name=str(msg.author), icon_url=avatar_handler(msg.author))
                image_url = re.search(r'(https?://\S+\.(?:jpg|jpeg|png|gif|webp))', msg.content)
                video_url = re.search(r'(https?://\S+\.(?:webm|mp4))', msg.content)
                content = msg.content
                if video_url and not image_url:
                    content = re.sub(r'(https?://\S+\.(?:webm|mp4))', '', content).strip()
                    content = re.sub(r'!\[\]\(\S+\)', '', content).strip()
                    embed.description = content
                elif image_url and not video_url:
                    embed.set_image(url=image_url.group(1))
                    content = re.sub(r'(https?://\S+\.(?:jpg|jpeg|png|gif|webp))', '', content).strip()
                    content = re.sub(r'!\[\]\(\S+\)', '', content).strip()
                    embed.description = content
                elif image_url and video_url:
                    content = re.sub(r'(https?://\S+\.(?:webm|mp4))', '', content).strip()
                    content = re.sub(r'!\[\]\(\S+\)', '', content).strip()
                    embed.set_image(url=image_url.group(1))
                    content = re.sub(r'(https?://\S+\.(?:jpg|jpeg|png|gif|webp))', '', content).strip()
                    content = re.sub(r'!\[\]\(\S+\)', '', content).strip()
                    embed.description = content
                
                embed.description = sign_all_content_attachments(msg)
                await other_channel.send(embed=embed)

            except asyncio.TimeoutError:
                try:
                    self.active_calls[ctx.author.id]
                    self.active_calls[other_id]
                    self.call_channels[ctx.author.id]
                    self.call_channels[other_id]
                except KeyError:
                    break
                await ctx.send(
                    embed=guilded.Embed(description="Call ended due to inactivity.", color=guilded.Color.red()))
                other_channel = self.bot.get_channel(self.call_channels[self.active_calls[ctx.author.id]])
                await other_channel.send(
                    embed=guilded.Embed(description="Call ended due to inactivity.", color=guilded.Color.red()))
                del self.active_calls[ctx.author.id]
                del self.active_calls[other_id]
                del self.call_channels[ctx.author.id]
                del self.call_channels[other_id]
                break

    @commands.command(name="hangup")
    async def hangup(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        """Ends the current userphone call."""
        if ctx.author.id not in self.active_calls:
            await ctx.send(embed=guilded.Embed(description="You are not in a call.", color=guilded.Color.red()))
            return

        other_id = self.active_calls[ctx.author.id]
        other_channel = self.bot.get_channel(self.call_channels[other_id])
        await ctx.send(embed=guilded.Embed(description="Call ended.", color=guilded.Color.red()))
        await other_channel.send(embed=guilded.Embed(description="Call ended.", color=guilded.Color.red()))

        del self.active_calls[ctx.author.id]
        del self.active_calls[other_id]
        del self.call_channels[ctx.author.id]
        del self.call_channels[other_id]

def setup(bot):
    bot.add_cog(Userphone(bot))