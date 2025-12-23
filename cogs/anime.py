import guilded
from guilded.ext import commands
import random, secrets
import os, io, PIL, asyncio
import checksfrfr
from gil_utility.gperms import *

class Animation(commands.Cog):
    def __init__(self, client):
        self.client = client
        with open('images/angry.txt') as f:
            self.choices_angry = f.readlines()
        with open('images/awkward.txt') as f:
            self.choices_awkward = f.readlines()
        with open('images/bite.txt') as f:
            self.choices_bite = f.readlines()
        with open('images/blush.txt') as f:
            self.choices_blush = f.readlines()
        with open('images/bored.txt') as f:
            self.choices_bored = f.readlines()
        with open('images/cry.txt') as f:
            self.choices_cry = f.readlines()
        with open('images/cuddle.txt') as f:
            self.choices_cuddle = f.readlines()
        with open('images/dance.txt') as f:
            self.choices_dance = f.readlines()
        with open('images/hug.txt') as f:
            self.choices_hug = f.readlines()
        with open('images/kiss.txt') as f:
            self.choices_kiss = f.readlines()
        with open('images/nom.txt') as f:
            self.choices_nom = f.readlines()
        with open('images/pat.txt') as f:
            self.choices_pat = f.readlines()
        with open('images/poke.txt') as f:
            self.choices_poke = f.readlines()
        with open('images/punch.txt') as f:
            self.choices_punch = f.readlines()
        with open('images/slap.txt') as f:
            self.choices_slap = f.readlines()
        with open('images/wave.txt') as f:
            self.choices_wave = f.readlines()
        with open('images/happy.txt') as f:
            self.choices_happy = f.readlines()
        self.error_img = "https://66.media.tumblr.com/98c6d9e942941712e0ef9518fca97a7c/tumblr_opni85yA931v8tshbo1_400.gif"
        self.categories = {
          "angry": self.choices_angry,
          "awkward": self.choices_awkward,
          "bite": self.choices_bite,
          "blush": self.choices_blush,
          "bored": self.choices_bored,
          "cry": self.choices_cry,
          "cuddle": self.choices_cuddle,
          "dance": self.choices_dance,
          "hug": self.choices_hug,
          "kiss": self.choices_kiss,
          "nom": self.choices_nom,
          "pat": self.choices_pat,
          "poke": self.choices_poke,
          "punch": self.choices_punch,
          "slap": self.choices_slap,
          "wave": self.choices_wave,
          "happy": self.choices_happy
        }

    async def self_interaction_error(self, ctx, interaction):
      embed = guilded.Embed(
                description=f"***{ctx.author.name} you can't {interaction} yourself!***",
                colour=guilded.Colour.blue()
            )
      embed.set_image(url=self.error_img)
      await ctx.send(embed=embed)

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
      
    async def embed_handler(self, ctx, phrase, interaction):
      embed = guilded.Embed(title=interaction, description=phrase,color=guilded.Colour.dark_theme_embed())
      embed.set_image(url=random.choice(self.categories[interaction.lower()]))
      await ctx.channel.send(embed=embed, silent=True)

    async def member_handler(self,ctx, member):
      if member is None:
        return False
      else:
        find_member = await find_member_named(ctx.message.server, member, ctx)
        if find_member is None:
          return False
        else:
          return find_member



    @commands.command()
    async def awkward(self, ctx):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      phrase = f"{ctx.author.mention} feels awkward"
      await self.embed_handler(ctx, phrase, "Awkward")
      
    @commands.command(name="angry", aliases=["rage", "angery"])
    async def angry(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} is angry"
        else:
          phrase = f"{ctx.author.mention} is angry with **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} is angry with {handler.mention}"
        else:
          phrase = f"{ctx.author.mention} is angry with themself"
      await self.embed_handler(ctx, phrase, "Angry")

    @commands.command()
    async def bite(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} bites **somebody**"
        else:
          phrase = f"{ctx.author.mention} bites **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} is biting {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "bite")
          return
      await self.embed_handler(ctx, phrase, "Bite")

    @commands.command()
    async def blush(self, ctx):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      phrase = f"{ctx.author.mention} blushes"
      await self.embed_handler(ctx, phrase, "Blush")


    @commands.command()
    async def bored(self, ctx):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      phrase = f"{ctx.author.mention} is bored"
      await self.embed_handler(ctx, phrase, "Bored")


    @commands.command()
    async def cry(self, ctx):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      phrase = f"{ctx.author.mention} cries :sob:"
      await self.embed_handler(ctx, phrase, "Cry")


    @commands.command()
    async def cuddle(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} cuddles with **somebody**"
        else:
          phrase = f"{ctx.author.mention} cuddles with **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} is cuddling with {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "cuddle with")
          return
      await self.embed_handler(ctx, phrase, "Cuddle")

    @commands.command()
    async def dance(self, ctx):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      phrase = f"{ctx.author.mention} is dancing"
      await self.embed_handler(ctx, phrase, "Dance")

    @commands.command()
    async def hug(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} hugs **somebody**"
        else:
          phrase = f"{ctx.author.mention} hugs **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} hugs {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "hug")
          return
      await self.embed_handler(ctx, phrase, "Hug")

    @commands.command()
    async def kiss(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} kisses **somebody**"
        else:
          phrase = f"{ctx.author.mention} kisses **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} kisses {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "kiss")
          return
      await self.embed_handler(ctx, phrase, "Kiss")


    @commands.command(name="nom", aliases=["eat", "hungry"])
    async def nom(self, ctx):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      phrase = f"{ctx.author.mention} eats"
      await self.embed_handler(ctx, phrase, "Nom")

    @commands.command()
    async def pat(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} pats **somebody**"
        else:
          phrase = f"{ctx.author.mention} pats **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} pats {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "pat")
          return
      await self.embed_handler(ctx, phrase, "Pat")

    @commands.command()
    async def poke(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} pokes **somebody**"
        else:
          phrase = f"{ctx.author.mention} pokes **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} pokes {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "poke")
          return
      await self.embed_handler(ctx, phrase, "Poke")

    @commands.command(name="punch", aliases=["hit"])
    async def punch(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} punches **somebody**"
        else:
          phrase = f"{ctx.author.mention} punches **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} punches {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "punch")
          return
      await self.embed_handler(ctx, phrase, "Punch")

    @commands.command(name="slap", aliases=["smack"])
    async def slap(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} slaps **somebody**"
        else:
          phrase = f"{ctx.author.mention} slaps **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} slaps {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "slap")
          return
      await self.embed_handler(ctx, phrase, "Slap")

    @commands.command()
    async def wave(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} waves"
        else:
          phrase = f"{ctx.author.mention} waves to **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} waves to {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "wave to")
          return
      await self.embed_handler(ctx, phrase, "Wave")

    @commands.command(name="smile", aliases=["joy", "happy"])
    async def smile(self, ctx, *, member = None):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
          return
      handler = await self.member_handler(ctx, member)
      if not handler:
        if not member:
          phrase = f"{ctx.author.mention} smiles"
        else:
          phrase = f"{ctx.author.mention} smiles to **{member}**"
      else:
        if not handler.id == ctx.author.id:
          phrase = f"{ctx.author.mention} smiles to {handler.mention}"
        else:
          await self.self_interaction_error(ctx, "smile to")
          return
      await self.embed_handler(ctx, phrase, "Happy")





def setup(client):
    client.add_cog(Animation(client))