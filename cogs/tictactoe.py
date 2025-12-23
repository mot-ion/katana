import guilded
from guilded.ext import commands
import random, asyncio
import checksfrfr
from gil_utility.gperms import *

player1 = {}#""
player2 = {}#""
turn = {}#""
gameOver = {}#True

board = {}

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
    ]

class Tictactoe(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(name="tictactoe", aliases=["ttt"])
    async def tictactoe(self, ctx,*, user=None):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
          return
        if user is None:
          return await ctx.send("You didn't mention your rival!")
        p1 = await find_member_named(ctx.guild, user, ctx)
        if not p1:
          await user_not_found(ctx, user)
          return
        if p1.id == ctx.author.id:
            return await ctx.send("You cannot play with yourself!")
        elif p1.bot:
            return await ctx.send("You cannot play against bots!")
        await ctx.channel.send(embed=guilded.Embed(description=f"{p1.mention}, would you like to play tictactoe against {ctx.author}?\nType yes to start a round", color=guilded.Color.dark_theme_embed()))
        try:
          answer = await self.client.wait_for("message", timeout=30, check=lambda response: response.author == p1 and response.channel == ctx.channel)
        except asyncio.TimeoutError:
          return await ctx.channel.send(f"{p1} did not join the game")
        accepted = False
        yeslist =  ["yes", "yeah", "ok", "accept", "okay"]
        for yes in yeslist:
          if str(answer.content).lower().startswith(yes):
            accepted = True
        if not accepted:
          return await ctx.channel.send(f"{p1} did not accept the join request") 
        global count
        global player1
        global player2
        global turn
        global gameOver
        try:
          if gameOver[f"{ctx.guild.id}"] is False:
            await ctx.send("There is already a match, end it via **.end** before you start a new round!")
            return
        except:
            gameOver[f"{ctx.guild.id}"] = True

        player1[f"{ctx.guild.id}"] = p1.id
        player2[f"{ctx.guild.id}"] = ctx.message.author.id


        try:
            if gameOver[f"{ctx.guild.id}"]:
                global board
                board[f"{ctx.guild.id}"] = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                         ":white_large_square:", ":white_large_square:", ":white_large_square:",
                         ":white_large_square:", ":white_large_square:", ":white_large_square:"]
                #turn = ""
                gameOver[f"{ctx.guild.id}"] = False
                count = 0

                # print the board
                line = ""
                indx = 0
                # for x in range(len(board)):
                #    if x == 2 or x == 5 or x == 8:
                #        line += " " + board[x]
                #        await ctx.send(line)
                #        line = ""
                #    else:
                #        line += " " + board[x]
                for i in board[f"{ctx.guild.id}"]:
                    indx += 1
                    if indx == 3 or indx == 6 or indx == 9:
                        line += f"{i}\n"
                    else:
                        line += i
                #await ctx.send(line)
                choices = [player1[f"{ctx.guild.id}"], player2[f"{ctx.guild.id}"]]

                # determine who goes first
                num = random.choice(choices)
                if str(num) == str(player1[f"{ctx.guild.id}"]):
                    turn[f"{ctx.guild.id}"] = player1[f"{ctx.guild.id}"]
                    pp1 = player1[f"{ctx.guild.id}"]
                    line+= f"\nIt\'s <@{pp1}>\'s turn"
                    embed = guilded.Embed(description=line,color=guilded.Colour.dark_theme_embed())
                    await ctx.send(embed=embed, silent=True)
                    #await ctx.send(f"<@{pp1}> ist an der Reihe.")
                elif str(num) == str(player2[f"{ctx.guild.id}"]):
                    turn[f"{ctx.guild.id}"] = player2[f"{ctx.guild.id}"]
                    pp2 = player2[f"{ctx.guild.id}"]
                    line+= f"\nIt\'s <@{pp2}>\'s turn"
                    embed = guilded.Embed(description=line,color=guilded.Colour.dark_theme_embed())
                    await ctx.send(embed=embed, silent=True)
                    #await ctx.send(f"<@{pp2}> ist an der Reihe.")
        except:
          pass


    @commands.command(name="place", aliases=["pl", "plc", "p"])
    async def place(self, ctx, pos: int):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
            return
        global turn
        global player1
        global player2
        global board
        global count
        global gameOver

        if not gameOver[f"{ctx.guild.id}"]:
            mark = ""
            if turn[f"{ctx.guild.id}"] == ctx.author.id:
                if turn[f"{ctx.guild.id}"] == player1[f"{ctx.guild.id}"]:
                    mark = ":x:"
                    winner = player1[f"{ctx.guild.id}"]
                elif turn[f"{ctx.guild.id}"] == player2[f"{ctx.guild.id}"]:
                    mark = ":o:"
                    winner = player2[f"{ctx.guild.id}"]
                if 0 < pos < 10 and board[f"{ctx.guild.id}"][pos - 1] == ":white_large_square:":
                    board[f"{ctx.guild.id}"][pos - 1] = mark
                    count += 1

                    # print the board
                    line = ""
                    indx = 0
                    # for x in range(len(board)):
                    #    if x == 2 or x == 5 or x == 8:
                    #        line += " " + board[x]
                    #        await ctx.send(line)
                    #        line = ""
                    #    else:
                    #        line += " " + board[x]
                    if turn[f"{ctx.guild.id}"] == player1[f"{ctx.guild.id}"]:
                        turn[f"{ctx.guild.id}"] = player2[f"{ctx.guild.id}"]
                    elif turn[f"{ctx.guild.id}"] == player2[f"{ctx.guild.id}"]:
                        turn[f"{ctx.guild.id}"] = player1[f"{ctx.guild.id}"]
                    for i in board[f"{ctx.guild.id}"]:
                        indx += 1
                        if indx == 3 or indx == 6:
                            line += f"{i}\n"
                        elif indx == 9:
                            line += f"{i}"
                        else:
                            line += i
                    #await ctx.send(line)

                    self.checkWinner(ctx, winningConditions, mark)
                    #print(count)
                    if gameOver[f"{ctx.guild.id}"]:
                        line+= f"\n<@{winner}> has won the game"
                        embed = guilded.Embed(description=line,color=guilded.Colour.dark_theme_embed())
                        await ctx.send(embed=embed, silent=True)
                        money_transfer_channel = await self.client.getch_channel("e9189390-1cf5-474f-8197-dc3145cfb08a")
                        await money_transfer_channel.send(f"ggmoney-transfer {winner} {ctx.guild.id} ttt")
                        #await ctx.send(f"<@{winner}> hat gewonnen!")
                    elif count >= 9:
                        gameOver[f"{ctx.guild.id}"] = True
                        #line+= f"\n<@{winner}> has won the game"
                        #embed = guilded.Embed(description=line)
                        #await ctx.send(embed=embed, silent=True)
                        await ctx.send("It\'s a tie!")
                    else:
                        rn =   turn[f"{ctx.guild.id}"]
                        line+= f"\nIt\'s <@{rn}>\'s turn"
                        embed = guilded.Embed(description=line,color=guilded.Colour.dark_theme_embed())
                        await ctx.send(embed=embed, silent=True)
                        #await ctx.send(f"<@{rn}> ist an der Reihe.")

                else:
                    await ctx.send("Please choose a valid spot between 1-9, the spot has to be free")
            else:
                await ctx.send("It\'s not your turn.")
        else:
            await ctx.send("Please start a round with the command **.ttt**")

    def checkWinner(self, ctx, winningConditions, mark):
        global gameOver
        for condition in winningConditions:
            if board[f"{ctx.guild.id}"][condition[0]] == mark and board[f"{ctx.guild.id}"][condition[1]] == mark and board[f"{ctx.guild.id}"][condition[2]] == mark:
                gameOver[f"{ctx.guild.id}"] = True

    #@tictactoe.error
    async def tictactoe_error(self, ctx, error):
        #print(error)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Bitte markiere deinen Rivalen.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Bitte stelle sicher dass du jemanden pingst (Bsp.: <@925126601547579502>).")

    #@place.error
    async def place_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Bitte gebe eine Position ein, die du markieren möchtest.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Bitte stelle sicher, dass du eine Ganzzahl eingibst.")

    @commands.command()
    async def end(self, ctx):
        check = await checksfrfr.enabled(ctx, ctx.command.name)
        if not check:
          return
        global gameOver
        try:
            gameOver[f"{ctx.guild.id}"]
        except:
            gameOver[f"{ctx.guild.id}"] = True
        if ban_users(ctx):
            if not gameOver[f"{ctx.guild.id}"]:
                gameOver[f"{ctx.guild.id}"] = True
                await ctx.send("Game was ended...")
            else:
                await ctx.send("There is no game running.")
        else:
            if ctx.message.author.id == player2[f"{ctx.guild.id}"] or ctx.message.author.id == player1[f"{ctx.guild.id}"]:
                if not gameOver[f"{ctx.guild.id}"]:
                    gameOver[f"{ctx.guild.id}"] = True
                    await ctx.send("Game was ended...")
                else:
                    await ctx.send("There is no game running.")
            else:
                if not gameOver[f"{ctx.guild.id}"]:
                    await ctx.send("You cannot end the round of other players...\n(Ban perms needed)")
                else:
                    await ctx.send("There is no game running.")

def setup(client):
    client.add_cog(Tictactoe(client))
