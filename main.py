# Import required libraries
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# set common variables
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
load_dotenv()

intents.message_content = True
intents.messages = True
intents.reactions = True
token = os.environ["TOKEN"]

# Run bot on discord
@client.event
async def on_ready():
    print("Fuck it, we'll do it live...")

@client.event
async def load_extensions():
  for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        await client.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loaded Cog: {filename[:-3]}")

async def main():
    async with client:
        await load_extensions()
        await client.start(token)

asyncio.run(main())