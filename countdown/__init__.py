from .countdown import HolidayCountdown


async def setup(bot):
    await bot.add_cog(HolidayCountdown(bot))