import asyncio
from datetime import datetime, date
from io import BytesIO

import aiocron
import discord
import pytz

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFilter
import os


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

        current_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        background_path = os.path.join(
            current_dir,
            "malaga_background.png"
        )

        background = Image.open(
            background_path
        ).convert("RGB")

        background = background.resize(
            (width, height),
            Image.LANCZOS
        )

        # Light blur so overlays blend naturally
        background = background.filter(
            ImageFilter.GaussianBlur(0.4)
        )

        image = background.convert("RGBA")

        overlay = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(overlay)

        # =========================
        # FONTS
        # =========================

        title_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            48
        )

        huge_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            112
        )

        small_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            24
        )

        fact_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            21
        )

        day_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            28
        )

        def text_size(text, font):
            bbox = draw.textbbox(
                (0, 0),
                text,
                font=font
            )

            return (
                bbox[2] - bbox[0],
                bbox[3] - bbox[1]
            )

        # =========================
        # MAIN WOODEN BOARD
        # =========================

        board_x1 = 35
        board_y1 = 35
        board_x2 = 585
        board_y2 = 535

        # Shadow
        draw.rounded_rectangle(
            [
                (board_x1 + 8, board_y1 + 10),
                (board_x2 + 8, board_y2 + 10)
            ],
            radius=32,
            fill=(0, 0, 0, 90)
        )

        # Main board
        draw.rounded_rectangle(
            [
                (board_x1, board_y1),
                (board_x2, board_y2)
            ],
            radius=32,
            fill=(56, 39, 24, 220),
            outline=(255, 255, 255, 35),
            width=2
        )

        # Wood plank highlights
        for y in [
            110,
            170,
            235,
            300,
            365,
            430
        ]:
            draw.line(
                [
                    (board_x1 + 20, y),
                    (board_x2 - 20, y)
                ],
                fill=(255, 255, 255, 10),
                width=2
            )

        # =========================
        # HEADER
        # =========================

        draw.rounded_rectangle(
            [
                (board_x1 + 18, board_y1 + 18),
                (board_x2 - 18, board_y1 + 85)
            ],
            radius=24,
            fill=(242, 151, 28, 235)
        )

        title = "MALAGA 2026"

        # Shadow
        draw.text(
            (74, 65),
            title,
            fill=(0, 0, 0),
            font=title_font
        )

        # Main text
        draw.text(
            (71, 62),
            title,
            fill=(255, 255, 255),
            font=title_font
        )

        # =========================
        # CALENDAR CARD
        # =========================

        card_x1 = 60
        card_y1 = 175
        card_x2 = 255
        card_y2 = 432

        # Shadow
        draw.rounded_rectangle(
            [
                (card_x1 + 6, card_y1 + 8),
                (card_x2 + 6, card_y2 + 8)
            ],
            radius=18,
            fill=(0, 0, 0, 70)
        )

        # Main card
        draw.rounded_rectangle(
            [
                (card_x1, card_y1),
                (card_x2, card_y2)
            ],
            radius=18,
            fill=(245, 225, 190, 245),
            outline=(120, 85, 40, 120),
            width=2
        )

        # Pin
        draw.rounded_rectangle(
            [
                (card_x1 + 80, card_y1 - 14),
                (card_x1 + 94, card_y1 + 10)
            ],
            radius=4,
            fill=(80, 55, 25, 255)
        )

        # =========================
        # BIG NUMBER
        # =========================

        days_text = str(days_left)

        text_w, text_h = text_size(
            days_text,
            huge_font
        )

        text_x = (
            card_x1 +
            ((card_x2 - card_x1) - text_w) / 2
        )

        # Shadow
        draw.text(
            (text_x + 4, card_y1 + 36 + 4),
            days_text,
            fill=(0, 0, 0),
            font=huge_font
        )

        # Main
        draw.text(
            (text_x, card_y1 + 36),
            days_text,
            fill=(232, 92, 39),
            font=huge_font
        )

        # =========================
        # DAY LABELS
        # =========================

        day_word = self.lithuanian_days(
            days_left
        )

        line1 = day_word
        line2 = "iki kelionės"

        l1_w, _ = text_size(
            line1,
            day_font
        )

        l2_w, _ = text_size(
            line2,
            day_font
        )

        draw.text(
            (
                card_x1 +
                ((card_x2 - card_x1) - l1_w) / 2,
                card_y1 + 178
            ),
            line1,
            fill=(40, 35, 28),
            font=day_font
        )

        draw.text(
            (
                card_x1 +
                ((card_x2 - card_x1) - l2_w) / 2,
                card_y1 + 212
            ),
            line2,
            fill=(40, 35, 28),
            font=day_font
        )

        # =========================
        # PROGRESS TEXT
        # =========================

        progress_text = (
            f"Kelionės progresas: "
            f"{progress_percent}%"
        )

        draw.text(
            (296, 177),
            progress_text,
            fill=(255, 255, 255, 235),
            font=small_font
        )

        # =========================
        # PROGRESS BAR
        # =========================

        bar_x1 = 295
        bar_y1 = 215
        bar_x2 = 545
        bar_y2 = 252

        # Shadow
        draw.rounded_rectangle(
            [
                (bar_x1 + 3, bar_y1 + 3),
                (bar_x2 + 3, bar_y2 + 3)
            ],
            radius=18,
            fill=(0, 0, 0, 110)
        )

        # Bar background
        draw.rounded_rectangle(
            [
                (bar_x1, bar_y1),
                (bar_x2, bar_y2)
            ],
            radius=18,
            fill=(55, 60, 75, 240),
            outline=(255, 255, 255, 40),
            width=1
        )

        # Fill
        fill_width = int(
            (bar_x2 - bar_x1) *
            (progress_percent / 100)
        )

        if fill_width > 0:

            draw.rounded_rectangle(
                [
                    (bar_x1, bar_y1),
                    (
                        bar_x1 + fill_width,
                        bar_y2
                    )
                ],
                radius=18,
                fill=(244, 145, 32)
            )

            # Shine
            draw.rounded_rectangle(
                [
                    (bar_x1 + 3, bar_y1 + 3),
                    (
                        bar_x1 +
                        max(3, fill_width - 3),
                        bar_y1 + 14
                    )
                ],
                radius=12,
                fill=(255, 220, 150, 120)
            )

        # =========================
        # FACT TEXT
        # =========================

        fact_x = 295
        fact_y = 285
        max_width = 245

        words = fact.split()

        lines = []
        current_line = ""

        for word in words:

            test_line = (
                current_line +
                " " +
                word
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
                if current_line:
                    lines.append(
                        current_line
                    )

                current_line = word

        if current_line:
            lines.append(
                current_line
            )

        y = fact_y

        for line in lines[:7]:

            # Shadow
            draw.text(
                (fact_x + 2, y + 2),
                line,
                fill=(0, 0, 0, 120),
                font=fact_font
            )

            # Main text
            draw.text(
                (fact_x, y),
                line,
                fill=(240, 240, 240, 245),
                font=fact_font
            )

            y += 28

        # =========================
        # WARM EDGE GLOW
        # =========================

        glow = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0)
        )

        glow_draw = ImageDraw.Draw(glow)

        glow_draw.rounded_rectangle(
            [
                (board_x1, board_y1),
                (board_x2, board_y2)
            ],
            radius=32,
            outline=(255, 180, 80, 45),
            width=3
        )

        overlay = Image.alpha_composite(
            overlay,
            glow
        )

        image = Image.alpha_composite(
            image,
            overlay
        )

        # =========================
        # EXPORT
        # =========================

        final_image = image.convert(
            "RGB"
        )

        buffer = BytesIO()

        final_image.save(
            buffer,
            format="PNG",
            quality=95
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
