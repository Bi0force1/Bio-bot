# Import required libraries
import discord
from discord.ext import commands
import random

class Funny(commands.Cog):
    def __init__(self, client):
        self.client = client

# Water / Hydration
    @commands.command()
    async def water(self, ctx):
        response = [ 
            "Hydrate before you Die-drate!!!",
            "Enjoy a nice glass of water!!!",
            "Don't stay thirsty, have some water!!!",
            "I could go for a swim!!!",
            "Time to refill your water!!!",
            "You look thirsty...",
            "HYDRATION!!!" ]
        await ctx.send(f"{random.choice(response)}")


# Goat Facts
    @commands.command()
    async def goat(self, ctx):
        response = [         
            ("In 1966 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>"),
            "In 1967 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1968 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1969 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1970 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1971 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1972 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1973 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1974 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1975 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1976 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1977 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1978 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1979 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1980 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1981 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1982 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1983 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1984 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1985 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1986 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1987 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1988 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1989 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1990 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1991 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1992 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1993 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1994 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1995 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1996 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1997 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 1998 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 1999 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2000 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2001 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2002 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2003 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2004 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2005 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2006 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2007 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2008 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2009 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2010 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2011 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2012 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2013 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2014 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2015 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2016 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2017 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2018 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2019 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2020 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2021 the Gävlebocken was burned <a:gavlebocken_fire:1171975133603307570>",
            "In 2022 the Gävlebocken survived!!! <:Gavlebocken:1171830684231401483>",
            "In 2023 the Gävlebocken survived, but the birds ate all his straw!!! <:Gavlebocken:1171830684231401483>"
            ]

        await ctx.send(f"{random.choice(response)}")


    @commands.command()
    async def goatcam(self, ctx):
        response = [ "https://www.youtube.com/live/RXIsDUtQIhQ?si=DpZnY64FFOT1gnqu" ]
        await ctx.send(f"{(response)}")


    @commands.command()
    async def ilyft(self, ctx):
        response = "You've got quite a nice set yourself!!!"
        await ctx.send(f"{(response)}")


    @commands.command()
    async def coin(self, ctx: commands.Context):
        outcome = random.choice(["Heads", "Tails"])
        await ctx.send(f'{ctx.author.mention} flipped a coin and got **{outcome}**!')


    @commands.command(name='dice')
    async def dice(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception as e:
            await ctx.send('Format has to be in #d#')
            return
        results = [random.randint(1, limit) for _ in range(rolls)]
        result_str = ', '.join(str(result) for result in results)
        total = sum(results)
        await ctx.send(f'{ctx.author.mention} rolled: {result_str}\nFor a total of: {total}')


    @commands.command()
    async def help_bot(self, ctx):
        """Main help command - shows all available help categories"""
        embed = discord.Embed(
            title="🤖 Bio-bot Help Center",
            description="Your friendly multi-purpose Discord bot for gaming communities and wellness!",
            color=discord.Color.purple()
        )
        
        # Add bot avatar/thumbnail if available
        if self.client.user.avatar:
            embed.set_thumbnail(url=self.client.user.avatar.url)
        
        embed.add_field(
            name="🎮 **Server Monitoring**",
            value="`!help_server` - Game server status and player counts",
            inline=False
        )
        
        embed.add_field(
            name="👥 **User Commands**",
            value="`!help_user` - Role management and personal info commands",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Admin Commands**",
            value="`!help_admin` - Administrative functions (Admin only)",
            inline=False
        )
        
        embed.add_field(
            name="🎲 **Fun & Wellness**",
            value="`!water` - Hydration reminders\n`!goat` - Random Gävlebocken facts\n`!goatcam` - Live goat cam\n`!weather <city>` - Weather information\n`!workout` - Random workout suggestions\n`!coin` - Flip a coin\n`!dice <#d#>` - Roll dice (e.g., !dice 2d6)",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Quick Server Check**",
            value="`!server` - See all running game servers right now",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ **About Bio-bot**",
            value="🎯 Server monitoring for ARK, Palworld & Enshrouded\n💪 Health & wellness reminders\n🎭 Role management system\n🌤️ Weather updates\n🔒 Privacy-focused (sensitive data sent via DM)",
            inline=False
        )
        
        embed.set_footer(text="💡 Use the specific help commands above for detailed information about each category")
        
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Funny(client))