import random
from constants import DEFAULT_PREFIX
#from dtbs import PREFIXES
import os, json


async def get_prefix(ctx):
    prefix = os.path.exists(f"Database/Prefixes/{ctx.guild.id}.json")
    

    if prefix is True:
        json_file = open(f"Database/Prefixes/{ctx.guild.id}.json", "r")
        json_content = json.load(json_file)
        json_file.close()
        return json_content["prefix"]
    else:
        return DEFAULT_PREFIX