import discord
from discord.ext import commands
import json
import os
import asyncio
import aiohttp
from decouple import config
from discord.errors import Forbidden, HTTPException

rate_limits = {}

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forced_nicks = {}
        self.infectoken = config("token")

    @commands.command(name='savebans', aliases=['saveban'], brief="Save bans list", usage=".saveban <filename>")
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def savebans(self, ctx, file_name):
        """
        Save the list of banned users to a JSON file.
        """
        try:
            ban_list = await ctx.guild.bans()
            data = [{"id": entry.user.id, "reason": str(entry.reason)} for entry in ban_list]
            with open(f'{file_name}.json', 'w') as f:
                json.dump(data, f)
            await ctx.send(f'Ban list has been saved to {file_name}.json')
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')

    @commands.command(name='exportbans', aliases=['exportban'], brief="Export bans list", usage=".exportban <filename>")
    @commands.has_permissions(ban_members=True)
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def exportbans(self, ctx, file_name):
        """
        Export the list of banned users from a JSON file and reapply bans to the server.
        """
        try:
            if not os.path.isfile(f'{file_name}.json'):
                await ctx.send(f'File {file_name}.json does not exist.')
                return

            with open(f'{file_name}.json', 'r') as f:
                ban_list = json.load(f)

            async with aiohttp.ClientSession() as session:
                for ban_entry in ban_list:
                    user_id = ban_entry["id"]
                    if user_id in rate_limits and rate_limits[user_id] > datetime.now():
                        await asyncio.sleep((rate_limits[user_id] - datetime.now()).total_seconds())

                    try:
                        async with session.get(f"https://discord.com/api/v10/users/{user_id}") as response:
                            if response.status == 429:
                                retry_after = int(response.headers.get("Retry-After"))
                                rate_limits[user_id] = datetime.now() + timedelta(seconds=retry_after)
                                await asyncio.sleep(retry_after)
                                continue 

                            user_data = await response.json()

                        user = self.bot.get_user(user_id)
                        if user is None:
                            user = await self.bot.fetch_user(user_id)

                        await ctx.guild.ban(user, reason=ban_entry["reason"])

                    except Exception as e:
                        await ctx.send(f'An unexpected error occurred: {e}', delete_after=30)

            await ctx.send(f'Ban list has been imported from {file_name}.json', delete_after=30)

        except Exception as e:
            await ctx.send(f'An unexpected error occurred: {e}')

    @commands.command(name='forcenick', aliases=['fucknick','fn'], brief="Force a user's nickname", usage=".forcenick <mention.user> <nick.name>")
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def forcenick(self, ctx, user: discord.Member, *, nickname: str):
        """
        Force a specific user's nickname to the provided value.
        """
        self.forced_nicks[user.id] = nickname
        try:
            await user.edit(nick=nickname)
            await ctx.send(f"Forced nickname '{nickname}' on {user.display_name}.")
        except discord.Forbidden:
            await ctx.send("I don't have permissions to edit nicknames.")

    @commands.command(name='stopforcenick', aliases=['sfn','stopfucknick'], brief="Stop forcing the nickname of a user", usage=".stopforcenick <mention.user>")
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def stopforcenick(self, ctx, user: discord.Member):
        """
        Stop forcing the nickname of a specific user.
        """
        if user.id in self.forced_nicks:
            del self.forced_nicks[user.id]
            try:
                await user.edit(nick=None)
                await ctx.send(f"Stopped forcing nickname on {user.display_name}.")
            except discord.Forbidden:
                await ctx.send("I don't have permissions to edit nicknames.")
        else:
            await ctx.send(f"No forced nickname found for {user.display_name}.")

    @commands.command(name="kick", usage="<@member> [reason]", description="Kick a user from the server")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def kick(self, ctx, user: discord.Member, *, reason: str = None):
        """
        Kick a user from the server with an optional reason.
        """
        await user.kick(reason=reason)
        await ctx.send(f"- {user.name} has been kicked.\nReason: {reason}")

    @commands.command(name="softban", usage="<@member> [reason]", description="Softban a user (ban and immediately unban)")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def softban(self, ctx, user: discord.Member, *, reason: str = None):
        """
        Softban a user by banning and then immediately unbanning them. 
        This will remove their messages.
        """
        await user.ban(reason=reason)
        await user.unban()
        await ctx.send(f"- {user.name} has been softbanned.\nReason: {reason}", delete_after=30)

    @commands.command(name="ban", aliases=['machuda','nikal'], usage="<@member> [reason]", description="Ban a user from the server")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def ban(self, ctx, user: discord.Member, *, reason: str = None):
        """
        Ban a user from the server with an optional reason.
        """
        await user.ban(reason=reason)
        await ctx.send(f"- {user.name} has been banned.\nReason: {reason}", delete_after=30)

    @commands.command(name="unban", usage="<user_id>", description="Unban a user by their ID")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def unban(self, ctx, user_id: int):
        """
        Unban a user from the server by their user ID.
        """
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.id == user_id:
                await ctx.guild.unban(user)
                await ctx.send(f"- {user.name} has been unbanned", delete_after=30)
                return
        await ctx.send(f"No banned user with the ID {user_id} was found", delete_after=30)

    @commands.command(name="mute", usage="<user> <time>", description="Mute a user for a specified duration")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.check(lambda ctx: ctx.author.id == int(config("userid")))
    async def mute(self, ctx, user: discord.Member, time: int):
        """
        Mute a user for a specified duration. Automatically creates a 'Muted' role if it doesn't exist.
        """
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if role is None:
            role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False)
        
        await user.add_roles(role)
        await ctx.send(f"Muted {user.mention} for {time} seconds.", delete_after=30)
        await asyncio.sleep(time)
        await user.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.id in self.forced_nicks and after.nick != self.forced_nicks[after.id]:
            try:
                await after.edit(nick=self.forced_nicks[after.id])
            except discord.Forbidden:
                pass

    @forcenick.error
    async def forcenick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need to have admin permissions.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user or nickname provided.")
        else:
            await ctx.send("An error occurred while executing the command.")

    @stopforcenick.error
    async def stopforcenick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need to have admin permissions to use this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user provided.")
        else:
            await ctx.send("An error occurred while executing the command.")

def setup(bot):
    bot.add_cog(Admin(bot))
