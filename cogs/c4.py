import sys, subprocess
import guilded
from guilded.ext import commands, tasks
import os
from connect4 import Board
import math
import random
import asyncio
import checksfrfr
from gil_utility.gperms import *

PLAYER_PIECE = 'R'
AI_PIECE = 'Y'
# Prefix to call bot

# Emotes used for the player to choose their move
EMOTES = {'90002199': 0, '90002200': 1, '90002201': 2, '90002202': 3, '90002203': 4, '90002204': 5, '90002205': 6,
          '90002275': 'F'}
# numbers to print above connect 4 board
TOP_NUM = '** **\n:one: :two: :three: :four: :five: :six: :seven: \n'
# dictionary to keep track of where the game is happening
IDS = {}
# what index stands for what in IDS
BRD, P1, P2, CURR_P, TIMER, CHAN = 0, 1, 2, 3, 4, 5
# to differentiate between both players
P_DICT = {True: [P1, 'R', guilded.Colour.red()],
          False: [P2, 'Y', guilded.Colour.gold()]}
# list of gifs to send when a player wins
GIFS = []
gif_file = open("./images/win_gifs.txt", "r")
content = gif_file.readline()
while content != '':
    content = gif_file.readline()
    GIFS.append(content)


class ConnectFour(commands.Cog):
    def __init__(self, client):
        self.client = client

    @tasks.loop(seconds=60)
    async def afk(self):
        remove = []
        for key in IDS:
            if IDS[key][TIMER] == 5:
                channel = IDS[key][CHAN]
                await channel.send(f'{IDS[key][P1].name} :crossed_swords:'
                                   f' {IDS[key][P2].name}: '
                                   f'The game has been cancelled due to inactivity')
                remove.append(key)
            else:
                IDS[key][TIMER] += 1
        for key in remove:
            del IDS[key]

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

    def cpu_minimax_move(self, board):
        """CPU minimax calculation - runs in thread to avoid blocking"""
        col, minimax_score = board.minimax(6, -math.inf, math.inf, True)
        return col

    @commands.command(name="4play", aliases=["4-play", "connect4", "connect-four"])
    async def _play(self, ctx, *, rival=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        """Starts a game with either a mentioned user or the bot and then
        adds it to IDS with message id as key, and a list with the board,
        player ids, and first move as the values"""

        # Check if user wants to play against bot
        if rival is None or rival.lower() in ["bot", "cpu", "computer", "ai", ""] or rival in ["4ZRw5qp4", "<@4ZRw5qp4>"]:
            player2 = self.client.user
            player1 = ctx.author
        else:
            enemy = await find_member_named(ctx.server, rival, ctx)
            if enemy is None:
                await ctx.send(embed=guilded.Embed(
                    description=':x: ERROR: You have to specify your opponent, please mention a valid User or type "bot" to play against me',
                    color=guilded.Colour.dark_theme_embed()))
                return
            elif enemy.bot and enemy.id != self.client.user.id:
                await ctx.send(embed=guilded.Embed(
                    description=':x: ERROR: You cannot choose other bots as a rival. Don\'t give extra parameters if you want to play against me, or mention a valid user',
                    color=guilded.Colour.dark_theme_embed()))
                return
            elif enemy == ctx.author:
                await ctx.send(embed=guilded.Embed(
                    description=':x: ERROR: You\'re not allowed to be your own opponent, please mention a valid User or type "bot" to play against me',
                    color=guilded.Colour.dark_theme_embed()))
                return
            else:
                player2 = enemy

        player1 = ctx.author

        # If playing against bot, skip confirmation
        if player2 == self.client.user:
            await ctx.channel.send(embed=guilded.Embed(
                description=f"{player1.mention}, you're about to play Connect Four against me! Good luck! :robot_face:",
                color=guilded.Color.dark_theme_embed()), silent=True)
        else:
            # Ask for confirmation from human player
            await ctx.channel.send(embed=guilded.Embed(
                description=f"{player2.mention}, would you like to play connect four against {ctx.author}?\nType yes to start a round",
                color=guilded.Color.dark_theme_embed()))
            try:
                answer = await self.client.wait_for("message", timeout=30, check=lambda
                    response: response.author == player2 and response.channel == ctx.channel)
            except asyncio.TimeoutError:
                return await ctx.channel.send(f"{player2} did not join the game")
            accepted = False
            yeslist = ["yes", "yeah", "ok", "accept", "okay"]
            for yes in yeslist:
                if str(answer.content).lower().startswith(yes):
                    accepted = True
            if not accepted:
                return await ctx.channel.send(f"{player2} did not accept the join request")

        board = Board()
        # Prints starting board
        embed = guilded.Embed(
            description=f':red_circle: {player1.name} :crossed_swords: {player2.name} :large_yellow_circle: \n{TOP_NUM + board.print_board()}\n Current Player: <@{player1.id}>\n :waving_white_flag:: Forfeit',
            color=guilded.Colour.dark_theme_embed())
        message = await ctx.send(embed=embed)
        # Adds the emotes the players will be clicking on and adds
        # the game to the global dictionary
        for emoji in EMOTES:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.01)
        IDS[message.id] = [board, player1, player2, 'R', 0, ctx.channel]

    @commands.Cog.listener()
    async def on_message_reaction_add(self, reaction):  # -> None:
        # print(dir(reaction))
        # print(reaction._user_id)
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
        channel = curr_channel[CHAN]
        curr_piece = curr_channel[CURR_P]
        curr_board = curr_channel[BRD]
        # for P_DICT
        player_red = True if curr_piece == 'R' else False
        curr_player = curr_channel[P_DICT[player_red][0]]
        other_player = curr_channel[P_DICT[not player_red][0]]
        # if user.id != self.client.user.id:
        # await reaction.remove(user)
        # stops the function if a reaction was added or if the reaction
        # was sent by a non-player
        if str(reaction.emoji.id) not in EMOTES.keys() \
                or (user != curr_player and user != other_player):
            print("return invalid")
            return None
        # At this point we know it's one of the two players who reacted to an emote.
        # Thus, we can directly cancel the game if one of the players forfeit.
        elif EMOTES[str(reaction.emoji.id)] == 'F':
            if user.id != self.client.user.id:
                del IDS[reaction.message.id]
                embed = guilded.Embed(title=f' {user.name} forfeited',
                                      # f'{curr_channel[1].name}'
                                      #                                    f' :crossed_swords: '
                                      # f'{curr_channel[2].name}',
                                      color=guilded.Colour.green())
                embed.set_image(url='https://media1.tenor.com/images/'
                                    '8c3cb918305bf277589c6ad84dfcea53/tenor.gif')
                await channel.send(embed=embed)
                return None
        # if the column is already filled, sends error message and does nothing
        # with the board
        if not curr_board.is_valid_location(0, EMOTES[str(reaction.emoji.id)]):
            embed = guilded.Embed(
                description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\n Current Player: <@{curr_player.id}>\n :waving_white_flag:: Forfeit',
                color=guilded.Colour.dark_theme_embed())
            await reaction.message.edit(embed=embed)
            try:
                await reaction.message.remove_reaction(reaction.emoji.id, user)
            except:
                pass
            return None
        # stops the function if user is the other player
        if user != curr_player:
            print("not your turn")
            try:
                await reaction.message.remove_reaction(reaction.emoji.id, user)
            except:
                pass
            return None
        # changes current piece to next player
        curr_channel[CURR_P] = P_DICT[not player_red][1]
        r = 5
        # finds a valid location to drop the piece in starting from the bottom
        # of the column
        while not curr_board.is_valid_location(r, EMOTES[str(reaction.emoji.id)]):
            r -= 1
        # drops the piece then edits the message to the updated board
        curr_board.drop_piece(r, EMOTES[str(reaction.emoji.id)], curr_piece)
        # reset afk timer
        curr_channel[TIMER] = 0
        # Checks if there are no more positions to drop a piece, then ends the game
        # as a draw if this is true.
        if len(curr_board.get_valid_locations()) == 0:
            del IDS[reaction.message.id]
            embed = guilded.Embed(title="It\'s a Draw",
                                  color=guilded.Colour.red())
            embed.set_image(url='https://media1.tenor.com/images/'
                                '729fc07335063f9d8a23002a71fdb0a8/tenor.gif')
            # await channel.send(embed=embed)
            try:
                await reaction.message.remove_reaction(reaction.emoji.id, user)
            except:
                pass
            return None
        # Checks if there is a connect 4, and if so, sends a winner message and
        # removes the game from IDS
        if curr_board.is_win(curr_piece):
            curr_color = P_DICT[player_red][2]
            # embed = guilded.Embed(title=f'{curr_player.name} wins!',
            #                      color=curr_color)
            # embed.set_image(url=random.choice(GIFS))
            # await channel.send(embed=embed)
            embed = guilded.Embed(
                description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\n<@{curr_player.id}> wins!',
                color=guilded.Colour.dark_theme_embed())
            await reaction.message.edit(embed=embed)
            del IDS[reaction.message.id]
            if curr_player.id != self.client.user.id:
                money_transfer_channel = await self.client.getch_channel("e9189390-1cf5-474f-8197-dc3145cfb08a")
                await money_transfer_channel.send(f"ggmoney-transfer {curr_player.id} {reaction.message.guild.id} c4")
            try:
                await reaction.message.remove_reaction(reaction.emoji.id, user)
            except:
                pass
            return None
        # If there is no connect 4, print the board and go to the next turn.
        else:
            embed = guilded.Embed(
                description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\n Current Player: <@{other_player.id}>\n :waving_white_flag:: Forfeit',
                color=guilded.Colour.dark_theme_embed())
            await reaction.message.edit(embed=embed)
            try:
                await reaction.message.remove_reaction(reaction.emoji.id, user)
            except:
                pass

        # If playing with bot, run the minimax algorithm asynchronously
        if other_player == self.client.user:
            # Show "thinking" indicator
            thinking_embed = guilded.Embed(
                description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\n Current Player: <@{other_player.id}> :thinking_gil:\n :waving_white_flag:: Forfeit',
                color=guilded.Colour.dark_theme_embed())
            await reaction.message.edit(embed=thinking_embed)

            # Run CPU calculation in thread to avoid blocking
            try:
                col = await asyncio.to_thread(self.cpu_minimax_move, curr_board)

                # Check if game still exists (user might have forfeited during CPU thinking)
                if reaction.message.id not in IDS:
                    return None

                row = curr_board.get_valid_locations()[col]
                # drop the piece into the board
                curr_board.drop_piece(row, col, AI_PIECE)
                curr_channel[TIMER] = 0

                # If bot plays winning move, send winning message and delete
                # game from IDS.
                if curr_board.is_win(curr_channel[CURR_P]):
                    other_color = P_DICT[not player_red][2]
                    embed = guilded.Embed(
                        description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\n<@{other_player.id}> wins!',
                        color=guilded.Colour.dark_theme_embed())
                    await reaction.message.edit(embed=embed)
                    del IDS[reaction.message.id]
                # Check for draw after bot move
                elif len(curr_board.get_valid_locations()) == 0:
                    del IDS[reaction.message.id]
                    embed = guilded.Embed(
                        description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\nIt\'s a Draw!',
                        color=guilded.Colour.dark_theme_embed())
                    await reaction.message.edit(embed=embed)
                # Otherwise, just print the board
                else:
                    embed = guilded.Embed(
                        description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\n Current Player: <@{curr_player.id}>\n :waving_white_flag:: Forfeit',
                        color=guilded.Colour.dark_theme_embed())
                    await reaction.message.edit(embed=embed)
                # changes current piece back to user
                curr_channel[CURR_P] = curr_piece

            except Exception as e:
                print(f"Error during CPU move: {e}")
                # Fallback to random move if minimax fails
                valid_locations = curr_board.get_valid_locations()
                if valid_locations and reaction.message.id in IDS:
                    col = random.choice(list(valid_locations.keys()))
                    row = valid_locations[col]
                    curr_board.drop_piece(row, col, AI_PIECE)
                    curr_channel[TIMER] = 0
                    curr_channel[CURR_P] = curr_piece
                    embed = guilded.Embed(
                        description=f':red_circle: {curr_channel[1].name} :crossed_swords: {curr_channel[2].name} :large_yellow_circle: \n{TOP_NUM + curr_board.print_board()}\n Current Player: <@{curr_player.id}>\n :waving_white_flag:: Forfeit',
                        color=guilded.Colour.dark_theme_embed())
                    await reaction.message.edit(embed=embed)


def setup(client):
    client.add_cog(ConnectFour(client))