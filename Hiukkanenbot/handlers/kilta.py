"""
handlers/kilta.py — Killaan soitettavat äänet ja koodin tarkistus.
"""
import logging
import os
import random
import time

import audio
import config
from handlers.utils import tarkista_kellonaika, tarkista_slowdown

ROOM_CODE_PATH = os.environ.get(
    "HB_ROOM_CODE_PATH",
    "/home/pi/magicmirror/MagicMirror/modules/MMM-RoomCode/room_code.txt",
)

_kilta_oikeudet: dict[int, float] = {}
_OIKEUS_KESTO = 60 * 15  # 15 minuuttia
_pending_koodi: list[int] = []


async def tarkista_koodi(context, chat_id: int) -> bool:
    if chat_id in _kilta_oikeudet:
        if time.time() - _kilta_oikeudet[chat_id] < _OIKEUS_KESTO:
            return True
        del _kilta_oikeudet[chat_id]

    await context.bot.send_message(chat_id, "Anna killan infonäytöllä oleva koodi")
    _pending_koodi.append(chat_id)
    return False


async def handle_koodi_viesti(context, chat_id: int, viesti: str) -> bool:
    if chat_id not in _pending_koodi:
        return False

    if viesti == "/peru":
        _pending_koodi.remove(chat_id)
        await context.bot.send_message(chat_id, "Koodin tarkistus peruttu.")
        return True

    try:
        with open(ROOM_CODE_PATH) as f:
            koodi = f.read().strip()
    except Exception:
        logging.exception("kilta: kooditiedoston luku epäonnistui")
        await context.bot.send_message(chat_id, "Koodin tarkistus epäonnistui teknisen virheen takia.")
        _pending_koodi.remove(chat_id)
        return True

    if viesti == koodi:
        _pending_koodi.remove(chat_id)
        _kilta_oikeudet[chat_id] = time.time()
        await context.bot.send_message(
            chat_id, "Kilta oikeudet annettu 15 minuutiksi ^o^! Kutsu komentoa uudestaan niin se toimii :)"
        )
        return True

    await context.bot.send_message(chat_id, "Väärä koodi. Kirjoita /peru peruaksesi")
    return True


async def ilmoitus_kiltaan(context, chat_id: int, audio_polku: str) -> bool:
    if not audio.is_ready():
        logging.info("kilta: mixer ei ole aktiivinen")
        return False
    if not await tarkista_kellonaika(context, chat_id):
        return False
    if not await tarkista_slowdown(context, chat_id):
        return False

    if audio_polku == "./audios/skilta.mp3" and random.randint(1, 100) > 10:
        await context.bot.send_message(chat_id, "Skilta-ääni on harvinainen, eikä sitä soiteta joka kerta >:3")
        return False

    nimi = os.path.splitext(os.path.basename(audio_polku))[0]
    await context.bot.send_message(chat_id, f"Soitan kiltaan ilmoituksen: {nimi}")
    audio.play(audio_polku, loops=1)
    return True


async def stop_all(context, chat_id: int) -> None:
    audio.stop()
    await context.bot.send_message(chat_id, "Korvat pelastettu.")


async def aanet_pois(context, chat_id: int, user: str) -> None:
    if user not in config.admins:
        return
    if audio.disable():
        await context.bot.send_message(chat_id, "Äänet poistettu käytöstä.")
    else:
        await context.bot.send_message(chat_id, "Äänien poistaminen käytöstä epäonnistui.")


async def aanet_paalle(context, chat_id: int, user: str) -> None:
    if user not in config.admins:
        return
    if audio.enable():
        await context.bot.send_message(chat_id, "Äänet käytössä.")
    else:
        await context.bot.send_message(chat_id, "Äänien käyttöön ottaminen epäonnistui.")
