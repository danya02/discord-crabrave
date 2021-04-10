import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import ffmpeg
import aioredis

import os
import concurrent.futures
import sys
import io
import logging
import traceback
import hashlib
import uuid
import asyncio

logging.basicConfig(level=logging.DEBUG)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or None
ERROR_IMAGE = os.getenv('ERROR_IMAGE') or 'https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png'  # This URL is for the blurple-colored Discord mark from https://discord.com/branding.
URL_PREFIX = os.getenv('URL_PREFIX')
if not URL_PREFIX:
    logging.error('URL_PREFIX unset, but it is necessary for bot to function. Exiting.')
    raise SystemExit(1)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
slash = SlashCommand(bot, sync_commands=True)

executor = concurrent.futures.ProcessPoolExecutor()

def render_video(style, message):
    if style not in ['classic', 'garfield', 'sans', 'otamatone']:
        return None
    fname = str(uuid.uuid4())
    _, err = ffmpeg\
            .input(f'/source/{style}.mp4')\
            .filter('fps', 10)\
            .filter('scale', '360', '-1')\
            .drawtext(message, fontfile='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', x='(w-text_w)/2', y='(h-text_h)/2', borderw=1, fontsize=36, fontcolor='white')\
            .output('/tmp/'+fname, format='gif')\
            .run(capture_stdout=True)
            # RE: output command: not writing to stdout because some containers do not support non-seekable outputs

    with open('/tmp/'+fname, 'rb') as file:
        data = file.read()
    os.unlink('/tmp/'+fname)

    return data, err


async def send_error(ctx, err_text):
    emb = discord.Embed()
    emb.title='Error'
    emb.description=err_text
    emb.set_image(url=ERROR_IMAGE)
    emb.color = discord.Color.red()
    await ctx.send(embed=emb)

def file_hash(data):
    return hashlib.sha256(data).hexdigest()

async def wait_for_playback_end_then_disconnect(client):
    while not client.is_playing():
        await asyncio.sleep(0.5)
    await client.disconnect()

@slash.slash(name="crabsong",
    description="Play the crab song",
    options=[create_option(name='style', description='Which style of crab to use?', option_type=3, required=False,
        choices=[
            create_choice(name='Classic', value='classic'),
            create_choice(name='Garfield', value='garfield'),
            create_choice(name='Otamatone', value='otamatone'),
            create_choice(name='Sans', value='sans'),
        ])],
    guild_ids=[775744109359923221],
)
async def crabrave_audio(ctx, style='classic', ignore_user_errors=False):
    try:
        if style not in ['classic', 'garfield', 'otamatone', 'sans']: return
        source = discord.FFmpegOpusAudio(f'/source-audio/{style}.opus')
        channel = None
        if ctx.author.voice is not None:
            channel = ctx.author.voice.channel
        if channel is None:
            if not ignore_user_errors:
                await ctx.send(ctx.author.mention+', you are not in a voice channel!', allowed_mentions=discord.AllowedMentions.none())
            return
        try:
            client = await channel.connect(timeout=5)
        except discord.Forbidden:
            if not ignore_user_errors:
                await ctx.send(ctx.author.mention+', you are in a voice channel that I cannot join!', allowed_mentions=discord.AllowedMentions.none())
            return


        def after_playback(error=None):
            if error:
                traceback.print_exception(type(error), error, error.__traceback__)

        client.play(source, after=after_playback)

        await wait_for_playback_end_then_disconnect(client)

    except:
        traceback.print_exc()
        await send_error(ctx, traceback.format_exc())


@slash.slash(name="crabrave",
    description="Unleash a crab",
    options=[create_option(name='text', description='Text to overlay', option_type=3, required=False)],
    guild_ids=[775744109359923221, 733301157992333373],
)
async def crabrave(ctx: SlashContext, text=''):
    try:
        await ctx.defer()
        audio_awaitable = crabrave_audio(ctx)
        video, err = await bot.loop.run_in_executor(None, render_video, 'classic', text)
        redis = await aioredis.create_redis('redis://redisserver')
        h = file_hash(video)
        #url = URL_PREFIX + h + '.mp4'
        await redis.set(h, video)
        msg = await ctx.send(content='Uploading content...')
        await ctx.channel.send(content=ctx.author.mention, file=discord.File(io.BytesIO(video), 'crab.gif'), allowed_mentions=discord.AllowedMentions.none())
        await msg.delete()
        #await audio_awaitable
    except:
        traceback.print_exc()
        await send_error(ctx, traceback.format_exc())

@slash.slash(name="garfield",
    description="Unleash a Garfield",
    options=[create_option(name='text', description='Text to overlay', option_type=3, required=False)],
    guild_ids=[775744109359923221, 733301157992333373],
)
async def crabrave(ctx: SlashContext, text=''):
    try:
        await ctx.defer()
        audio_awaitable = crabrave_audio(ctx)
        video, err = await bot.loop.run_in_executor(None, render_video, 'garfield', text)
        redis = await aioredis.create_redis('redis://redisserver')
        h = file_hash(video)
        #url = URL_PREFIX + h + '.mp4'
        await redis.set(h, video)
        msg = await ctx.send(content='Uploading content...')
        await ctx.channel.send(content=ctx.author.mention, file=discord.File(io.BytesIO(video), 'crab.gif'), allowed_mentions=discord.AllowedMentions.none())
        await msg.delete()
        #await audio_awaitable
    except:
        traceback.print_exc()
        await send_error(ctx, traceback.format_exc())

@slash.slash(name="sansrave",
    description="Unleash a Sans",
    options=[create_option(name='text', description='Text to overlay', option_type=3, required=False)],
    guild_ids=[775744109359923221, 733301157992333373],
)
async def crabrave(ctx: SlashContext, text=''):
    try:
        await ctx.defer()
        audio_awaitable = crabrave_audio(ctx)
        video, err = await bot.loop.run_in_executor(None, render_video, 'sans', text)
        redis = await aioredis.create_redis('redis://redisserver')
        h = file_hash(video)
        #url = URL_PREFIX + h + '.mp4'
        await redis.set(h, video)
        msg = await ctx.send(content='Uploading content...')
        await ctx.channel.send(content=ctx.author.mention, file=discord.File(io.BytesIO(video), 'crab.gif'), allowed_mentions=discord.AllowedMentions.none())
        await msg.delete()
        #await audio_awaitable
    except:
        traceback.print_exc()
        await send_error(ctx, traceback.format_exc())

@slash.slash(name="otamatone",
    description="Unleash an Otamatone",
    options=[create_option(name='text', description='Text to overlay', option_type=3, required=False)],
    guild_ids=[775744109359923221, 733301157992333373],
)
async def otamatone(ctx: SlashContext, text=''):
    try:
        await ctx.defer()
        audio_awaitable = crabrave_audio(ctx)
        video, err = await bot.loop.run_in_executor(None, render_video, 'otamatone', text)
        redis = await aioredis.create_redis('redis://redisserver')
        h = file_hash(video)
        #url = URL_PREFIX + h + '.mp4'
        await redis.set(h, video)
        msg = await ctx.send(content='Uploading content...')
        await ctx.channel.send(content=ctx.author.mention, file=discord.File(io.BytesIO(video), 'crab.gif'), allowed_mentions=discord.AllowedMentions.none())
        await msg.delete()
        #await audio_awaitable
    except:
        traceback.print_exc()
        await send_error(ctx, traceback.format_exc())
bot.run(DISCORD_TOKEN)
