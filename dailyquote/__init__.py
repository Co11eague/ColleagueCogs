from .dailyquote import DailyQuoteCog


async def setup(bot):
    await bot.add_cog(DailyQuoteCog(bot))