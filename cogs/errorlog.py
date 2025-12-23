import guilded
from guilded.ext import commands
import traceback
import logging
from discord_webhook import AsyncDiscordWebhook
import random
import string
import aiofiles
import os

class ErrorLog(commands.Cog):
    def __init__(self, bot, webhook_url):
        self.bot = bot
        self.webhook_url = webhook_url
        self.logger = logging.getLogger('guilded')
        self.logger.setLevel(logging.ERROR)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levellevelname)s - %(message)s'))
        self.logger.addHandler(handler)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        cog_name = ctx.cog.qualified_name if ctx.cog else 'Unknown'
        if cog_name == 'Unknown':
            return
        error_traceback = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        error_details = {
            'filename': getattr(error.__traceback__.tb_frame.f_code, 'co_filename', 'Unknown') if error.__traceback__ else 'Unknown',
            'line_number': getattr(error.__traceback__, 'tb_lineno', 'Unknown') if error.__traceback__ else 'Unknown',
            'error': str(error),
            'server_name': getattr(ctx.server, 'name', 'DM'),
            'server_id': getattr(ctx.server, 'id', 'DM'),
            'message_id': getattr(ctx.message, 'id', 'Unknown'),
            'message_link': f"https://www.guilded.gg/{ctx.server.id}/channels/{ctx.channel.id}/chat?messageId={ctx.message.id}" if ctx.message else 'Unknown',
            'cog_name': cog_name,
            'traceback': error_traceback
        }
        self.logger.error(f"Error in command {ctx.command}: {error_details}")

        # Generate a 6-digit random ID
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Create a txt file with error details and send it to webhook asynchronously
        async with aiofiles.open(f'error_details_{ctx.server.id}.txt', mode='w') as file:
            await file.write(f"Error in command {ctx.command}:\n"
                             f"File: {error_details['filename']}\n"
                             f"Line: {error_details['line_number']}\n"
                             f"Error: {error_details['error']}\n"
                             f"Server: {error_details['server_name']} (ID: {error_details['server_id']})\n"
                             f"Message ID: {error_details['message_id']}\n"
                             f"Message Link: {error_details['message_link']}\n"
                             f"Cog Name: {error_details['cog_name']}\n"
                             f"Traceback: {error_details['traceback']}")

        async with aiofiles.open(f'error_details_{ctx.server.id}.txt', mode='rb') as file:
            file_content = await file.read()
            await file.close()  # Explicitly close the file

        webhook = AsyncDiscordWebhook(url=self.webhook_url, content=f"Error ID: {random_id}")
        webhook.add_file(file=file_content, filename='error_details.txt')

        # Add an embed to the webhook
        embed = {
            "title": "Error Notification",
            "description": (f"Error in command {ctx.command}:\nServer: {error_details['server_name']} "
                            f"(ID: {error_details['server_id']})\nMessage Link: [link]({error_details['message_link']})"),
            "color": 0xff0000
        }
        webhook.embeds.append(embed)
        await webhook.execute()

        # Delete the file
        try:
            os.remove(f'error_details_{ctx.server.id}.txt')
        except:
            pass

        # Send a message in the ctx.channel
        embed = guilded.Embed(title="Error Notification",
                              description=f"An error occurred in the `{ctx.command}` command.\nPlease join the [support server](https://www.guilded.gg/karma/) and provide the following ID for assistance: `{random_id}`",
                              color=0xff0000)
        await ctx.channel.send(embed=embed)

# Directly use webhook URL
webhook_url = ''
def setup(bot):
    bot.add_cog(ErrorLog(bot, webhook_url))
