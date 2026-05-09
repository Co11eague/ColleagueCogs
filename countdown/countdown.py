import asyncio
from datetime import datetime, date
from io import BytesIO

import aiocron
import discord
import pytz

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from redbot.core import commands
from redbot.core.bot import Red


COUNTDOWN_FACTS = {
    53: "53 dienos – maždaug tiek truko Apollo 11 astronautų pasiruošimo simuliacijos prieš nusileidimą Mėnulyje.",
    52: "Metuose yra 52 savaitės – beveik po vieną countdown žinutę kiekvienai savaitei iki kitų atostogų.",
    51: "Didžiausi kruiziniai laivai pasaulyje gali plukdyti daugiau nei 5100 keleivių.",
    50: "Ispanija beveik kasmet sulaukia daugiau nei 50 milijonų turistų.",
    49: "Originalus Monopoly žaidimas išverstas į daugiau nei 49 kalbas.",
    48: "48 valandos laikomos idealia europietiško city break trukme.",
    47: "Europą sudaro 47 valstybės.",
    46: "Pirmasis vaizdo kasečių grotuvas buvo pristatytas 46 metais anksčiau nei Netflix pradėjo streaminimą.",
    45: "Standartinė vinilinė plokštelė sukasi 45 RPM greičiu.",
    44: "Malaga turi apie 44 kilometrus pakrantės.",
    43: "Seniausias vis dar veikiantis restoranas pasaulyje buvo atidarytas Ispanijoje prieš daugiau nei 300 metų.",
    42: "42 garsiai vadinamas „atsakymu į gyvenimą, visatą ir viską“.",
    41: "Per dideles karščio bangas Malagoje temperatūra gali pasiekti 41°C.",
    40: "Phileas Fogg apkeliavo pasaulį per 80 dienų.",
    39: "39 kalbomis pasaulyje kalba daugiau nei milijonas žmonių.",
    38: "Vidutinis žmogus apie 38 dienas savo gyvenime praleidžia laukdamas prie šviesoforų.",
    37: "37°C laikoma normalia žmogaus kūno temperatūra.",
    36: "Pirmajai pasaulio fotografijai reikėjo kelių valandų ekspozicijos.",
    35: "35mm juosta tapo pasauliniu kino standartu.",
    34: "Eifelio bokštas iš pradžių turėjo stovėti tik 20 metų.",
    33: "Tarp Kanados ir JAV esančiame Thousand Islands regione gyvena žmonės 33 salose.",
    32: "Šachmatų figūros žaidimo pradžioje gali būti judinamos iš 32 pradinių pozicijų.",
    31: "Šalčiausia temperatūra užfiksuota Ispanijoje buvo −32°C.",
    30: "Žmonės vidutiniškai apie 30 minučių per dieną praleidžia rinkdamiesi ką žiūrėti internete.",
    29: "Pilnas Mėnulio ciklas trunka apie 29,5 dienos.",
    28: "Europoje kalbama daugiau nei 200 kalbų.",
    27: "27 valstybės yra Europos Sąjungos narės.",
    26: "Maratono ilgis yra 26,2 mylios.",
    25: "Ispanija pagamina beveik pusę viso pasaulio alyvuogių aliejaus.",
    24: "Malagoje per metus būna apie 300 saulėtų dienų.",
    23: "23 valstybės ribojasi su Viduržemio jūra.",
    22: "Futbolo rungtynes pradeda 22 žaidėjai aikštėje.",
    21: "Seniausias pasaulio viešbutis Japonijoje veikia jau daugiau nei 1300 metų.",
    20: "Andalūziją kasmet aplanko daugiau nei 20 milijonų turistų.",
    19: "Titanikas turėjo tik 20 gelbėjimosi valčių.",
    18: "Ispanijoje legalus alkoholio vartojimo amžius yra 18 metų.",
    17: "Ispanija turi 17 autonominių regionų.",
    16: "Pirmoji Žemės nuotrauka iš kosmoso buvo padaryta 1946 metais.",
    15: "15 minučių pasivaikščiojimas po valgio gali pagerinti virškinimą.",
    14: "Dvi savaitės yra populiariausia atostogų trukmė Europoje.",
    13: "Ispanijoje nelaiminga diena laikoma antradienis 13-oji.",
    12: "Per Naujuosius metus Ispanijoje valgoma 12 vynuogių sėkmei.",
    11: "Greičiausias pasaulio liftas juda daugiau nei 11 metrų per sekundę.",
    10: "Ispanija yra tarp 10 lankomiausių pasaulio šalių.",
    9: "Katės vidutiniškai miega apie 9 valandas dienos metu.",
    8: "Vidutinis tolimųjų skrydžių lėktuvas skrenda apie 8 mylias per minutę.",
    7: "Po savaitės jau sakysi „šiuo metu kitą savaitę jau būsim Malagoj“.",
    6: "Jungtinės Tautos naudoja šešias oficialias kalbas.",
    5: "Žmonės geriau prisimena patirtis nei daiktus.",
    4: "Turistai dažniausiai pamiršta keturis dalykus: pakrovėjus, akinius, pasą ir dantų šepetėlį.",
    3: "3 dienos iki pirmo kokteilio Malagoje.",
    2: "Pirmasis sėkmingas lėktuvo skrydis truko mažiau nei 2 minutes.",
    1: "Dar vienas miegas iki Malagos.",
    0: "Laukimas baigėsi – sveiki atvykę į Malagą."
}


class HolidayCountdown(commands.Cog):
    """Malaga countdown."""

    def __init__(self, bot: Red):
        self.bot = bot

        self.channel_id = 202397765941198848

        self.start_date = date(2026, 5, 8)
        self.holiday_date = date(2026, 6, 30)

        self.timezone = pytz.timezone(
            "Europe/London"
        )

        self.total_days = (
            self.holiday_date -
            self.start_date
        ).days

        self.hour = 8
        self.minute = 0

        self.cron = None

        self.set_cron_job(
            self.hour,
            self.minute
        )

    def set_cron_job(
        self,
        hour,
        minute
    ):
        if self.cron:
            self.cron.stop()

        self.hour = hour
        self.minute = minute

        cron_expr = (
            f"{minute} {hour} * * *"
        )

        self.cron = aiocron.crontab(
            cron_expr,
            func=lambda: asyncio.create_task(
                self.send_countdown()
            ),
            start=True
        )

    def lithuanian_days(
        self,
        days: int
    ):
        if (
            days % 10 == 1 and
            days % 100 != 11
        ):
            return "diena"

        if (
            days % 10 in [2, 3, 4, 5, 6, 7, 8, 9]
            and not (
                11 <= days % 100 <= 19
            )
        ):
            return "dienos"

        return "dienų"

    def create_countdown_image(
        self,
        days_left,
        progress_percent,
        fact
    ):
        width = 1000
        height = 560

        image = Image.new(
            "RGB",
            (width, height),
            (15, 23, 42)
        )

        draw = ImageDraw.Draw(image)

        # Header
        draw.rectangle(
            [(0, 0), (width, 140)],
            fill=(255, 140, 0)
        )

        title_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            56
        )

        huge_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            120
        )

        text_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            40
        )

        small_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            28
        )

        fact_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            24
        )

        # Header text
        draw.text(
            (50, 40),
            "MALAGA 2026",
            fill="white",
            font=title_font
        )

        # Number
        draw.text(
            (60, 170),
            str(days_left),
            fill=(255, 210, 90),
            font=huge_font
        )

        # Correct Lithuanian grammar
        day_word = self.lithuanian_days(
            days_left
        )

        draw.text(
            (320, 235),
            f"{day_word} iki kelionės",
            fill="white",
            font=text_font
        )

        # Progress bar background
        bar_x = 60
        bar_y = 360
        bar_width = 860
        bar_height = 44

        draw.rounded_rectangle(
            [
                (bar_x, bar_y),
                (
                    bar_x + bar_width,
                    bar_y + bar_height
                )
            ],
            radius=25,
            fill=(60, 70, 90)
        )

        # Progress fill
        fill_width = int(
            bar_width * (
                progress_percent / 100
            )
        )

        draw.rounded_rectangle(
            [
                (bar_x, bar_y),
                (
                    bar_x + fill_width,
                    bar_y + bar_height
                )
            ],
            radius=25,
            fill=(255, 140, 0)
        )

        draw.text(
            (60, 425),
            (
                f"Kelionės progresas: "
                f"{progress_percent}%"
            ),
            fill="white",
            font=small_font
        )

        # Wrap fact text
        max_width = 850

        words = fact.split()

        lines = []
        current_line = ""

        for word in words:
            test_line = (
                current_line + " " + word
            ).strip()

            bbox = draw.textbbox(
                (0, 0),
                test_line,
                font=fact_font
            )

            text_width = (
                bbox[2] - bbox[0]
            )

            if text_width <= max_width:
                current_line = test_line

            else:
                lines.append(
                    current_line
                )

                current_line = word

        if current_line:
            lines.append(
                current_line
            )

        y_text = 470

        for line in lines:
            draw.text(
                (60, y_text),
                line,
                fill=(220, 220, 220),
                font=fact_font
            )

            y_text += 30

        buffer = BytesIO()

        image.save(
            buffer,
            format="PNG"
        )

        buffer.seek(0)

        return buffer

    async def send_countdown(
        self,
        custom_channel=None
    ):
        try:
            if custom_channel:
                channel = custom_channel

            else:
                channel = (
                    await self.bot.fetch_channel(
                        self.channel_id
                    )
                )

        except Exception:
            return

        now = datetime.now(
            self.timezone
        )

        today = now.date()

        days_left = (
            self.holiday_date -
            today
        ).days

        if days_left < 0:
            return

        days_passed = (
            today -
            self.start_date
        ).days

        progress_percent = round(
            (
                days_passed /
                self.total_days
            ) * 100
        )

        fact = COUNTDOWN_FACTS.get(
            days_left,
            (
                "Kiekviena diena "
                "priartina prie Malagos."
            )
        )

        image_buffer = (
            self.create_countdown_image(
                days_left,
                progress_percent,
                fact
            )
        )

        file = discord.File(
            image_buffer,
            filename="malaga.png"
        )

        embed = discord.Embed(
            description=(
                "☀️ Kasdien vis arčiau "
                "atostogų."
            ),
            color=discord.Color.orange()
        )

        embed.set_image(
            url="attachment://malaga.png"
        )

        await channel.send(
            embed=embed,
            file=file
        )

    @commands.command()
    async def malagacountdown(
        self,
        ctx
    ):
        """Parodo countdown."""

        await self.send_countdown(
            custom_channel=ctx.channel
        )

    @commands.command()
    async def setcountdowntime(
        self,
        ctx,
        hour: int,
        minute: int
    ):
        """Nustato countdown laiką."""

        if not (
            0 <= hour <= 23 and
            0 <= minute <= 59
        ):
            await ctx.send(
                "Neteisingas laikas."
            )

            return

        self.set_cron_job(
            hour,
            minute
        )

        await ctx.send(
            (
                "⏰ Countdown laikas "
                f"nustatytas į "
                f"{hour:02}:{minute:02}"
            )
        )


async def setup(bot):
    await bot.add_cog(
        HolidayCountdown(bot)
    )
