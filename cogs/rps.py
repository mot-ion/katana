import sys, subprocess
import checksfrfr
import guilded
from guilded.ext import commands, tasks
import os
import random
import asyncio
from gil_utility.gperms import *
IDS = {}

EMOTES = {'90003217': 0, '90002056': 1, '90002009': 2}

class RPS(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def member_handler(self,ctx, member):
      if member is None:
        return False
      else:
        find_member = await find_member_named(ctx.message.server, member, ctx)
        if find_member is None:
          return False
        else:
          return find_member


    @commands.command(name="rps")
    async def rps(self,ctx,*, enemy=None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return

        # Doesn't start if no one or a bot is mentioned

        # Prints starting board
      if enemy is None:
        embed = guilded.Embed(description=f':rock:, :roll_of_paper: or :scissors:?',color=guilded.Colour.dark_theme_embed())
        embed.set_author(name=ctx.author.name, icon_url=avatar_handler(ctx.author))
        message = await ctx.send(embed=embed)
        # Adds the emotes the players will be clicking on and adds
        # the game to the global dictionary
        for emoji in EMOTES:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.01)
        IDS[message.id] = [ctx.channel, ctx.author.id,ctx.author.name, avatar_handler(ctx.author), "single"]
        await asyncio.sleep(30)
        try:
          del IDS[message.id]
        except: pass
      else:
        list_emoji = [":rock:", ":roll_of_paper:", ":scissors:"]
        handler = await self.member_handler(ctx, enemy)
        if not handler:
          return await ctx.channel.send("You did not mention a valid member!")
        else:
          if handler.id == ctx.author.id:
            return await ctx.channel.send("You cannot play against yourself!")
        await ctx.channel.send(embed=guilded.Embed(description=f"{handler.mention}, would you like to play RPS against {ctx.author}?\nType yes to start a round", color=guilded.Color.dark_theme_embed()))
        try:
          answer = await self.client.wait_for("message", timeout=30, check=lambda response: response.author == handler and response.channel == ctx.channel)
        except asyncio.TimeoutError:
          return await ctx.channel.send(f"{handler} did not join the game")
        accepted = False
        yeslist =  ["yes", "yeah", "ok", "accept", "okay"]
        for yes in yeslist:
          if str(answer.content).lower().startswith(yes):
            accepted = True
        if not accepted:
          return await ctx.channel.send(f"{handler} did not accept the join request") 
        aembed = guilded.Embed(description=f':rock:, :roll_of_paper: or :scissors:?\n\n{ctx.author.mention}',color=guilded.Colour.dark_theme_embed())
        aembed.set_author(name=ctx.author.name, icon_url=avatar_handler(ctx.author))
        eembed = guilded.Embed(description=f':rock:, :roll_of_paper: or :scissors:?\n\n{handler.mention}',color=guilded.Colour.dark_theme_embed())
        eembed.set_author(name=handler.name, icon_url=avatar_handler(handler))

        author_msg = await ctx.send(embed=aembed, private=True)

        enemy_msg = await ctx.send(embed=eembed, private=True)
        
        for emoji in EMOTES:
          await author_msg.add_reaction(emoji)
          await asyncio.sleep(0.01)
          await enemy_msg.add_reaction(emoji)
          await asyncio.sleep(0.01)

        try:

          ret = await asyncio.gather(
    self.client.wait_for("message_reaction_add", timeout=30, check=lambda rctn: rctn._user_id == ctx.author.id and rctn.message.id == author_msg.id and str(rctn.emoji.id) in EMOTES.keys()),
    self.client.wait_for("message_reaction_add", timeout=31, check=lambda rctn: rctn._user_id == handler.id and rctn.message.id == enemy_msg.id and str(rctn.emoji.id) in EMOTES.keys()),
    return_exceptions = True
)
        except:
          return await ctx.channel.send("Ended the game due to inactivity")
        ret = [r if not isinstance(r, Exception) else None for r in ret]
        rctn1, rctn2 = ret[0], ret[1]
        print(rctn1)
        print(rctn2)
        print(ret)

        if rctn1.emoji.id == rctn2.emoji.id:
          state = "It's a tie"
        else:
          if EMOTES[str(rctn1.emoji.id)] == 0:
            if EMOTES[str(rctn2.emoji.id)] == 1:
              state = f"{handler.mention} wins!"
            else:
              state = f"{ctx.author.mention} wins!"
          elif EMOTES[str(rctn1.emoji.id)] == 1:
            if EMOTES[str(rctn2.emoji.id)] == 2:
              state = f"{handler.mention} wins!"
            else:
              state = f"{ctx.author.mention} wins!"
          if EMOTES[str(rctn1.emoji.id)] == 2:
            if EMOTES[str(rctn2.emoji.id)] == 0:
              state = f"{handler.mention} wins!"
            else:
              state = f"{ctx.author.mention} wins!"

        desc = f"{ctx.author.mention} chose {list_emoji[EMOTES[str(rctn1.emoji.id)]]} and {handler.mention} chose {list_emoji[EMOTES[str(rctn2.emoji.id)]]}\n\n{state}"
          
        embed = guilded.Embed(description=desc, color=guilded.Color.dark_theme_embed())
          
        await ctx.channel.send(embed=embed, silent=True)
        
        
        


    @commands.Cog.listener()
    async def on_message_reaction_add(self, reaction):# -> None:
        #print(str(reaction.emoji.id) + " " + reaction.emoji.name)
        #print(dir(reaction))
        #print(reaction._user_id)
      ctx = None
      user = await find_member_named(reaction.message.guild, reaction._user_id, ctx)
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
      if curr_channel[4] == "single":
        if str(reaction.emoji.id) not in EMOTES.keys() \
                or (user.id != curr_channel[1]):
            print("return invalid")
            return None
        list_emoji = [":rock:", ":roll_of_paper:", ":scissors:"]
        choose = random.randint(0, 2)
        if EMOTES[str(reaction.emoji.id)] == choose:
          state = "tie"
        else:
          if EMOTES[str(reaction.emoji.id)] == 0:
            if choose == 1:
              state = "lose"
            else:
              state = "win"
          elif EMOTES[str(reaction.emoji.id)] == 1:
            if choose == 2:
              state = "lose"
            else:
              state = "win"
          if EMOTES[str(reaction.emoji.id)] == 2:
            if choose == 0:
              state = "lose"
            else:
              state = "win"
        text = f":computer: chose {list_emoji[choose]}, you chose {list_emoji[EMOTES[str(reaction.emoji.id)]]}"
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
    client.add_cog(RPS(client))