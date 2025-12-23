import guilded
from guilded.ext import commands
import json
import random
from pathlib import Path
import time
import asyncio, os
from fuzzywuzzy import process
import re
import checksfrfr
from gil_utility.gperms import *


class Skidae(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = self.load_characters()

    def load_characters(self):
        with open('anilist_characters.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_server_data(self, guild_id):
        server_file = Path(f'skidaetabase/{guild_id}.json')
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                server_data = json.load(f)
        else:
        # Erstelle eine neue JSON-Datei, wenn keine existiert
            server_data = {"claimed_characters": [], "cooldowns": {"rolldowns": {}, "claimdowns": {}}, "wishes": {}, "last_reset": -1}
            self.save_server_data(guild_id, server_data)
        if self.reset_cooldowns(server_data):
            self.save_server_data(guild_id, server_data)
        return server_data

  
    def save_server_data(self, guild_id, data):
    # Stelle sicher, dass der Ordner existiert
        folder_path = Path('skidaetabase')
        folder_path.mkdir(parents=True, exist_ok=True)
    
    # Speichere die JSON-Datei im Ordner
        with open(folder_path / f'{guild_id}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    def reset_cooldowns(self, server_data):
        current_time = time.time()
        current_hour = int(current_time // 3600)
        if server_data.get('last_reset', -1) != current_hour:
            server_data['cooldowns'] = {"rolldowns": {}, "claimdowns": {}}
            server_data['last_reset'] = current_hour
            return True
        return False

    def get_unclaimed_characters(self, server_data, gender=None):
        claimed_names = {char['name'] for char in server_data['claimed_characters']}
        if gender:
            return [char for char in self.characters if char['name'] not in claimed_names and char['gender'] == gender]
        return [char for char in self.characters if char['name'] not in claimed_names]


    def can_claim(self, user_id, server_data):
        self.reset_cooldowns(server_data)
        cooldowns = server_data.get('cooldowns', {})
        claimdowns = cooldowns.get('claimdowns', {})
        user_cooldowns = claimdowns.get(str(user_id), [])

        return len(user_cooldowns) < self.limit_check(server_data, "custom_claims_per_hour")#< 2
  
    def can_roll(self, user_id, server_data):
        self.reset_cooldowns(server_data)
        cooldowns = server_data.get('cooldowns', {})
        rolldowns = cooldowns.get('rolldowns', {})
        user_cooldowns = rolldowns.get(str(user_id), [])

        return len(user_cooldowns) < self.limit_check(server_data, "custom_rolls") #< 7

    def add_claimdown(self, user_id, server_data, guild_id):
        #cooldowns = server_data.get('cooldowns', {})
        claimdowns = server_data['cooldowns']["claimdowns"]#cooldowns.get('claimdowns', {})
        if str(user_id) not in claimdowns:
            claimdowns[str(user_id)] = []
        claimdowns[str(user_id)].append(time.time())

        server_data['cooldowns']["claimdowns"] = claimdowns
        self.save_server_data(guild_id, server_data)
        
    def add_rolldown(self, user_id, server_data, guild_id):
        #cooldowns = server_data.get('cooldowns', {})
        rolldowns = server_data['cooldowns']["rolldowns"]# cooldowns.get('rolldowns')
        #try:
         # print(rolldowns[str(user_id)])
       # except Exception as e:
        #  print(e)
         # print(rolldowns)
        if str(user_id) not in rolldowns:
           # print("new")
            rolldowns[str(user_id)] = []
        rolldowns[str(user_id)].append(time.time())

        server_data['cooldowns']["rolldowns"] = rolldowns
        self.save_server_data(guild_id, server_data)

    def add_or_update_custom(self, data, key, value):
        if key not in data:
            data[key] = value
        else:
            if key in ["custom_claims_total", "custom_wishlist"] and value == 10 or key == "custom_rolls" and value == 7 or key == "custom_claims_per_hour" and value == 2:
                del data[key]
            else:
                data[key] = value
        return data
    def limit_check(self, data, key):
        if key not in data:
            if key in ["custom_claims_total", "custom_wishlist"]:
                return 10
            elif key == "custom_rolls":
                return 7
            elif key == "custom_claims_per_hour":
                return 2
        else:
            return data[key]

    @commands.command(name='customize', help='Customize skidae limits.')
    async def customize(self, ctx, argument=None, new_amount=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        if not (await manage_guild(ctx)):
            return
        arguments_list = {
            "claims_per_hour": "custom_claims_per_hour",
            "total_claims": "custom_claims_total",
            "wishlist": "custom_wishlist",
            "rolls": "custom_rolls"
        }
        server_data = self.load_server_data(ctx.guild.id)

        # Check if the argument is in arguments_list
        if argument not in arguments_list:
            accepted_keys = ', '.join(arguments_list.keys())
            embed = guilded.Embed(
                title="Error",
                description=f"Invalid argument. Accepted arguments are: {accepted_keys}. Example: `.customize claims_per_hour 5`",
                color=guilded.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the new amount is an integer
        try:
            new_amount = int(new_amount)
        except ValueError:
            embed = guilded.Embed(
                title="Error",
                description=f"Invalid amount. Please enter an integer. Example: `.customize {argument} 5`",
                color=guilded.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the new amount is greater than or equal to 1
        if new_amount < 1:
            embed = guilded.Embed(
                title="Error",
                description=f"The amount must be greater than or equal to 1. Example: `.customize {argument} 5`",
                color=guilded.Color.red()
            )
            await ctx.send(embed=embed)
            return
        old_amount = self.limit_check(server_data, arguments_list[argument])
        new_server_data = self.add_or_update_custom(server_data, arguments_list[argument], new_amount)
        self.save_server_data(ctx.guild.id, new_server_data)
        if argument == "claims_per_hour":
            description = f"You can now claim up to {new_amount} characters per hour."
        elif argument == "total_claims":
            description = f"You can now collect up to {new_amount} characters."
        elif argument == "wishlist":
            description = f"You can now wish up to {new_amount} characters."
        elif argument == "rolls":
            description = f"You can now roll up to {new_amount} characters."
        description += f"\nPreviously {old_amount}."
        embed = guilded.Embed(title=f"{argument.replace('_', ' ').capitalize()} has been modified",
                              description=description, color=guilded.Color.green() if old_amount < new_amount else guilded.Color.red())
        await ctx.send(embed=embed)


        




    @commands.command(name='character', help='Zeigt Informationen über einen Charakter an.')
    async def character(self, ctx, *, character_name: str):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        character = next((c for c in self.characters if c['name'].lower() == character_name.lower()), None)
        server_data = self.load_server_data(ctx.guild.id)
        claimed_characters = {char['name']: char['owner'] for char in server_data['claimed_characters']}
        server_character = next((char for char in server_data['claimed_characters'] if char['name'].lower() == character_name.lower()), None)

        if character:
            embed = guilded.Embed(title=character['name'], color=guilded.Color.blue())
            embed.add_field(name='Gender', value=character['gender'])
            embed.add_field(name='Anime', value=character['anime'])
            embed.add_field(name='Popularity', value=character['popularity'])
            try:
                if server_character is not None and 'custom_image' in server_character:
                  embed.set_image(url=server_character['custom_image'])
                else:
                  embed.set_image(url=character['image'])
            except:
              embed.set_image(url=character['image'])
            embed.add_field(name='More information', value=f"[Click here]({character['character_url']})")

            if character['name'] in claimed_characters:
                owner = claimed_characters[character['name']]
                embed.add_field(name='Status', value=f"Married to <@{owner}>", inline=False)

            await ctx.send(embed=embed, silent=True)
        else:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Character '{character_name}' not found.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name='list-characters', help='Listet alle gespeicherten Charaktere auf. Optional: Anime-Name, Geschlecht und/oder Seitenzahl.')
    async def list_characters(self, ctx, *args):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        anime_name = None
        gender = None
        page = 1

        args_list = list(args)
        for arg in args_list:
            if arg.lower() in ['male', 'female']:
                gender = 'Male' if arg.lower() == 'male' else 'Female'
                args_list.remove(arg)
            elif arg.isdigit():
                page = int(arg)
                args_list.remove(arg)
    
        anime_name = " ".join(args_list) if args_list else None

        characters = self.characters

        if anime_name:
            characters = [char for char in characters if char['anime'].lower() == anime_name.lower()]

        if gender:
            characters = [char for char in characters if char['gender'] == gender]

        characters_per_page = 10
        total_pages = (len(characters) + characters_per_page - 1) // characters_per_page

        if page < 1 or page > total_pages:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Page {page} doesn\'t exist. Please choose a page between 1 and {total_pages}.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        start = (page - 1) * characters_per_page
        end = start + characters_per_page
        n_characters = characters[start:end]

        server_data = self.load_server_data(ctx.guild.id)
        claimed_names = {char['name']: char['owner'] for char in server_data['claimed_characters']}

        embed = guilded.Embed(title=f"Character list - Page {page}/{total_pages}", color=guilded.Color.blue())
        for character in n_characters:
            gender_emoji = '♂️' if character['gender'] == 'Male' else '♀️'
            claimed_emoji = ' 💖' if character['name'] in claimed_names else ''
            embed.add_field(name=f"{character['name']} {gender_emoji}{claimed_emoji}",
                            value=f"Anime: {character['anime']} - Popularity: {character['popularity']}", inline=False)

        message = await ctx.send(embed=embed)

        if total_pages > 1:
            await message.add_reaction('90002097')
            await message.add_reaction('90002093')

            def check(reaction):
                return reaction.user.id == ctx.author.id and str(reaction.emoji.id) in ['90002097', '90002093']

            while True:
                try:
                    reaction= await self.bot.wait_for('message_reaction_add', timeout=60.0, check=check)
                    if str(reaction.emoji.id) == '90002093' and page < total_pages:
                        page += 1
                    elif str(reaction.emoji.id) == '90002093' and page >= total_pages:
                      page = 1
                    elif str(reaction.emoji.id) == '90002097' and page > 1:
                        page -= 1
                    elif str(reaction.emoji.id) == '90002097' and page <= 1:
                      page = total_pages
                    else:
                        continue
                      
                    start = (page - 1) * characters_per_page
                    end = start + characters_per_page
                    n_characters = characters[start:end]
                    

                  

                    embed = guilded.Embed(title=f"Character list - Page {page}/{total_pages}", color=guilded.Color.blue())
                    for character in n_characters:
                        gender_emoji = '♂️' if character['gender'] == 'Male' else '♀️'
                        claimed_emoji = ' 💖' if character['name'] in claimed_names else ''
                        embed.add_field(name=f"{character['name']} {gender_emoji}{claimed_emoji}",
                            value=f"Anime: {character['anime']} - Popularity: {character['popularity']}", inline=False)

                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction.emoji, ctx.author)
                except asyncio.TimeoutError:
                    break


    @commands.command(name='search-character', help='Sucht nach einem Charakter.')
    async def search_character(self, ctx, *, character_name: str):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        characters = self.characters
        server_data = self.load_server_data(ctx.guild.id)
        claimed_names = {char['name']: char['owner'] for char in server_data['claimed_characters']}

    # Use fuzzy matching to find close matches
        matched_characters = process.extract(character_name.lower(), [char['name'].lower() for char in characters], limit=10)
        matched_characters = [char for char, score in matched_characters if score > 60]

        if not matched_characters:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"No characters found that are similar to '{character_name}'.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        def format_character_list(matched_characters):
            embed = guilded.Embed(title="Found characters", color=guilded.Color.blue())
            for idx, char_name in enumerate(matched_characters, 1):
                character = next((c for c in characters if c['name'].lower() == char_name), None)
                gender_emoji = '♂️' if character['gender'] == 'Male' else '♀️'
                claimed_emoji = ' 💖' if character['name'] in claimed_names else ''
                embed.add_field(name=f"{idx}. {character['name']} {gender_emoji}{claimed_emoji}",
                                value=f"Anime: {character['anime']} - Popularity: {character['popularity']}", inline=False)
            return embed

        # message = await ctx.send(embed=format_character_list(matched_characters))
        await ctx.send(embed=format_character_list(matched_characters), silent = True)

        def check(m):
            return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= len(matched_characters)

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            selected_char_idx = int(response.content) - 1
            selected_char_name = matched_characters[selected_char_idx]
            character = next((c for c in characters if c['name'].lower() == selected_char_name), None)
            server_character = next((char for char in server_data['claimed_characters'] if char['name'].lower() == selected_char_name.lower()), None)

            if character:
                embed = guilded.Embed(title=character['name'], color=guilded.Color.blue())
                embed.add_field(name='Gender', value=character['gender'])
                embed.add_field(name='Anime', value=character['anime'])
                embed.add_field(name='Popularity', value=character['popularity'])
                try:
                    if server_character is not None and 'custom_image' in server_character:
                      embed.set_image(url=server_character['custom_image'])
                    else:
                      embed.set_image(url=character['image'])
                except:
                  embed.set_image(url=character['image'])
                embed.add_field(name='More information', value=f"[Click here]({character['character_url']})")

                if character['name'] in claimed_names:
                    owner = claimed_names[character['name']]
                    embed.add_field(name='Status', value=f"Married to <@{owner}>", inline=False)

                await ctx.send(embed=embed, silent=True)
        except asyncio.TimeoutError:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Time\'s over, please try again.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)


    @commands.command(name='search-anime', help='Sucht nach einem Anime und zeigt Charaktere.')
    async def search_anime(self, ctx, *, anime_name: str):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        characters = self.characters
        server_data = self.load_server_data(ctx.guild.id)
        claimed_names = {char['name']: char['owner'] for char in server_data['claimed_characters']}

        # Liste der Animes ohne Duplikate
        anime_list = list({char['anime'] for char in characters})

        # Use fuzzy matching to find close matches
        matched_animes = process.extract(anime_name.lower(), [anime.lower() for anime in anime_list], limit=10)
        matched_animes = [anime for anime, score in matched_animes if score > 60]

        if not matched_animes:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=f"No animes found that are similar to '{anime_name}'.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        embed = guilded.Embed(title="Found Animes", color=guilded.Color.blue())
        for idx, anime in enumerate(matched_animes, 1):
            embed.add_field(name=f"{idx}. {anime.title()}", value="", inline=False)

        await ctx.send(embed=embed, silent=True)

        def check_anime(m):
            return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= len(matched_animes)

        try:
            response = await self.bot.wait_for('message', check=check_anime, timeout=30.0)
            selected_anime_idx = int(response.content) - 1
            selected_anime = matched_animes[selected_anime_idx].title()

            anime_characters = [char for char in characters if char['anime'].lower() == selected_anime.lower()]

            def format_character_list(anime_characters):
                embed = guilded.Embed(title=f"Characters from {selected_anime}", color=guilded.Color.blue())
                description = ""
                for idx, character in enumerate(anime_characters, 1):
                    gender_emoji = '♂️' if character['gender'] == 'Male' else '♀️'
                    claimed_emoji = ' 💖' if character['name'] in claimed_names else ''
                    char_info = f"{idx}. {character['name']} {gender_emoji}{claimed_emoji} - Popularity: {character['popularity']}\n"
                    description += char_info
                embed.description = description
                return embed

            await ctx.send(embed=format_character_list(anime_characters), silent=True)

        except asyncio.TimeoutError:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description="Time's over, please try again.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name='waifu', help='Finde eine zufällige Waifu.')
    async def waifu(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        server_data = self.load_server_data(ctx.guild.id)
        if not self.can_roll(ctx.author.id, server_data):
          color = guilded.Color.from_rgb(239, 83, 80)
          embed = guilded.Embed(
                description=
                f"You have already rolled {self.limit_check(server_data, 'custom_rolls')} characters, come back at the next hour.",
                color=color)
          embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
          return await ctx.channel.send(embed=embed, silent=True)
        self.add_rolldown(ctx.author.id, server_data, ctx.server.id)
          

        wishlist = server_data.get('wishes', {}).get(str(ctx.author.id), [])
        wishlist_names = [wish['name'] for wish in wishlist]
        unclaimed_waifus = self.get_unclaimed_characters(server_data, gender='Female')
    
    # Filter the unclaimed waifus based on the wishlist
        enhanced_pool = unclaimed_waifus + [char for char in unclaimed_waifus if char['name'] in wishlist_names] * 10
        waifu = random.choice(enhanced_pool)
    
        embed = guilded.Embed(title=f"{waifu['name']}", color=guilded.Color.purple())
        embed.add_field(name='Anime', value=waifu['anime'])
        embed.add_field(name='Popularity', value=waifu['popularity'])
        embed.set_image(url=waifu['image'])
        embed.add_field(name='More information', value=f"[Click here]({waifu['character_url']})")

        wishers = [user_id for user_id, wishes in server_data.get('wishes', {}).items() if any(wish['name'] == waifu['name'] for wish in wishes)]
        if wishers:
            mentions = " ".join([f"<@{wisher}>" for wisher in wishers])
            embed.add_field(name="Wished by", value=mentions, inline=False)

        message = await ctx.send(embed=embed, silent=False)
        async def reaction_cycle(message, repeat):
            try:
                await message.add_reaction('90001288')
            except Exception as e:
                print(e)
                await asyncio.sleep(0.05)
                repeat += 1
                if repeat <= 10:
                    await reaction_cycle(message, repeat)
                else:
                    return await message.channel.send("Failed to add reaction.\nPlease react manually if you wish to marry the Waifu...")
            return None
        await reaction_cycle(message, repeat=0)

        def check(reaction):
            return str(reaction.emoji.id) == '90001288' and reaction.user.id != self.bot.user.id and reaction.message.id == message.id

        while True:
            try:
                reaction = await self.bot.wait_for('message_reaction_add', timeout=60.0, check=check)
                server_data = self.load_server_data(ctx.guild.id)
                user = reaction.user
                user_claims = len([char for char in server_data['claimed_characters'] if char['owner'] == user.id])
                if user_claims >= self.limit_check(server_data, "custom_claims_total"):
                    color = guilded.Color.from_rgb(239, 83, 80)
                    mbed = guilded.Embed(
                        description=
                        f"{user.name}, you have already hit the limit of {self.limit_check(server_data, 'custom_claims_total')} total characters.",
                        color=color)
                    mbed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=mbed, silent=True)
                    await message.remove_reaction(reaction.emoji, user)
                    continue

                if not self.can_claim(user.id, server_data):
                    color = guilded.Color.from_rgb(239, 83, 80)
                    mbed = guilded.Embed(
                        description=
                        f"{user.name}, you have already hit the limit of {self.limit_check(server_data, 'custom_claims_per_hour')} Waifus per hour.",
                        color=color)
                    mbed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=mbed, silent=True)
                    await message.remove_reaction(reaction.emoji, user)
                    continue

                server_data['claimed_characters'].append({"name": waifu['name'], "owner": user.id})
                self.add_claimdown(user.id, server_data, ctx.server.id)
                self.save_server_data(ctx.guild.id, server_data)

                embed.title = f"{user.name}'s new Waifu: {waifu['name']}"
                if user != ctx.author:
                    embed.add_field(name='Status', value=f"{user.name} stole {ctx.author.name}\'s Waifu!", inline=False)
                await message.edit(embed=embed)
                break
            except asyncio.TimeoutError:
                break

    @commands.command(name='husbando', help='Finde einen zufälligen Husbando.')
    async def husbando(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        server_data = self.load_server_data(ctx.guild.id)
        if not self.can_roll(ctx.author.id, server_data):
          color = guilded.Color.from_rgb(239, 83, 80)
          embed = guilded.Embed(
                description=
                f"You have already rolled {self.limit_check(server_data, 'custom_rolls')} characters, come back at the next hour.",
                color=color)
          embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
          return await ctx.channel.send(embed=embed, silent=True)
        self.add_rolldown(ctx.author.id, server_data, ctx.server.id)

        wishlist = server_data.get('wishes', {}).get(str(ctx.author.id), [])
        wishlist_names = [wish['name'] for wish in wishlist]
        unclaimed_husbandos = self.get_unclaimed_characters(server_data, gender='Male')
    
    # Filter the unclaimed husbandos based on the wishlist
        enhanced_pool = unclaimed_husbandos + [char for char in unclaimed_husbandos if char['name'] in wishlist_names] * 10
        husbando = random.choice(enhanced_pool)
    
        embed = guilded.Embed(title=f"{husbando['name']}", color=guilded.Color.green())
        embed.add_field(name='Anime', value=husbando['anime'])
        embed.add_field(name='Popularity', value=husbando['popularity'])
        embed.set_image(url=husbando['image'])
        embed.add_field(name='More information', value=f"[Click here]({husbando['character_url']})")

        wishers = [user_id for user_id, wishes in server_data.get('wishes', {}).items() if any(wish['name'] == husbando['name'] for wish in wishes)]
        if wishers:
            mentions = " ".join([f"<@{wisher}>" for wisher in wishers])
            embed.add_field(name="Wished by", value=mentions, inline=False)

        message = await ctx.send(embed=embed, silent=False)

        async def reaction_cycle(message, repeat):
            try:
                await message.add_reaction('90001288')
            except Exception as e:
                print(e)
                await asyncio.sleep(0.05)
                repeat += 1
                if repeat <= 10:
                    await reaction_cycle(message, repeat)
                else:
                    return await message.channel.send(
                        "Failed to add reaction.\nPlease react manually if you wish to marry the Husbando...")
            return None

        await reaction_cycle(message, repeat=0)

        def check(reaction):
            return str(reaction.emoji.id) == '90001288' and reaction.user.id != self.bot.user.id and reaction.message.id == message.id

        while True:
            try:
                reaction = await self.bot.wait_for('message_reaction_add', timeout=60.0, check=check)
                server_data = self.load_server_data(ctx.guild.id)
                user = reaction.user
            
                user_claims = len([char for char in server_data['claimed_characters'] if char['owner'] == user.id])
                if user_claims >= self.limit_check(server_data, "custom_claims_total"):
                    color = guilded.Color.from_rgb(239, 83, 80)
                    mbed = guilded.Embed(
                        description=
                        f"{user.name}, you have already hit the limit of {self.limit_check(server_data, 'custom_claims_total')} total characters.",
                        color=color)
                    mbed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=mbed, silent=True)
                    await message.remove_reaction(reaction.emoji, user)
                    continue

                if not self.can_claim(user.id, server_data):
                    color = guilded.Color.from_rgb(239, 83, 80)
                    mbed = guilded.Embed(
                        description=
                        f"{user.name}, you have already hit the limit of {self.limit_check(server_data, 'custom_claims_per_hour')} Husbandos per hour.",
                        color=color)
                    mbed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=mbed, silent=True)
                    await message.remove_reaction(reaction.emoji, user)
                    continue

                server_data['claimed_characters'].append({"name": husbando['name'], "owner": user.id})
                self.add_claimdown(user.id, server_data, ctx.server.id)
                self.save_server_data(ctx.guild.id, server_data)

                embed.title = f"{user.name}'s new Husbando: {husbando['name']}"
                if user != ctx.author:
                    embed.add_field(name='Status', value=f"{user.name} stole {ctx.author.name}\'s Husbando!", inline=False)
                await message.edit(embed=embed)
                break
            except asyncio.TimeoutError:
                break


            
    @commands.command(name='wishlist', help='Zeigt die Wunschliste an.')
    async def wishlist(self, ctx):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
            return
      server_data = self.load_server_data(ctx.guild.id)
      user_wishes = server_data.get('wishes', {}).get(str(ctx.author.id), [])

      if not user_wishes:
          color = guilded.Color.from_rgb(239, 83, 80)
          embed = guilded.Embed(
              description=
              f"Your wishlist is empty.",
              color=color)
          embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
          await ctx.channel.send(embed=embed, silent=True)
          return

      claimed_names = {char['name']: char['owner'] for char in server_data['claimed_characters']}

      embed = guilded.Embed(title=f"{ctx.author.name}'s wishlist", color=guilded.Color.blue())
      for wish in user_wishes:
        character = next((c for c in self.characters if c['name'].lower() == wish['name'].lower()), None)
        if character:
            gender_emoji = '♂️' if character['gender'] == 'Male' else '♀️'
            claimed_emoji = ' 💖' if character['name'] in claimed_names else ''
            embed.add_field(name=f"{character['name']} {gender_emoji}{claimed_emoji}", value="")
            
    

      await ctx.send(embed=embed)
      
  
    @commands.command(name='wish', help='Wünscht sich einen Charakter.')
    async def wish(self, ctx, *, character_name: str):
      check = await checksfrfr.enabled(ctx, ctx.command.name)
      if not check:
            return
      server_data = self.load_server_data(ctx.guild.id)
      user_wishes = server_data.get('wishes', {}).get(str(ctx.author.id), [])

      if len(user_wishes) >= self.limit_check(server_data, 'custom_wishlist'):
          color = guilded.Color.from_rgb(239, 83, 80)
          embed = guilded.Embed(
              description=
              f"You have already hit the limit of {self.limit_check(server_data, 'custom_wishlist')} total wishes.",
              color=color)
          embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
          await ctx.channel.send(embed=embed, silent=True)
          return

      character = next((c for c in self.characters if c['name'].lower() == character_name.lower()), None)
      if character:
        if character['name'] in [wish['name'] for wish in user_wishes]:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"{character['name']} is already on your list.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        user_wishes.append({"name": character['name']})
        server_data.setdefault('wishes', {}).update({str(ctx.author.id): user_wishes})
        self.save_server_data(ctx.guild.id, server_data)

        color = guilded.Color.green()
        embed = guilded.Embed(
            description=
            f"{character['name']} has been added to your wishlist.",
            color=color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)

      else:
          color = guilded.Color.from_rgb(239, 83, 80)
          embed = guilded.Embed(
              description=
              f"Character '{character_name}' not found.",
              color=color)
          embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
          await ctx.channel.send(embed=embed, silent=True)


    @commands.command(name='unwish', help='Entfernt einen Charakter von der Wunschliste.')
    async def unwish(self, ctx, *, character_name: str):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        server_data = self.load_server_data(ctx.guild.id)
        user_wishes = server_data.get('wishes', {}).get(str(ctx.author.id), [])

        character = next((wish for wish in user_wishes if wish['name'].lower() == character_name.lower()), None)
        if not character:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"{character_name} is not on your list.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        user_wishes.remove(character)
        server_data['wishes'][str(ctx.author.id)] = user_wishes
        self.save_server_data(ctx.guild.id, server_data)

        color = guilded.Color.green()
        embed = guilded.Embed(
            description=
            f"{character['name']} has been removed from your wishlist.",
            color=color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed, silent=True)

    @commands.command(name='top_claimed_characters', help='Zeigt die beliebtesten geclaimten Charaktere an.', aliases = ["tcc"])
    async def top_claimed_characters(self, ctx, *args):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        gender = None
        page = 1

        for arg in args:
            if arg.lower() in ['male', 'female']:
                gender = arg.lower()
            elif arg.isdigit():
                page = int(arg)

        limit = 10  # Fester Wert

        server_data = self.load_server_data(ctx.guild.id)
        claimed_chars = [char for char in self.characters if char['name'] in {c['name'] for c in server_data['claimed_characters']}]

        if gender:
            claimed_chars = [char for char in claimed_chars if char['gender'].lower() == gender]

        top_claimed = sorted(claimed_chars, key=lambda x: x['popularity'], reverse=True)

        total_pages = (len(top_claimed) + limit - 1) // limit
        if page < 1 or page > total_pages:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Page {page} doesn\'t exist. Please choose a page between 1 and {total_pages}.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        start = (page - 1) * limit
        end = start + limit
        top_claimed_page = top_claimed[start:end]

        embed = guilded.Embed(title=f"Top {limit} claimed characters - Page {page}/{total_pages}", color=guilded.Color.blue())
        for char in top_claimed_page:
            gender_emoji = '♂️' if char['gender'] == 'Male' else '♀️'
            owner = next((c['owner'] for c in server_data['claimed_characters'] if c['name'] == char['name']), 'Unknown')
            embed.add_field(name=f"{char['name']} {gender_emoji} 💖", value=f"Anime: {char['anime']} - Popularity: {char['popularity']} - Claimed by: <@{owner}>", inline=False)
        message = await ctx.send(embed=embed, silent=True)

        if total_pages > 1:
            await message.add_reaction('90002097')
            await message.add_reaction('90002093')

            def check(reaction):
                return reaction.user.id == ctx.author.id and str(reaction.emoji.id) in ['90002097', '90002093']

            while True:
                try:
                    reaction = await self.bot.wait_for('message_reaction_add', timeout=60.0, check=check)
                    user = reaction.user
                    if str(reaction.emoji.id) == '90002093' and page < total_pages:
                        page += 1
                    elif str(reaction.emoji.id) == '90002093' and page >= total_pages:
                      page = 1
                    elif str(reaction.emoji.id) == '90002097' and page > 1:
                        page -= 1
                    elif str(reaction.emoji.id) == '90002097' and page <= 1:
                      page = total_pages
                    else:
                        continue
                    

                    start = (page - 1) * limit
                    end = start + limit
                    top_claimed_page = top_claimed[start:end]

                    embed = guilded.Embed(title=f"Top {limit} claimed characters - Page {page}/{total_pages}", color=guilded.Color.blue())
                    for char in top_claimed_page:
                        gender_emoji = '♂️' if char['gender'] == 'Male' else '♀️'
                        owner = next((c['owner'] for c in server_data['claimed_characters'] if c['name'] == char['name']), 'Unknown')
                        embed.add_field(name=f"{char['name']} {gender_emoji} 💖", value=f"Anime: {char['anime']} - Popularity: {char['popularity']} - Claimed by: <@{owner}>", inline=False)

                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction.emoji, ctx.author)
                except asyncio.TimeoutError:
                    break
    @commands.command(name='top_unclaimed_characters', help='Zeigt die beliebtesten nicht geclaimten Charaktere an.', aliases = ["tuc"])
    async def top_unclaimed_characters(self, ctx, *args):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        gender = None
        page = 1

        for arg in args:
            if arg.lower() in ['male', 'female']:
                gender = arg.lower()
            elif arg.isdigit():
                page = int(arg)

        limit = 10  # Fester Wert

        server_data = self.load_server_data(ctx.guild.id)
        claimed_names = {c['name'] for c in server_data['claimed_characters']}
        unclaimed_chars = [char for char in self.characters if char['name'] not in claimed_names]

        if gender:
            unclaimed_chars = [char for char in unclaimed_chars if char['gender'].lower() == gender]

        top_unclaimed = sorted(unclaimed_chars, key=lambda x: x['popularity'], reverse=True)

        total_pages = (len(top_unclaimed) + limit - 1) // limit
        if page < 1 or page > total_pages:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"Page {page} doesn\'t exist. Please choose a page between 1 and {total_pages}.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)
            return

        start = (page - 1) * limit
        end = start + limit
        top_unclaimed_page = top_unclaimed[start:end]

        embed = guilded.Embed(title=f"Top {limit} unclaimed characters - Page {page}/{total_pages}", color=guilded.Color.blue())
        for char in top_unclaimed_page:
            gender_emoji = '♂️' if char['gender'] == 'Male' else '♀️'
            embed.add_field(name=f"{char['name']} {gender_emoji}", value=f"Anime: {char['anime']} - Popularity: {char['popularity']}", inline=False)
        message = await ctx.send(embed=embed)

        if total_pages > 1:
            await message.add_reaction('90002097')
            await message.add_reaction('90002093')

            def check(reaction):
                return reaction.user.id == ctx.author.id and str(reaction.emoji.id) in ['90002097', '90002093']

            while True:
                try:
                    reaction = await self.bot.wait_for('message_reaction_add', timeout=60.0, check=check)
                    user = reaction.user
                    if str(reaction.emoji.id) == '90002093' and page < total_pages:
                        page += 1
                    elif str(reaction.emoji.id) == '90002093' and page >= total_pages:
                      page = 1
                    elif str(reaction.emoji.id) == '90002097' and page > 1:
                        page -= 1
                    elif str(reaction.emoji.id) == '90002097' and page <= 1:
                      page = total_pages
                    else:
                        continue

                    start = (page - 1) * limit
                    end = start + limit
                    top_unclaimed_page = top_unclaimed[start:end]

                    embed = guilded.Embed(title=f"Top {limit} unclaimed characters - Page {page}/{total_pages}", color=guilded.Color.blue())
                    for char in top_unclaimed_page:
                        gender_emoji = '♂️' if char['gender'] == 'Male' else '♀️'
                        embed.add_field(name=f"{char['name']} {gender_emoji}", value=f"Anime: {char['anime']} - Popularity: {char['popularity']}", inline=False)

                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction.emoji, ctx.author)
                except asyncio.TimeoutError:
                    break
    @commands.command(name='stats', help='Zeigt die Wunschliste und alle Charaktere eines markierten Nutzers an oder, falls keiner markiert ist, dein eigenes Profil.')
    async def stats(self, ctx,*, user = None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        member = ctx.author if not user else user
        if user:
            member = await find_member_named(ctx.guild, user, ctx)
            if not member:
                await user_not_found(ctx, user)
                return
        user = member

        server_data = self.load_server_data(ctx.guild.id)
        claimed_names = {c['name'] for c in server_data['claimed_characters']}
        user_wishes = server_data.get('wishes', {}).get(str(user.id), [])
        user_claims = [char for char in server_data['claimed_characters'] if char['owner'] == user.id]
        
        embed = guilded.Embed(title=f"Stats for {user.name}", color=guilded.Color.blue())
        
        # Wunschliste hinzufügen
        if user_wishes:
          wishlist_str = "**Wishlist:**\n"
          count = 0
          for wish in user_wishes:
            count += 1
            character = next((c for c in self.characters if c['name'].lower() == wish['name'].lower()), None)
            if character:
                gender_emoji = '♂️' if character['gender'] == 'Male' else '♀️'
                claimed_emoji = ' 💖' if character['name'] in claimed_names else ''
                wishlist_str += f"{count}. {character['name']} {gender_emoji}{claimed_emoji}\n"
            
          wishlist_str += "\n"
        else:
                wishlist_str ="No characters on wishlist.\n\n"
        
        # Geclaimte Charaktere hinzufügen
        
        if user_claims:
          claimlist_str = "**Claimed Characters:**\n"
          count = 0
          for claim in user_claims:
            count += 1
            character = next((c for c in self.characters if c['name'].lower() == claim['name'].lower()), None)
            if character:
                gender_emoji = '♂️' if character['gender'] == 'Male' else '♀️'
                claimed_emoji = ' 💖' if character['name'] in claimed_names else ''
                claimlist_str += f"{count}. {character['name']} {gender_emoji}{claimed_emoji}\n"
          claimlist_str += "\n"
            
        else:
                claimlist_str ="No characters claimed."
                
        embed.description = wishlist_str + claimlist_str
        
        await ctx.send(embed=embed)





    @commands.command(name='custom-image', help='Assign a custom image to one of your characters.')
    async def custom_image(self, ctx, *, character_name_and_url: str):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        try:
            # Separate the character name and the URL
            character_name, image_url = character_name_and_url.rsplit(' ', 1)
        except ValueError:
            await ctx.send(embed=guilded.Embed(description="Please provide both a character name and a valid image URL.", color=guilded.Color.red()))
            return
        
        # Check the URL
        if not re.match(r'^https?://.*\.(webp|png|jpg|jpeg|gif)$', image_url, re.IGNORECASE):
            await ctx.send(embed=guilded.Embed(description="The URL must end with .webp, .png, .jpg, .jpeg, or .gif.", color=guilded.Color.red()))
            return
        
        server_data = self.load_server_data(ctx.guild.id)
        user_id = str(ctx.author.id)
        character = next((char for char in server_data['claimed_characters'] if char['owner'] == user_id and char['name'].lower() == character_name.lower()), None)
        
        if character is None:
            await ctx.send(embed=guilded.Embed(description=f"Character '{character_name}' not found or does not belong to you.", color=guilded.Color.red()))
            return

        character['custom_image'] = image_url
        self.save_server_data(ctx.guild.id, server_data)
        embed = guilded.Embed(description=f"Custom image for {character_name} has been successfully updated!", color=guilded.Color.green())
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

    @commands.command(name='rem-custom-image', help='Remove a custom image from one of your characters.')
    async def remove_custom_image(self, ctx, *, character_name: str):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        server_data = self.load_server_data(ctx.guild.id)
        user_id = str(ctx.author.id)
        character = next((char for char in server_data['claimed_characters'] if char['owner'] == user_id and char['name'].lower() == character_name.lower()), None)

        if character is None:
            await ctx.send(embed=guilded.Embed(description=f"Character '{character_name}' not found or does not belong to you.", color=guilded.Color.red()))
            return

        if 'custom_image' in character:
            del character['custom_image']
            self.save_server_data(ctx.guild.id, server_data)
            await ctx.send(embed=guilded.Embed(description=f"Custom image for {character_name} has been successfully removed!", color=guilded.Color.green()))
        else:
            await ctx.send(embed=guilded.Embed(description=f"Character '{character_name}' does not have a custom image.", color=guilded.Color.red()))

    @commands.command(name='skidae-stats',
                      help='Zeigt die Wunschliste und alle Charaktere eines markierten Nutzers an oder, falls keiner markiert ist, dein eigenes Profil.')
    async def skidae_stats(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return

        server_data = self.load_server_data(ctx.guild.id)
        claimed_chars = [char for char in self.characters if
                         char['name'] in {c['name'] for c in server_data['claimed_characters']}]

        claimed_female_chars = [ch for ch in claimed_chars if ch['gender'] == "Female"]
        claimed_female_count = len(claimed_female_chars)
        claimed_male_count = len(claimed_chars) - claimed_female_count
        total_chars_in_db = len(self.characters)
        total_female = [female for female in self.characters if female['gender'] == "Female"]
        total_female_chars_in_db = len(total_female)
        total_male_chars_in_db = total_chars_in_db - total_female_chars_in_db
        claimed_count = len(claimed_chars)
        claims_per_hour = self.limit_check(server_data, "custom_claims_per_hour")
        max_claims_user = self.limit_check(server_data, "custom_claims_total")
        wishlist_limit = self.limit_check(server_data, "custom_wishlist")
        rolls = self.limit_check(server_data, "custom_rolls")

        embed = guilded.Embed(title=f"Skidae Stats for {ctx.server.name}", color=guilded.Color.blue())
        embed.add_field(name="Total claimed characters", value=f"{claimed_count} out of {total_chars_in_db}")
        embed.add_field(name="Total female claimed characters", value=f"{claimed_female_count} out of {total_female_chars_in_db}")
        embed.add_field(name="Total male claimed characters",
                        value=f"{claimed_male_count} out of {total_male_chars_in_db}")
        embed.add_field(name="Allowed claims per hour",
                        value=f"{claims_per_hour} characters (each user)")
        embed.add_field(name="Allowed max claims",
                        value=f"{max_claims_user} characters (each user)")
        embed.add_field(name="Max size for wishlist",
                        value=f"{wishlist_limit} characters")
        embed.add_field(name="Max rolls per hour",
                        value=f"{rolls} rolls (each user)")

        await ctx.channel.send(embed=embed)





    @commands.command(name='married', help='Shows a list of your married characters.')
    async def married_list(self, ctx, gender: str = None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        server_data = self.load_server_data(ctx.guild.id)
        user_id = str(ctx.author.id)
        claimed_characters = [char for char in server_data['claimed_characters'] if char['owner'] == user_id]

        if gender:
            claimed_characters = [char for char in claimed_characters if char['gender'].lower() == gender.lower()]

        claimed_characters.sort(key=lambda x: x['name'])

        if len(claimed_characters) == 0:
            await ctx.send(f"No characters found matching your criteria.")
            return

        limit = 1
        total_pages = (len(claimed_characters) + limit - 1) // limit
        page = 1

        def create_embed(page):
            start = (page - 1) * limit
            server_character = claimed_characters[start]
            anilist_character = next((char for char in self.characters if char['name'].lower() == server_character['name'].lower()), None)

            embed = guilded.Embed(
                title=server_character['name'],
                description="",
                color=guilded.Color.blue()
            )

            if anilist_character:
                embed.add_field(name="Gender", value=anilist_character['gender'], inline=False)
                embed.add_field(name="Anime", value=anilist_character['anime'], inline=False)
                embed.add_field(name="Popularity", value=anilist_character['popularity'], inline=False)
                embed.add_field(name="More Information", value=f"[Link]({anilist_character['character_url']})", inline=False)
                try:

                    if 'custom_image' in server_character and server_character['custom_image']:
                        embed.set_image(url=server_character['custom_image'])
                    else:
                        embed.set_image(url=anilist_character['image'])
                except:
                  embed.set_image(url=anilist_character['image'])

            embed.set_footer(text=f"Page {page}/{total_pages}")
            return embed

        embed = create_embed(page)
        message = await ctx.send(embed=embed)

        if total_pages > 1:  
            await message.add_reaction('90002097')
            await message.add_reaction('90002093')

            def check(reaction):
                return reaction.user.id == ctx.author.id and str(reaction.emoji.id) in ['90002097', '90002093']

            while True:
                try:
                    reaction = await self.bot.wait_for('message_reaction_add', timeout=60.0, check=check)

                    if str(reaction.emoji.id) == '90002093' and page < total_pages:
                        page += 1
                    elif str(reaction.emoji.id) == '90002093' and page >= total_pages:
                      page = 1
                    elif str(reaction.emoji.id) == '90002097' and page > 1:
                        page -= 1
                    elif str(reaction.emoji.id) == '90002097' and page <= 1:
                      page = total_pages
                    else:
                        continue

                    embed = create_embed(page)
                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction.emoji, ctx.author)

                except asyncio.TimeoutError:
                    break

    @commands.command(name='clear-db', help='Lässt einen Charakter los.')
    async def force_divorce(self, ctx):
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

        characters = server_data['claimed_characters']

        if len(characters) > 0:
            color = guilded.Color.from_rgb(239, 83, 80)
            info_text = "Are you sure that you remove all the left users from the database?"
            first_embed = guilded.Embed(
                title="Clear Database",
                description=
                "Once the database was purged, you won\'t be able to recover it :(\nType 'yes' oder 'no'.",
                color=color)
            await ctx.channel.send(info_text, embed=first_embed, silent=True)

            # confirm_message = await ctx.send(f"Bist du sicher, dass du dich von {character_name} scheiden lassen möchtest? Antworte mit 'ja' oder 'nein'.")

            def check(message):
                return message.author == ctx.author and message.content.lower() in ['yes', 'no']

            try:
                response = await self.bot.wait_for('message', check=check, timeout=30.0)
                if response.content.lower() == 'yes':
                    await ctx.server.fill_members()
                    memberlist = []
                    for member in ctx.server.members:
                        memberlist.append(member.id)
                    removed_chars = 0
                    for character in characters:
                        if character["owner"] not in memberlist:
                            removed_chars += 1
                            server_data['claimed_characters'].remove(character)
                    self.save_server_data(ctx.guild.id, server_data)
                    color = guilded.Color.from_rgb(239, 83, 80)
                    embed = guilded.Embed(
                        description=
                        f"Force-divorced {removed_chars} character(s) from users who left the server.",
                        color=color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=embed, silent=True)
                else:
                    color = guilded.Color.green()
                    embed = guilded.Embed(
                        description=
                        f"Process has been cancelled.",
                        color=color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await ctx.channel.send(embed=embed, silent=True)
            except asyncio.TimeoutError:
                color = guilded.Color.from_rgb(239, 83, 80)
                embed = guilded.Embed(
                    description=
                    f"Time over, process has been cancelled.",
                    color=color)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                await ctx.channel.send(embed=embed, silent=True)
        else:
            color = guilded.Color.from_rgb(239, 83, 80)
            embed = guilded.Embed(
                description=
                f"There are no characters in the server database.",
                color=color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            await ctx.channel.send(embed=embed, silent=True)

 

    



def setup(bot):
    bot.add_cog(Skidae(bot))
