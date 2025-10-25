# D&D 5e Character Creator using the official D&D 5e API
import discord
from discord.ext import commands
import aiohttp
import random
import json



class DnDCharacterCreator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.api_base = "https://www.dnd5eapi.co/api/2014"
        
    async def fetch_api_data(self, endpoint):
        """Fetch data from the D&D 5e API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}{endpoint}") as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception:
            return None

    def roll_ability_scores(self, method="4d6_drop_lowest"):
        """Generate ability scores using various methods"""
        if method == "4d6_drop_lowest":
            # Roll 4d6, drop lowest
            scores = []
            for _ in range(6):
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.sort(reverse=True)
                scores.append(sum(rolls[:3]))
            return scores
        elif method == "standard_array":
            # Standard array from PHB
            return [15, 14, 13, 12, 10, 8]
        elif method == "point_buy":
            # Point buy default array (can be customized)
            return [13, 13, 13, 12, 12, 12]
        else:
            # 3d6 straight
            return [sum(random.randint(1, 6) for _ in range(3)) for _ in range(6)]

    def calculate_modifier(self, score):
        """Calculate ability modifier from ability score"""
        return (score - 10) // 2

    @commands.command()
    async def dnd_races(self, ctx):
        """List all available D&D races"""
        races_data = await self.fetch_api_data("/races")
        if not races_data:
            await ctx.send("Unable to fetch races data from the API.")
            return

        embed = discord.Embed(
            title="Available D&D 5e Races",
            description="Choose from these official races for your character:",
            color=discord.Color.gold()
        )
        
        race_list = []
        for race in races_data["results"]:
            race_list.append(f"• **{race['name']}** (`{race['index']}`)")
        
        # Split into chunks if too long
        race_text = "\n".join(race_list)
        if len(race_text) > 1024:
            mid = len(race_list) // 2
            embed.add_field(name="Races (1/2)", value="\n".join(race_list[:mid]), inline=True)
            embed.add_field(name="Races (2/2)", value="\n".join(race_list[mid:]), inline=True)
        else:
            embed.add_field(name="All Races", value=race_text, inline=False)
        
        embed.set_footer(text="Use !dnd_race <race_name> for detailed info about a specific race")
        await ctx.send(embed=embed)

    @commands.command()
    async def dnd_classes(self, ctx):
        """List all available D&D classes"""
        classes_data = await self.fetch_api_data("/classes")
        if not classes_data:
            await ctx.send("Unable to fetch classes data from the API.")
            return

        embed = discord.Embed(
            title="Available D&D 5e Classes",
            description="Choose from these official classes for your character:",
            color=discord.Color.red()
        )
        
        class_list = []
        for char_class in classes_data["results"]:
            class_list.append(f"• **{char_class['name']}** (`{char_class['index']}`)")
        
        # Split into chunks if too long
        class_text = "\n".join(class_list)
        if len(class_text) > 1024:
            mid = len(class_list) // 2
            embed.add_field(name="Classes (1/2)", value="\n".join(class_list[:mid]), inline=True)
            embed.add_field(name="Classes (2/2)", value="\n".join(class_list[mid:]), inline=True)
        else:
            embed.add_field(name="All Classes", value=class_text, inline=False)
        
        embed.set_footer(text="Use !dnd_class <class_name> for detailed info about a specific class")
        await ctx.send(embed=embed)

    @commands.command()
    async def dnd_race(self, ctx, *, race_name: str):
        """Get detailed information about a specific race"""
        race_data = await self.fetch_api_data(f"/races/{race_name.lower().replace(' ', '-')}")
        if not race_data:
            await ctx.send(f"Race '{race_name}' not found. Use `!dnd_races` to see available races.")
            return

        embed = discord.Embed(
            title=f"{race_data['name']}",
            description="\n".join(race_data.get('desc', ['No description available.'])),
            color=discord.Color.gold()
        )

        # Ability Score Increases
        if 'ability_score_increases' in race_data:
            asi_text = []
            for asi in race_data['ability_score_increases']:
                asi_text.append(f"**{asi['ability_score']['name']}** +{asi['bonus']}")
            embed.add_field(name="Ability Score Increases", value="\n".join(asi_text), inline=True)

        # Size and Speed
        embed.add_field(name="Size", value=race_data.get('size', 'Unknown'), inline=True)
        embed.add_field(name="Speed", value=f"{race_data.get('speed', 'Unknown')} ft", inline=True)

        # Languages
        if 'languages' in race_data and race_data['languages']:
            lang_text = [lang['name'] for lang in race_data['languages']]
            embed.add_field(name="Languages", value=", ".join(lang_text), inline=False)

        # Traits
        if 'traits' in race_data and race_data['traits']:
            trait_text = [trait['name'] for trait in race_data['traits']]
            if len(", ".join(trait_text)) > 1024:
                trait_text = trait_text[:5] + ["..."]
            embed.add_field(name="Racial Traits", value=", ".join(trait_text), inline=False)

        # Subraces
        if 'subraces' in race_data and race_data['subraces']:
            subrace_text = [subrace['name'] for subrace in race_data['subraces']]
            embed.add_field(name="Subraces", value=", ".join(subrace_text), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def dnd_class(self, ctx, *, class_name: str):
        """Get detailed information about a specific class"""
        class_data = await self.fetch_api_data(f"/classes/{class_name.lower().replace(' ', '-')}")
        if not class_data:
            await ctx.send(f"Class '{class_name}' not found. Use `!dnd_classes` to see available classes.")
            return

        embed = discord.Embed(
            title=f"{class_data['name']}",
            description=f"**Hit Die:** d{class_data.get('hit_die', 'Unknown')}",
            color=discord.Color.red()
        )

        # Primary Ability
        if 'primary_ability' in class_data and class_data['primary_ability']:
            primary_abilities = [ability['name'] for ability in class_data['primary_ability']]
            embed.add_field(name="Primary Ability", value=", ".join(primary_abilities), inline=True)

        # Saving Throw Proficiencies
        if 'saving_throws' in class_data and class_data['saving_throws']:
            saving_throws = [save['name'] for save in class_data['saving_throws']]
            embed.add_field(name="Saving Throws", value=", ".join(saving_throws), inline=True)

        # Proficiencies (condensed)
        if 'proficiencies' in class_data and class_data['proficiencies']:
            prof_count = len(class_data['proficiencies'])
            embed.add_field(name="Proficiencies", value=f"{prof_count} total proficiencies", inline=True)

        # Starting Equipment
        if 'starting_equipment' in class_data and class_data['starting_equipment']:
            eq_count = len(class_data['starting_equipment'])
            embed.add_field(name="Starting Equipment", value=f"{eq_count} starting items", inline=True)

        # Spellcasting
        if 'spellcasting' in class_data:
            spell_ability = class_data['spellcasting'].get('spellcasting_ability', {}).get('name', 'Unknown')
            embed.add_field(name="Spellcasting", value=f"Ability: {spell_ability}", inline=True)

        # Subclasses
        if 'subclasses' in class_data and class_data['subclasses']:
            subclass_count = len(class_data['subclasses'])
            embed.add_field(name="Subclasses", value=f"{subclass_count} available subclasses", inline=True)

        embed.set_footer(text=f"Use !dnd_create to start creating a {class_data['name']} character!")
        await ctx.send(embed=embed)

    @commands.command()
    async def dnd_create(self, ctx, race_name: str = None, class_name: str = None, *, character_name: str = None):
        """Create a random D&D character or specify race/class"""
        
        # Get races and classes data
        races_data = await self.fetch_api_data("/races")
        classes_data = await self.fetch_api_data("/classes")
        
        if not races_data or not classes_data:
            await ctx.send("Unable to fetch character data from the API.")
            return

        # Select race
        if race_name:
            race_index = race_name.lower().replace(' ', '-')
            race_info = next((r for r in races_data["results"] if r["index"] == race_index), None)
            if not race_info:
                await ctx.send(f"Race '{race_name}' not found. Use `!dnd_races` to see available races.")
                return
        else:
            race_info = random.choice(races_data["results"])

        # Select class
        if class_name:
            class_index = class_name.lower().replace(' ', '-')
            class_info = next((c for c in classes_data["results"] if c["index"] == class_index), None)
            if not class_info:
                await ctx.send(f"Class '{class_name}' not found. Use `!dnd_classes` to see available classes.")
                return
        else:
            class_info = random.choice(classes_data["results"])

        # Get detailed race data for ability score increases
        race_details = await self.fetch_api_data(f"/races/{race_info['index']}")
        class_details = await self.fetch_api_data(f"/classes/{class_info['index']}")

        # Generate character name if not provided
        if not character_name:
            name_prefixes = ["Aed", "Bren", "Cor", "Dar", "Eld", "Finn", "Gar", "Hal", "Ira", "Jor", "Kel", "Lyr", "Mor", "Nyx", "Ori", "Pax", "Quin", "Ren", "Syl", "Tor", "Uma", "Vex", "Wyl", "Xar", "Yor", "Zar"]
            name_suffixes = ["wyn", "dor", "ion", "eth", "ara", "iel", "ost", "and", "rin", "las", "mir", "nor", "val", "thas", "ael", "orn", "ith", "ul", "an", "en"]
            character_name = f"{random.choice(name_prefixes)}{random.choice(name_suffixes)}"

        # Roll ability scores
        base_scores = self.roll_ability_scores("4d6_drop_lowest")
        ability_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        
        # Apply racial bonuses
        final_scores = base_scores.copy()
        racial_bonuses = {}
        
        if race_details and 'ability_score_increases' in race_details:
            for asi in race_details['ability_score_increases']:
                ability_name = asi['ability_score']['name']
                bonus = asi['bonus']
                ability_index = ability_names.index(ability_name)
                final_scores[ability_index] += bonus
                racial_bonuses[ability_name] = bonus

        # Create character embed
        embed = discord.Embed(
            title=f"{character_name}",
            description=f"**Race:** {race_info['name']}\n**Class:** {class_info['name']}\n**Level:** 1",
            color=discord.Color.purple()
        )

        # Ability Scores
        ability_text = []
        for i, (name, base, final) in enumerate(zip(ability_names, base_scores, final_scores)):
            modifier = self.calculate_modifier(final)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            
            if name in racial_bonuses:
                ability_text.append(f"**{name}:** {final} ({modifier_str}) *[{base}+{racial_bonuses[name]}]*")
            else:
                ability_text.append(f"**{name}:** {final} ({modifier_str})")

        embed.add_field(name="Ability Scores", value="\n".join(ability_text), inline=True)

        # Character details
        details = []
        if race_details:
            details.append(f"**Size:** {race_details.get('size', 'Medium')}")
            details.append(f"**Speed:** {race_details.get('speed', 30)} ft")
        
        if class_details:
            details.append(f"**Hit Die:** d{class_details.get('hit_die', 8)}")
            
        embed.add_field(name="Details", value="\n".join(details), inline=True)

        # HP Calculation (max at level 1)
        if class_details:
            hit_die = class_details.get('hit_die', 8)
            con_modifier = self.calculate_modifier(final_scores[2])  # CON is index 2
            hp = hit_die + con_modifier
            embed.add_field(name="Hit Points", value=f"{max(1, hp)} HP", inline=True)

        embed.set_footer(text="Character created! Use !dnd_race and !dnd_class for more details about your character's abilities.")
        
        # Send to user via DM for privacy
        try:
            await ctx.author.send(embed=embed)
            await ctx.send(f"{ctx.author.mention} Your D&D character has been sent to your DMs!")
        except discord.Forbidden:
            await ctx.send(embed=embed)

    @commands.command()
    async def dnd_rolls(self, ctx, method: str = "4d6"):
        """Generate ability scores using different methods"""
        methods = {
            "4d6": "4d6_drop_lowest",
            "standard": "standard_array", 
            "point": "point_buy",
            "3d6": "3d6_straight"
        }
        
        if method not in methods:
            embed = discord.Embed(
                title="Ability Score Generation Methods",
                description="Choose a method to generate ability scores:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Available Methods",
                value="• `4d6` - Roll 4d6, drop lowest (default)\n• `standard` - Standard Array [15,14,13,12,10,8]\n• `point` - Point Buy Array [13,13,13,12,12,12]\n• `3d6` - Straight 3d6 rolls",
                inline=False
            )
            embed.add_field(
                name="Usage",
                value="`!dnd_rolls <method>`\nExample: `!dnd_rolls standard`",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        scores = self.roll_ability_scores(methods[method])
        ability_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        
        embed = discord.Embed(
            title=f"Ability Scores ({method.upper()})",
            color=discord.Color.blue()
        )
        
        score_text = []
        total = 0
        for name, score in zip(ability_names, scores):
            modifier = self.calculate_modifier(score)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            score_text.append(f"**{name}:** {score} ({modifier_str})")
            total += score
        
        embed.add_field(name="Generated Scores", value="\n".join(score_text), inline=True)
        embed.add_field(name="Total", value=f"{total} points", inline=True)
        
        if method == "4d6":
            embed.set_footer(text="These scores are rolled fresh each time! Assign them to abilities as you see fit.")
        else:
            embed.set_footer(text="These are the standard scores for this method. Assign them to abilities as you see fit.")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def dnd_help(self, ctx):
        """Show D&D character creator help"""
        embed = discord.Embed(
            title="D&D 5e Character Creator Help",
            description="Create amazing D&D characters using the official 5e API!",
            color=discord.Color.dark_purple()
        )
        
        embed.add_field(
            name="Browse Options",
            value="`!dnd_races` - List all available races\n`!dnd_classes` - List all available classes\n`!dnd_race <name>` - Detailed race info\n`!dnd_class <name>` - Detailed class info",
            inline=False
        )
        
        embed.add_field(
            name="Character Creation", 
            value="`!dnd_create` - Create random character\n`!dnd_create <race> <class>` - Create specific character\n`!dnd_create <race> <class> <name>` - Create named character",
            inline=False
        )
        
        embed.add_field(
            name="Ability Scores",
            value="`!dnd_rolls` - Show rolling methods\n`!dnd_rolls <method>` - Generate scores\nMethods: 4d6, standard, point, 3d6",
            inline=False
        )
        
        embed.add_field(
            name="Examples",
            value="`!dnd_create elf wizard Gandalf`\n`!dnd_race dragonborn`\n`!dnd_rolls standard`",
            inline=False
        )
        
        embed.set_footer(text="All character sheets are sent via DM for privacy! Data from dnd5eapi.co")
        await ctx.send(embed=embed)


    @commands.command(name='dice')
    async def dice(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception as e:
            await ctx.send('Format has to be in #d#')
            return
        results = [random.randint(1, limit) for _ in range(rolls)]
        result_str = ', '.join(str(result) for result in results)
        total = sum(results)
        await ctx.send(f'{ctx.author.mention} rolled: {result_str}\nFor a total of: {total}')
        

async def setup(client):
    await client.add_cog(DnDCharacterCreator(client))
