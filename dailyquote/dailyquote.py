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
import base64


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
                        f"Interpret the emotional tone, mood, and deeper meaning of the quote, but portray it in a **funny, witty, or lighthearted way** using humor and visual storytelling. "
                        f"The image should feature realistic, emotionally expressive cats as the main characters — lifelike in texture, fur, and anatomy, but filled with personality and emotion. "
                        f"Each cat should have clear facial expressions and body language that convey humor, irony, or exaggerated emotion relevant to the quote’s meaning. "
                        f"Their eyes, poses, and interactions should tell a mini comedic story that visually represents the spirit or hidden truth of the quote. "
                        f"The scene must look believable and photorealistic, but the situation or environment can be surreal, symbolic, or dreamlike — a visual metaphor that represents the quote’s message in a humorous way. "
                        f"The environment should look cinematic yet playful, mixing realistic lighting and materials with surreal or absurd details that create a sense of clever visual irony. "
                        f"The cats may be performing human-like actions, existing in imaginative or funny places, or interacting with symbolic props that visually echo the spirit of the quote. "
                        f"Focus on expressive realism, emotional storytelling, and symbolic yet entertaining imagery — as if the quote has come to life as a short, funny, photorealistic story.\n\n"
                        f"Guidelines:\n"
                        f"- Do NOT include the actual quote text anywhere in the image.\n"
                        f"- Optional small text may appear naturally in the environment (like signs, labels, or graffiti) but never the quote itself.\n"
                        f"- Keep lighting, materials, and fur highly realistic, with cinematic depth, mood, and composition.\n"
                        f"- The background should enhance the tone — for example, peaceful, dramatic, hopeful, mysterious, or funny — while staying photorealistic and coherent.\n"
                        f"- Ensure the humor feels clever and expressive, not cartoonish — the cats should look real, not animated.\n"
                        f"- Each image should tell a short, visual story that represents the message or emotional core of the quote through surreal realism and witty expression.\n"
                        f"- Aspect ratio: 1:1 (square), suitable for daily posts."
                    ),
                    n=1,
                    size="1024x1024",
                    quality="medium"
                )

            # Execute in background thread
            response = await asyncio.to_thread(_generate)

            if response and response.data:
                b64_image = response.data[0].b64_json
                img_bytes = base64.b64decode(b64_image)
                print("Image successfully generated")
                return img_bytes  # Return raw bytes, not a URL
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
            image_bytes = await self.generate_image_from_quote(random_quote["quote"], random_quote["author"])
            if image_bytes:
                image_file = discord.File(io.BytesIO(image_bytes), filename="quote_image.png")
                message = await channel.send(embed=embed, file=image_file)
            else:
                message = await channel.send(embed=embed)

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
