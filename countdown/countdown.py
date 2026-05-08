import asyncio
from datetime import datetime, date

import aiocron
import discord
import pytz
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
    """Kasdienis Malagos countdown."""

    def __init__(self, bot: Red):
        self.bot = bot

        self.channel_id = 202397765941198848

        # Countdown start
        self.start_date = date(2026, 5, 8)

        # Holiday date
        self.holiday_date = date(2026, 6, 30)

        self.timezone = pytz.timezone("Europe/London")

        self.total_days = (
            self.holiday_date - self.start_date
        ).days

        self.cron = aiocron.crontab(
            "0 8 * * *",
            func=lambda: asyncio.create_task(
                self.send_countdown()
            ),
            start=True
        )

    def lithuanian_days(self, days: int):
        if days % 10 == 1 and days % 100 != 11:
            return "diena"

        elif days % 10 in [2, 3, 4, 5, 6, 7, 8, 9] and not (
            11 <= days % 100 <= 19
        ):
            return "dienos"

        return "dienų"

    def generate_progress_bar(self, current, total, length=20):
        progress = current / total
        filled = int(length * progress)

        bar = "▓" * filled + "░" * (length - filled)

        percentage = round(progress * 100)

        return f"`{bar}` {percentage}%"

    async def send_countdown(self):
        try:
            channel = await self.bot.fetch_channel(
                self.channel_id
            )
        except Exception:
            return

        now = datetime.now(self.timezone)
        today = now.date()

        days_left = (
            self.holiday_date - today
        ).days

        if days_left < 0:
            return

        days_passed = (
            today - self.start_date
        ).days

        progress_bar = self.generate_progress_bar(
            days_passed,
            self.total_days
        )

        fact = COUNTDOWN_FACTS.get(
            days_left,
            "Kiekviena diena priartina prie Malagos."
        )

        if days_left == 0:
            message = (
                f"Pagaliau! Šiandien skrendam į Malagą.\n\n"
                f"{progress_bar}\n\n"
                f"{fact}"
            )

        elif days_left == 1:
            message = (
                f"Liko tik 1 diena iki mūsų kelionės į Malagą.\n\n"
                f"{progress_bar}\n\n"
                f"{fact}"
            )

        else:
            day_word = self.lithuanian_days(days_left)

            message = (
                f"Liko {days_left} {day_word} iki mūsų kelionės į Malagą.\n\n"
                f"{progress_bar}\n\n"
                f"{fact}"
            )

        await channel.send(message)

    @commands.command()
    async def malagacountdown(self, ctx):
        """Parodo countdown."""

        now = datetime.now(self.timezone)
        today = now.date()

        days_left = (
            self.holiday_date - today
        ).days

        if days_left < 0:
            await ctx.send(
                "Kelionė į Malagą jau praėjo."
            )
            return

        days_passed = (
            today - self.start_date
        ).days

        progress_bar = self.generate_progress_bar(
            days_passed,
            self.total_days
        )

        fact = COUNTDOWN_FACTS.get(
            days_left,
            "Kiekviena diena priartina prie Malagos."
        )

        if days_left == 0:
            message = (
                f"Šiandien skrendam į Malagą!\n\n"
                f"{progress_bar}\n\n"
                f"{fact}"
            )

        elif days_left == 1:
            message = (
                f"Liko tik 1 diena iki Malagos.\n\n"
                f"{progress_bar}\n\n"
                f"{fact}"
            )

        else:
            day_word = self.lithuanian_days(days_left)

            message = (
                f"Liko {days_left} {day_word} iki Malagos.\n\n"
                f"{progress_bar}\n\n"
                f"{fact}"
            )

        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(HolidayCountdown(bot))