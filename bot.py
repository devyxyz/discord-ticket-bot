import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store ticket categories
TICKET_CATEGORIES = {
    "1": "Partnership",
    "2": "Any Concern",
    "3": "Buy Product"
}

# YOUR BOT TOKEN HERE
TOKEN = "your_discord_bot_token_here"

@bot.event
async def on_ready():
    print(f"{bot.user} is now running! 🤖")
    print(f"Connected to {len(bot.guilds)} server(s)")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tickets | !post"))

@bot.command(name="post")
async def post_message(ctx, channel: discord.TextChannel):
    """Create a post with ticket category selection"""
    
    embed = discord.Embed(
        title="Welcome sa bago! 🎉",
        description="Pumili ng kategori para sa iyong ticket:",
        color=discord.Color.blue()
    )
    
    for key, category in TICKET_CATEGORIES.items():
        embed.add_field(name=f"{key}. {category}", value="Click sa reaction", inline=False)
    
    embed.set_footer(text="React with 1️⃣, 2️⃣, or 3️⃣ para magbukas ng ticket")
    
    message = await channel.send(embed=embed)
    
    # Add reactions
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    
    await ctx.send(f"✅ Post na gawa sa {channel.mention}")

@bot.event
async def on_reaction_add(reaction, user):
    """Handle ticket creation when user reacts"""
    
    if user.bot:
        return
    
    # Check if reaction is one of our ticket reactions
    if reaction.emoji not in ["1️⃣", "2️⃣", "3️⃣"]:
        return
    
    # Map emoji to category
    emoji_map = {"1️⃣": "1", "2️⃣": "2", "3️⃣": "3"}
    category_key = emoji_map[reaction.emoji]
    category_name = TICKET_CATEGORIES[category_key]
    
    guild = reaction.message.guild
    
    # Check if ticket category exists, if not create it
    ticket_category = None
    for cat in guild.categories:
        if cat.name.lower() == "ticket":
            ticket_category = cat
            break
    
    if not ticket_category:
        ticket_category = await guild.create_category("ticket")
    
    # Create ticket channel
    ticket_channel_name = f"ticket-{user.name.lower()}"
    
    # Check if user already has a ticket
    existing_channel = discord.utils.get(
        guild.text_channels,
        name=ticket_channel_name,
        category=ticket_category
    )
    
    if existing_channel:
        await user.send(f"❌ Mayroon ka nang ticket: {existing_channel.mention}")
        return
    
    # Create new ticket channel
    ticket_channel = await ticket_category.create_text_channel(
        ticket_channel_name,
        topic=f"Ticket Category: {category_name} | User: {user.mention}"
    )
    
    # Set permissions - only user and admins can see
    await ticket_channel.set_permissions(guild.default_role, view_channel=False)
    await ticket_channel.set_permissions(user, view_channel=True)
    
    # Send welcome message
    embed = discord.Embed(
        title=f"Ticket Opened - {category_name}",
        description=f"Hello {user.mention}! 👋\n\nKategori: **{category_name}**\n\nMagsulat ng iyong concern dito. Maghihintay kami ng team.",
        color=discord.Color.green()
    )
    
    await ticket_channel.send(embed=embed)
    await user.send(f"✅ Ticket na gawa! {ticket_channel.mention}")

@bot.command(name="close")
async def close_ticket(ctx):
    """Close a ticket (admin only)"""
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Kailangan mo ng admin permissions!")
        return
    
    # Check if this is a ticket channel
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("❌ Hindi ito ticket channel!")
        return
    
    embed = discord.Embed(
        title="Ticket Closed",
        description="Ang ticket na ito ay sarado na.",
        color=discord.Color.red()
    )
    
    await ctx.send(embed=embed)
    await asyncio.sleep(2)
    await ctx.channel.delete()

@bot.command(name="help")
async def help_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="Available Commands",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="!post #channel", value="Lumikha ng post na may ticket options", inline=False)
    embed.add_field(name="!close", value="Tutuparin ang ticket (admin only)", inline=False)
    embed.add_field(name="!help", value="Ipakita ang commands", inline=False)
    
    await ctx.send(embed=embed)

# Run the bot
print("🚀 Starting Discord Ticket Bot...")
bot.run(TOKEN)
