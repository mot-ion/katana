import guilded, os, discord_webhook, io, json
from PIL import Image
webhooks = [""]
current = 0
async def upload_file(attachment, filename="image.png"):
  global webhooks
  global current
  webhook = discord_webhook.AsyncDiscordWebhook(url=webhooks[current])
  if current < len(webhooks) - 1:
    current += 1
  else:
    current = 0
  webhook.add_file(file=attachment, filename=filename)
  response = await webhook.execute()
  obj = json.loads(response.content)
  return obj["attachments"][0]["url"]
  