import os
#import dtbs as db
import json
from gil_utility.gperms import *

intervals = (
    ('years', 86400 * 30 * 12),
    ('months', 86400 * 30),
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1))


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(str(int(value)), name))
    string_final = ""
    for i in result:
        string_final += f"{i}, "
    return string_final[:-2]


class Toggle(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.nick_cache = {}

        self.aliases = {
            "rage": "angry",
            "angery": "angry",
            "eat": "nom",
            "hungry": "nom",
            "hit": "punch",
            "smack": "slap",
            "joy": "smile",
            "happy": "smile",
            "4-play": "4play",
            "connect-four": "4play",
            "connect4": "4play",
            "gstart": "giveaway",
            "g-start": "giveaway",
            "gcancel": "gstop",
            "g-cancel": "gstop",
            "g-stop": "gstop",
            "gdelete": "g-delete",
            "gjoin": "g-join",
            "gquit": "gleave",
            "g-quit": "gleave",
            "g-leave": "gleave",
            "gblock": "g-block",
            "gunblock": "g-unblock",
            "giveaway-info": "show-giveaway",
            "glock": "g-lock",
            "gunlock": "g-unlock",
            "gwhitelist": "g-whitelist",
            "gunwhitelist": "g-unwhitelist",
            "g-reroll": "greroll",
            "remind": "create-reminder",
            "remind-me": "create-reminder",
            "tcc": "top_claimed_characters",
            "tuc": "top_unclaimed_characters",
            "add": "add-to-trade",
            "att": "add-to-trade",
            "rem-char": "remove-from-trade",
            "confirm": "confirm_trade",
            "cancel": "cancel_trade",
            "prison": "jail"
        }

    @commands.command(name="toggle")
    async def toggle(self, ctx, *, commandname):
        if not (await administrator_check(ctx)):
            return
        cmdname = commandname.lower()
        try:
            cmdname = self.aliases[cmdname]
        except:
            pass
        unblockable_commands = [
            "help", "invite", "toggle", "prefix", "set-prefix", "load",
            "reload", "unload", "loadall", "reloadall", "unloadall", "allcmds",
            "about", "recache", "uptime"
        ]
        all_cmds = [
            "load", "reload", "unload", "loadall", "unloadall", "reloadall",
            "eval", "afk", "image-gen", "anime-gen", "awkward", "angry",
            "bite", "blush", "bored", "cry", "cuddle", "dance", "hug", "kiss",
            "nom", "pat", "poke", "punch", "slap", "wave", "smile",
            "4play", "channelphone", "changup", "8ball", "rate", "ship", "giveaway",
            "gstop", "g-delete", "g-join", "gleave", "g-block",
            "g-unblock", "show-giveaway", "g-lock", "g-unlock", "g-whitelist",
            "g-unwhitelist", "greroll", "help", "higher-lower", "mute-role",
            "del-mute-role", "tempmute", "mute", "unmute", "prefix", "set-prefix",
            "create-reminder", "rps", "character", "list-characters", "search-character", "search-anime",
            "waifu", "husbando", "wishlist", "wish", "unwish", "top_claimed_characters",
            "top_unclaimed_characters", "stats", "custom-image", "rem-custom-image",
            "married", "snipe", "editsnipe", "user-snipe", "usereditsnipe",
            "clean-snipe-json", "tictactoe", "place", "end", "toggle",
            "trade", "add-to-trade", "remove-from-trade", "confirm_trade",
            "cancel_trade", "divorce", "get-emoteid", "uptime", "userphone",
            "hangup", "betaimage", "allcmds", "reaction-test", "fetch-servers",
            "emoji-list", "testdel", "kick", "ban", "unban", "about", "purge", "ping",
            "invite", "server", "whois", "av", "categoryid", "recache", "banner",
            "award-xp", "roles", "permcheck", "securitycheck", "customize", "triggered",
            "polaroid", "rip", "invert", "mirror", "sadify", "blur", "jail", "grayscale", "flip"
            "force-divorce", "clear-db"]
        if cmdname in unblockable_commands:
            return await ctx.channel.send("This command cannot be toggled!")
        if cmdname not in all_cmds:
            return await ctx.channel.send(
                "This command was not found, make sure to write it correctly")
    #   u = await db.DisabledCommands.find_one(
    #        {"_id": ctx.guild.id}
    #    )
        if not os.path.exists(f"Database/Disabled/{ctx.guild.id}.json"):
            toggletype = "disabled"
            creating_file = open(f'Database/Disabled/{ctx.guild.id}.json', "w")
            data = {"_id": f"{ctx.guild.id}", "disabled": [cmdname]}
            creating_file.write(json.dumps(data))
            try:
                creating_file.close()
            except:
                pass
        # await db.DisabledCommands.insert_one(
        #         data
        #     )

        else:
            json_file = open(f"Database/Disabled/{ctx.guild.id}.json", "r")
            json_content = json.load(json_file)
            newlist = json_content["disabled"]
            if cmdname in newlist:
                toggletype = "enabled"
                newlist.remove(cmdname)
            else:
                toggletype = "disabled"
                newlist.append(cmdname)
            if len(newlist) == 0:
                deletedict = True
            else:
                deletedict = False
            json_file.close()
            if deletedict:
                os.remove(f"Database/Disabled/{ctx.guild.id}.json")
                #await db.DisabledCommands.delete_one({"_id": f"{ctx.message.guild.id}"})
            else:
                json_content["disabled"] = newlist
                json_db = open(f"Database/Disabled/{ctx.guild.id}.json", "w")
                clean_json = json.dumps(json_content,
                                        indent=4,
                                        separators=(",", ": "))
                json_db.write(clean_json)
                json_db.close()
            #  data = {"_id": ctx.guild.id,
        #             "disabled": newlist}
        #      await db.DisabledCommands.update_one(
        #         {"_id": f"{ctx.guild.id}"}, {"$set": data}

    #         )
        await ctx.send(
            f"The command {cmdname} has been {toggletype} in this server.")


def setup(bot):
    bot.add_cog(Toggle(bot))
