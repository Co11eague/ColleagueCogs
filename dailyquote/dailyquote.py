import base64
import os
from io import BytesIO

import discord
import csv
import random
import aiocron
import pytz
from craiyon import Craiyon, craiyon_utils
from datetime import datetime, timedelta
from redbot.core import commands
from redbot.core.bot import Red
import requests
from bs4 import BeautifulSoup



class DailyQuoteCog(commands.Cog):
    """A cog to send a daily quote with a random emote reaction."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.channel_id = 202397765941198848  # Default channel ID
        self.scheduled_cron = None
        self.current_cron_time = (11, 0)  # Default time
        self.set_cron_job(11, 0)  # Default time

    def set_cron_job(self, hour, minute):
        if self.scheduled_cron:
            self.scheduled_cron.stop()  # Remove the previous cron job

        self.current_cron_time = (hour, minute)
        cron_expr = f"{minute} {hour} * * *"
        self.scheduled_cron = aiocron.crontab(cron_expr, func=self.send_scheduled_message, start=True)

    def get_random_quote_from_csv(self):
        print("Getting random quote from csv")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        quotes_path = os.path.join(current_dir, "quotes.csv")
        try:
            with open(quotes_path, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                quotes = [
                    {"quote": row[0], "author": row[1]}
                    for row in reader
                ]

                print("Quotes loaded")

                if quotes:
                    print("Returning random quote")
                    return random.choice(quotes)
        except Exception as e:
            print(f"Error reading CSV: {e}")

        return None

    async def generate_image_from_quote(self, quote_text):
        print("Generating image from quote")
        try:
            # Initialize Craiyon
            generator = Craiyon()

            # Generate images asynchronously using the provided quote
            generated_images = await generator.async_generate(quote_text)

            # Encode images to base64
            b64_list = await craiyon_utils.async_encode_base64(generated_images.images)

            # If there are any images, use the first one
            if b64_list:
                image = b64_list[0]  # Take the first image

                # Decode the base64 image to bytes
                img_bytes = BytesIO(base64.b64decode(image))
                discord_image = discord.File(img_bytes)  # Create a Discord file object
                discord_image.filename = "quote_image.webp"  # Name the file

                return discord_image  # Return only one image

            else:
                print("No images generated.")
                return None

        except Exception as e:
            print(f"An error occurred while generating the image: {e}")
            return None

    async def send_scheduled_message(self):
        print("Sending scheduled message")
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print("Channel not found")
            return

        random_quote = self.get_random_quote_from_csv()
        if random_quote:
            print("Sending random quote")
            embed = discord.Embed(
                title="Dienos mintis",
                description=random_quote["quote"],
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"- {random_quote['author']}")

            # Generate an image based on the quote
            image = await self.generate_image_from_quote(random_quote["quote"])
            if image:
                # Send the embed with the image as an attachment
                message = await channel.send(embed=embed, files=[image])
            else:
                message = await channel.send(embed=embed)

            guild = channel.guild
            emotes = guild.emojis

            if emotes:
                random_emote = random.choice(emotes)
                await message.add_reaction(random_emote)


    @commands.command()
    async def set_quote_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where daily quotes will be sent."""
        self.channel_id = channel.id
        await ctx.send(f"Daily quotes channel set to {channel.mention}.")

    @commands.command()
    async def set_quote_time(self, ctx, hour: int, minute: int):
        """Set the time for daily quotes (24-hour format)."""
        if 0 <= hour < 24 and 0 <= minute < 60:
            self.set_cron_job(hour, minute)
            await ctx.send(f"Daily quotes time set to {hour:02}:{minute:02}.")
        else:
            await ctx.send("Invalid time. Please provide a valid hour (0-23) and minute (0-59).")

    @commands.command()
    async def time_until_next_quote(self, ctx):
        """Get the time remaining until the next scheduled quote."""
        now = datetime.now(pytz.utc)
        hour, minute = self.current_cron_time
        next_quote_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If the next quote time is in the past, move to the next day
        if now >= next_quote_time:
            next_quote_time += timedelta(days=1)

        time_remaining = next_quote_time - now
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        await ctx.send(f"Time remaining until the next quote: {hours} hours and {minutes} minutes.")


async def setup(bot):
    await bot.add_cog(DailyQuoteCog(bot))
