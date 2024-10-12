import discord
from discord.ext import commands
import aiohttp
import requests
from decouple import config

class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.command(name="stealav", usage="<@member>", description="Steal the avatar")
    async def stealav(self, ctx, user: discord.Member):
        url = user.avatar_url
        prefix = config("prefix", default="")
        password = config("tokenpass", default="")
        if not password:
            await ctx.send(f"You didn't configure your password yet, use `{prefix}setpass <password>`")
            return
        
        try:
            with open('PFP-1.png', 'wb') as f:
                r = requests.get(url, stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
            
            with open('PFP-1.png', 'rb') as f:
                await self.bot.user.edit(password=password, avatar=f.read())
            await ctx.send(f"Stole {user}'s avatar")
        except discord.HTTPException as e:
            await ctx.send(str(e))

    @commands.command(name="setavatar", aliases=["setav"], usage="<url>", description="Set your avatar")
    async def setavatar(self, ctx, url: str):
        prefix = config("prefix", default="")
        password = config("tokenpass", default="")
        if not password:
            await ctx.send(f"You didn't configure your password yet, use `{prefix}setpass <password>`")
            return
        
        try:
            with open('PFP-1.png', 'wb') as f:
                r = requests.get(url, stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
            
            with open('PFP-1.png', 'rb') as f:
                await self.bot.user.edit(password=password, avatar=f.read())
            await ctx.send("Changed avatar")
        except discord.HTTPException as e:
            await ctx.send(str(e))

    @commands.command(name="invisav", usage="", description="Invisible avatar")
    async def invisav(self, ctx):
        prefix = config("prefix", default="")
        url = "https://i.ibb.co/Wgn91T7/Infected-Invisible.png"
        password = config("tokenpass", default="")
        if not password:
            await ctx.send(f"You didn't configure your password yet, use `{prefix}setpass <password>`")
            return
        
        try:
            with open('PFP-1.png', 'wb') as f:
                r = requests.get(url, stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
            
            with open('PFP-1.png', 'rb') as f:
                await self.bot.user.edit(password=password, avatar=f.read())
            await ctx.send("Changed to an invisible avatar")
        except discord.HTTPException as e:
            await ctx.send(str(e))
            
    @commands.command(name="setpass", usage="<password>", description="Set selfbot password")
    async def setpassword(self, ctx, password: str):
        with open(".env", "w") as f:
            f.write(f"tokenpass={password}\n")
        await ctx.send("Password set successfully")

    @commands.command(name="gif", usage="<search query>", description="Search for a GIF using multiple APIs")
    async def gif(self, ctx, *, query: str):
        giphy_key = config("GIPHY_API_KEY", default="")
        tenor_key = config("TENOR_API_KEY", default="")
        giphy_endpoint = "https://api.giphy.com/v1/gifs/search"
        tenor_endpoint = "https://api.tenor.com/v1/search"
        
        async def fetch_giphy_gif(query):
            params = {
                "api_key": giphy_key,
                "q": query,
                "limit": 1,
                "offset": 0,
                "rating": "G",
                "lang": "en"
            }
            async with self.session.get(giphy_endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        return data['data'][0]['images']['original']['url']
            return None
        
        async def fetch_tenor_gif(query):
            params = {
                "key": tenor_key,
                "q": query,
                "limit": 1,
                "contentfilter": "low"
            }
            async with self.session.get(tenor_endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['results']:
                        return data['results'][0]['media'][0]['gif']['url']
            return None

        gif_url = await fetch_giphy_gif(query)
        if not gif_url:
            gif_url = await fetch_tenor_gif(query)

        if gif_url:
            await ctx.send(gif_url)
        else:
            await ctx.send("No GIFs found for your query.")

def setup(bot):
    bot.add_cog(Image(bot))
