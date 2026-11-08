"""
handlers/utils.py — Jaetut apufunktiot handlereille.
"""
import time as time_mod
from datetime import datetime, time

_announcement_last: float = 0.0


async def tarkista_slowdown(context, chat_id: int, sallittu_s: float = 10.0) -> bool:
    global _announcement_last
    nyt = time_mod.time()
    kulunut_aika = nyt - _announcement_last
    if kulunut_aika >= sallittu_s:
        _announcement_last = nyt
        return True
    jaljella = sallittu_s - kulunut_aika
    await context.bot.send_message(
        chat_id,
        f"Et voi käyttää tätä komentoa juuri nyt, kokeile {jaljella:.1f}s päästä uudestaan.",
    )
    return False


def paivita_announcement_last() -> None:
    global _announcement_last
    _announcement_last = time_mod.time()


async def tarkista_kellonaika(context, chat_id: int, alkuaika: int = 6, loppuaika: int = 22) -> bool:
    if time(alkuaika, 0) <= datetime.now().time() <= time(loppuaika, 0):
        return True
    await context.bot.send_message(
        chat_id, f"Tätä ääntä voi soittaa killassa välillä {alkuaika}–{loppuaika}"
    )
    return False
