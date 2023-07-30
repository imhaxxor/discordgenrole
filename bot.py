import discord
from discord.ext import commands
import random
import asyncio
import time

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)
keys_list = []
key_expirations = {}

def get_remaining_time(seconds):
    seconds = max(seconds, 0)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours} hours, {minutes} minutes, and {seconds} seconds"

def is_admin_or_owner():
    def predicate(ctx):
        return ctx.author.guild_permissions.administrator or ctx.author.id == bot.owner_id
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@is_admin_or_owner()
async def generate(ctx, target_user_or_duration=None, *, duration=None):
    if not target_user_or_duration and not duration:
        # Generate a key without mentioning a user and specifying duration
        key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=12))
        keys_list.append(key)
        await ctx.send(f'{ctx.author.mention}, the key has been successfully generated: {key}')
        return

    if not target_user_or_duration:
        await ctx.send("Invalid format. Usage: ?generate @user 1m")
        return

    target_user = ctx.message.mentions[0] if ctx.message.mentions else None

    if not duration:
        await ctx.send("Invalid format. Usage: ?generate @user 1m")
        return

    try:
        duration_seconds = int(duration[:-1])
    except ValueError:
        await ctx.send("Invalid time format. Use numbers with 's', 'm', 'h', or 'd'. Example: 1m")
        return

    if duration.endswith("s"):
        duration_seconds = duration_seconds
    elif duration.endswith("m"):
        duration_seconds = duration_seconds * 60
    elif duration.endswith("h"):
        duration_seconds = duration_seconds * 60 * 60
    elif duration.endswith("d"):
        duration_seconds = duration_seconds * 60 * 60 * 24
    else:
        await ctx.send("Invalid time format. Use numbers with 's', 'm', 'h', or 'd'. Example: 1m")
        return

    key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=12))
    keys_list.append(key)
    key_expirations[key] = time.time() + duration_seconds

    if target_user:
        await target_user.send(f'Generated key: {key}. This key will expire in {get_remaining_time(duration_seconds)}.')
        await ctx.send(f'{ctx.author.mention}, the key has been successfully sent to {target_user.mention} in DM.')
    else:
        await ctx.send(f'{ctx.author.mention}, the key has been successfully generated: {key}. This key will expire in {get_remaining_time(duration_seconds)}.')

@bot.command()
async def redeem(ctx, key=None):
    if not key:
        await ctx.send("Invalid format. Usage: ?redeem [key]")
        return

    if key in keys_list:
        keys_list.remove(key)
        key_expirations.pop(key)
        role = discord.utils.get(ctx.guild.roles, name="GenAccess")
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention}, the key has been successfully redeemed.")
        await asyncio.sleep(30)  # Adjust the time duration as needed
        await ctx.author.remove_roles(role)
    else:
        await ctx.send("Invalid key. The key does not exist or has already been redeemed.")

async def check_expired_keys():
    while not bot.is_closed():
        await asyncio.sleep(10)
        current_time = time.time()
        expired_keys = [key for key, exp_time in key_expirations.items() if exp_time <= current_time]

        for key in expired_keys:
            key_expirations.pop(key)
            keys_list.remove(key)
            print(f"Key {key} has expired and been removed.")

loop = asyncio.get_event_loop()
loop.create_task(check_expired_keys())

# Replace "YOUR_BOT_TOKEN" with your actual bot token
bot.run("MTAzMjY0NDEwNzQwMDY1MDc2NA.GJXlh0.zQJii-McDwoCZk5HUw9hOVnsErxu8qVspbjPS0")
