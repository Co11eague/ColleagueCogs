import asyncio
from datetime import datetime, date
from io import BytesIO

import aiocron
import discord
import pytz

import json

import os
import base64
from openai import OpenAI
API_KEY_FILE = (
    "/home/colleague/bot/cogs/"
    "CogManager/cogs/"
    "holidaycountdown/"
    "openai_api_key.json"
)


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

COUNTDOWN_ACTIVITIES = {
    53: "calmly sipping coffee while checking travel plans",
    52: "wearing sunglasses and reading a Malaga tourist brochure",
    51: "applying sunscreen very seriously",
    50: "drinking a huge pint of beer proudly",
    49: "sunbathing dramatically in a deck chair",
    48: "covered in absurd amounts of tanning oil",
    47: "wearing inflatable armbands and snorkel gear",
    46: "building a tiny sandcastle",
    45: "wearing giant diving flippers indoors",
    44: "attempting to surf on the terrace floor",
    43: "being fanned by robots like royalty",
    42: "floating indoors on a flamingo pool float",
    41: "wearing six pairs of sunglasses",
    40: "holding a beach umbrella in fake wind",
    39: "buried in sand up to his waist",
    38: "doing beach yoga with sangria",
    37: "wearing a ridiculous gold Malaga crown",
    36: "being carried by robots like a king",
    35: "DJing for invisible beach guests",
    34: "driving the tractor like a yacht captain",
    33: "parasailing low across the terrace",
    32: "waterskiing across nothing",
    31: "wearing full scuba gear",
    30: "conducting tropical birds",
    29: "lifeguarding the robots",
    28: "launching beach balls from a cannon",
    27: "hosting Malaga news live",
    26: "flying a tiny plane banner",
    25: "pool noodle sword fighting a robot",
    24: "wrapped entirely in hotel towels",
    23: "being worshipped by coconut-bearing robots",
    22: "crowdsurfing over nobody",
    21: "wearing a tuxedo while swimming",
    20: "captaining a pirate ship",
    19: "juggling flaming coconuts",
    18: "painted like a tropical deity",
    17: "descending by parachute",
    16: "emerging dramatically from smoke",
    15: "wearing angel wings and beach shorts",
    14: "piloting a cardboard rocket",
    13: "floating midair magically",
    12: "arriving on a dolphin",
    11: "riding a robot like a horse",
    10: "wearing diamond swimwear",
    9: "breaking through a wall heroically",
    8: "summoning sangria telekinetically",
    7: "levitating and glowing",
    6: "carried by tiny beach servants",
    5: "surfing on lava",
    4: "ascending into heaven",
    3: "transforming into a tropical god",
    2: "opening a portal to Malaga",
    1: "exploding with excitement while smiling",
    0: "standing triumphantly on Malaga beach like an emperor"
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
        self.api_key = None
        self.client = None


        self.cron = None
        
        self.load_api_key()


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

    async def generate_countdown_image(
        self,
        days_left,
        progress_percent,
        fact
    ):
        current_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        cache_dir = os.path.join(
            current_dir,
            "generated"
        )

        os.makedirs(
            cache_dir,
            exist_ok=True
        )

        cached_file = os.path.join(
            cache_dir,
            f"day_{days_left}.png"
        )

        if os.path.exists(
            cached_file
        ):
            with open(
                cached_file,
                "rb"
            ) as f:
                return f.read()

        template_path = os.path.join(
            current_dir,
            "malaga_background.png"
        )

        activity = (
            COUNTDOWN_ACTIVITIES.get(
                days_left,
                "relaxing"
            )
        )

        try:

            def _generate():

                with open(
                    template_path,
                    "rb"
                ) as img:

                    return self.client.images.edit(
                        model="gpt-image-2",
                        image=img,
                        prompt=f"""
Use this exact image as base template.

Preserve:
- same recognizable young man
- same festive robots
- same tractor
- same terrace
- same warm Malaga sunset
- same cinematic visual identity

Today the man is:

{activity}

As countdown approaches zero,
his behaviour becomes increasingly absurd,
surreal and overdramatic,
while staying photorealistic.

Update the countdown board naturally.

Board title:
MALAGA 2026

Pinned calendar:
{days_left}

Below:
{self.lithuanian_days(days_left)} iki kelionės

Progress bar visually filled to exactly
{progress_percent}%

Fact:
{fact}

Typography must be:
sharp
readable
natural
physically integrated

Professional luxury travel campaign.
No digital overlays.
No fake pasted graphics.
Photorealistic.
"""
                    )

            response = await asyncio.to_thread(
                _generate
            )

            if (
                response
                and response.data
            ):
                image_bytes = (
                    base64.b64decode(
                        response.data[0]
                        .b64_json
                    )
                )

                with open(
                    cached_file,
                    "wb"
                ) as f:
                    f.write(
                        image_bytes
                    )

                return image_bytes

        except Exception as e:
            print(
                f"Generation error: {e}"
            )

        return None

    async def send_countdown(
        self,
        custom_channel=None
    ):
        if not self.client:
            return

        try:

            # Manual command
            if custom_channel is not None:
                channel = custom_channel

            # Scheduled cron send
            else:
                channel = await self.bot.fetch_channel(
                    self.channel_id
                )

        except Exception as e:
            print(
                f"Channel error: {e}"
            )
            return


        now = datetime.now(
            self.timezone
        )

        today = now.date()

        days_left = (
            self.holiday_date
            - today
        ).days

        if days_left < 0:
            return

        days_passed = (
            today
            - self.start_date
        ).days

        progress_percent = round(
            (
                days_passed
                / self.total_days
            )
            * 100
        )

        fact = COUNTDOWN_FACTS.get(
            days_left,
            "Kiekviena diena priartina prie Malagos."
        )

        image_bytes = await (
            self.generate_countdown_image(
                days_left,
                progress_percent,
                fact
            )
        )

        if not image_bytes:
            return

        file = discord.File(
            BytesIO(
                image_bytes
            ),
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
    def load_api_key(self):
        if os.path.exists(API_KEY_FILE):
            with open(
                API_KEY_FILE,
                "r"
            ) as f:
                data = json.load(f)

                self.api_key = data.get(
                    "api_key"
                )

                if self.api_key:
                    self.client = OpenAI(
                        api_key=self.api_key
                    )

    def save_api_key(
        self,
        api_key
    ):
        with open(
            API_KEY_FILE,
            "w"
        ) as f:
            json.dump(
                {"api_key": api_key},
                f
            )

    @commands.command()
    async def set_openai_key_forcountdown(
        self,
        ctx,
        api_key: str
    ):
        self.save_api_key(
            api_key
        )

        self.client = OpenAI(
            api_key=api_key
        )

        await ctx.send(
            "OpenAI key saved."
        )


async def setup(bot):
    await bot.add_cog(
        HolidayCountdown(bot)
    )
