import aiofiles
import ffmpeg
import asyncio
import os
import shutil
import psutil
import subprocess
import requests
import aiohttp
import yt_dlp

from os import path
from typing import Union
from asyncio import QueueEmpty
from PIL import Image, ImageFont, ImageDraw
from typing import Callable

from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputAudioStream
from oda.utils.decorators import authorized_users_only
from youtube_search import YoutubeSearch

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    Voice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant

from oda.tgcalls import calls, queues
from oda.tgcalls.calls import client as ASS_ACC
from oda.database.queue import (
    get_active_chats,
    is_active_chat,
    add_active_chat,
    remove_active_chat,
    music_on,
    is_music_playing,
    music_off,
)
from oda import app
import oda.tgcalls
from oda.tgcalls import youtube
from oda.config import (
    DURATION_LIMIT,
    que,
    SUDO_USERS,
    BOT_ID,
    ASSNAME,
    ASSUSERNAME,
    ASSID,
    SUPPORT,
    UPDATE,
    BOT_USERNAME,
)
from oda.utils.filters import command
from oda.utils.decorators import errors, sudo_users_only
from oda.utils.administrator import adminsOnly
from oda.utils.errors import DurationLimitError
from oda.utils.gets import get_url, get_file_name
from oda.modules.admins import member_permissions


chat_id = None
DISABLED_GROUPS = []
useer = "NaN"


def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes:
            return await func(client, cb)
        await cb.answer("You ain't allowed!", show_alert=True)
        return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/igrisxmusic.jpg")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/fontx.otf", 32)
    draw.text((190, 550), f"Title: {title}", (255, 255, 255), font=font)
    draw.text((190, 590), f"Duration: {duration}", (255, 255, 255), font=font)
    draw.text((190, 630), f"Views: {views}", (255, 255, 255), font=font)
    draw.text(
        (190, 670),
        f"Added By: {requested_by}",
        (190, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(
    filters.command("igrisxmusic") & ~filters.edited & ~filters.bot & ~filters.private
)
@authorized_users_only
async def hfmm(_, message):
    global DISABLED_GROUPS
    try:
        user_id = message.from_user.id
    except:
        return
    if len(message.command) != 2:
        await message.reply_text(
            "I only recognize `/igrisxmusic on` and /igrisxmusic `off only`"
        )
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status == "ON" or status == "on" or status == "On":
        lel = await message.reply("`Processing...`")
        if not message.chat.id in DISABLED_GROUPS:
            await lel.edit("IGRISX Music Already Activated In This Chat")
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"IGRISX Music Successfully Enabled For Users"
        )

    elif status == "OFF" or status == "off" or status == "Off":
        lel = await message.reply("`Processing...`")
        
        if message.chat.id in DISABLED_GROUPS:
            await lel.edit("IGRISX Music Already turned off In This Chat")
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"IGRISX Music Successfully Deactivated For Users"
        )
    else:
        await message.reply_text(
            "I only recognize `/igrisxmusic on` and /igrisxmusic `off only`"
        )           

@Client.on_callback_query(filters.regex(pattern=r"^(cls)$"))
@cb_admin_check
async def m_cb(b, cb):
    global que
    qeue = que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    chat_id = cb.message.chat.id
    m_chat = cb.message.chat

    if type_ == "cls":
        await cb.answer("Closed Menu")
        await cb.message.delete()

@Client.on_callback_query(filters.regex(pattern=r'^(playlist)$'))
async def p_cb(b, cb):
    global que       
    qeue = que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    chat_id = cb.message.chat.id
    m_chat = cb.message.chat
    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == 'playlist':           
        queue = que.get(cb.message.chat.id)
        if not queue:   
            await cb.message.edit('Player is idle')
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style='md')
        msg = "**Now Playing** in {}".format(cb.message.chat.title)
        msg += "\n- "+ now_playing
        msg += "\n- Req by "+by
        temp.pop(0)
        if temp:
             msg += '\n\n'
             msg += '**Queue**'
             for song in temp:
                 name = song[0]
                 usr = song[1].mention(style='md')
                 msg += f'\n- {name}'
                 msg += f'\n- Req by {usr}\n'
        await cb.message.edit(msg)      

# play
@Client.on_message(
    command("playx")
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    global que
    global useer
    if message.chat.id in DISABLED_GROUPS:
        return
    lel = await message.reply("**__Processing__**")

    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "@IGRISXMUSIC"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                await lel.edit(
                    "<b>Add me to your channel to play in channels</b>",
                )
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Add me as admin of yor group first</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id,
                        "<b>IGRISXMUSIC</b> joined this group as you commanded",
                    )
                    await lel.edit(
                        "<b>IGRISXMUSIC joined this chat as you commanded</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"<b>🛑 Flood Wait Error 🛑</b> \nHey {user.first_name}, assistant userbot couldn't join your group due to heavy join requests. Make sure userbot is not banned in group and try again later!"
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>Hey {user.first_name}, assistant userbot is not in this chat, ask admin to send `/playx` command for first time to add it.</i>"
        )
        return

    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ Videos longer than {DURATION_LIMIT} minutes aren't allowed to play!"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/04e57b49a3fece158eba7.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [   
                [
                               
                    InlineKeyboardButton('📖 Playlist', callback_data='playlist'),
                
                ],                     
                [
                    InlineKeyboardButton('Updates⚜️', url=f"t.me/IGRISXUPDATES"),
                    InlineKeyboardButton('Support❗', url=f"t.me/IGRISROBOTSUPPORT"),
                
                ],
                [
                    InlineKeyboardButton('Close 🗑', callback_data='cls') 
                ]                            
            ]
        )

        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            keyboard = InlineKeyboardMarkup(
            [   
                [
                               
                    InlineKeyboardButton('📖 Playlist', callback_data='playlist'),
                
                ],                     
                [
                    InlineKeyboardButton('Updates⚜️', url=f"t.me/IGRISXUPDATES"),
                    InlineKeyboardButton('Support❗', url=f"t.me/IGRISROBOTSUPPORT"),
                
                ],
                [
                    InlineKeyboardButton('Close 🗑', callback_data='cls') 
                ]                            
            ]
        )


        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/04e57b49a3fece158eba7.jpg"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="YouTube 🎬", url="https://youtube.com")]]
            )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ Videos longer than {DURATION_LIMIT} minutes aren't allowed to play!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit("**Give me song name!!!**")
        await lel.edit("🔎 **Finding the song...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        await lel.edit("🎵 **Processing sounds...**")
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            await lel.edit(
                "❌ Song not found.\n\nTry another song or maybe spell it properly."
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
            [   
                [
                               
                    InlineKeyboardButton('📖 Playlist', callback_data='playlist'),
                
                ],                     
                [
                    InlineKeyboardButton('Updates⚜️', url=f"t.me/IGRISXUPDATES"),
                    InlineKeyboardButton('Support❗', url=f"t.me/IGRISROBOTSUPPORT"),
                
                ],
                [
                    InlineKeyboardButton('Close 🗑', callback_data='cls') 
                ]                            
            ]
        )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ Video longer than {DURATION_LIMIT} minutes aren't allowed to play!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))

    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        x = await message.reply_photo(
            photo="final.png",
            caption="**🎵 Song:** {}\n**🕒 Duration:** {} min\n**👤 Added By:** {}\n\n**#⃣ Queued Position:** {}".format(
                title,
                duration,
                message.from_user.mention(),
                position,
            ),
            reply_markup=keyboard,
        )
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        x = await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**🎵 Song:** {}\n**🕒 Duration:** {} min\n**👤 Added By:** {}\n\n**".format(
                title, duration, message.from_user.mention(), message.chat.title
            ),
        )

    os.remove("final.png")
    x.delete
    return await lel.delete()
