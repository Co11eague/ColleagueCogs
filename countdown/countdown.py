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
    52: "52 savaites per metus Ispanijoje nuolat vyksta tūkstančiai vietinių festivalių (fiestų).",
    51: "Pagal sausumos plotą Ispanija yra 51-a didžiausia valstybė pasaulyje.",
    50: "Ispanija yra politiškai padalinta į lygiai 50 skirtingų provincijų.",
    49: "Numatoma, kad 2025 m. pabaigoje Ispanijos gyventojų skaičius sieks apie 49 milijonus.",
    48: "Ispanija ilgą laiką didžiavosi lygiai 48 UNESCO pasaulio paveldo objektais.",
    47: "Seniausiam Europos urvų menui Šiaurės Ispanijoje yra daugiau nei 47 000 metų.",
    46: "Oficialus Ispanijos gyventojų skaičius 46 milijonų ribą peržengė 2010-aisiais.",
    45: "Ispanijoje yra 45 UNESCO biosferos rezervatai – tai pasaulinė ekologijos lyderė.",
    44: "Ispanijos plotas yra maždaug 44 kartus didesnis už Kataro valstybės.",
    43: "Garsus ispanų likeris „Licor 43“ gaminamas iš 43 slaptų žolelių, vaisių ir prieskonių.",
    42: "Valensijos maratonas (42 km) yra vienas greičiausių ir lygiausių bėgimų pasaulyje.",
    41: "Daugiau nei 41 % Ispanijos žemės naudojama žemės ūkiui (vynuogynams, alyvuogėms).",
    40: "Ispanija pagamina apie 40 % viso pasaulio alyvuogių aliejaus.",
    39: "Į UNESCO nematerialaus kultūros paveldo sąrašą įtrauktos 39 ispanų tradicijos, tarp jų ir flamenkas.",
    38: "Ispanijos aukščiausios futbolo lygos „La Liga“ sezoną sudaro 38 rungtynių dienos.",
    37: "Vidutinė vasaros temperatūra pietinėje Andalūzijoje dažnai siekia karštus 37°C.",
    36: "Ispanijos pilietinis karas oficialiai prasidėjo 1936 metais.",
    35: "Madrido vertybinių popierių biržos pagrindinis indeksas yra „IBEX 35“.",
    34: "Norint paskambinti į Ispaniją, reikia rinkti tarptautinį kodą +34.",
    33: "Ispanijos baruose standartinis alaus buteliukas („tercio“) yra 33 cl (330 ml).",
    32: "Ispanų tyrinėtojui V. N. de Balboa buvo 32 metai, kai jis pirmasis iš europiečių pasiekė Ramųjį vandenyną.",
    31: "Garsus ispanų dailininkas Franciskas Goja gimė kovo 31 dieną.",
    30: "Pagal bendrą gyventojų skaičių Ispanija užima 30-ąją vietą pasaulyje.",
    29: "Raidė „ñ“ yra 29-oji klasikinės ispanų abėcėlės raidė ir kalbos simbolis.",
    28: "Ispaniškas Melagių dienos atitikmuo švenčiamas gruodžio 28 dieną.",
    27: "„27-ųjų karta“ buvo garsus Ispanijos literatūrinis judėjimas su F. G. Lorca priešakyje.",
    26: "Barselonos „Sagrada Família“ planuojama baigti 2026 m. – praėjus šimtmečiui po A. Gaudi mirties.",
    25: "25-osios moderniosios olimpinės žaidynės vyko Barselonoje 1992 metais.",
    24: "Kūčios („Nochebuena“) Ispanijoje švenčiamos gruodžio 24 d. su masine šeimos vakariene.",
    23: "Balandžio 23 d. Katalonijoje švenčiama Sant Jordi – įsimylėjėliai dovanoja knygas ir rožes.",
    22: "Didžiausios Ispanijos Kalėdų loterijos „El Gordo“ traukimas vyksta gruodžio 22 d.",
    21: "Ispanų kalba yra oficiali 21 pasaulio valstybėje.",
    20: "Biologiškai optimali ispaniška siesta trunka lygiai 20–30 minučių.",
    19: "Pirmoji Ispanijos konstitucija („La Pepa“) priimta 1812 m. kovo 19 dieną.",
    18: "Ispanijoje legalus amžius balsuoti ir vartoti alkoholį yra 18 metų.",
    17: "Ispanija yra padalinta į 17 autonominių regionų, turinčių savo kultūrą ir valdžią.",
    16: "Ispanija saugo savo nuostabią gamtą 16-oje nacionalinių parkų.",
    15: "Reconquista baigėsi 15-ojo amžiaus pabaigoje (1492 m.), suvienydama Ispaniją.",
    14: "Pablui Pikasui buvo vos 14 metų, kai jis nutapė savo pirmąjį didelį aliejinį paveikslą.",
    13: "Ispanijoje nelaiminga diena laikoma ne penktadienis, o antradienis, 13-oji.",
    12: "Per Naujuosius metus ispanai suvalgo lygiai 12 vynuogių – po vieną su kiekvienu laikrodžio dūžiu sėkmei.",
    11: "Kovo 11-oji (11-M) žymi 2004 m. Madrido traukinių tragediją, stipriai suvienijusią šalį.",
    10: "X amžiaus karalius Alfonsas X „Išmintingasis“ pavertė ispanų kalbą mokslo ir literatūros kalba.",
    9: "Tradicinė ispanų vakarienė retai prasideda anksčiau nei 9 val. vakaro.",
    8: "8-ajame amžiuje į Iberijos pusiasalį atvykę maurai pradėjo 800 metų trukusią kultūrinę įtaką.",
    7: "Ispanijai priklausantį Kanarų salyną sudaro 7 pagrindinės salos.",
    6: "Sausio 6 dieną dovanas ispanų vaikams atneša ne Kalėdų Senelis, o Trys Karaliai.",
    5: "Pablas Pikasas savo ankstyvojoje karjeroje perėjo per 5 skirtingus kūrybos periodus.",
    4: "Šalia kastilų ispanų, Ispanijoje yra 4 oficialios regioninės kalbos (katalonų, galisų, baskų, araniečių).",
    3: "Ispanija užima 3-iąją vietą pasaulyje pagal UNESCO pasaulio paveldo objektų skaičių.",
    2: "Ispanai tradiciškai naudoja 2 pavardes: pirmąją iš tėvo, antrąją – iš motinos.",
    1: "Ispanija turi 1 oficialią sausumos sieną tarp Europos ir Afrikos (Seutos ir Meliljos anklavai).",
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
