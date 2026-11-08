"""
handlers/ovi.py — Ovisensori ja ovenavaus.
"""
import logging
import os
import time
from datetime import datetime, time as dtime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import config
from http_utils import safe_get

OVI_URL = os.environ.get("HB_OVI_URL", "http://192.168.0.230/data")

_last_request: float = 0.0
_request_msg = None
_request_from: int = 0
_request_msg_id: int = 0

_sensori_auki: float = 0.0
_sensori_kiinni: float = 0.0
_OVERRIDE_KESTO = 60 * 60  # 1 tunti


async def sensori_auki(context, chat_id: int, user: str) -> bool:
    if user not in config.admins:
        return False
    global _sensori_auki
    _sensori_auki = time.time()
    await context.bot.send_message(chat_id, "Sensori-override: ovi auki (voimassa 1h)")
    return True


async def sensori_kiinni(context, chat_id: int, user: str) -> bool:
    if user not in config.admins:
        return False
    global _sensori_kiinni
    _sensori_kiinni = time.time()
    await context.bot.send_message(chat_id, "Sensori-override: ovi kiinni (voimassa 1h)")
    return True


async def sensori_reset(context, chat_id: int, user: str) -> bool:
    if user not in config.admins:
        return False
    global _sensori_auki, _sensori_kiinni
    _sensori_auki = 0.0
    _sensori_kiinni = 0.0
    await context.bot.send_message(chat_id, "Sensori-override nollattu.")
    return True


async def killan_ovi(context, chat_id: int) -> None:
    nyt = time.time()

    if nyt - _sensori_auki < _OVERRIDE_KESTO:
        await context.bot.send_message(chat_id, "Killan ovi on auki")
        return
    if nyt - _sensori_kiinni < _OVERRIDE_KESTO:
        await context.bot.send_message(chat_id, "Killan ovi on kiinni")
        return

    vastaus = safe_get(OVI_URL)
    if vastaus is None:
        await context.bot.send_message(chat_id, "Ovisensorin haku epäonnistui.")
        return

    try:
        arvo = float(vastaus.text.strip())
    except ValueError:
        await context.bot.send_message(chat_id, "Ovisensorin data ei kelpaa.")
        return

    if arvo < 0.5:
        await context.bot.send_message(chat_id, "Killan ovi on kiinni")
    else:
        await context.bot.send_message(chat_id, "Killan ovi on auki")


async def oven_avaus(context, chat_id: int, msg) -> None:
    global _last_request, _request_msg, _request_from, _request_msg_id

    if not config.hallitus_id:
        await context.bot.send_message(chat_id, "Hallitus-chatin ID puuttuu asetuksista.")
        return

    nyt = datetime.now()
    if not (dtime(8, 0) <= nyt.time() <= dtime(22, 0)):
        await context.bot.send_message(chat_id, "Ovipyyntöjä voi lähettää välillä 8–22")
        return

    kulunut = round(time.time() - _last_request) if _last_request else 7201
    if kulunut <= 7200:
        jaljella = 7200 - kulunut
        await context.bot.send_message(chat_id, f"Pyyntö on jo lähetetty. Koita {jaljella}s päästä uudestaan.")
        return

    etunimi = msg.from_user.first_name
    sukunimi = msg.from_user.last_name or ""
    _request_msg_id = msg.message_id
    _request_from = chat_id
    _last_request = time.time()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Mä hoidan!", callback_data="oven_avaus")]
    ])
    sent = await context.bot.send_message(
        config.hallitus_id,
        f"Voisitteko avata oven henkilölle: {etunimi} {sukunimi}",
        reply_markup=keyboard,
    )
    _request_msg = sent
    await context.bot.send_message(chat_id, "Ovenavauspyyntö lähetetty. Odotathan kuittausta :)")


async def callback_oven_avaus(update, context) -> None:
    query = update.callback_query
    await query.answer()

    if _request_msg is None:
        return

    etunimi = query.from_user.first_name
    await query.edit_message_text(f"Hyvää duunia {etunimi} <3")
    await context.bot.send_message(
        _request_from,
        f"{etunimi} tulee avaamaan piakkoin :)",
        reply_to_message_id=_request_msg_id,
    )
