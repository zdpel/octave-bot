import os
from dotenv import load_dotenv
from discord import Color, Embed, Intents, Message
from discord.ext import commands
from AudioController import AudioController

#load toxen from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#intents
intents: Intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

controller = AudioController()
    
#bot startup
@bot.event
async def on_ready():
    print(f'{bot.user} is now running')

@bot.command(aliases=['j', 'connect', 'c'])
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await ctx.send(f"Connecting to {channel}")
        await channel.connect()
    else:
        await ctx.send("You are not connected to a voice channel")

@bot.command(aliases=['dc', 'leave'])
async def disconnect(ctx):
    if ctx.author.voice and ctx.voice_client:
        await ctx.send("Leaving voice channel")
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I am not connected to a voice channel")

@bot.command(aliases=['p'])
async def play(ctx, *, query):
    if not ctx.voice_client:
        await join(ctx)
    await controller.play(ctx, query)

@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        await ctx.send("Paused")
        ctx.voice_client.pause()

@bot.command()
async def clear(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Clearing...")
        controller.playlist.clear()

@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        await ctx.send("Resuming...")
        ctx.voice_client.resume()

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        await ctx.send("Skipped")
        ctx.voice_client.stop()

@bot.command()
async def queue(ctx):
    if len(controller.playlist) == 0:
        await ctx.send("Queue is empty")
    else:
        embed = controller.get_queue_embed()
        await ctx.send(embed=embed)

@bot.command()
async def remove(ctx, index: int):
    if index < 0 or index > len(controller.playlist):
        await ctx.send("Invalid index")
    else:
        controller.remove(index-1)
        await ctx.send(f'Removed song at index {index}')

@bot.command()
async def current(ctx):
    if controller.current_song:
        await ctx.send(f'Currently playing: {controller.current_song}')
    else:
        await ctx.send('Nothing is currently playing')

@bot.command()
async def help(ctx):
    embed = Embed(title="Commands", color=Color.random())
    embed.add_field(name="!join", value="Join your voice channel", inline=False)
    embed.add_field(name="!disconnect", value="Leave your voice channel", inline=False)
    embed.add_field(name="!play <query>", value="Play song from youtube (can be youtube link or search)", inline=False)
    embed.add_field(name="!pause", value="Pause current song", inline=False)
    embed.add_field(name="!resume", value="Resume current song", inline=False)
    embed.add_field(name="!skip", value="Skip current song", inline=False)
    embed.add_field(name="!queue", value="Display queue", inline=False)
    embed.add_field(name="!remove <index>", value="Remove song at index from queue", inline=False)
    embed.add_field(name="!current", value="Display current song info", inline=False)
    embed.add_field(name="!clear", value="Stop current song and clear queue", inline=False)
    await ctx.send(embed=embed)



#main entry
def main():
    bot.run(token=TOKEN)

if __name__ == '__main__':
    main()



