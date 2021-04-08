import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

import os
import concurrent.futures
import sys
import io

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or None
ERROR_IMAGE = os.getenv('ERROR_IMAGE') or 'https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png'  # This URL is for the blurple-colored Discord mark from https://discord.com/branding.

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot)

executor = concurrent.futures.ProcessPoolExecutor()

def render_video(style, message):
    if style not in ['classic', 'garfield', 'megalovania', 'otamatone']:
        return None
    gif, err = ffmpeg\
            .input(f'/source/{style}.mp4')\
            .filter('fps', 10)\
            .filter('scale', '480', '-1')\
            .drawtext(message, x='(w-text_w)/2', y='(h-text_h)/2', borderw=1, fontsize=36, fontcolor='white')\
            .output('-', format='gif')\
            .run(capture_stdout=True, capture_stderr=True)

    print(err, file=sys.stderr, flush=True)

    return gif, err


async def send_error(ctx, err_text):
    emb = discord.Embed()
    emb.title='Error'
    emb.description=err_text
    emb.set_image(url=ERROR_IMAGE)
    await ctx.send(embed=emb)

@slash.slash(name="crabrave",
    description="Unleash a crab",
    options=[create_option(name='text', description='Text to overlay', option_type=3, required=False)],
    guild_ids=[775744109359923221],
)
async def crabrave(ctx: SlashContext, text=''):
    await ctx.defer()
    gif, err = await bot.loop.run_in_executor(executor, render_video, 'classic', text)
    file = io.BytesIO(gif)
    file = discord.File(file, 'crab.gif')
    await ctx.send(file=file)



bot.run(DISCORD_TOKEN)
