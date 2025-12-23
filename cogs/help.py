import guilded, random
from guilded.ext import commands
from gil_utility.gperms import *


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    async def help(self, ctx, category=None):
        if category is None:
            category = "penis"
        if category.lower() == "tictactoe" or category.lower() == "ttt":
            embed = guilded.Embed(
                title='TicTacToe',
  
                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.ttt <@member>',
                            value='> starts a round of tictactoe',
                            inline=False),
            embed.add_field(name='.p <1-9>',
                            value='> places an X or O at the marked place (image below describes the tictactoe board more)',
                            inline=False),
            embed.add_field(name='.end',
                            value='> ends round')
            embed.set_image(url="https://cdn.discordapp.com/attachments/981904880514007121/1003269326377340988/8EEAE7D7-F01A-42B7-8745-460840F07FDF.jpeg")
            embed.set_footer(text="For more info, join guilded.gg/karma")

            await ctx.send(embed=embed)
        elif category.lower() == "mod" or category.lower() == "moderation":
            embed = guilded.Embed(
                title='Moderation',

                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.kick <@member>',
                            value='> kicks the user',
                            inline=False),
            embed.add_field(name='.ban <@member>',
                            value='> bans the user',
                            inline=False),
            embed.add_field(name='.unban <user>',
                            value='> unbans the user',
                            inline=False),
      #      embed.add_field(name='gg timeout (<@member> oder id), (Dauer in Minuten)',
              #              value='> timeouted den User ',
           #                 inline=False),
      #      embed.add_field(name='gg untimeout (<@member> oder id)',
#         #                   value='> untimeouted den User',
        #                    inline=False),
         #   embed.add_field(name='gg toggle (<@member> oder id)',
               #             value='> erlaubt dem user nicht mehr in dem Channel zu schreiben',
        #                    inline=False),
         #   embed.add_field(name='gg untoggle (<@member> oder id)',
                         #   value='> erlaubt dem user wieder\n> in dem zuvor getoggletem Channel zu schreiben',
                         #   inline=False),
          #  embed.add_field(name='gg nuke',
                            #value='> löscht alle Nachrichten aus dem Channel und erstellt einen Backup von den Nachrichten',
                          #  inline=False),
            #embed.add_field(name='gg instant-nuke',
                            #value='> deletes all messages in channel',
                            #inline=False),

            embed.add_field(name='.purge <limit>',
                            value='> purges messages',
                            inline=False)
            embed.add_field(name='.award-xp <amount> <@member>',
                            value='> gives xp to the target member, using negative values will remove xp.',
                            inline=False)
            embed.add_field(name='.mute <@member>',
                            value='> mutes the user',
                            inline=False)
            embed.add_field(name='.unmute <@member>',
                            value='> unmutes the user',
                            inline=False)
            embed.add_field(name='.tempmute <duration> <@member>',
                            value='> mutes the user, but will unmute him automatically after the given mute-duration',
                            inline=False)
            embed.set_footer(text="For more info, join guilded.gg/karma")

            await ctx.send(embed=embed)
        elif category.lower() in ["config", "setup", "configuration"]:
            embed = guilded.Embed(
                title='Setup',

                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.prefix',
                            value='> Shows the current prefix',
                            inline=False),
            embed.add_field(name='.set-prefix',
                            value='> let\'s you change the prefix',
                            inline=False),
            embed.add_field(name='.recache',
                            value='> will recache the server, use this if you made some server changes',
                            inline=False),
            embed.add_field(name='.mute-role', value='> sets the mute role for the server', inline=False),
            
            embed.add_field(name='.del-mute-role',value='> removes the mute role for the server',inline=False),
      #      embed.add_field(name='gg timeout (<@member> oder id), (Dauer in Minuten)',
              #              value='> timeouted den User ',
           #                 inline=False),
      #      embed.add_field(name='gg untimeout (<@member> oder id)',
#         #                   value='> untimeouted den User',
        #                    inline=False),
         #   embed.add_field(name='gg toggle (<@member> oder id)',
               #             value='> erlaubt dem user nicht mehr in dem Channel zu schreiben',
        #                    inline=False),
         #   embed.add_field(name='gg untoggle (<@member> oder id)',
                         #   value='> erlaubt dem user wieder\n> in dem zuvor getoggletem Channel zu schreiben',
                         #   inline=False),
          #  embed.add_field(name='gg nuke',
                            #value='> löscht alle Nachrichten aus dem Channel und erstellt einen Backup von den Nachrichten',
                          #  inline=False),
            #embed.add_field(name='gg instant-nuke',
                            #value='> deletes all messages in channel',
                            #inline=False),

            #embed.add_field(name='.mute <@member>',
                            #value='> mutes the user',
                            #inline=False)
            #embed.add_field(name='.unmute <@member>',
                            #value='> unmutes the user',
                            #inline=False)
            embed.set_footer(text="For more info, join guilded.gg/karma")

            await ctx.send(embed=embed)
        elif category.lower() == "tools" or category.lower() == "utility":
            embed = guilded.Embed(
                title='Utility',
                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.av [@member]',
                            value='> PfP of the user',
                            inline=False),
            embed.add_field(name='.banner [@member]',
                            value='> banner of the user',
                            inline=False),
            embed.add_field(name=".afk [note]",value="> Sets your status to AFK" )
            #embed.add_field(name='gg serveravatar (<@member> oder id)',
                          #  value='> Zeigt das serverspezifische Profilbild der gewählten Person, falls diese solch ein Profilbild besitzt',
                          #  inline=False),
            #embed.add_field(name='.banner <@member>',
                            #value='> Displays user banner',
                            #inline=False),
            embed.add_field(name='.server',
                            value='> server information',
                            inline=False),
            embed.add_field(name=".remind <duration> [note]",
                            value="> reminder that tags you automatically.")
            embed.add_field(name='.user [@member]',
                            value='> user information', inline=False)
            embed.add_field(name='.permcheck [@member]',
                            value='> shows all dangerous permissions', inline=False)
            embed.add_field(name='.securitycheck',
                            value='> Scan all roles and show the dangerous ones', inline=False)
            embed.add_field(name='.roles',
                            value='> lists the server roles',
                            inline=False)
            embed.add_field(name='.about',
                            value='> Information about the bot',
                            inline=False)
            embed.add_field(name='.invite',
                            value='> Invite link of the bot',
                            inline=False)
            #embed.add_field(name="gg disclaimer",
                            #value="> Kleiner Disclaimer zum Bot,\n> damit später keiner rumheult,\n> dass er nicht vorgewarnt wurde",
                           # inline=True)
            embed.add_field(name=".ping",
                            value="> Bot and API ping", inline=False)
            embed.add_field(name=".uptime",
                            value="> Uptime and total usage of commands", inline=False)
            embed.set_footer(text="For more info, join guilded.gg/karma")
            #embed.add_field(name=".snipe",
                            #value="> Sniped last deleted message", inline=False)
           # embed.add_field(name="gg imagesnipe",
                          #  value="> Sniped das zuletzt gelöschte Bild", inline=False)
            #embed.add_field(name=".editsnipe",
                            #value="> Sniped last edited message", inline=False)

            await ctx.send(embed=embed)
        elif category.lower() == "snipe":
          embed = guilded.Embed(color=guilded.Colour.blue(), title="Snipe")
          embed.add_field(name=".snipe [1-10]", value="> Snipes the given deleted Message, if no number was given, it will automatically snipe the last deleted message", inline=False)
          embed.add_field(name=".esnipe [1-10]", value="> Snipes the given edited Message, if no number was given, it will automatically snipe the last edited message", inline=False)
          embed.add_field(name=".usnipe <1-10> <@member>", value="> Snipes the given deleted message of the target member", inline=False)
          embed.add_field(name=".uesnipe <1-10> <@member>", value="> Snipes the given edited message of the target member", inline=False)
          await ctx.channel.send(embed=embed)
          return
          
        elif category.lower() == "4play":
            embed = guilded.Embed(color=guilded.Colour.blue(), title="Connect 4")
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author))
            embed.add_field(name='How to start a round',
                            value='.4play <@member>', inline=False)#; if nobody was pinged'
                                  #' you\'ll play'
                                  #' against the bot',
            await ctx.send(embed=embed)
        elif category.lower() == "strikes":
            return
            embed = guilded.Embed(
                title='Brauchst du Hilfe?',
                description=
                'Hier wird dir das Strikesystem erklärt',
                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='gg strike (<@member> oder id) (Grund)',
                            value='> Striked den markierten Member',
                            inline=False)
            embed.add_field(name='gg delete-strike (Strike ID)',
                            value='> Löscht den Strike aus der Datenbank',
                            inline=False)
            embed.add_field(name='gg clear-strikes (<@member> oder id)',
                            value='> Löscht alle Strikes vom gegebenen User',
                            inline=False)
            embed.add_field(name='gg show-strikes (<@member> oder id)',
                            value='> Listet alle Strikes des gegebenen Users',
                            inline=False)
            embed.add_field(name='gg strike-info (Strike ID)',
                            value='> Zeigt alle Details zu einem Strike',
                            inline=False)
            embed.add_field(name='Das Strike-System kurz erklärt:',
                            value='Beim ersten Strike passiert nichts.\nBeim zweiten Strike bekommt der User 10 Minuten Timeout\nBeim dritten Strike bekommt der User eine Stunde Timeout\nBeim vierten Strike bekommt der User eine Woche Timeout\nBeim fünten Strike wird der User gebannt\n\nUm jemanden striken zu können, benötigt man Bannrechte.',
                            inline=False)

            await ctx.send(embed=embed)
        elif category.lower() == "animation":
          embed = guilded.Embed(
        title='Animation',
          colour=guilded.Colour.blue())
          embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
          #embed.add_field(name='gg kill <@member>',
                    #value='> ded ☠️',
                    #inline=False),
          embed.add_field(name='.punch [@member]',
                    value='> :facepunch:',
                    inline=True)
          embed.add_field(name='.angry [@member]',
                    value='> :angry:',
                    inline=True)
          embed.add_field(name='.awkward',
                    value='> :sweat_gil:',
                    inline=True)
          embed.add_field(name='.bite [@member]',
                    value='> :vampire:',
                    inline=True)
          embed.add_field(name='.blush',
                    value='> :flushed:',
                    inline=True)
          embed.add_field(name='.bored',
                    value='> :face_with_rolling_eyes::',
                    inline=True)
          embed.add_field(name='.cry',
                    value='> :sob:',
                    inline=True)
          embed.add_field(name='.cuddle [@member]',
                    value='> :people_hugging::',
                    inline=True)
          embed.add_field(name='.dance',
                    value='> :man_dancing:',
                    inline=True)
          embed.add_field(name='.happy',
                    value='> :smile_guilded:',
                    inline=True)
          embed.add_field(name='.hug [@member]',
                    value='> :hugging_face:',
                    inline=True)
          embed.add_field(name='.kiss [@member]',
                    value='> :kissing_heart::',
                    inline=True)
          embed.add_field(name='.nom',
                    value='> :fork_and_knife:',
                    inline=True)
          embed.add_field(name='.pat [@member]',
                    value='> :derp_guilded:',
                    inline=True)
          embed.add_field(name='.poke [@member]',
                    value='> :smug:',
                    inline=True)
          embed.add_field(name='.slap [@member]',
                    value='> :cry_gil:',
                    inline=True)
          embed.add_field(name='.wave [@member]',
                    value='> :wave:',
                    inline=True)
          #embed.add_field(name='.twitter <@member> text',
          #          value='> fake tweet',
          #          inline=False)
          #embed.add_field(name='.comment <@member> text',
          #          value='> fake-yt comment',
         #           inline=False)
          #embed.add_field(name='.simp <@member>',
          #          value='> Simp-Card',
          #          inline=False)
          #embed.add_field(name='.horny <@member>',
          #          value='> howny license',
          #          inline=False)
          #embed.add_field(name='.androiduser <@member>',
          #          value='> Avatar command (Android quality)',
          #          inline=False)
          embed.set_footer(text="For more info, join guilded.gg/karma")
          await ctx.channel.send(embed=embed)

        elif category.lower()in ["giveaways", "giveaway"]:
          #return
          embed = guilded.Embed(
        title='Giveaway',
          colour=guilded.Colour.blue())
          embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
          embed.add_field(name='.g-start',
                    value='> Create a new giveaway',
                    inline=False),
          embed.add_field(name='.g-stop <giveaway_id>',
                    value='> Stop a giveaway manually',
                    inline=False)
          embed.add_field(name='.g-delete <giveaway_id>',
                    value='> Delete a giveaway',
                    inline=False)
          embed.add_field(name='.g-reroll <giveaway_id>',
                    value='> Reroll a finished giveaway',
                    inline=False)
          embed.add_field(name='.g-join <giveaway_id>',
                    value='> Join a giveaway through the giveaway id',
                    inline=False)
          embed.add_field(name='.g-leave <giveaway_id>',
                    value='> Leave a giveaway through the giveaway id',
                    inline=False)
          embed.add_field(name='.show-giveaway <giveaway_id>',
                    value='> Obtain information about a giveaway',
                    inline=False)
          embed.add_field(name='.g-lock <giveaway_id>',
                    value='> Locks the given giveaway',
                    inline=False)
          embed.add_field(name='.g-unlock <giveaway_id>',
                    value='> Unlocks the given giveaway',
                    inline=False)
          embed.add_field(name='.g-block <giveaway_id> <@member>',
                    value='> Blocks User from the given giveaway',
                    inline=False)
          embed.add_field(name='.g-unblock <giveaway_id> <@member>',
                    value='> Unblocks User from the given giveaway',
                    inline=False)
          embed.add_field(name='.g-whitelist <giveaway_id> <@role>',
                    value='> Whitelists Role from participating at giveaway',
                    inline=False)
          embed.add_field(name='.g-unwhitelist <giveaway_id> <@role>',
                    value='> Unwhitelists Role from participating at giveaway',
                    inline=False)
          embed.set_footer(text="For more info, join guilded.gg/karma")
          await ctx.channel.send(embed=embed)
        elif category.lower() == "fun":
            embed = guilded.Embed(
                title='Funie',
                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.rps [@member]',
                            value='> Play rock, paper, scissor against a member or the Bot',
                            inline=False),
            embed.add_field(name='.8ball <question>',
                            value='> Will answer all your questions',
                            inline=False)
            embed.add_field(name='.rate <topic>',
                            value='> Will rate a topic for you',
                            inline=False)
            embed.add_field(name='.ship [@member], [@member]',
                            value='> Will ship 2 users', inline=False)
            embed.add_field(name='.anime-gen <prompt> [ratio, e.g. 9:16]',
                            value='> Will create an Image of your prompt in anime style', inline=False)
            embed.add_field(name='.image-gen <prompt> [ratio, e.g. 16:9]',
                            value='> Will create an Image of your prompt', inline=False)
            embed.add_field(name='.triggered [@user]',
                            value='> Makes user avatar triggered',
                            inline=False)
            embed.add_field(name='.jail [@user]',
                            value='> Puts user in jail',
                            inline=False)
            embed.add_field(name='.rip [@user]',
                            value='> You will be missed...',
                            inline=False)
            embed.add_field(name='.sadify [@user]',
                            value='> Makes user avatar sad',
                            inline=False)
            embed.add_field(name='.polaroid [@user]',
                            value='> Edits the user avatar to have a Polaroid style',
                            inline=False)
            embed.add_field(name='.invert [@user]',
                            value='> Inverts colors of user avatar',
                            inline=False)
            embed.add_field(name='.mirror [@user]',
                            value='> Mirrors user avatar',
                            inline=False)
            embed.add_field(name='.flip [@user]',
                            value='> Flips user avatar',
                            inline=False)
            embed.add_field(name='.blur [@user]',
                            value='> Blurs user avatar sad',
                            inline=False)
            embed.add_field(name='.grayscale [@user]',
                            value='> Makes user avatar in grayscale',
                            inline=False)
            embed.add_field(name='.hl',
                            value='> Play the higher-lower game',
                            inline=False)
            embed.set_footer(text="For more info, join guilded.gg/karma")
            await ctx.send(embed=embed)
        elif category.lower() == "userphone":
            embed = guilded.Embed(
                title='Userphone',
                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.userphone',
                            value='> Talk to somebody across one of the Bot\'s servers',
                            inline=False),
            embed.add_field(name='.hangup',
                            value='> Will hangup the userphone',
                            inline=False)
            embed.add_field(name='.channelphone',
                            value='> Connect with a Server-Channel, shoutout YumYummity',
                            inline=False),
            embed.add_field(name='.changup',
                            value='> Get it? Channel hangup, haha funny i know',
                            inline=False)
                            
            embed.set_footer(text="For more info, join guilded.gg/karma")
            await ctx.send(embed=embed)
        elif category.lower() == "skidae":
            embed = guilded.Embed(
                title='Skidae',
                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.waifu',
                            value='> draw a random Waifu',
                            inline=False),
            embed.add_field(name='.husbando',
                            value='> draw a random Husbando',
                            inline=False),
            embed.add_field(name='.character <character name>',
                            value='> Information about character',
                            inline=False),
            embed.add_field(name='.list-characters [page] [male or female] [anime]',
                            value='> lists all characters or all filtered characters',
                            inline=False),
            embed.add_field(name='.search-character <name>',
                            value='> Searches for character, even if there are typos.',
                            inline=False),
            embed.add_field(name='.search-anime <name>',
                            value='> Searches for anime, even if there are typos.',
                            inline=False),
            embed.add_field(name='.wishlist',
                            value='> shows your wishlist',
                            inline=False),
            embed.add_field(name='.wish <character name>',
                            value='> Adds character to your wishlist, increases luck (default: 13x).',
                            inline=False),
            embed.add_field(name='.unwish <character name>',
                            value='> Removes character from wishlist.',
                            inline=False),
            embed.add_field(name='.tcc',
                            value='> Shows the top claimed characters',
                            inline=False)

            embed.add_field(name='.tuc',
                            value='> Shows the top unclaimed characters',
                            inline=False)
            embed.add_field(name='.married [male or female]',
                            value='> Shows your characters detailed',
                            inline=False)
            embed.add_field(name='.custom-image <character> <url>',
                            value='> Set a custom image for your character',
                            inline=False)
            embed.add_field(name='.rem-custom-image <character> <url>',
                            value='> Remove custom image from your character',
                            inline=False)
            embed.add_field(name='.stats [@user]',
                            value='> Shows user stats',
                            inline=False)
            embed.add_field(name='.skidae-stats',
                            value='> Shows server stats',
                            inline=False)
            embed.add_field(name='.divorce <character name>',
                            value='> Divorce a character',
                            inline=False)
            embed.add_field(name='.trade <user>',
                            value='> Start a trade with user.',
                            inline=False)
            embed.add_field(name='.add <character name>',
                            value='> Add character to trade',
                            inline=False)
            embed.add_field(name='.rem-char <character name>',
                            value='> remove character from trade',
                            inline=False)
            embed.add_field(name='.confirm',
                            value='> confirms trade',
                            inline=False)
            embed.add_field(name='.cancel',
                            value='> cancels trade',
                            inline=False)
            embed.add_field(name='.customize <module> <amount>',
                            value='> Customize limits, use command for more info, requires `update server` permission',
                            inline=False)
            embed.add_field(name='.force-divorce <character name>',
                            value='> Force-divorce a character, requires `update server` permission',
                            inline=False)
            embed.add_field(name='.clear-db',
                            value='> Removes characters from users who left the server, requires `update server` permission',
                            inline=False)

            embed.set_footer(text="For more info, join guilded.gg/karma")
            await ctx.send(embed=embed)
        else:
            embed = guilded.Embed(
                title='Help',
                colour=guilded.Colour.blue())
            embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),
            embed.add_field(name='.help mod',
                            value='> Shows all moderation commands',
                            inline=False),
            embed.add_field(name='.help tictactoe',
                            value='> Shows all tictactoe commands',
                            inline=False)
            embed.add_field(name='.help tools',
                            value="> Shows all utility commands",
                            inline=False)
            embed.add_field(name='.help giveaway',
                            value="> Shows all giveaway commands",
                            inline=False)
            embed.add_field(name='.help snipe',
                            value="> Shows all sniping commands",
                            inline=False)
            embed.add_field(name='.help setup',
                            value="> Shows all bot-setup commands",
                            inline=False)
            # embed.add_field(name='gghelpnsfw',value="> Zeigt dir alle NSFW-Befehle", inline= False)
            embed.add_field(name='.help animation', value="> Shows all Anime commands", inline=False)
            # embed.add_field(name='eastereggs??',
            # value='> Es gibt einige Eastereggs in diesem Bot..\n> Viel Spaß beim Erkunden :>',
            # inline=False)
            embed.add_field(name='.help 4play',
                            value='> Shows you all the connect 4 commands',
                            inline=False)
            embed.add_field(name='.help fun',
                            value='> Shows you all funie commands',
                            inline=False)
            embed.add_field(name='.help userphone',
                            value='> Shows you all userphone commands',
                            inline=False)
            embed.add_field(name='.help skidae',
                            value='> A Mudae rip-off.',
                            inline=False)
            # embed.add_field(name='gghelpeconomy',
            # value='> Zeigt dir alle Casino-Befehle',
            # inline=False)
          #  embed.add_field(name='gghelp strikes',
                         #   value='> erklärt dir das eingebaute Strikesystem ',
                          #  inline=False),

            embed.set_footer(text="For more info, join guilded.gg/karma")

            await ctx.send(embed=embed)

 #   @commands.command()
    async def disclaimer(self, ctx):
        embed = guilded.Embed(
            title='Kleiner Disclaimer am Rande...',
            description=
            'Einige Aussagen des Bots könnten eventuell beleidigend oder verletzend wirken. Keine dieser Aussagen sind Ernst gemeint sondern fallen in die Kategorie **Sarkasmus** bzw. **Schwarzer Humor**. Durch die Nutzung des Bots, willigt man automatisch ein, dass man jede Aussage mit Humor nehmen wird. Falls es einem trotzdem aus diversen Gründen nicht passen sollte, kann er gerne den Bot vom Server entfernen oder (falls ihm die Rechte dazu fehlen)  den Server selber verlassen. Vielen Dank für euer Verständnis :>',
            colour=guilded.Colour.blue())
        embed.set_author(name=ctx.message.author, icon_url=avatar_handler(ctx.author)),

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Help(client))




