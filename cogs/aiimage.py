import random

import guilded
from guilded.ext import commands
import aiohttp
import asyncio
import re
from datetime import datetime, timedelta
import checksfrfr
import json
from gil_utility.gperms import *

valid_image_types = [4, 5]
valid_ratios = ["1:1", "1:2", "3:2", "3:4", "16:9", "9:16"]
base_image_url = "https://img.muryou-aigazou.com"
cooldown_period = timedelta(seconds=15)  # Cooldown period of 15 seconds
global_cooldown_period = timedelta(minutes=1)  # Global cooldown period of 1 minute

class ImageGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.global_cooldown = None
        self.request_count = 0
        self.bot.loop.create_task(self.refresh_cooldowns())

    async def refresh_cooldowns(self):
        while True:
            now = datetime.now()
            next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
            wait_time = (next_minute - now).total_seconds()
            await asyncio.sleep(wait_time)
            self.cooldowns.clear()
            self.request_count = 0
            self.global_cooldown = None
            #print("Cooldowns and request count have been refreshed.")

    async def check(self, ctx, ratio, prompt):
        if ratio not in valid_ratios:
            await ctx.send(f"Invalid ratio value: {ratio}. Valid values are: {', '.join(valid_ratios)}")
            return False

        if self.global_cooldown and datetime.now() < self.global_cooldown:
            remaining_seconds = (self.global_cooldown - datetime.now()).seconds
            await ctx.send(f"Global cooldown in effect. Please wait {remaining_seconds} seconds before using this command again.")
            return False

        server_id = ctx.guild.id
        current_time = datetime.now()
        if server_id in self.cooldowns and current_time < self.cooldowns[server_id]:
            remaining_seconds = (self.cooldowns[server_id] - current_time).seconds
            await ctx.send(f"Please wait {remaining_seconds} seconds before using this command again.")
            return False
        if not prompt:
            await ctx.send("Please provide a valid prompt.")
            return

        return True

    async def is_sfw(self, prompt):
        for word in ["venus"]:
            if word in prompt.lower():
                return False
        url = "https://muryou-aigazou.com/api/prompt/check"
        payload = {
            "prompt": prompt
        }
        #{"pass": False}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                js = await response.json()
                return js["pass"]

    async def main_generate(self, ctx, prompt, image_type, ratio="1:1"):
        try:

            message = await ctx.reply("Started generation...")
        except:
            message = await ctx.send("Started generation...")
        self.request_count += 1
        if self.request_count > 14:
            self.global_cooldown = datetime.now() + global_cooldown_period
            await message.edit(content="Rate limit exceeded. Entering global cooldown.")
            return

        url = "https://muryou-aigazou.com/api/images/generate-stream"
        payload = {
            "type": image_type,
            "prompt": prompt,
            "isPublic": False,
            "locale": "en",
            "ratio": ratio,
            "token": random.choice([""])
        }
        if not await self.is_sfw(prompt):
            return await message.edit("NSFW content detected. Please modify your prompt.")


        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_data = line.decode('utf-8').strip()
                        if line_data.startswith("data:"):
                            data = line_data[5:].strip()
                            if '"status":"started"' in data:
                                await message.edit(content="Processing generation...")
                            elif '"status":"processing"' in data:
                                await message.edit(content="Still processing generation...")
                            elif '"status":"completed"' in data:
                                image_data = eval(data)
                                image_url = f"{base_image_url}{image_data['imageUrl'].replace('/images', '')}"
                                embed = guilded.Embed(title="Image Generation Completed", color=guilded.Colour.green())
                                embed.set_image(url=image_url)
                                await message.edit(content=None, embed=embed)
                                break
                            elif '"status":"error"' in data:
                                error_data = eval(data)
                                if error_data['errorCode'] != 3030:
                                    await message.edit(content=f"An Error has occured: {error_data['error']}.\nError-Code: {error_data['errorCode']}\nTry again with a different prompt.")
                                else:
                                    await message.edit("NSFW content detected. Please modify your prompt.")
                                break

                else:
                    await message.edit(content=f"Error generating image: {response.status}")

    @commands.command(name="image-gen")
    async def image_gen(self, ctx, *args):
        ch = await checksfrfr.enabled(ctx, ctx.command.name)
        if not ch:
            return
        # Default ratio value
        ratio = "1:1"
        prompt = []

        # Analyze args
        for arg in args:
            if re.match(r'^\d+:\d+$', arg):  # Check for ratio format
                ratio = arg
            else:  # Everything else is part of the prompt
                prompt.append(arg)
        
        prompt = " ".join(prompt)  # Join prompt words


        # Check cooldown
        if not await self.check(ctx, ratio, prompt):
            return
        
        # Update server-specific cooldown
        server_id = ctx.guild.id
        current_time = datetime.now()
        self.cooldowns[server_id] = current_time + cooldown_period

        await self.main_generate(ctx, prompt, image_type=4, ratio=ratio)


    @commands.command(name="anime-gen")
    async def anime_gen(self, ctx, *args):
        ch = await checksfrfr.enabled(ctx, ctx.command.name)
        if not ch:
            return
        # Default ratio value
        ratio = "1:1"
        prompt = []

        # Analyze args
        for arg in args:
            if re.match(r'^\d+:\d+$', arg):  # Check for ratio format
                ratio = arg
            else:  # Everything else is part of the prompt
                prompt.append(arg)
        
        prompt = " ".join(prompt)  # Join prompt words

        if not await self.check(ctx, ratio, prompt):
            return
        
        # Update server-specific cooldown
        server_id = ctx.guild.id
        current_time = datetime.now()
        self.cooldowns[server_id] = current_time + cooldown_period

        await self.main_generate(ctx, prompt, image_type=5, ratio=ratio)


def setup(bot):
    bot.add_cog(ImageGenerator(bot))
