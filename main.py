import guilded
from discord_webhook import AsyncDiscordWebhook
from guilded.ext import commands
import os, sys, asyncio, json, traceback, itertools
import datetime
from web.app import create_app
import socket

# keep.alive()
owner = ["dzOn13bm", "4WG7wrP4"]
# import dtbs as db
import constants as var
import logging, zipfile

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s | %(name)s | %(message)s')  # ,    level=logging.DEBUG,   datefmt='%Y-%m-%d %H:%M:%S', filename="log.txt")


def log_exceptions(type, value, tb):
    for line in traceback.TracebackException(type, value,
                                             tb).format(chain=True):
        logging.exception(line)
    logging.exception(value)

    sys.__excepthook__(type, value, tb)  # calls default excepthook


sys.excepthook = log_exceptions
traceback.print_exc()
default_prefix = "."


def generate_prefix_variants(prefix):
    return [''.join(variant) for variant in itertools.product(*((char.lower(), char.upper()) for char in prefix))]


def is_owner(id):
    if id in owner:
        return True
    return False


async def guild_prefix_single(_bot, message):
    if not message.guild:
        # return commands.when_mentioned_or(var.DEFAULT_PREFIX)(_bot, message)
        return var.DEFAULT_PREFIX

    prefix = os.path.exists(f"Database/Prefixes/{message.guild.id}.json")

    if prefix is True:
        json_file = open(f"Database/Prefixes/{message.guild.id}.json", "r")
        json_content = json.load(json_file)
        json_file.close()

    if not prefix:
        # return commands.when_mentioned_or(var.DEFAULT_PREFIX)(_bot, message)
        return var.DEFAULT_PREFIX

    # return commands.when_mentioned_or(prefix_doc["prefix"])(_bot, message)
    return json_content["prefix"]


async def guild_prefix(_bot, message):
    if not message.guild:
        # return commands.when_mentioned_or(var.DEFAULT_PREFIX)(_bot, message)
        return [
            "<@4ZRw5qp4> ", "<@4ZRw5qp4>", "@Katana ", "@Katana", f"{var.DEFAULT_PREFIX} ", var.DEFAULT_PREFIX
        ]

    # prefix_doc = await db.PREFIXES.find_one({"_id": message.guild.id})
    prefix = os.path.exists(f"Database/Prefixes/{message.guild.id}.json")

    if prefix is True:
        json_file = open(f"Database/Prefixes/{message.guild.id}.json", "r")
        json_content = json.load(json_file)
        json_file.close()
    if not prefix:
        # return commands.when_mentioned_or(var.DEFAULT_PREFIX)(_bot, message)
        return [
            "<@4ZRw5qp4> ", "<@4ZRw5qp4>", "@Katana ", "@Katana", f"{var.DEFAULT_PREFIX} ", var.DEFAULT_PREFIX
        ]

    # return commands.when_mentioned_or(prefix_doc["prefix"])(_bot, message)
    return [
        "<@4ZRw5qp4> ", "<@4ZRw5qp4>", "@Katana ", "@Katana", f'{json_content["prefix"]} ',
        f'{json_content["prefix"]}'
    ]


cogs = [
    'cogs.mod', 'cogs.tictactoe', 'cogs.strike', 'cogs.snipe', 'cogs.help',
    'cogs.animation', 'cogs.4gewinnt'
]  # 'cogs' signifies the name of the folder, 'x' signifies the file name.
client = commands.Bot(command_prefix=guild_prefix, case_insensitive=True)
client.remove_command("help")
activity_status = "YOUR BOT ACTIVITY"


@client.event
async def on_ready():
    if not client.user:
        await asyncio.sleep(5)
    client.devids = []
    print(client.user)
    print(f"Running guilded.py version", guilded.__version__)
    try:
        print(f'Logged in as: {client.user.name}')
        print(f'With ID: {client.user.id}')
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    client.load_extension(f'cogs.{filename[:-3]}')

                except Exception as e:
                    print(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(
                        exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
        print("Loaded all Cogs")
    # logging.getLogger().setLevel(logging.INFO)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    # server = await client.fetch_server('rRp93Ddl')
    # devroleid = 27270298
    # devrole = await server.getch_role(devroleid)
    devids = []
    # for member in devrole.members:
    #    devids.append(member.id)
    for id in owner:
        if id not in devids:
            devids.append(id)
    client.devids = devids
    print("Reloaded all Cogs")


local_cache = {

}


@client.listen("on_message")
async def on_msg(message):
    current_time = datetime.datetime.now()
    try:
        if message.server.id in local_cache:
            difference = current_time - local_cache[message.server.id]
            if difference.total_seconds() >= 60:
                await message.server.fill_roles()
                await message.server.fill_members()
                local_cache[message.server.id] = current_time
        else:
            raise KeyError("Server roles haven\'t been fetched yet.")



    except KeyError as e:
        await message.server.fill_roles()
        await message.server.fill_members()
        local_cache[message.server.id] = current_time
    send = False
    msg = str(message.content).rstrip()
    new_msg = msg.split(" ")
    if len(new_msg) == 1:
        if len(message.raw_mentions
               ) == 1 and client.user.id in message.raw_mentions and message.author.id != client.user.id:
            send = True
            embed = guilded.Embed(
                title="Huh? You pinged me?",
                description=
                f"My prefix for this guild is {await guild_prefix_single(client, message)}",
                color=guilded.Colour.dark_theme_embed())
        if send:
            await message.reply(embed=embed, silent=True)

    if len(message.replied_to_ids) >= 1 and message.author_id in client.devids[0]:
        rt = message.replied_to_ids
        rt = [(await message.channel.fetch_message(value)) for value in rt
              if value is not None]
        rts = rt
        for rt in rts:
            rt = [rt, 0]
            if message.content == 'delete':
                await rt[0].delete()
                await message.add_reaction(90001164)
                await message.delete()
            if rt[0].author_id == client.user.id:
                if message.content.splitlines(
                )[0] == 'edit' and message.author_id in client.devids[0]:
                    nm = message.content.splitlines()
                    em = []
                    del nm[0]
                    for m in nm.copy():
                        if m.startswith('guilded.Embed('):
                            try:
                                em.append(eval(m))
                                nm.remove(m)
                            except:
                                pass
                    if len(em) == 0:
                        em = None
                    nm = [value for value in nm if value.strip() != '']
                    if em:
                        await rt[0].edit('\n'.join(nm), embeds=em)
                    else:
                        await rt[0].edit('\n'.join(nm))
                    await message.add_reaction(90001164)
                    await message.delete()


@client.command()
# @commands.is_owner()
async def load(ctx, extension):
    owner = is_owner(ctx.message.author.id)
    if not owner:
        return
    client.load_extension(f"cogs.{extension}")
    embed = guilded.Embed(title='Load',
                          description=f'{extension} successfully loaded',
                          color=0xff00c8)
    await ctx.send(embed=embed, silent=True)


@client.command()
# @commands.is_owner()
async def reload(ctx, extension):
    owner = is_owner(ctx.message.author.id)
    if not owner:
        return
    client.reload_extension(f"cogs.{extension}")
    embed = guilded.Embed(title='Reload',
                          description=f'{extension} successfully reloaded',
                          color=0xff00c8)
    await ctx.send(embed=embed, silent=True)


@client.command()
# @commands.is_owner()
async def unload(ctx, extension):
    owner = is_owner(ctx.message.author.id)
    if not owner:
        return
    client.unload_extension(f"cogs.{extension}")
    embed = guilded.Embed(title='Unload',
                          description=f'{extension} successfully unloaded',
                          color=0xff00c8)
    await ctx.send(embed=embed, silent=True)


@client.command()
# @commands.is_owner()
async def loadall(ctx):
    owner = is_owner(ctx.message.author.id)
    if not owner:
        return
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.load_extension(f'cogs.{filename[:-3]}')
            except:
                pass
    await ctx.message.add_reaction(90002171)


@client.command()
# @commands.is_owner()
async def unloadall(ctx):
    owner = is_owner(ctx.message.author.id)
    if not owner:
        return
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.unload_extension(f'cogs.{filename[:-3]}')
            except:
                pass
    await ctx.message.add_reaction(90002171)


@client.command()
# @commands.is_owner()
async def reloadall(ctx):
    owner = is_owner(ctx.message.author.id)
    if not owner:
        return
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.reload_extension(f'cogs.{filename[:-3]}')
            except:
                pass
    await ctx.message.add_reaction(90002171)


@client.command(name='eval',
                aliases=['exec'],
                description='eval/exec something for devs only')
async def eval_command(ctx: commands.Context, *, code: str):
    async def evalcheck(userid):
        return userid in client.devids[0]

    async def aexec(code, message, user, replies):
        exec(
            f'async def __ex(message, user, replies):\n    ' +
            (''.join(f'\n    {l}' for l in code.split('\n'))).strip(),
            globals(), locals())
        return await locals()['__ex'](message, user, replies)

    prefix = ctx.clean_prefix
    cmd = ((ctx.message.content)[len(prefix) + 4:]).strip()
    if await evalcheck(ctx.author.id):
        try:
            # Execute the async code using aexec()
            ### create some useful locals
            replies = []
            user = None
            for msg in ctx.message.replied_to_ids:
                msg = await ctx.channel.fetch_message(msg)
                replies.append(msg)
            if len(replies) == 1:
                user = replies[0].author
            result = await aexec(cmd, ctx.message, user, replies)
            if result is not None:
                # Send the result as a message
                await ctx.send(f'**Result:**\n```\n{result}\n```')
        except Warning as w:
            # result = ("".join(traceback.format_exception(w, w, w.__traceback__))).replace('`', '\`')
            # await ctx.send(f'**Eval ran with a warning:**\n\n```\n{result}\n```')
            await ctx.message.add_reaction(90002078)
            raise w
        except Exception as e:
            # result = ("".join(traceback.format_exception(e, e, e.__traceback__))).replace('`', '\`')
            # await ctx.send(f'**Eval failed with an Exception:**\n\n```\n{result}\n```')
            await ctx.message.add_reaction(90002175)
            raise e
        else:
            await ctx.message.add_reaction(90002171)
    else:
        await ctx.send("You are not authorized to use this command.")


async def get_all_ips():
    """Get all IP addresses of the machine."""
    ips = []
    try:
        hostname = socket.gethostname()
        for addr in socket.gethostbyname_ex(hostname)[2]:
            if not addr.startswith("127."):  # Exclude localhost
                ips.append(addr)
    except Exception as e:
        ips.append("127.0.0.1")  # Fallback to localhost
    for ip in ips:
        print(f"Running on http://{ip}:8000")


async def main():
    app = create_app(client)
    bot_task = asyncio.create_task(
        client.start(os.environ["token"]))
    app_task = asyncio.create_task(app.run_task(host='0.0.0.0', port=8000, debug=True))
    ip_task = asyncio.create_task(get_all_ips())

    await asyncio.gather(bot_task, app_task, ip_task)


if __name__ == '__main__':
    asyncio.run(main())