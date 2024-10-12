import discord
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lockdown_mode = False
        self.anti_spam_enabled = False
        self.anti_nuke_enabled = False
        self.spam_threshold = 5
        self.spam_timeframe = 10
        self.message_counts = {}
        self.last_channel = None

    @commands.command(name='lockdown')
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx, status: str):
        owner = ctx.guild.owner
        if status.lower() == 'on':
            if self.lockdown_mode:
                await ctx.send("Lockdown mode is already enabled.")
                return

            self.lockdown_mode = True

            # Create or find the maintenance channel
            maint_channel = discord.utils.get(ctx.guild.channels, name='🚧-maintenance')
            if maint_channel is None:
                maint_channel = await ctx.guild.create_text_channel('🚧-maintenance')

            # Hide all channels from everyone except the owner
            for channel in ctx.guild.channels:
                if channel != maint_channel:
                    await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                    for role in ctx.guild.roles:
                        await channel.set_permissions(role, view_channel=False)
                else:
                    await channel.set_permissions(owner, view_channel=True, send_messages=True)

            # Restrict the ability to send invites, join voice channels, etc.
            for role in ctx.guild.roles:
                if role != ctx.guild.default_role:
                    await role.edit(permissions=role.permissions.update(create_instant_invite=False, connect=False))

            await ctx.send("Server lockdown enabled. All channels are hidden except for the maintenance channel, visible only to the server owner.")

        elif status.lower() == 'off':
            if not self.lockdown_mode:
                await ctx.send("Lockdown mode is not enabled.")
                return

            self.lockdown_mode = False

            # Restore view permissions to all channels
            for channel in ctx.guild.channels:
                await channel.set_permissions(ctx.guild.default_role, overwrite=None)
                for role in ctx.guild.roles:
                    await channel.set_permissions(role, overwrite=None)

            # Restore permissions for sending invites and joining voice channels
            for role in ctx.guild.roles:
                if role != ctx.guild.default_role:
                    await role.edit(permissions=role.permissions.update(create_instant_invite=True, connect=True))

            maint_channel = discord.utils.get(ctx.guild.channels, name='🚧-maintenance')
            if maint_channel:
                await maint_channel.delete()

            await ctx.send("Server lockdown disabled. All channels are now visible.")

        else:
            await ctx.send("Invalid status. Use 'on' or 'off'.")

    @commands.command(name='antispam')
    @commands.has_permissions(administrator=True)
    async def antispam(self, ctx, status: str):
        if status.lower() == 'on':
            self.anti_spam_enabled = True
            await ctx.send("Anti-spam protection enabled.")
        elif status.lower() == 'off':
            self.anti_spam_enabled = False
            await ctx.send("Anti-spam protection disabled.")
        else:
            await ctx.send("Invalid status. Use 'on' or 'off'.")

    @commands.command(name='antinuke')
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx, status: str):
        if status.lower() == 'on':
            self.anti_nuke_enabled = True
            await ctx.send("Anti-nuke protection enabled.")
        elif status.lower() == 'off':
            self.anti_nuke_enabled = False
            await ctx.send("Anti-nuke protection disabled.")
        else:
            await ctx.send("Invalid status. Use 'on' or 'off'.")

    @commands.command(name='nuke')
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx, *, args: str):
        if '|' not in args:
            await ctx.send("Invalid format. Use `.nuke <channel name> | <what to spam in all channels>`")
            return

        channel_name, spam_message = args.split('|', 1)
        channel_name = channel_name.strip()
        spam_message = spam_message.strip()

        # Delete all channels
        for channel in ctx.guild.channels:
            await channel.delete()

        # Create 30 new text channels and spam each one
        for i in range(30):
            new_channel = await ctx.guild.create_text_channel(f"{channel_name}-{i+1}")
            await new_channel.send(spam_message)

        await ctx.send("Nuke completed. Created 30 new channels and spammed them.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.anti_spam_enabled:
            now = asyncio.get_event_loop().time()
            user_id = message.author.id
            if user_id not in self.message_counts:
                self.message_counts[user_id] = []
            self.message_counts[user_id].append(now)
            self.message_counts[user_id] = [timestamp for timestamp in self.message_counts[user_id] if now - timestamp < self.spam_timeframe]

            if len(self.message_counts[user_id]) > self.spam_threshold:
                await message.author.ban(reason="Anti-spam system triggered")
                await message.channel.send(f"{message.author} was banned for spamming.")
                del self.message_counts[user_id]

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if hasattr(self, 'anti_nuke_enabled') and self.anti_nuke_enabled:
            if not getattr(self, 'last_channel', None):
                self.last_channel = channel

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if hasattr(self, 'anti_nuke_enabled') and self.anti_nuke_enabled:
            if getattr(self, 'last_channel', None):
                # Check if more than 10 channels were deleted in a short time
                deleted_channels = [channel]
                for ch in channel.guild.channels:
                    if ch.created_at < (discord.utils.utcnow() - datetime.timedelta(seconds=30)):
                        deleted_channels.append(ch)

                if len(deleted_channels) > 10:
                    await channel.guild.create_text_channel(name="**CHANNELS RESTORED**")
                    await channel.guild.create_voice_channel(name="**VOICE CHANNEL RESTORED**")
                    await channel.send(f"**Anti-Nuke System Activated!** More than 10 channels were deleted.")
                    
                self.last_channel = None

def setup(bot):
    bot.add_cog(Security(bot))
