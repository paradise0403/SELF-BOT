import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os



class StatusRotator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_rotating = False
        self.interval = 10  # Default interval in seconds
        self.statuses = []
        self.current_index = 0
        self.status_file = 'status.txt'
        self.load_statuses()

    @commands.command(description="Start rotating statuses with a specified activity type")
    async def start_rotation(self, ctx, activity_type: str, *, statuses: str):
        if self.is_rotating:
            await ctx.send("Status rotation is already running.")
            return

        # Parse the activity type
        activity_map = {
            'streaming': discord.ActivityType.streaming,
            'playing': discord.ActivityType.playing,
            'listening': discord.ActivityType.listening,
        }

        if activity_type.lower() not in activity_map:
            await ctx.send("Invalid activity type. Choose from `streaming`, `playing`, or `listening`.")
            return

        activity = activity_map[activity_type.lower()]

        # Parse and store statuses
        self.statuses = [{"type": activity, "name": status.strip()} for status in statuses.split('|')]
        self.save_statuses()

        if not self.statuses:
            await ctx.send("No valid statuses provided. Please provide at least one status.")
            return

        self.is_rotating = True
        await ctx.send(f"Starting status rotation with {len(self.statuses)} statuses, rotating every {self.interval} seconds.")
        self.run_rotation.start()

    @commands.command(description="Stop the status rotation")
    async def stop_rotation(self, ctx):
        if self.is_rotating:
            self.is_rotating = False
            self.run_rotation.cancel()
            await ctx.send("Stopping status rotation...")
        else:
            await ctx.send("Status rotation is not currently running.")

    @commands.command(description="List all current statuses")
    async def list_statuses(self, ctx):
        if not self.statuses:
            await ctx.send("No statuses available.")
            return

        status_list = "\n".join([f"{i}: {status['type']} - {status['name']}" for i, status in enumerate(self.statuses)])
        await ctx.send(f"Current statuses:\n{status_list}")

    @commands.command(description="Remove a status by its index")
    async def remove_status(self, ctx, index: int):
        if index < 0 or index >= len(self.statuses):
            await ctx.send("Invalid index. Use `!list_statuses` to see valid indexes.")
            return

        removed_status = self.statuses.pop(index)
        self.save_statuses()  # Update the file after removal
        await ctx.send(f"Removed status: {removed_status['type']} - {removed_status['name']}")

    @commands.command(description="Edit a status at a specific index")
    async def edit_status(self, ctx, index: int, *, new_status: str):
        if index < 0 or index >= len(self.statuses):
            await ctx.send("Invalid index. Use `!list_statuses` to see valid indexes.")
            return

        status = self.statuses[index]
        self.statuses[index] = {"type": status["type"], "name": new_status}
        self.save_statuses()  # Update the file after editing
        await ctx.send(f"Updated status at index {index} to: {new_status}")

    @commands.command(description="Preview a status at a specific index")
    async def preview_status(self, ctx, index: int):
        if index < 0 or index >= len(self.statuses):
            await ctx.send("Invalid index. Use `!list_statuses` to see valid indexes.")
            return

        status = self.statuses[index]
        await ctx.send(f"Preview of status at index {index}: {status['type']} - {status['name']}")

    @commands.command(description="Set the interval for status rotation")
    async def set_interval(self, ctx, interval: int):
        if interval <= 0:
            await ctx.send("Interval must be a positive number.")
            return

        self.interval = interval
        if self.is_rotating:
            await ctx.send(f"Interval updated to {self.interval} seconds. Rotation will resume shortly.")
        else:
            await ctx.send(f"Interval updated to {self.interval} seconds.")

    @tasks.loop(seconds=10)
    async def run_rotation(self):
        if not self.statuses:
            logging.warning("No statuses available to rotate.")
            return

        current_status = self.statuses[self.current_index]
        if current_status["type"] == discord.ActivityType.streaming:
            activity = discord.Streaming(name=current_status["name"], url="https://twitch.tv/kaori_0_7")
        else:
            activity = discord.Activity(type=current_status["type"], name=current_status["name"])

        await self.bot.change_presence(activity=activity)
        logging.info(f"Status changed to: {current_status['name']}")

        # Cycle to the next status
        self.current_index = (self.current_index + 1) % len(self.statuses)
        await asyncio.sleep(self.interval)

    @run_rotation.before_loop
    async def before_rotation(self):
        await self.bot.wait_until_ready()

    def load_statuses(self):
        """Load statuses from the status.txt file."""
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as file:
                self.statuses = []
                for line in file:
                    if not line.strip():
                        continue
                    parts = line.split(':', 1)
                    if len(parts) != 2:
                        continue
                    activity_type, statuses = parts
                    activity_map = {
                        'streaming': discord.ActivityType.streaming,
                        'playing': discord.ActivityType.playing,
                        'listening': discord.ActivityType.listening,
                    }
                    activity = activity_map.get(activity_type.strip().lower())
                    if activity:
                        for status in statuses.split('|'):
                            self.statuses.append({"type": activity, "name": status.strip()})
        else:
            logging.warning(f"{self.status_file} not found. Starting with an empty status list.")

    def save_statuses(self):
        """Save the statuses to the status.txt file."""
        with open(self.status_file, 'w') as file:
            for status in self.statuses:
                activity_type = {
                    discord.ActivityType.streaming: 'streaming',
                    discord.ActivityType.playing: 'playing',
                    discord.ActivityType.listening: 'listening',
                }.get(status['type'], 'unknown')
                file.write(f"{activity_type}:{status['name']}\n")

def setup(bot):
    bot.add_cog(StatusRotator(bot))
