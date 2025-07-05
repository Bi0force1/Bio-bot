# setup imports
import discord
from discord.ext import commands
from discord import Embed, Member
import asyncio
import os


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

    @commands.command()
    async def member_servers(self, ctx, member: discord.Member = None):
        """List all servers that a member is part of (visible to the bot) - sent via DM"""
        if member is None:
            member = ctx.author
        
        # Check if the user has permission to view other members' server lists
        if member != ctx.author and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to check other members' server lists.")
            return
        
        # Send confirmation in channel that command was received
        await ctx.send(f"📨 Sending server list for {member.display_name} via DM...")
        
        # Get all mutual guilds between the bot and the member
        mutual_guilds = []
        for guild in self.client.guilds:
            if guild.get_member(member.id):
                mutual_guilds.append(guild)
        
        if not mutual_guilds:
            try:
                await ctx.author.send(f"❌ {member.display_name} is not in any servers that I can see.")
            except discord.Forbidden:
                await ctx.send("❌ I couldn't send you a DM. Please check your privacy settings.")
            return
        
        # Create embed
        embed = discord.Embed(
            title=f"Server List for {member.display_name}",
            description=f"Servers that {member.display_name} shares with me",
            color=discord.Color.blue()
        )
        
        # Add member's avatar
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Add server information
        server_info = []
        for guild in mutual_guilds:
            guild_member = guild.get_member(member.id)
            if guild_member:
                # Get member's highest role in that server
                highest_role = guild_member.top_role.name if guild_member.top_role.name != "@everyone" else "No special roles"
                # Get join date
                join_date = guild_member.joined_at.strftime("%Y-%m-%d") if guild_member.joined_at else "Unknown"
                
                server_info.append(f"**{guild.name}**\n"
                                 f"├ Members: {guild.member_count}\n"
                                 f"├ Highest Role: {highest_role}\n"
                                 f"└ Joined: {join_date}")
        
        # Split into multiple fields if too many servers
        if len(server_info) <= 5:
            embed.add_field(
                name=f"Mutual Servers ({len(mutual_guilds)})",
                value="\n\n".join(server_info),
                inline=False
            )
        else:
            # Split into chunks of 5 servers per field
            for i in range(0, len(server_info), 5):
                chunk = server_info[i:i+5]
                field_name = f"Servers {i+1}-{min(i+5, len(server_info))}" if i > 0 else f"Mutual Servers ({len(mutual_guilds)})"
                embed.add_field(
                    name=field_name,
                    value="\n\n".join(chunk),
                    inline=False
                )
        
        # Add footer with additional info
        embed.set_footer(text=f"Requested by {ctx.author.display_name} • Total mutual servers: {len(mutual_guilds)}")
        
        # Send via DM with error handling
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I couldn't send you a DM. Please check your privacy settings and try again.")

    @commands.command()
    async def server_info(self, ctx, member: discord.Member = None):
        """Get detailed information about a member in the current server - sent via DM"""
        if member is None:
            member = ctx.author
            
        # Check permissions for viewing other members
        if member != ctx.author and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to check other members' information.")
            return
        
        # Send confirmation in channel that command was received
        await ctx.send(f"📨 Sending server info for {member.display_name} via DM...")
        
        embed = discord.Embed(
            title=f"Server Info for {member.display_name}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue()
        )
        
        # Basic info
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Username", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        
        # Server-specific info
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown", inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Highest Role", value=member.top_role.name, inline=True)
        
        # Roles (excluding @everyone)
        roles = [role.name for role in member.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(name=f"Roles ({len(roles)})", value=", ".join(roles), inline=False)
        
        # Status and activity
        status_emoji = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡", 
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        embed.add_field(name="Status", value=f"{status_emoji.get(member.status, '❓')} {member.status.name.title()}", inline=True)
        
        # Permissions check
        if member.guild_permissions.administrator:
            embed.add_field(name="Permissions", value="🛡️ Administrator", inline=True)
        elif member.guild_permissions.manage_guild:
            embed.add_field(name="Permissions", value="⚙️ Manage Server", inline=True)
        elif member.guild_permissions.manage_messages:
            embed.add_field(name="Permissions", value="🔧 Manage Messages", inline=True)
        
        # Send via DM with error handling
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I couldn't send you a DM. Please check your privacy settings and try again.")

    @commands.command()
    async def help_admin(self, ctx):
        """Display help for admin commands (admin only)"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ This command is only available to administrators.")
            return
            
        # Send confirmation in channel
        await ctx.send("📨 Sending admin command help via DM...")
        
        embed = discord.Embed(
            title="🛡️ Admin Commands",
            description="Administrative commands for server management (Admin Only)",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🔍 `!member_servers [member]`",
            value="List all servers that a member shares with the bot\n*Results sent via DM for privacy*",
            inline=False
        )
        
        embed.add_field(
            name="📋 `!server_info [member]`", 
            value="Get detailed information about a member in the current server\n*Results sent via DM for privacy*",
            inline=False
        )
        
        embed.add_field(
            name="🎭 `!group <keyword>`",
            value="Toggle gaming group roles\n**Available:** juicers, shooters, pga, palworld",
            inline=False
        )
        
        embed.add_field(
            name="🎨 `!color <color>`",
            value="Assign color roles (removes existing color roles)\n**Available:** red, orange, yellow, green, blue, purple, pink, grey, black, white",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Examples",
            value="`!member_servers @username` - Check user's servers\n`!server_info` - Your own server info\n`!group palworld` - Toggle Palworld role\n`!color blue` - Get blue color role",
            inline=False
        )
        
        embed.add_field(
            name="🔒 Privacy Notes",
            value="• Member information commands send results privately via DM\n• Only administrators can check other members' information\n• Users can always check their own information",
            inline=False
        )
        
        embed.set_footer(text="🛡️ Administrator Commands • Results sent privately for security")
        
        # Send via DM with error handling
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I couldn't send you a DM. Please check your privacy settings and try again.")

    @commands.command()
    async def help_user(self, ctx):
        """Display help for user commands available to everyone"""
        embed = discord.Embed(
            title="👥 User Commands",
            description="Commands available to all server members",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🎭 `!group <keyword>`",
            value="Toggle your gaming group roles\n**Available:** juicers, shooters, pga, palworld",
            inline=False
        )
        
        embed.add_field(
            name="🎨 `!color <color>`",
            value="Change your color role (removes existing color roles)\n**Available:** red, orange, yellow, green, blue, purple, pink, grey, black, white",
            inline=False
        )
        
        embed.add_field(
            name="📋 `!server_info`",
            value="Get your own server information\n*Results sent via DM for privacy*",
            inline=False
        )
        
        embed.add_field(
            name="🔍 `!member_servers`", 
            value="List all servers you share with the bot\n*Results sent via DM for privacy*",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Examples",
            value="`!group palworld` - Join/leave Palworld group\n`!color blue` - Get blue color role\n`!server_info` - Check your server details",
            inline=False
        )
        
        embed.set_footer(text="💡 Role changes are sent via DM • Use !help_server for game server commands")
        
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Admin(client))

