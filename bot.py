import discord
import re
from discord.ext import commands
from config import token  

intents = discord.Intents.default()
intents.members = True  
intents.message_content = True  

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')


@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="general")
    if welcome_channel:
        await welcome_channel.send(f"👋 Welcome {member.mention} to {member.guild.name}! Please read the rules.")


@bot.event
async def on_member_remove(member):
    log_channel = discord.utils.get(member.guild.text_channels, name="log")
    if log_channel:
        await log_channel.send(f"❌ {member.name} has left the server.")


@bot.event
async def on_message_delete(message):
    log_channel = discord.utils.get(message.guild.text_channels, name="log")
    if log_channel:
        await log_channel.send(f"🗑️ A message from {message.author.name} was deleted: {message.content}")


@bot.event
async def on_message_edit(before, after):
    if before.content == after.content:
        return  

    log_channel = discord.utils.get(before.guild.text_channels, name="log")
    if log_channel:
        await log_channel.send(f"✏️ {before.author.name} edited a message:\n**Before:** {before.content}\n**After:** {after.content}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  

    link_pattern = re.compile(r'https?://\S+|www\.\S+')
    if link_pattern.search(message.content):
        try:
            await message.guild.ban(message.author, reason="Posting links is not allowed")
            await message.channel.send(f"🚨 {message.author.name} has been banned for sending a link.")
        except discord.Forbidden:
            await message.channel.send("❌ I don't have permission to ban members.")
        except discord.HTTPException:
            await message.channel.send("⚠️ Failed to ban the user due to an error.")

    await bot.process_commands(message)  


@bot.command()
async def start(ctx):
    await ctx.send("👋 Hi! I'm a chat manager bot!")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member:
        if ctx.author.top_role <= member.top_role:
            await ctx.send("⛔ You cannot ban a user with equal or higher rank!")
        else:
            await ctx.guild.ban(member)
            await ctx.send(f"✅ User {member.name} was banned.")
    else:
        await ctx.send("⚠️ Use `!ban @user` to ban someone.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You do not have permission to ban members.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("🔍 User not found.")

bot.run(token)
