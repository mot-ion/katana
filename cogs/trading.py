import guilded
from guilded.ext import commands, tasks
from collections import defaultdict
import asyncio
import json, os
from pathlib import Path
from gil_utility.gperms import *

class Trade:
    def __init__(self):
        self.offers = defaultdict(list)
        self.confirmations = defaultdict(list)
        self.start_time = None
        self.channel_id = None

    def add_offer(self, user_id, character):
        if len(self.offers[user_id]) < 3:
            self.offers[user_id].append(character)
            return True
        return False

    def remove_offer(self, user_id, character_name):
        for character in self.offers[user_id]:
            if character['name'].lower() == character_name.lower():
                self.offers[user_id].remove(character)
                return True
        return False

    def confirm_trade(self, user_id, server_id):
      if user_id not in self.confirmations[server_id]:
        self.confirmations[server_id].append(user_id)

    def is_trade_confirmed(self, user1_id, user2_id, server_id):
        return user1_id in self.confirmations[server_id] and user2_id in self.confirmations[server_id]

    def is_any_confirmed(self, user1_id, user2_id, server_id):
        return bool(self.confirmations[server_id][user1_id]) or bool(self.confirmations[server_id][user2_id])

    def clear_trade(self, server_id):
        self.offers[server_id].clear()
        self.confirmations[server_id].clear()
        self.start_time = None
        self.channel_id = None

class Trading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trades = defaultdict(dict)  # Verknüpft mit Server-IDs
        self.characters = []  # Diese Liste muss mit den verfügbaren Charakteren gefüllt werden
        self.check_trade_timeout.start()
    @tasks.loop(seconds=10)
    async def check_trade_timeout(self):
        current_time = asyncio.get_event_loop().time()
        for server_id, trades in list(self.trades.items()):
            for trade in list(trades.values()):
                if trade.start_time and current_time - trade.start_time >= 240:
                    tr = self.trades[server_id]#[ctx.author.id]
        #print(trade)
                    trade_users = list(tr.keys())
                    print(trade_users)
                    channel = self.bot.get_channel(trade.channel_id)
                    for user_id in trade_users:
                        user = self.bot.get_user(user_id)
                        await channel.send(f"{user.mention}, trade has been cancelled due to inactivity.")
                    trade.clear_trade(server_id)
                    for user_id in trade_users:
                        del trades[user_id]


    def load_server_data(self, guild_id):
        server_file = Path(f'skidaetabase/{guild_id}.json')
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                server_data = json.load(f)
        else:
        # Erstelle eine neue JSON-Datei, wenn keine existiert
            server_data = {"claimed_characters": [], "cooldowns": {"rolldowns": {}, "claimdowns": {}}, "wishes": {}, "last_reset": -1}
            self.save_server_data(guild_id, server_data)
        return server_data

    def save_server_data(self, guild_id, data):
    # Stelle sicher, dass der Ordner existiert
        folder_path = Path('skidaetabase')
        folder_path.mkdir(parents=True, exist_ok=True)
    
    # Speichere die JSON-Datei im Ordner
        with open(folder_path / f'{guild_id}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def is_user_in_trade(self, guild_id, user_id):
        return user_id in self.trades[guild_id]

    def get_user_claimed_characters(self, guild_id, user_id):
        server_data = self.load_server_data(guild_id)
        return [char for char in server_data['claimed_characters'] if char['owner'] == str(user_id)]



    @commands.command(name='trade', help='Starte einen Trade mit einem anderen Benutzer.')
    async def start_trade(self, ctx, *, user=None):
        if user is None:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You must mention somebody.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return
        if user:
            member = await find_member_named(ctx.guild, user, ctx)
            if not member:
                await user_not_found(ctx, user)
                return
        user = member

        server_id = ctx.guild.id

        if len(self.trades[server_id]) > 0:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Somebody is already trading in this Server.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        trade = Trade()
        trade.start_time = asyncio.get_event_loop().time()
        trade.channel_id = ctx.channel.id
        self.trades[server_id][ctx.author.id] = trade
        self.trades[server_id][user.id] = trade
        color = guilded.Color.blue()
        embed = guilded.Embed(
            description=
            f"{ctx.author.mention} started a trade with {user.mention}. Add characters to the trade via `add-to-trade` and confirm the trade by using `confirm`\nYou may cancel the trade by using `cancel`",
            color=color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name='add-to-trade', help='Fügt einen Charakter zum Trade hinzu.', aliases = ["att", "add"])
    async def add_to_trade(self, ctx, *, character_name: str):
        server_id = ctx.guild.id
        if ctx.author.id not in self.trades[server_id]:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You are not in a trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        claimed_characters = self.get_user_claimed_characters(server_id, ctx.author.id)
        character = next((char for char in claimed_characters if char['name'].lower() == character_name.lower()), None)
        if not character:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You don\'t have '{character_name}'.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        trade = self.trades[server_id][ctx.author.id]
        if trade.add_offer(ctx.author.id, character):
            color = guilded.Color.blue()
            embed = guilded.Embed(
                description=
                f"{character_name} has been added to the trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
        else:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You cannot trade more than 3 characters at once!",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name='remove-from-trade', help='Entfernt einen Charakter aus dem Trade.', aliases="rem-char")
    async def remove_from_trade(self, ctx, *, character_name: str):
        server_id = ctx.guild.id
        if ctx.author.id not in self.trades[server_id]:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You are not in a trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        trade = self.trades[server_id][ctx.author.id]
        trade_users = list(trade.offers.keys())
        if trade.is_any_confirmed(trade_users[0], trade_users[1]):
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You cannot remove any characters after one of you confirms the trade. You may use `cancel` if you feel unsatisfied.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        if trade.remove_offer(ctx.author.id, character_name):
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"{character_name} has been removed from the trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
        else:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Character '{character_name}' is not in the trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name='confirm_trade', help='Bestätige den Trade.', aliases = ["confirm"])
    async def confirm_trade(self, ctx):
        server_id = ctx.guild.id
        if ctx.author.id not in self.trades[server_id]:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You are not in a trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        trade_users = list(self.trades[server_id].keys())
        if ctx.author.id not in trade_users:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You are not part of this trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        trade = self.trades[server_id]  # [user1_id]
        trade_users = list(trade.keys())
        try:
            user1_chars = dict(trade[ctx.author.id].offers)[ctx.author.id]  # trade.offers[user1_id]
        except KeyError as e:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You did not add a character yet.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return


        trade = self.trades[server_id][ctx.author.id]
        trade.confirm_trade(ctx.author.id, ctx.guild.id)
        color = guilded.Color.green()
        embed = guilded.Embed(
            description=
            f"{ctx.author.mention} has confirmed the trade.",
            color=color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)

        if len(trade_users) == 2 and trade.is_trade_confirmed(trade_users[0], trade_users[1], ctx.guild.id):
            await self.execute_trade(ctx.channel, server_id, trade_users[0], trade_users[1])

    @commands.command(name='cancel_trade', help='Bricht den aktuellen Trade ab.', aliases = ["cancel"])
    async def cancel_trade(self, ctx):
        server_id = ctx.guild.id
        if ctx.author.id not in self.trades[server_id]:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You are not in a trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        trade = self.trades[server_id]#[ctx.author.id]
        #print(trade)
        trade_users = list(trade.keys())
        #print(trade_users)
        for user_id in trade_users:
            user = self.bot.get_user(user_id)
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"{user.mention}, trade has been cancelled.",
                color=color)
            embed.set_author(name=user, icon_url=user.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            print(trade[user_id].__dict__)
            print(dict(trade[user_id].offers))
           # print(self.trades[server_id][user_id])
            trade[user_id].clear_trade(server_id)
        for user_id in trade_users:
            del self.trades[server_id][user_id]

    async def execute_trade(self, channel, server_id, user1_id, user2_id):
        trade = self.trades[server_id]#[user1_id]
        trade_users = list(trade.keys())
        user1_chars = dict(trade[user1_id].offers)[user1_id]#trade.offers[user1_id]
        user2_chars = dict(trade[user2_id].offers)[user2_id]#trade.offers[user2_id]

        server_data = self.load_server_data(channel.guild.id)
        for char in user1_chars:
            char_entry = next((c for c in server_data['claimed_characters'] if c['name'] == char['name']), None)
            if char_entry:
                char_entry['owner'] = str(user2_id)
        
        for char in user2_chars:
            char_entry = next((c for c in server_data['claimed_characters'] if c['name'] == char['name']), None)
            if char_entry:
                char_entry['owner'] = str(user1_id)

        self.save_server_data(channel.guild.id, server_data)
        #trade.clear_trade()
        trade[user1_id].clear_trade(server_id)
        trade[user2_id].clear_trade(server_id)
        del self.trades[server_id][user1_id]
        del self.trades[server_id][user2_id]


        color = guilded.Color.green()
        embed = guilded.Embed(
            description=
            f"Trade successfully finished!",
            color=color)
        await channel.send(embed=embed, silent=True)




    @commands.command(name='divorce', help='Lässt einen Charakter los.')
    async def divorce(self, ctx, *, character_name: str):
        server_id = ctx.guild.id
        if self.is_user_in_trade(server_id, ctx.author.id):
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You cannot divorce a character during a trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        server_data = self.load_server_data(ctx.guild.id)
        character = next((char for char in server_data['claimed_characters'] if char['name'].lower() == character_name.lower() and char['owner'] == ctx.author.id), None)

        if character:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Are you sure, that you want to divorce {character_name}? Type 'yes' oder 'no'.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            #confirm_message = await ctx.send(f"Bist du sicher, dass du dich von {character_name} scheiden lassen möchtest? Antworte mit 'ja' oder 'nein'.")

            def check(message):
                return message.author == ctx.author and message.content.lower() in ['yes', 'no']

            try:
                response = await self.bot.wait_for('message', check=check, timeout=30.0)
                if response.content.lower() == 'yes':
                    server_data['claimed_characters'].remove(character)
                    self.save_server_data(ctx.guild.id, server_data)
                    color = guilded.Color.from_rgb(239, 83, 80)
                    embed = guilded.Embed(
                        description=
                        f"You divorced {character_name}.",
                        color=color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=embed, silent=True)
                else:
                    color = guilded.Color.green()
                    embed = guilded.Embed(
                        description=
                        f"{character_name} stays with you.",
                        color=color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=embed, silent=True)
            except asyncio.TimeoutError:
                color = guilded.Color.from_rgb(239, 83, 80)
                embed = guilded.Embed(
                    description=
                    f"Time over, divorce has been cancelled.",
                    color=color)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                await ctx.channel.send(embed=embed, silent=True)
        else:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"{character_name} either doesn\'t exist or doesn\'t belong to you.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)


    @commands.command(name='force-divorce', help='Lässt einen Charakter los.')
    async def force_divorce(self, ctx, *, character_name: str):
        if not (await manage_guild(ctx)):
            return
        server_id = ctx.guild.id
        """if self.is_user_in_trade(server_id, ctx.author.id):
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"You cannot divorce a character during a trade.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return"""

        server_data = self.load_server_data(ctx.guild.id)
        character = next((char for char in server_data['claimed_characters'] if char['name'].lower() == character_name.lower()), None)

        if character:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Are you sure, that you want to divorce {character_name} from <@{character['owner']}>? Type 'yes' oder 'no'.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            #confirm_message = await ctx.send(f"Bist du sicher, dass du dich von {character_name} scheiden lassen möchtest? Antworte mit 'ja' oder 'nein'.")

            def check(message):
                return message.author == ctx.author and message.content.lower() in ['yes', 'no']

            try:
                response = await self.bot.wait_for('message', check=check, timeout=30.0)
                if response.content.lower() == 'yes':
                    server_data['claimed_characters'].remove(character)
                    self.save_server_data(ctx.guild.id, server_data)
                    color = guilded.Color.from_rgb(239, 83, 80)
                    embed = guilded.Embed(
                        description=
                        f"You divorced {character_name} from <@{character['owner']}>.",
                        color=color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=embed, silent=True)
                else:
                    color = guilded.Color.green()
                    embed = guilded.Embed(
                        description=
                        f"{character_name} stays with <@{character['owner']}>.",
                        color=color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=embed, silent=True)
            except asyncio.TimeoutError:
                color = guilded.Color.from_rgb(239, 83, 80)
                embed = guilded.Embed(
                    description=
                    f"Time over, divorce has been cancelled.",
                    color=color)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                await ctx.channel.send(embed=embed, silent=True)
        else:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"{character_name} either doesn\'t exist or doesn\'t belong to anybody.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)


    @commands.command(name='get-emoteid')
    async def get_emoteid(self, ctx):
        message = await ctx.send("React to this message with an emoji.")
        
        def check(reaction):
            return reaction.user == ctx.author and reaction.message.id == message.id

        try:
            reaction = await self.bot.wait_for('message_reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Timeout. Please try again.")
        else:
            emoji_id = reaction.emoji.id
            await ctx.send(f"The emoji ID is: {emoji_id}")


# Füge die setup-Funktion hinzu
def setup(bot):
    bot.add_cog(Trading(bot))
