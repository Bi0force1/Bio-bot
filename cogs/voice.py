# Import required libraries
import discord
from discord.ext import commands
import time


class Voice(commands.Cog):
    def __init__(self, client):
        self.client = client
        # Dictionary to track created temporary channels
        self.temp_channels = {}
        # Name of the channel to monitor
        self.founders_channel_name = "Welcome to the Party, PALS"

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Event listener that triggers when a user's voice state changes
        (joins/leaves/moves between voice channels)
        """
        # Check if user joined a voice channel
        if after.channel is not None:
            await self.handle_voice_join(member, after.channel)
        
        # Check if user left a voice channel
        if before.channel is not None:
            await self.handle_voice_leave(member, before.channel)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """
        Event listener that triggers when a channel is updated (like name changes)
        """
        # Check if this is a voice channel we're tracking and the name changed
        if (isinstance(after, discord.VoiceChannel) and 
            after.id in self.temp_channels and 
            before.name != after.name):
            
            await self.handle_manual_rename(before, after)

    async def handle_voice_join(self, member, channel):
        """Handle when a user joins a voice channel"""
        # Check if the user joined the Founders Chat channel
        if channel.name == self.founders_channel_name:
            await self.create_user_channel(member, channel)
        
        # Check if user joined a temporary channel we're tracking
        elif channel.id in self.temp_channels:
            await self.add_user_to_channel_tracking(member, channel)

    async def handle_voice_leave(self, member, channel):
        """Handle when a user leaves a voice channel"""
        # Check if the channel is a temporary channel we created
        if channel.id in self.temp_channels:
            # Remove user from tracking
            await self.remove_user_from_channel_tracking(member, channel)
            
            # If the channel is now empty, delete it
            if len(channel.members) == 0:
                await self.delete_temp_channel(channel)
            # If the host left but channel isn't empty, transfer ownership
            elif self.temp_channels[channel.id]['creator'] == member.id:
                await self.transfer_channel_ownership(channel)

    async def create_user_channel(self, member, founders_channel):
        """Create a new temporary voice channel for the user"""
        try:
            guild = founders_channel.guild
            
            # Create the new channel name
            new_channel_name = f"{member.display_name}'s Chat"
            
            # Get the category of the founders channel (to keep organization)
            category = founders_channel.category
            
            # Create the new voice channel
            new_channel = await guild.create_voice_channel(
                name=new_channel_name,
                category=category,
                # Copy some settings from the founders channel
                bitrate=founders_channel.bitrate,
                user_limit=founders_channel.user_limit if founders_channel.user_limit else None
            )
            
            # Store the channel ID in our tracking dictionary with join time tracking
            current_time = time.time()
            self.temp_channels[new_channel.id] = {
                'creator': member.id,
                'channel': new_channel,
                'join_times': {member.id: current_time},  # Track when each user joined
                'manually_renamed': False,  # Track if channel was manually renamed
                'original_name_pattern': True  # Track if following original naming pattern
            }
            
            # Move the user to their new channel
            await member.move_to(new_channel)
            
            print(f"Created temporary channel '{new_channel_name}' for {member.display_name}")
            
        except discord.Forbidden:
            print(f"Bot lacks permissions to create voice channels or move members")
        except discord.HTTPException as e:
            print(f"Failed to create voice channel: {e}")
        except Exception as e:
            print(f"Unexpected error creating voice channel: {e}")

    async def add_user_to_channel_tracking(self, member, channel):
        """Add a user to the join time tracking for a temporary channel"""
        if channel.id in self.temp_channels:
            current_time = time.time()
            self.temp_channels[channel.id]['join_times'][member.id] = current_time
            print(f"{member.display_name} joined tracked channel: {channel.name}")

    async def handle_manual_rename(self, before, after):
        """Handle when a temporary channel is manually renamed"""
        channel_data = self.temp_channels[after.id]
        
        # Check if the name change follows the original pattern (owner's name + 's Chat)
        current_creator_id = channel_data['creator']
        guild = after.guild
        creator = guild.get_member(current_creator_id)
        
        if creator:
            expected_name = f"{creator.display_name}'s Chat"
            
            # If the new name doesn't match the expected owner pattern, mark as manually renamed
            if after.name != expected_name:
                channel_data['manually_renamed'] = True
                channel_data['original_name_pattern'] = False
                print(f"Channel '{before.name}' manually renamed to '{after.name}' - disabling auto-rename")
            else:
                # If it was renamed back to the owner pattern, re-enable auto-rename
                channel_data['manually_renamed'] = False
                channel_data['original_name_pattern'] = True
                print(f"Channel '{after.name}' renamed back to owner pattern - enabling auto-rename")

    async def remove_user_from_channel_tracking(self, member, channel):
        """Remove a user from the join time tracking"""
        if channel.id in self.temp_channels:
            join_times = self.temp_channels[channel.id]['join_times']
            if member.id in join_times:
                del join_times[member.id]
                print(f"{member.display_name} left tracked channel: {channel.name}")

    async def transfer_channel_ownership(self, channel):
        """Transfer ownership to the user who's been in the channel longest"""
        try:
            if channel.id not in self.temp_channels:
                return
            
            channel_data = self.temp_channels[channel.id]
            join_times = channel_data['join_times']
            
            # Find the user who joined earliest (excluding the leaving creator)
            current_creator = channel_data['creator']
            
            # Get all remaining users and their join times
            remaining_users = []
            for member in channel.members:
                if member.id in join_times and member.id != current_creator:
                    remaining_users.append((member, join_times[member.id]))
            
            if not remaining_users:
                # No one else to transfer to, channel will be deleted
                return
            
            # Sort by join time (earliest first) and get the longest-staying user
            remaining_users.sort(key=lambda x: x[1])
            new_owner = remaining_users[0][0]
            
            # Update the creator in our tracking
            old_creator_id = self.temp_channels[channel.id]['creator']
            self.temp_channels[channel.id]['creator'] = new_owner.id
            
            # Only rename if the channel hasn't been manually renamed
            if not channel_data.get('manually_renamed', False):
                old_name = channel.name
                new_name = f"{new_owner.display_name}'s Chat"
                
                await channel.edit(name=new_name)
                print(f"Transferred ownership and renamed '{old_name}' to '{new_name}' (new owner: {new_owner.display_name})")
            else:
                # Just transfer ownership without renaming
                guild = channel.guild
                old_creator = guild.get_member(old_creator_id)
                old_creator_name = old_creator.display_name if old_creator else "Unknown User"
                print(f"Transferred ownership of '{channel.name}' from {old_creator_name} to {new_owner.display_name} (custom name preserved)")
            
        except discord.Forbidden:
            print(f"Bot lacks permissions to edit voice channel: {channel.name}")
        except Exception as e:
            print(f"Error transferring channel ownership: {e}")

    async def delete_temp_channel(self, channel):
        """Delete a temporary voice channel when it becomes empty"""
        try:
            # Remove from our tracking dictionary
            if channel.id in self.temp_channels:
                creator_name = self.temp_channels[channel.id]['channel'].name
                del self.temp_channels[channel.id]
                
                # Delete the channel
                await channel.delete(reason="Temporary voice channel is empty")
                print(f"Deleted empty temporary channel: {creator_name}")
                
        except discord.Forbidden:
            print(f"Bot lacks permissions to delete voice channel: {channel.name}")
        except discord.NotFound:
            # Channel was already deleted
            if channel.id in self.temp_channels:
                del self.temp_channels[channel.id]
        except Exception as e:
            print(f"Error deleting temporary channel: {e}")

    @commands.command()
    async def voice_help(self, ctx):
        """Show help for voice channel management"""
        embed = discord.Embed(
            title="Voice Channel Management",
            description="Automatic voice channel creation system",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="How it works",
            value=f"• Join the **{self.founders_channel_name}** voice channel\n"
                  f"• A new private channel will be created: **Your Name's Chat**\n"
                  f"• You'll be automatically moved to your new channel\n"
                  f"• If the host leaves, ownership transfers to longest-staying user\n"
                  f"• **Manual rename disables auto-rename** (preserves custom names)\n"
                  f"• The channel will be deleted when everyone leaves",
            inline=False
        )
        
        embed.add_field(
            name="Features",
            value="• Automatic channel creation\n"
                  "• Smart ownership transfer when host leaves\n"
                  "• Respects manually renamed channels\n"
                  "• Join time tracking for fair ownership rotation\n"
                  "• Automatic cleanup when empty\n"
                  "• Maintains server organization\n"
                  "• Preserves voice quality settings",
            inline=False
        )
        
        embed.add_field(
            name="Custom Names",
            value="• Rename your channel to anything you want\n"
                  "• Auto-rename is **disabled** for custom names\n"
                  "• Example: 'Chris's Chat' → 'Dance Party' stays 'Dance Party'\n"
                  "• Ownership still transfers, but name is preserved",
            inline=False
        )
        
        embed.add_field(
            name="Commands",
            value="`!voice_status` - Show current temporary channels\n"
                  "`!voice_cleanup` - Force cleanup empty channels (Admin only)",
            inline=False
        )
        
        embed.set_footer(text="Voice management system active")
        await ctx.send(embed=embed)

    @commands.command()
    async def voice_status(self, ctx):
        """Show current temporary voice channels"""
        if not self.temp_channels:
            await ctx.send("No temporary voice channels are currently active.")
            return
        
        embed = discord.Embed(
            title="Active Temporary Voice Channels",
            color=discord.Color.green()
        )
        
        for channel_id, info in self.temp_channels.items():
            channel = info['channel']
            creator_id = info['creator']
            join_times = info.get('join_times', {})
            manually_renamed = info.get('manually_renamed', False)
            
            # Get creator member object
            creator = ctx.guild.get_member(creator_id)
            creator_name = creator.display_name if creator else "Unknown User"
            
            # Count current members and show join order
            member_count = len(channel.members)
            
            # Sort members by join time (earliest first)
            member_info = []
            for member in channel.members:
                if member.id in join_times:
                    join_time = join_times[member.id]
                    duration = int(time.time() - join_time)
                    mins, secs = divmod(duration, 60)
                    time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
                    member_info.append((member.display_name, join_time, time_str))
            
            # Sort by join time (earliest first)
            member_info.sort(key=lambda x: x[1])
            member_display = [f"{name} ({duration})" for name, _, duration in member_info]
            
            # Add rename status indicator
            rename_status = "🔒 Custom name (auto-rename disabled)" if manually_renamed else "🔄 Auto-rename enabled"
            
            embed.add_field(
                name=f"{channel.name}",
                value=f"**Creator:** {creator_name}\n"
                      f"**Members:** {member_count}\n"
                      f"**Users (by join time):** {', '.join(member_display) if member_display else 'None'}\n"
                      f"**Status:** {rename_status}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def voice_cleanup(self, ctx):
        """Force cleanup of empty temporary channels (Admin only)"""
        cleaned_count = 0
        
        # Make a copy of the keys to avoid dictionary size change during iteration
        channel_ids = list(self.temp_channels.keys())
        
        for channel_id in channel_ids:
            channel_info = self.temp_channels.get(channel_id)
            if channel_info:
                channel = channel_info['channel']
                
                # Check if channel still exists and is empty
                try:
                    # Refresh channel data
                    channel = await channel.guild.fetch_channel(channel.id)
                    if len(channel.members) == 0:
                        await self.delete_temp_channel(channel)
                        cleaned_count += 1
                except discord.NotFound:
                    # Channel was already deleted, remove from tracking
                    if channel_id in self.temp_channels:
                        del self.temp_channels[channel_id]
                        cleaned_count += 1
                except Exception as e:
                    print(f"Error during cleanup of channel {channel_id}: {e}")
        
        if cleaned_count > 0:
            await ctx.send(f"Cleaned up {cleaned_count} empty temporary voice channel(s).")
        else:
            await ctx.send("No empty temporary channels found to clean up.")

    @voice_cleanup.error
    async def voice_cleanup_error(self, ctx, error):
        """Handle errors for voice_cleanup command"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need administrator permissions to use this command.")


async def setup(client):
    await client.add_cog(Voice(client))