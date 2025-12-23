import sys, subprocess
import checksfrfr
import guilded
from guilded.ext import commands, tasks
import os
import random
import asyncio
from gil_utility.gperms import *

class Status(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.status_task.start()
        self.statuses = [{"content":"_servers_ servers | .help", "emote":"1260354"},
                         {"content": "katana.pages.dev | .help", "emote": "1260354"}]
        self.number = 0
    def cog_unload(self):
        self.status_task.cancel()

    @tasks.loop(seconds=120)
    async def status_task(self):
      await self.client.wait_until_ready()
      servers = await self.client.fetch_servers()
      try:
        await self.client.set_status(emote=self.statuses[self.number]["emote"], content=self.statuses[self.number]["content"].replace("_servers_", str(len(servers))))
      except Exception as e:
        print(e)
      if self.number == 1:
        self.number = 0
      else:
        self.number +=1


def setup(client):
    client.add_cog(Status(client))