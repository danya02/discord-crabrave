import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import ffmpeg

import os
import concurrent.futures
import sys
import io
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or None
ERROR_IMAGE = os.getenv('ERROR_IMAGE') or 'https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png'  # This URL is for the blurple-colored Discord mark from https://discord.com/branding.

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

executor = concurrent.futures.ProcessPoolExecutor()

def render_video(style, message):
    if style not in ['classic', 'garfield', 'megalovania', 'otamatone']:
        return None
    gif, err = ffmpeg\
            .input(f'/source/{style}.mp4')\
            .filter('fps', 10)\
            .filter('scale', '480', '-1')\
            .drawtext(message, fontfile='/NotoSans-Medium.ttf', x='(w-text_w)/2', y='(h-text_h)/2', borderw=1, fontsize=36, fontcolor='white')\
            .output('-', format='gif')\
            .run(capture_stdout=True)

    return gif, err


async def send_error(ctx, err_text):
    emb = discord.Embed()
    emb.title='Error'
    emb.description=err_text
    emb.set_image(url=ERROR_IMAGE)
    emb.color = discord.Color.red()
    await ctx.send(embed=emb)

@slash.slash(name="crabrave",
    description="Unleash a crab",
    options=[create_option(name='text', description='Text to overlay', option_type=3, required=False)],
    guild_ids=[775744109359923221],
)
async def crabrave(ctx: SlashContext, text=''):
    try:
        await ctx.defer()
        gif, err = await bot.loop.run_in_executor(None, render_video, 'classic', text)
        file = io.BytesIO(gif)
        file = discord.File(file, 'crab.gif')
        await ctx.send(file=file)
    except:
        traceback.print_exc()
        await send_error(ctx, traceback.format_exc())


bot.run(DISCORD_TOKEN)
