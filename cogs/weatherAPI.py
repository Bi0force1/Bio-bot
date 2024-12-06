# setup imports
import discord
from discord.ext import commands
import aiohttp
import asyncio
import os

WEATHER_KEY = os.environ["WEATHER_KEY"]
WEATHER_KEY2 = os.environ["WEATHER_KEY2"]

# set common variables
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)


class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Weather query and response
    @client.command()
    async def weather(self, ctx: commands.Context, *, city: str):

        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": WEATHER_KEY,
            "q": city
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as res:
                data = await res.json()
                location = data["location"]["name"]
                region = data["location"]["region"]
                localtime = data["location"]["localtime"]
                temp_c = data["current"]["temp_c"]
                temp_f = data["current"]["temp_f"]
                humidity = data["current"]["humidity"]
                wind_kph = data["current"]["wind_kph"]
                wind_mph = data["current"]["wind_mph"]
                condition = data["current"]["condition"]["text"]
                image_url = "http:" + data["current"]["condition"]["icon"]

                embed = discord.Embed(title=f"The current weather for {location}, {region}", description=f"The condition in `{location}` is `{condition}` as of {localtime}", colour=discord.Color.from_rgb(83,195,190))
                embed.add_field(name="Temperature", value=f"{temp_c} C°  |  {temp_f} F°")
                embed.add_field(name="Humidity",value=f"{humidity}%")
                embed.add_field(name="Wind",value=f"{wind_kph} kph | {wind_mph} mph")
                embed.set_thumbnail(url=image_url)

                await ctx.send(embed=embed)


class Forecast(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Weather query and response
    @client.command()
    async def forecast(self, ctx: commands.Context, *, city: str):
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": WEATHER_KEY,
            "q": city,
            "days": 3
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as res:
                data = await res.json()

                location = data["location"]["name"]
                region = data["location"]["region"]
                forecastday = data["forecast"]["forecastday"][0]
                day = forecastday["date"]
                maxtemp_c = forecastday["day"]["maxtemp_c"]
                maxtemp_f = forecastday["day"]["maxtemp_f"]
                mintemp_c = forecastday["day"]["mintemp_c"]
                mintemp_f = forecastday["day"]["mintemp_f"]
                rain = forecastday["day"]["daily_chance_of_rain"]
                snow = forecastday["day"]["daily_chance_of_snow"]
                forecastday2 = data["forecast"]["forecastday"][1]
                day2 = forecastday2["date"]
                maxtemp_c2 = forecastday2["day"]["maxtemp_c"]
                maxtemp_f2 = forecastday2["day"]["maxtemp_f"]
                mintemp_c2 = forecastday2["day"]["mintemp_c"]
                mintemp_f2 = forecastday2["day"]["mintemp_f"]
                rain2 = forecastday2["day"]["daily_chance_of_rain"]
                snow2 = forecastday2["day"]["daily_chance_of_snow"]
                forecastday3 = data["forecast"]["forecastday"][2]
                day3 = forecastday3["date"]
                maxtemp_c3 = forecastday3["day"]["maxtemp_c"]
                maxtemp_f3 = forecastday3["day"]["maxtemp_f"]
                mintemp_c3 = forecastday3["day"]["mintemp_c"]
                mintemp_f3 = forecastday3["day"]["mintemp_f"]
                rain3 = forecastday3["day"]["daily_chance_of_rain"]
                snow3 = forecastday3["day"]["daily_chance_of_snow"]

                embed = discord.Embed(title=f"{location}, {region}", colour=discord.Color.from_rgb(83,195,190))
                
                embed.add_field(name=" ", value=f"""**Date:** {day} \n **Low:** {mintemp_c} C° | {mintemp_f} F° \n **High:** {maxtemp_c} C° | {maxtemp_f} F°""", inline=True )
                embed.add_field(name=" ",value=f"""Chance of Rain: {rain} % \n Chance of Snow: {snow} %""", inline=False)

                embed.add_field(name=" ", value=f"""**Date:** {day2} \n **Low:** {mintemp_c2} C° | {mintemp_f2} F° \n **High:** {maxtemp_c2} C° | {maxtemp_f2} F°""", inline=True )
                embed.add_field(name=" ",value=f"""Chance of Rain: {rain2} % \n Chance of Snow: {snow2} %""", inline=False)

                embed.add_field(name=" ", value=f"""**Date:** {day3} \n **Low:** {mintemp_c3} C° | {mintemp_f3} F° \n **High:** {maxtemp_c3} C° | {maxtemp_f3} F°""", inline=True )
                embed.add_field(name=" ",value=f"""Chance of Rain: {rain3} % \n Chance of Snow: {snow3} %""", inline=False)

                await ctx.send(embed=embed)


class Weather2(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def weather2(self, ctx: commands.Context, *, city: str):
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        weather_url = "http://api.openweathermap.org/data/2.5/weather"
        params_geo = {
            "q": city,
            "limit": 1,
            "appid": WEATHER_KEY2
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url, params=params_geo) as res_geo:
                geo_data = await res_geo.json()
                if not geo_data:
                    await ctx.send(f"Could not find geolocation for city: {city}")
                    return
                
                lat = geo_data[0]['lat']
                lon = geo_data[0]['lon']
                
                params_weather = {
                    "lat": lat,
                    "lon": lon,
                    "appid": WEATHER_KEY2,
                    "units": "metric"  # Change to 'imperial' for Fahrenheit
                }

                async with session.get(weather_url, params=params_weather) as res_weather:
                    weather_data = await res_weather.json()
                    if res_weather.status != 200:
                        await ctx.send(f"Failed to retrieve weather data for {city}")
                        return

                    location = f"{geo_data[0]['name']}, {geo_data[0]['state']}" if 'state' in geo_data[0] else geo_data[0]['name']
                    localtime = weather_data["dt"]
                    temp_c = weather_data["main"]["temp"]
                    temp_f = temp_c * 9/5 + 32
                    humidity = weather_data["main"]["humidity"]
                    wind_speed = weather_data["wind"]["speed"]
                    condition = weather_data["weather"][0]["description"]
                    image_url = f"http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@2x.png"

                    embed = discord.Embed(title=f"The current weather for {location}", description=f"The condition in `{location}` is `{condition}`.", colour=discord.Color.from_rgb(83, 195, 190))
                    embed.add_field(name="Temperature", value=f"{temp_c} °C | {temp_f} °F")
                    embed.add_field(name="Humidity", value=f"{humidity}%")
                    embed.add_field(name="Wind Speed", value=f"{wind_speed} m/s")
                    embed.set_thumbnail(url=image_url)

                    await ctx.send(embed=embed)


class Forecast2(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def forecast2(self, ctx: commands.Context, *, city: str):
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        params_geo = {
            "q": city,
            "limit": 1,
            "appid": WEATHER_KEY2
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url, params=params_geo) as res_geo:
                geo_data = await res_geo.json()
                if not geo_data:
                    await ctx.send(f"Could not find geolocation for city: {city}")
                    return
                
                lat = geo_data[0]['lat']
                lon = geo_data[0]['lon']
                
                params_forecast = {
                    "lat": lat,
                    "lon": lon,
                    "appid": WEATHER_KEY2,
                    "units": "metric",  # Change to 'imperial' for Fahrenheit
                    "cnt": 24 * 3  # Get forecast for next 3 days (8 intervals per day)
                }

                async with session.get(forecast_url, params=params_forecast) as res_forecast:
                    forecast_data = await res_forecast.json()
                    if res_forecast.status != 200:
                        await ctx.send(f"Failed to retrieve forecast data for {city}")
                        return

                    daily_forecasts = {}
                    for forecast in forecast_data['list']:
                        date = forecast['dt_txt'].split(' ')[0]
                        temp_max = forecast['main']['temp_max']
                        temp_min = forecast['main']['temp_min']
                        if date not in daily_forecasts:
                            daily_forecasts[date] = {'max': temp_max, 'min': temp_min, 'pop': forecast['pop']}
                        else:
                            daily_forecasts[date]['max'] = max(daily_forecasts[date]['max'], temp_max)
                            daily_forecasts[date]['min'] = min(daily_forecasts[date]['min'], temp_min)
                            daily_forecasts[date]['pop'] = max(daily_forecasts[date]['pop'], forecast['pop'])  # Use max pop for chance of rain

                    embed = discord.Embed(title=f"{city} 3-day Forecast", colour=discord.Color.from_rgb(83, 195, 190))
                    for i, (date, temps) in enumerate(daily_forecasts.items()):
                        if i >= 3:
                            break
                        maxtemp_c = temps['max']
                        mintemp_c = temps['min']
                        maxtemp_f = maxtemp_c * 9/5 + 32
                        mintemp_f = mintemp_c * 9/5 + 32
                        rain = temps['pop'] * 100  # Probability of precipitation
                        # Retrieve condition and image_url for the first forecast entry of each day
                        condition = forecast_data['list'][i * 8]['weather'][0]['description']
                        image_url = f"http://openweathermap.org/img/wn/{forecast_data['list'][i * 8]['weather'][0]['icon']}@2x.png"

                        embed.add_field(name=f"Date: {date}",
                                        value=f"**Condition:** {condition}\n**Low:** {mintemp_c} °C | {mintemp_f} °F\n**High:** {maxtemp_c} °C | {maxtemp_f} °F\n**Chance of Rain:** {rain}%",
                                        inline=False)
                        if i == 0:
                            embed.set_thumbnail(url=image_url)

                    await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Weather(client))
    await client.add_cog(Forecast(client))
    await client.add_cog(Weather2(client))
    await client.add_cog(Forecast2(client))
