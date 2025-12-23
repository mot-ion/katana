import guilded, random, asyncio
from guilded.ext import commands
from guilded.ext.commands.converters import (_INT_ID_REGEX, _UUID_REGEX, _GENERIC_ID_REGEX,)
import re


def avatar_handler(member: guilded.Member):

    if "howdy-Large" in str(member.avatar):
        return "https://www.guilded.gg/asset/DefaultBotAvatars/howdy-bot.png?v=1"
    if "xp-Large" in str(member.avatar):
        return "https://www.guilded.gg/asset/DefaultBotAvatars/xp-bot.png?v=1"
    if "patreon-Large" in str(member.avatar):
        return "https://www.guilded.gg/asset/DefaultBotAvatars/patreon-bot.png?v=1"
    if "youtube-Large" in str(member.avatar):
        return "https://www.guilded.gg/asset/DefaultBotAvatars/youtube-bot.png?v=1"
    if "twitch-Large" in str(member.avatar):
        return "https://www.guilded.gg/asset/DefaultBotAvatars/twitch-bot.png?v=1"

    if member.avatar == "None" or member.avatar is None:
        return f"https://www.guilded.gg/asset/DefaultUserAvatars/profile_{random.randint(1, 5)}.png"
    return member.avatar


async def missing_perms(ctx, permission):
    color = guilded.Color.from_rgb(239, 83, 80)
    embed = guilded.Embed(description=f"🔒 Requires {permission} permissions",
                          color=color)
    embed.set_author(name=ctx.author, icon_url=avatar_handler(ctx.author))
    await ctx.channel.send(embed=embed)
    return

async def roles_too_low(ctx, bot=False):
    if bot:
        desc = f"🔒 My roles are too low, action cannot be performed"
    else:
        desc = f"🔒 Your roles are too low to perform this action."
    color = guilded.Color.from_rgb(239, 83, 80)
    embed = guilded.Embed(description=desc,
                          color=color)
    embed.set_author(name=ctx.author, icon_url=avatar_handler(ctx.author))
    await ctx.channel.send(embed=embed)
    return

async def dev_check(ctx, valid):
    if ctx.author.id in ctx.bot.devids:
        if valid:
            return True

        def check(message):
            return (message.author.id == ctx.author.id
                    and message.content.lower() == 'bypass')

        try:
            message = await ctx.bot.wait_for('message',
                                             timeout=5.0,
                                             check=check)
            await message.add_reaction(90002171)
            return True
        except asyncio.TimeoutError:
            return False
    return False


def guild_owner(ctx):
    if ctx.author.id == ctx.guild.owner_id:
        return True
    return False


def administrator(ctx:commands.Context):
    for role in ctx.author.roles:
        if role.permissions.administrator:
            return True


def admin_owner_check(ctx):
    if guild_owner(ctx):
        return True
    if administrator(ctx):
        return True
    return False


async def administrator_check(ctx):
    return await manage_guild(ctx)
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        valid = False
    if not valid:
        await missing_perms(ctx, "administrator")
    if (await dev_check(ctx, valid)):
        return True
    return valid


async def ban_users(ctx):
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        for role in ctx.author.roles:
            if role.permissions.ban_members:
                valid = True
    if not valid:
        await missing_perms(ctx, "kick users")
    if (await dev_check(ctx, valid)):
        return True
    return valid


async def manage_guild(ctx):
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        for role in ctx.author.roles:
            if role.permissions.manage_guild:
                return True
    if not valid:
        await missing_perms(ctx, "update guild")
    if (await dev_check(ctx, valid)):
        return True
    return valid


async def manage_roles(ctx):
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        for role in ctx.author.roles:
            if role.permissions.manage_roles:
                valid = True
    if not valid:
        await missing_perms(ctx, "manage roles")
    if (await dev_check(ctx, valid)):
        return True
    return valid


async def manage_channels(ctx):
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        for role in ctx.author.roles:
            if role.permissions.manage_channels:
                valid = True
    if not valid:
        await missing_perms(ctx, "manage channels")
    if (await dev_check(ctx, valid)):
        return True
    return valid


async def mention_everyone(ctx):
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        for role in ctx.author.roles:
            if role.permissions.mention_everyone:
                valid = True
    if not valid:
        await missing_perms(ctx, "mention everyone")
    if (await dev_check(ctx, valid)):
        return True
    return valid


async def manage_xp(ctx):
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        for role in ctx.author.roles:
            if role.permissions.manage_server_xp:
                valid = True
    if not valid:
        await missing_perms(ctx, "manage xp")
    if (await dev_check(ctx, valid)):
        return True
    return valid


async def manage_messages(ctx, snipe=False):
    valid = False
    if admin_owner_check(ctx):
        valid = True
    else:
        for role in ctx.author.roles:
            if role.permissions.manage_messages:
                valid = True
    if not valid:
        if not snipe:
            await missing_perms(ctx, "manage messages")
    if (await dev_check(ctx, valid)):
        return True
    return valid

def get_top_role(member: guilded.Member, ctx=None):
    top_role = 0
    for role in member.roles:
        if role.position > top_role:
            top_role = role.position
    if ctx is not None:
        if guild_owner(ctx):
            top_role = 100000
    return top_role

async def is_higher(ctx, target: guilded.Member, bot_user):
    valid = False
    if get_top_role(ctx.author, ctx) < get_top_role(target):
        await roles_too_low(ctx)
        return valid
    if get_top_role(bot_user) < get_top_role(target):
        await roles_too_low(ctx, True)
        return valid
    return True


async def find_channel_named(team, argument: str):
    if argument.startswith("<#") and argument.endswith(">"):
        argument = argument.removeprefix("<#").removesuffix(">")
    match = _UUID_REGEX.match(argument)
    result = None
    channel_id = None
    if match:
        channel_id = match.group(1)
        try:
            result = await team.getch_channel(channel_id)
        except (guilded.NotFound, guilded.BadRequest):
            pass

    if result is not None:
        return result
    try:
        argument = argument.replace("#", "")
    except:
        pass
    return guilded.utils.find(
        lambda m: m.name == argument or m.id == argument, team.channels)

async def find_role_named(team, argument: str):
    if argument.startswith("<@&") and argument.endswith(">"):
        argument = argument.removeprefix("<@&").removesuffix(">")
    match = _INT_ID_REGEX.match(argument)
    result = None
    role_id = None
    if match:
        role_id = match.group(1)
        try:
            result = await team.getch_role(role_id)
        except (guilded.NotFound, guilded.BadRequest):
            pass

    if result is not None:
        return result
    try:
        argument = argument.replace("@", "")
    except:
        pass
    return guilded.utils.find(
        lambda m: m.name == argument or str(m.id) == argument, team.roles)

async def find_member_named(team: guilded.Server, argument: str, ctx=None):
    if argument.startswith("<@") and argument.endswith(">"):
        argument = argument.removeprefix("<@").removesuffix(">")
    match = _GENERIC_ID_REGEX.match(argument)
    result = None
    user_id = None
    if match:
        user_id = match.group(1)
        try:
            result = await team.getch_member(user_id)
        except (guilded.NotFound, guilded.BadRequest):
            pass

    if result is not None:
        return result
    try:
        argument = argument.replace("@", "")
    except:
        pass
    mem = guilded.utils.find(
        lambda m: m.name == argument or m.nick == argument or m.id ==
        argument, team.members)
    if mem is not None:
        return mem
    try:
        if len(ctx.message.mentions) != 0:
            return ctx.message.mentions[0]
        return None
    except:
        return None

async def user_not_found(ctx, member):
    color = guilded.Color.from_rgb(239, 83, 80)
    embed = guilded.Embed(
        description=
        f"Couldn\'t find a member with the name/id {member}\nTry putting in the user ID, if the mention doesn\'t work.",
        color=color)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
    await ctx.channel.send(embed=embed, silent=True)
    return

async def role_not_found(ctx, role):
    color = guilded.Color.from_rgb(239, 83, 80)
    embed = guilded.Embed(
        description=
        f"Couldn\'t find a role with the name/id {role}\nTry putting in the role ID, if the mention doesn\'t work.",
        color=color)
    embed.set_author(name=ctx.author,
                     icon_url=avatar_handler(ctx.author))
    await ctx.channel.send(embed=embed, silent=True)
    return


