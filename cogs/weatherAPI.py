# setup imports
import discord
from discord.ext import commands
import aiohttp
import asyncio
import os

WEATHER_KEY = os.environ["WEATHER_KEY"]
WEATHER_KEY2 = os.environ["WEATHER_KEY2"]


class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def weather(self, ctx: commands.Context, *, city: str):
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

                    # Format location with city and abbreviated state/country
                    city_name = geo_data[0]['name']
                    if 'state' in geo_data[0] and geo_data[0]['state']:
                        # For US cities, use abbreviated state
                        state_abbrev = {
                            'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
                            'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
                            'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
                            'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
                            'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
                            'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
                            'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
                            'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
                            'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
                            'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
                            'District of Columbia': 'DC'
                        }.get(geo_data[0]['state'], geo_data[0]['state'])
                        location = f"{city_name}, {state_abbrev}"
                    else:
                        # For international cities, use abbreviated country
                        country_code = geo_data[0]['country']
                        country_abbrev = {
                            'US': 'USA', 'CA': 'Can', 'GB': 'UK', 'AU': 'Aus',
                            'DE': 'Ger', 'FR': 'Fra', 'IT': 'Ita', 'ES': 'Spa',
                            'AT': 'Aut', 'CH': 'Swi', 'NL': 'Net', 'BE': 'Bel',
                            'JP': 'Jpn', 'CN': 'Chn', 'IN': 'Ind', 'BR': 'Bra',
                            'MX': 'Mex', 'RU': 'Rus', 'SE': 'Swe', 'NO': 'Nor',
                            'DK': 'Den', 'FI': 'Fin', 'PL': 'Pol', 'CZ': 'Cze'
                        }.get(country_code, country_code)
                        location = f"{city_name}, {country_abbrev}"

                    temp_c = round(weather_data["main"]["temp"])
                    temp_f = round(temp_c * 9/5 + 32)
                    feels_like_c = round(weather_data["main"]["feels_like"])
                    feels_like_f = round(feels_like_c * 9/5 + 32)
                    humidity = weather_data["main"]["humidity"]
                    wind_speed = weather_data["wind"]["speed"]
                    condition = weather_data["weather"][0]["description"]
                    image_url = f"http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@2x.png"

                    # Get precipitation probability if available
                    precip_percent = 0
                    if 'pop' in weather_data:
                        precip_percent = round(weather_data['pop'] * 100)
                    elif 'rain' in weather_data or 'snow' in weather_data:
                        precip_percent = 100  # If there's active precipitation, assume 100%

                    # Get local time from timezone offset
                    import datetime
                    timezone_offset = weather_data.get('timezone', 0)
                    local_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timezone_offset)
                    time_str = local_time.strftime("%H:%M")

                    embed = discord.Embed(colour=discord.Color(int("98FBCA", 16)))
                    embed.add_field(name="", value=f"```ansi\n\u001b[0;36m\u001b[1mCurrently in {location}: {condition}\u001b[0m\n```", inline=False)

                    # Use separate fields like the old code for better spacing
                    embed.add_field(name="Temp", value=f"{temp_c}c / {temp_f}f", inline=True)
                    embed.add_field(name="Precip", value=f"{precip_percent}%", inline=True)
                    embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
                    embed.add_field(name="Feels like", value=f"{feels_like_c}c / {feels_like_f}f", inline=True)
                    embed.add_field(name="Wind", value=f"{wind_speed} m/s", inline=True)
                    embed.add_field(name="Local time", value=f"{time_str}", inline=True)
                    embed.set_thumbnail(url=image_url)

                    await ctx.send(embed=embed)

    @commands.command()
    async def friends(self, ctx: commands.Context):
        cities = [
            "graz", "stuttgart", "gavle", "london", 
            "new york", "nashville", "port of spain", 
            "chicago", "st louis", "fargo", "denver", 
            "tucson", "los angeles", "vancouver"
        ]
        
        spaces = "     "  # 5 spaces for formatting
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        weather_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Step 1: Make API calls and collect all data
        city_results = {}
        
        async with aiohttp.ClientSession() as session:
            for city in cities:
                try:
                    # Get coordinates
                    params_geo = {"q": city, "limit": 1, "appid": WEATHER_KEY2}
                    async with session.get(geo_url, params=params_geo) as res_geo:
                        if res_geo.status != 200:
                            continue
                        geo_data = await res_geo.json()
                        if not geo_data:
                            continue

                        lat = geo_data[0]['lat']
                        lon = geo_data[0]['lon']

                        # Get weather data
                        params_weather = {
                            "lat": lat, "lon": lon, "appid": WEATHER_KEY2, "units": "metric"
                        }
                        async with session.get(weather_url, params=params_weather) as res_weather:
                            if res_weather.status != 200:
                                continue
                            weather_data = await res_weather.json()

                            # Format location
                            city_name = geo_data[0]['name']
                            if 'state' in geo_data[0] and geo_data[0]['state']:
                                state_abbrev = {
                                    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
                                    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
                                    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
                                    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
                                    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
                                    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
                                    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
                                    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
                                    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
                                    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
                                    'District of Columbia': 'DC'
                                }.get(geo_data[0]['state'], geo_data[0]['state'])
                                location = f"{city_name}, {state_abbrev}"
                            else:
                                country_code = geo_data[0]['country']
                                country_abbrev = {
                                    'US': 'USA', 'CA': 'Can', 'GB': 'UK', 'AU': 'Aus',
                                    'DE': 'Ger', 'FR': 'Fra', 'IT': 'Ita', 'ES': 'Spa',
                                    'AT': 'Aut', 'CH': 'Swi', 'NL': 'Net', 'BE': 'Bel',
                                    'JP': 'Jpn', 'CN': 'Chn', 'IN': 'Ind', 'BR': 'Bra',
                                    'MX': 'Mex', 'RU': 'Rus', 'SE': 'Swe', 'NO': 'Nor',
                                    'DK': 'Den', 'FI': 'Fin', 'PL': 'Pol', 'CZ': 'Cze'
                                }.get(country_code, country_code)
                                location = f"{city_name}, {country_abbrev}"

                            # Get weather info
                            temp_c = round(weather_data["main"]["temp"])
                            temp_f = round(temp_c * 9/5 + 32)
                            condition = weather_data["weather"][0]["description"]

                            # Get local time
                            import datetime
                            timezone_offset = weather_data.get('timezone', 0)
                            local_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timezone_offset)
                            time_str = local_time.strftime("%H:%M")

                            # Step 2: Store formatted result for this city
                            city_results[location] = f"{time_str}{spaces}{temp_c}c / {temp_f}f{spaces}{condition}"

                except Exception:
                    continue
        
        # Step 3: Build embed with pre-formatted values
        embed = discord.Embed(colour=discord.Color(int("98FBCA", 16)))
        embed.add_field(name="", value=f"```ansi\n\u001b[0;36m\u001b[1mFriends Weather Overview\u001b[0m\n```", inline=False)
        
        # Add each city as separate fields with bold location names
        for location, formatted_result in city_results.items():
            embed.add_field(name=f"**{location}**", value=f"```\n{formatted_result}\n```", inline=False)
        
        await ctx.send(embed=embed)


class Forecast(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def forecast(self, ctx: commands.Context, *, city: str):
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

                    # Format location with city and abbreviated state/country
                    city_name = geo_data[0]['name']
                    if 'state' in geo_data[0] and geo_data[0]['state']:
                        # For US cities, use abbreviated state
                        state_abbrev = {
                            'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
                            'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
                            'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
                            'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
                            'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
                            'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
                            'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
                            'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
                            'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
                            'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
                            'District of Columbia': 'DC'
                        }.get(geo_data[0]['state'], geo_data[0]['state'])
                        location = f"{city_name}, {state_abbrev}"
                    else:
                        # For international cities, use abbreviated country
                        country_code = geo_data[0]['country']
                        country_abbrev = {
                            'US': 'USA', 'CA': 'Can', 'GB': 'UK', 'AU': 'Aus',
                            'DE': 'Ger', 'FR': 'Fra', 'IT': 'Ita', 'ES': 'Spa',
                            'AT': 'Aut', 'CH': 'Swi', 'NL': 'Net', 'BE': 'Bel',
                            'JP': 'Jpn', 'CN': 'Chn', 'IN': 'Ind', 'BR': 'Bra',
                            'MX': 'Mex', 'RU': 'Rus', 'SE': 'Swe', 'NO': 'Nor',
                            'DK': 'Den', 'FI': 'Fin', 'PL': 'Pol', 'CZ': 'Cze'
                        }.get(country_code, country_code)
                        location = f"{city_name}, {country_abbrev}"

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

                    embed = discord.Embed(colour=discord.Color(int("98FBCA", 16)))
                    embed.add_field(name="", value=f"```ansi\n\u001b[0;36m\u001b[1mThe 3 day forecast for {location}\u001b[0m\n```", inline=False)
                    for i, (date, temps) in enumerate(daily_forecasts.items()):
                        if i >= 3:
                            break
                        maxtemp_c = round(temps['max'])
                        mintemp_c = round(temps['min'])
                        maxtemp_f = round(maxtemp_c * 9/5 + 32)
                        mintemp_f = round(mintemp_c * 9/5 + 32)
                        precip_percent = round(temps['pop'] * 100)

                        # Retrieve condition and image_url for the first forecast entry of each day
                        condition = forecast_data['list'][i * 8]['weather'][0]['description']
                        image_url = f"http://openweathermap.org/img/wn/{forecast_data['list'][i * 8]['weather'][0]['icon']}@2x.png"

                        # Format date nicely
                        import datetime
                        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%a, %b %d")

                        # Use separate fields like the old code for better spacing
                        embed.add_field(name=f"**{formatted_date}**", value="", inline=False)
                        embed.add_field(name="", value="     High:   " + f"{maxtemp_c}c / {maxtemp_f}f", inline=False)
                        embed.add_field(name="", value="     Low:   " + f"{mintemp_c}c / {mintemp_f}f", inline=False)
                        embed.add_field(name="", value="     Cond:   " + f"{condition}", inline=False)
                        embed.add_field(name="", value="     Precip:   " + f"{precip_percent}%", inline=False)

                        if i == 0:
                            embed.set_thumbnail(url=image_url)

                    await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Weather(client))
    await client.add_cog(Forecast(client))

