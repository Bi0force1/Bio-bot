# setup imports
import discord
from discord.ext import commands
import psutil
import aiohttp
import asyncio
import socket
import struct
import os


processes = {
    "ark": {
        "process": "ArkAscendedServer.exe",
        "port": 7777,  # Default ARK query port
        "query_type": "ark"
    },
    "palworld": {
        "process": "PalServer-Win64-Shipping-Cmd.exe", 
        "port": 8211,  # Default Palworld game port (UDP)
        "query_port": 25575,  # RCON port for queries (TCP)
        "rest_api_port": 8212,  # REST API port (HTTP)
        "query_type": "palworld_rest",  # Use REST API as primary method
        "fallback_query": "palworld_rcon"  # Fallback to RCON if REST API fails
    },
    "enshrouded": {
        "process": "enshrouded.exe",
        "port": 15636,  # Default Enshrouded port  
        "query_type": "steam"
    }
}


class Hosting(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def query_steam_server(self, host="127.0.0.1", port=27015, timeout=5):
        """Query a Steam-based game server for player count using A2S_INFO protocol"""
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # A2S_INFO query packet
            query = b'\xFF\xFF\xFF\xFF\x54Source Engine Query\x00'
            
            # Send query
            sock.sendto(query, (host, port))
            
            # Receive response
            data, addr = sock.recvfrom(1024)
            sock.close()
            
            # Parse response (simplified)
            if len(data) > 6 and data[4] == 0x49:  # A2S_INFO response
                # Skip header and parse
                offset = 6
                # Skip server name (null-terminated string)
                while offset < len(data) and data[offset] != 0:
                    offset += 1
                offset += 1
                
                # Skip map name
                while offset < len(data) and data[offset] != 0:
                    offset += 1
                offset += 1
                
                # Skip folder name  
                while offset < len(data) and data[offset] != 0:
                    offset += 1
                offset += 1
                
                # Skip game name
                while offset < len(data) and data[offset] != 0:
                    offset += 1
                offset += 1
                
                if offset + 2 < len(data):
                    # Skip app ID (2 bytes)
                    offset += 2
                    # Get player count
                    players = data[offset] if offset < len(data) else 0
                    # Get max players
                    max_players = data[offset + 1] if offset + 1 < len(data) else 0
                    return players, max_players
                    
        except Exception as e:
            # Error querying server - silently handle
            pass
            
        return None, None

    async def query_ark_server(self, host="127.0.0.1", port=7777):
        """Query ARK server using RCON or Steam query (simplified version)"""
        # ARK uses Steam query protocol on query port
        return await self.query_steam_server(host, port + 1)  # ARK query port is usually game port + 1

    async def query_palworld_rcon(self, host="127.0.0.1", port=25575, password="", timeout=5):
        """Query Palworld server using RCON protocol"""
        try:
            # Simple RCON implementation for Palworld
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            
            # RCON packet structure: length(4) + id(4) + type(4) + body + null(2)
            request_id = 12345  # Use a specific ID to track
            auth_type = 3  # SERVERDATA_AUTH
            exec_type = 2  # SERVERDATA_EXECCOMMAND
            
            # Authentication packet - MUST be done properly
            if password:
                auth_packet = struct.pack('<iii', request_id, auth_type, 0) + password.encode('utf-8') + b'\x00\x00'
                length = len(auth_packet)
                full_packet = struct.pack('<i', length) + auth_packet
                sock.send(full_packet)
                
                # Read auth response and validate
                auth_response = sock.recv(1024)
                if len(auth_response) >= 12:
                    auth_length, auth_id, auth_type_resp = struct.unpack('<iii', auth_response[:12])
                    
                    # Check if authentication succeeded
                    if auth_id == -1:
                        sock.close()
                        return None, None
                    elif auth_id != request_id:
                        sock.close()
                        return None, None
                else:
                    sock.close()
                    return None, None
            else:
                sock.close()
                return None, None
            
            # Send ShowPlayers command with new request ID
            command_id = request_id + 1
            command = "ShowPlayers"
            exec_packet = struct.pack('<iii', command_id, exec_type, 0) + command.encode('utf-8') + b'\x00\x00'
            length = len(exec_packet)
            full_packet = struct.pack('<i', length) + exec_packet
            sock.send(full_packet)
            
            # Read command response
            response = sock.recv(4096)
            sock.close()
            
            # Parse response for player count
            if len(response) >= 12:
                try:
                    resp_length, resp_id, resp_type = struct.unpack('<iii', response[:12])
                    
                    # Extract the actual response string
                    response_str = response[12:].decode('utf-8', errors='ignore').rstrip('\x00')
                    
                    # If response is empty or just whitespace, it means no players online
                    if not response_str.strip():
                        return 0, 32  # Return 0 players, 32 max
                    
                    # Parse response for player count using multiple methods
                    player_count = 0
                    lines = response_str.strip().split('\n')
                    
                    # Method 1: Count lines with player info patterns
                    for line in lines:
                        line_lower = line.lower().strip()
                        if any(keyword in line_lower for keyword in ['name:', 'player', 'uid:', 'steamid:']):
                            if line_lower and not line_lower.startswith(('welcome', 'server', 'version')):
                                player_count += 1
                    
                    # Method 2: Try regex patterns if no players found
                    if player_count == 0:
                        import re
                        # Look for various player patterns
                        patterns = [
                            r'name:\s*([^\s,]+)',
                            r'player[^\s]*:\s*([^\s,]+)',
                            r'([^\s]+)\s*,\s*uid:',
                            r'([^\s]+)\s*,\s*steamid:'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, response_str, re.IGNORECASE)
                            if matches:
                                player_count = len(matches)
                                break
                    
                    # For max players, we'll use default or try to parse from server info
                    max_players = 32  # Default Palworld max
                    
                    return player_count, max_players
                    
                except Exception as parse_error:
                    # Even if parsing fails, if we got a response, assume 0 players
                    return 0, 32
            else:
                # If we got a connection but short response, assume 0 players
                return 0, 32
            
        except socket.timeout:
            return None, None
        except ConnectionRefusedError:
            return None, None
        except Exception as e:
            # If we authenticated but got an error during query, assume 0 players
            # This handles cases where the server is running but has issues
            if "Authentication successful" in str(e) or hasattr(e, 'errno'):
                return 0, 32
            
        return None, None

    async def query_palworld_rest_api(self, host="127.0.0.1", port=8212, timeout=5):
        """Query Palworld server using REST API for player information"""
        try:
            # Get REST API credentials from environment
            rest_username = os.environ.get("PALWORLD_REST_USERNAME", "admin")
            rest_password = os.environ.get("PALWORLD_REST_PASSWORD", "")
            
            if not rest_password:
                return None, None
            
            # Use aiohttp to make HTTP requests to the REST API with basic auth
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            auth = aiohttp.BasicAuth(rest_username, rest_password)
            
            async with aiohttp.ClientSession(timeout=timeout_config, auth=auth) as session:
                # Get server info and player list
                base_url = f"http://{host}:{port}/v1/api"
                
                # First get server info for max players
                async with session.get(f"{base_url}/info") as response:
                    if response.status == 401:
                        return None, None
                    elif response.status != 200:
                        return None, None
                        
                    server_info = await response.json()
                    
                    # Extract server name and version for reference
                    server_name = server_info.get("servername", "Unknown")
                    max_players = server_info.get("serverPlayerMaxNum", 32)
                    
                # Get current players
                async with session.get(f"{base_url}/players") as response:
                    if response.status == 401:
                        return None, None
                    elif response.status != 200:
                        return None, None
                        
                    players_data = await response.json()
                    
                    # Count current players
                    if isinstance(players_data, dict) and "players" in players_data:
                        current_players = len(players_data["players"])
                    elif isinstance(players_data, list):
                        current_players = len(players_data)
                    else:
                        current_players = 0
                    
                    return current_players, max_players
                    
        except aiohttp.ClientConnectorError:
            return None, None
        except aiohttp.ClientResponseError as e:
            return None, None
        except asyncio.TimeoutError:
            return None, None
        except Exception as e:
            return None, None

    async def get_server_player_count(self, server_name, server_info):
        """Get player count for a specific server"""
        try:
            if server_info["query_type"] == "steam":
                players, max_players = await self.query_steam_server(port=server_info["port"])
            elif server_info["query_type"] == "ark":
                players, max_players = await self.query_ark_server(port=server_info["port"])
            elif server_info["query_type"] == "palworld_rcon":
                query_port = server_info.get("query_port", 25575)
                rcon_password = os.environ.get("PALWORLD_RCON_PASSWORD", "")
                players, max_players = await self.query_palworld_rcon(port=query_port, password=rcon_password)
                
                # If RCON fails and we have a fallback, try it
                if (players is None or max_players is None) and "fallback_query" in server_info:
                    if server_info["fallback_query"] == "steam":
                        players, max_players = await self.query_steam_server(port=server_info["port"])
            elif server_info["query_type"] == "palworld_rest":
                query_port = server_info.get("rest_api_port", 8212)
                players, max_players = await self.query_palworld_rest_api(port=query_port)
                
                # If REST API fails and we have a fallback, try it
                if (players is None or max_players is None) and "fallback_query" in server_info:
                    if server_info["fallback_query"] == "palworld_rcon":
                        query_port = server_info.get("query_port", 25575)
                        rcon_password = os.environ.get("PALWORLD_RCON_PASSWORD", "")
                        players, max_players = await self.query_palworld_rcon(port=query_port, password=rcon_password)
            else:
                return None, None
                
            return players, max_players
        except Exception as e:
            return None, None


    @commands.command()
    async def server(self, ctx):
        running_processes = []

        for name, server_info in processes.items():
            process_name = server_info["process"]
            if any(proc.name() == process_name for proc in psutil.process_iter()):
                # Server is running, now get player count
                players, max_players = await self.get_server_player_count(name, server_info)
                
                if players is not None and max_players is not None:
                    running_processes.append(f"**{name}** ({players}/{max_players} players)")
                else:
                    running_processes.append(f"**{name}** (player count unavailable)")

        if running_processes:
            await ctx.send(f"The following server(s) are running:\n{chr(10).join(running_processes)}")
        else:
            await ctx.send("No specified servers are currently running.")

    @commands.command()
    async def players(self, ctx, server_name: str = None):
        """Get detailed player information for a specific server"""
        if server_name is None:
            server_list = ", ".join(processes.keys())
            await ctx.send(f"Please specify a server name. Available servers: {server_list}")
            return
            
        server_name = server_name.lower()
        if server_name not in processes:
            server_list = ", ".join(processes.keys())
            await ctx.send(f"Unknown server '{server_name}'. Available servers: {server_list}")
            return
            
        server_info = processes[server_name]
        process_name = server_info["process"]
        
        # Check if server is running
        if not any(proc.name() == process_name for proc in psutil.process_iter()):
            await ctx.send(f"**{server_name}** server is not currently running.")
            return
            
        # Get player count
        players, max_players = await self.get_server_player_count(server_name, server_info)
        
        if players is not None and max_players is not None:
            embed = discord.Embed(
                title=f"{server_name.title()} Server Status",
                color=discord.Color.green()
            )
            embed.add_field(name="Status", value="Online", inline=True)
            embed.add_field(name="Players", value=f"{players}/{max_players}", inline=True)
            embed.add_field(name="Port", value=server_info["port"], inline=True)
            
            if players == 0:
                embed.add_field(name="Activity", value="No players online", inline=False)
            elif players < max_players * 0.5:
                embed.add_field(name="Activity", value="Low activity", inline=False)
            elif players < max_players * 0.8:
                embed.add_field(name="Activity", value="Moderate activity", inline=False)
            else:
                embed.add_field(name="Activity", value="High activity", inline=False)
                
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"**{server_name}** is running but player count is unavailable. The server may not have query enabled or may be using a different query protocol.")

    @commands.command()
    async def help_server(self, ctx):
        """Display help for server monitoring commands"""
        embed = discord.Embed(
            title="Server Monitoring Commands",
            description="Commands for checking game server status and player counts",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="`!server`",
            value="Shows all running game servers with player counts",
            inline=False
        )
        
        embed.add_field(
            name="`!players <server_name>`",
            value="Get detailed information about a specific server\n**Available servers:** ark, palworld, enshrouded",
            inline=False
        )
        
        embed.add_field(
            name="Examples",
            value="`!server` - List all running servers\n`!players palworld` - Check Palworld server details",
            inline=False
        )
        
        embed.set_footer(text="Tip: Server queries may take a few seconds to complete")
        
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Hosting(client))

