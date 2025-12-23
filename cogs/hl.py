import sys, subprocess
import guilded
from guilded.ext import commands, tasks
import os, json
import random
import asyncio
import checksfrfr
from gil_utility.gperms import *
IDS = {}

EMOTES = {'90002091': 0, '90002095': 1}#, '90003375': 2}

class HIGHERLOWER(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.json_file = open(f"files/higherlower.json", "r")
        self.jsn = json.load(self.json_file)

    @commands.command(name="higher-lower", aliases=["hl", "higherlower"])
    async def hl(self,ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
          return
        jsn_l = self.jsn
        print(len(jsn_l))
        frst_ch = random.choice(jsn_l)
        jsn_l.remove(frst_ch)
        print(len(jsn_l))
        scnd_ch = random.choice(jsn_l)

        # Doesn't start if no one or a bot is mentioned

        # Prints starting board
        embed = guilded.Embed(description=f'Has **{frst_ch["name"]}** been googled more or less than **{scnd_ch["name"]}?**',color=guilded.Colour.dark_theme_embed())
        embed.set_author(name=ctx.author.name, icon_url=avatar_handler(ctx.author))
        message = await ctx.send(embed=embed)
        # Adds the emotes the players will be clicking on and adds
        # the game to the global dictionary
        for emoji in EMOTES:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.01)
        IDS[message.id] = [ctx.channel, ctx.author.id,ctx.author.name, avatar_handler(ctx.author), frst_ch, scnd_ch]
        await asyncio.sleep(30)
        try:
          del IDS[message.id]
        except: pass


    @commands.Cog.listener()
    async def on_message_reaction_add(self, reaction):# -> None:
        #print(dir(reaction))
        #print(reaction._user_id)
        user = await find_member_named(reaction.message.guild, reaction._user_id)
        """
        Check which reaction role was pressed and changes the board accordingly.
        """
        # If reaction is in a channel where no one is playing, or if the person
        # adding the reactions is the bot, do nothing.
        if reaction.message.id not in IDS or \
                user.id == self.client.user.id:
            return None
        curr_channel = IDS[reaction.message.id]
        # for P_DICT
        #if user.id != self.client.user.id:
            #await reaction.remove(user)
        # stops the function if a reaction was added or if the reaction
        # was sent by a non-player
        if str(reaction.emoji.id) not in EMOTES.keys() \
                or (user.id != curr_channel[1]):
            print("return invalid")
            return None
        if curr_channel[4]["searches"] > curr_channel[5]["searches"]:
          right_emoji = 0
          mark = ">"
        else:
          right_emoji = 1
          mark = "<"
        if EMOTES[str(reaction.emoji.id)] == right_emoji:
          state = "win"
        else:
          state = "lose"
        text = f'**{curr_channel[4]["name"]}:** {curr_channel[4]["searches"]} {mark} **{curr_channel[5]["name"]}:** {curr_channel[5]["searches"]}'
        if state == "win":
          text += "\nYou win!"
          color = guilded.Colour.green()
        elif state == "lose":
          text += "\nYou lose!"
          color = guilded.Colour.red()
        else:
          text += "\nIt's a tie!"
          color = guilded.Colour.dark_theme_embed()
        embed=guilded.Embed(description=text,color=color)
        embed.set_author(name=curr_channel[2], icon_url=curr_channel[3])
        await reaction.message.edit(embed=embed)


        try: del IDS[reaction.message.id]
        except: pass



def setup(client):
    client.add_cog(HIGHERLOWER(client))