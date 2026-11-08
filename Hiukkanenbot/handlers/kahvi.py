"""
handlers/kahvi.py — Kahvinkeittopyyntö.
"""
import audio
from handlers.utils import tarkista_kellonaika, tarkista_slowdown

_pending: dict[int, float] = {}


async def kaynnista(context, chat_id: int) -> bool:
    if not await tarkista_slowdown(context, chat_id):
        return False
    if not await tarkista_kellonaika(context, chat_id):
        return False
    import time
    _pending[chat_id] = time.time()
    await context.bot.send_message(chat_id, "Monelleko hengelle kahvia keitetään? Voit perua pyynnön /peru")
    audio.play("./audios/kahvia.mp3")
    return True


async def handle_viesti(context, chat_id: int, viesti: str) -> bool:
    if chat_id not in _pending:
        return False

    if viesti == "/peru":
        _pending.pop(chat_id, None)
        await context.bot.send_message(chat_id, "Kahvinkeittopyyntö peruttu.")
        audio.queue("./audios/peruttu.mp3")
        return True

    try:
        maara = int(viesti)
        if maara <= 0:
            raise ValueError
    except (TypeError, ValueError):
        await context.bot.send_message(
            chat_id, "Henkilömäärä on positiivinen kokonaisluku -_- Voit lopettaa /peru"
        )
        return True

    _pending.pop(chat_id, None)
    await _soita_aani(context, chat_id, maara)
    return True


async def _soita_aani(context, chat_id: int, maara: int) -> None:
    #polku_map = {1: "yksi", 1.5: "puolitoista", 2: "kaksi", 3: "kolme", 4: "nelja"}
    #nimi = polku_map.get(maara, "taysi_pannu" if maara >= 5 else "voieinuo")


    if maara == 67:
        nimi = "puolitoista"
    elif maara >= 5:
        nimi = "taysi_pannu"
    elif maara == 1:
        nimi = "yksi"
    elif maara == 2:
        nimi = "kaksi"
    elif maara == 3:
        nimi = "kolme"
    elif maara == 4:
        nimi = "nelja"


    polku = f"./audios/{nimi}.mp3"

    if audio.queue(polku):
        if maara == 67:
            await context.bot.send_message(chat_id, "Aten henkilökohtainen kahvinkeittopyyntö välitetty kiltaan.")
        elif maara >= 5:
            await context.bot.send_message(chat_id, "Kahvinkeittopyyntö AINA MAKSIMIT hengelle välitetty kiltaan.")
        else:
            await context.bot.send_message(chat_id, f"Kahvinkeittopyyntö {maara} hengelle välitetty kiltaan.")
    else:
        await context.bot.send_message(chat_id, "Kahvinkeittopyynnön äänimerkki epäonnistui.")
