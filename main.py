import os
import discord
from discord.ext import commands
from discord.ext.voice_recv import VoiceRecvClient, BasicSink, VoiceData
from dotenv import load_dotenv
import wave
import audioop

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.connect(cls=VoiceRecvClient)
        await ctx.send(f"Joined {channel}")
    else:
        await ctx.send("You are not in a voice channel!")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel!")
    else:
        await ctx.send("I am not in a voice channel!")

audio_packets = []

@bot.command(name='start_capture')
async def start_capture(ctx):
    global audio_packets
    if ctx.voice_client:
        audio_packets = []  # Reset the list
        def callback(user, data: VoiceData):
            if data.opus is not None:
                audio_packets.append(data.pcm)

        vc = ctx.voice_client
        vc.listen(BasicSink(callback))
        await ctx.send("Started capturing audio!")
    else:
        await ctx.send("I am not in a voice channel!")

@bot.command(name='stop_capture')
async def stop_capture(ctx):
    global audio_packets
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Stopped capturing audio!")
        if audio_packets:
                    with wave.open(f'recording_{ctx.guild.id}.wav', 'wb') as wf:
                        wf.setnchannels(2)
                        wf.setsampwidth(2)
                        wf.setframerate(48000)
                        for audio in audio_packets:
                            wf.writeframes(audioop.mul(audio, 2, 1))


@bot.command(name='die')
async def die(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
    await ctx.bot.close()

@bot.event
async def on_ready():
    if bot.user != None:
        print(f'Logged in as {bot.user.id}/{bot.user.name}')
        print('------')

if TOKEN != None:
    bot.run(TOKEN)
else:
    print("Token is None")
