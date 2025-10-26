import io
import os

import discord
import csv
import random
import aiocron
import json
import pytz
from datetime import datetime, timedelta
from redbot.core import commands
from redbot.core.bot import Red
from openai import OpenAI
import aiohttp
import asyncio

API_KEY_FILE = "/home/colleague/bot/cogs/CogManager/cogs/dailyquote/openai_api_key.json"


class DailyQuoteCog(commands.Cog):
    """A cog to send a daily quote with a random emote reaction."""


    def __init__(self, bot: Red):
        self.bot = bot
        self.channel_id = 202397765941198848  # Default channel ID
        self.scheduled_cron = None
        self.current_cron_time = (11, 0)  # Default time
        self.set_cron_job(11, 0)  # Default time
        self.client = None  # Initialize client as None
        self.api_key = None
        self.load_api_key()

    def set_cron_job(self, hour, minute):
        if self.scheduled_cron:
            self.scheduled_cron.stop()  # Remove the previous cron job

        self.current_cron_time = (hour, minute)
        cron_expr = f"{minute} {hour} * * *"
        self.scheduled_cron = aiocron.crontab(
            cron_expr,
            func=lambda: asyncio.create_task(self.send_scheduled_message()),
            start=True
        )

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


    def load_api_key(self):
        """Load the OpenAI API key from the file."""
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as file:
                data = json.load(file)
                self.api_key = data.get('api_key')
                if self.api_key:
                    # Updated API client setup
                    self.client = OpenAI(api_key=self.api_key)

    def save_api_key(self, api_key):
        """Save the OpenAI API key to a file."""
        with open(API_KEY_FILE, 'w') as file:
            json.dump({"api_key": api_key}, file)

    @commands.command()
    async def set_openai_key(self, ctx, api_key: str):
        """Set the OpenAI API key."""
        self.save_api_key(api_key)
        # Updated API client setup
        self.client = OpenAI(api_key=api_key)
        await ctx.send("OpenAI API key has been set successfully.")

    @commands.command()
    async def check_openai_key(self, ctx):
        """Check if the OpenAI API key is set."""
        if self.api_key:
            await ctx.send("The OpenAI API key is set and ready to use.")
        else:
            await ctx.send("No OpenAI API key has been set.")

    async def generate_image_from_quote(self, quote_text, author):
        if not self.api_key:
            return None

        try:
            # Run the synchronous OpenAI call in a background thread
            def _generate():
                return self.client.images.generate(
                    model="gpt-image-1",
                    prompt=(
                        f"Create a highly detailed, photo-realistic image directly inspired by the quote: \"{quote_text}\" - {author}. "
                        f"Interpret the emotional tone, mood, and deeper meaning of the quote and express it visually through the scene. "
                        f"The image should feature realistic cats as the main characters — lifelike, expressive, and fully integrated into the story being told by the quote. "
                        f"The scene must look believable and photorealistic, but the situation or environment can be surreal, symbolic, or dreamlike — a visual metaphor that represents the quote’s message. "
                        f"The cats may be performing human-like actions, existing in imaginative places, or engaging with surreal elements that visually echo the spirit of the quote. "
                        f"Focus on emotional storytelling and symbolic imagery, as if the quote has come to life visually.\n\n"
                        f"Guidelines:\n"
                        f"- Do NOT include the actual quote text anywhere in the image.\n"
                        f"- Optional small text may appear naturally in the environment (like signs, labels, or graffiti) but never the quote itself.\n"
                        f"- Keep lighting, materials, and fur highly realistic, with cinematic depth, mood, and composition.\n"
                        f"- The background should enhance the quote’s tone — for example, peaceful, dramatic, hopeful, or mysterious — while staying photorealistic and coherent.\n"
                        f"- Each image should tell a short, visual story that represents the message or emotional core of the quote through surreal realism.\n"
                        f"- Aspect ratio: 1:1 (square), suitable for daily posts."
                    ),
                    n=1,
                    size="1024x1024",
                    quality="medium"
                )

            # Execute in background thread
            response = await asyncio.to_thread(_generate)

            if response and response.data:
                image_url = response.data[0].url
                print(f"Image successfully generated: {image_url}")
                return image_url
            else:
                print("No image data returned from OpenAI.")
                return None

        except Exception as e:
            print(f"Error generating image from OpenAI: {e}")
            return None


    async def send_scheduled_message(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        random_quote = self.get_random_quote_from_csv()
        if random_quote:
            embed = discord.Embed(
                title="Dienos mintis",
                description=random_quote["quote"],
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"- {random_quote['author']}")

            # Generate the image as raw data
            # Generate the image and handle as an attachment
            image_url = await self.generate_image_from_quote(random_quote["quote"], random_quote["author"])
            if image_url:
                try:
                    print("Image generated")
                    # Download the image
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url) as response:
                            if response.status == 200:
                                # Read image data
                                img_data = await response.read()

                                # Send the image as a file
                                image_file = discord.File(io.BytesIO(img_data), filename="quote_image.png")
                                message = await channel.send(embed=embed, file=image_file)
                            else:
                                message = await channel.send("Failed to download the generated image.")

                except Exception as e:
                    print(f"Error downloading or sending the image: {e}")
                    message = await channel.send(embed=embed)  # Send the embed without an image if an error occurs
            else:
                message = await channel.send(embed=embed)  # Send the embed without an image if generation failed

            # React to the message with a random emote
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
        uk_tz = pytz.timezone("Europe/London")
        now = datetime.now(uk_tz)
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
