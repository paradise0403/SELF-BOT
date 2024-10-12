import os

os.system('pip uninstall discord.py -y')

os.system('pip install -r infreq.txt')

os.system('pip uninstall decouple')

os.system('pip install python-decouple')
import discord
import asyncio
from discord.ext import commands
from decouple import config
from colorama import Fore, Style

# Load prefix and other configurations
infectpre = config('prefix')
bot = commands.Bot(command_prefix=infectpre, self_bot=True, help_command=None)

authorized_user = int(config("userid"))

# Event when the bot receives a message
@bot.event
async def on_message(message):
    if message.author != bot.user:
        return
    await bot.process_commands(message)

# Authorization check
def infected():
    def predicate(ctx):
        return ctx.author.id == authorized_user
    return commands.check(predicate)

# Help command
@bot.command()
@infected()
async def help(ctx, *, query=None):
    prefix = infectpre
    await ctx.message.delete()

    if not query:
        cogs = bot.cogs.keys()

        helpinfected = f"👑 **Paradise Self Bot - Help Panel 👑**\n"
        helpinfected += f"Use `{prefix}help <module>` to see commands for a specific module.\n\n"

        for cog in cogs:
            helpinfected += f"🔧 **{cog}** - `{prefix}help {cog}`\n"

        await ctx.send(helpinfected, delete_after=60)
    else:
        query = query.lower()

        found_cog = None

        for cog in bot.cogs:
            if query == cog.lower():
                found_cog = bot.get_cog(cog)
                break

        if not found_cog:
            await ctx.send("🚫 Module not found. Use the help command without arguments to list available modules.", delete_after=10)
            return

        cog_commands = found_cog.get_commands()

        helpinfected = f"📜 **{found_cog.qualified_name} Commands**\n\n"

        for command in cog_commands:
            helpinfected += f"🔹 `{prefix}{command.name}` - {command.help or 'No description'}\n"

        await ctx.send(helpinfected, delete_after=60)

# Command to list all commands
@bot.command()
@infected()
async def allcmds(ctx):
    command_list = bot.commands
    sorted_commands = sorted(command_list, key=lambda x: x.name)

    response = "# **Kaori Self Bot**\n\n"
    for command in sorted_commands:
        response += f"🔹 _{command.name}_, "
        
    await ctx.send(response, delete_after=30)

# On bot ready event
@bot.event
async def on_ready():
    infbanner = """
 _  __                     _ 
| |/ /  __ _   ___   _ __ (_)
| ' /  / _ | / _ \ | '__|| |
| . \ | (_| || (_) || |   | |
|_|\_\ \__,_| \___/ |_|   |_|
                             
"""
    print(Fore.GREEN + infbanner + Style.RESET_ALL)
    print(f"{'='*30}")
    print(f"        Logged in as: {bot.user.name}")
    print(f"        Selfbot ID: {bot.user.id}")
    print(f"{'='*30}\n")
    print("KAORI BOT IS WORKING 😺")
    print(f"{'-'*30}")
    print(f"   Username: {bot.user.name}")
    print(f"   Guilds: {len(bot.guilds)}")
    print(f"   Members: {sum([guild.member_count for guild in bot.guilds])}")
    print(f"{'-'*30}")
    print("Developer - K A O R I")

# Load cogs
def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog_name = filename[:-3]
            bot.load_extension(f'cogs.{cog_name}')

load_cogs()

# Run the bot
infection = config('token')
bot.run(infection, reconnect=True)

   
