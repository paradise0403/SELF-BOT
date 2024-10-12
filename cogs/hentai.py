import discord
from discord.ext import commands
from main import infected
import requests

class Hentai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def fetch_image(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get('message')  # nekobot.xyz uses 'message' for image URLs
        except requests.RequestException:
            return None

    @commands.command(name="hrandom", description="Random hentai")
    @infected()
    async def hrandom(self, ctx):
        url = "https://nekobot.xyz/api/image?type=hentai"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="hass", description="Random hentai ass")
    @infected()
    async def hass(self, ctx):
        url = "https://nekobot.xyz/api/image?type=hass"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="ass", description="Random ass")
    @infected()
    async def ass(self, ctx):
        url = "https://nekobot.xyz/api/image?type=ass"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="boobs", description="Real breasts")
    @infected()
    async def boobs(self, ctx):
        url = "https://nekobot.xyz/api/image?type=boobs"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="pussy", description="Random pussy")
    @infected()
    async def pussy(self, ctx):
        url = "https://nekobot.xyz/api/image?type=pussy"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="4k", description="4k NSFW")
    @infected()
    async def fk(self, ctx):
        url = "https://nekobot.xyz/api/image?type=4k"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="cumm", description="Baby gravy!")
    @infected()
    async def cumm(self, ctx):
        url = "https://nekobot.xyz/api/image?type=cum"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="hblowjob", description="Self explainable")
    @infected()
    async def blowjob(self, ctx):
        url = "https://nekobot.xyz/api/image?type=blowjob"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="ahegao", description="Ahegao")
    @infected()
    async def ahegao(self, ctx):
        url = "https://nekobot.xyz/api/image?type=ahegao"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="feet", description="Random feet")
    @infected()
    async def feet(self, ctx):
        url = "https://nekobot.xyz/api/image?type=feet"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="lesbian", description="Girls rule!")
    @infected()
    async def lesbian(self, ctx):
        url = "https://nekobot.xyz/api/image?type=lesbian"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="spank", description="NSFW for butts")
    @infected()
    async def spank(self, ctx):
        url = "https://nekobot.xyz/api/image?type=spank"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

    @commands.command(name="hwallpaper", description="99% SFW")
    @infected()
    async def hwallpaper(self, ctx):
        url = "https://nekobot.xyz/api/image?type=wallpaper"
        image_url = self.fetch_image(url)
        if image_url:
            await ctx.send(image_url)
        else:
            await ctx.send("An error occurred while fetching the image.")

def setup(bot):
    bot.add_cog(Hentai(bot))
