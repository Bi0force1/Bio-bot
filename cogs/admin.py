# setup imports
import discord
from discord.ext import commands
from discord import Embed, Member
import asyncio
import os

# set common variables
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)


role_name = {
"juicers":int(os.environ["Juicers"]),
"shooters":int(os.environ["Shooters"]),
"pga":int(os.environ["pga"]),
"palworld":int(os.environ["Palworld"])
}

role_color = {
"red":int(os.environ["red"]),
"orange":int(os.environ["orange"]),
"yellow":int(os.environ["yellow"]),
"green":int(os.environ["green"]),
"blue":int(os.environ["blue"]),
"purple":int(os.environ["purple"]),
"pink":int(os.environ["pink"]),
"grey":int(os.environ["grey"]),
"black":int(os.environ["black"]),
"white":int(os.environ["white"])
}


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def group(self, ctx, keyword: str):        
        role_id = role_name.get(keyword)
        
        if role_id:
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            
            if role:
                if role in ctx.author.roles:
                    await ctx.author.remove_roles(role)
                    await ctx.author.send(f'Removed role: {role.name}')
                else:
                    await ctx.author.add_roles(role)
                    await ctx.author.send(f'Added role: {role.name}')
            else:
                await ctx.author.send(f'Role with ID "{role_id}" not found.')
        else:
            await ctx.author.send('Invalid keyword. Please use a valid keyword.')

    @commands.command()
    async def color(self, ctx, color: str):
        role_id = role_color.get(color.lower())

        if role_id:
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            
            if role:
                if role in ctx.author.roles:
                    await ctx.author.send(f'{ctx.author.mention}, you already have the {role.name} role.')
                    return

                # Remove existing color roles
                existing_roles = [discord.utils.get(ctx.guild.roles, id=int(id)) for id in role_color.values()]
                for existing_role in existing_roles:
                    if existing_role in ctx.author.roles:
                        await ctx.author.remove_roles(existing_role)

                # Add the new role
                await ctx.author.add_roles(role)
                await ctx.author.send(f'{ctx.author.mention} has been added to the {role.name}!')

            else:
                await ctx.author.send(f'Role with ID "{role_id}" not found.')
        else:
            await ctx.author.send(f'Color "{color}" not recognized.')


async def setup(client):
    await client.add_cog(Admin(client))
    
