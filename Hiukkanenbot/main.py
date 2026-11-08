"""
main.py — Hiukkanenbot, pääohjelma.
"""
import logging

from handlers.jyrkipasianssi import kaynnista_kysely
from handlers.jyrkipasianssi import kaynnista_kysely
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import sqlite3

import audio
import config
import calendar_handler
from handlers import hallitus, kahvi, kilta, ovi, jyrkipasianssi

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
# sammutetaan telegrambotin turha loggaus
logging.getLogger("httpx").setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# Komento-handlerit
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        update.effective_chat.id,
        "Tervetuloa käyttämään Hiukkasbottia! :3\n\n"
        "Tämä botti sisältää Hiukkasille hyödyllisiä ominanisuuksia." \
        " Botti toimii lähettämällä sille komennon. Listan komennoista saat" \
        " kun aloitat kirjoittamaan / -viivan jolloin botti ehdottaa käytössä oleavia komentoja. \n\n"
        "Botti toimii vain täällä yksityisviesteissä :)\n\n"
        "Jos huomaat ongelmia, ota yhteyttä Hiukkasen ATK-vastaavaan.\n\n"
        "Hallituslaisten omat komennot näkee /komennot."
    )

async def cmd_oviaukikiitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ovi.oven_avaus(context, update.effective_chat.id, update.message)

async def cmd_killanovi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ovi.killan_ovi(context, update.effective_chat.id)

async def cmd_sensori_auki(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ovi.sensori_auki(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_sensori_kiinni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ovi.sensori_kiinni(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_sensori_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ovi.sensori_reset(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_kahviakeittoonkiitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await kahvi.kaynnista(context, update.effective_chat.id)

async def cmd_kalenteri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await calendar_handler.kaynnista(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_jyrkipasianssi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await jyrkipasianssi.kaynnista_kysely(context, update.effective_user.username or "", update.effective_chat.id)

async def cmd_hallitushaku(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await hallitus.kaynnista_haku(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_wipehallitus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await hallitus.kaynnista_wipe(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_hallituslaiset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await hallitus.listaa_jasenet(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_uusihallitus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await hallitus.aseta_hallitus_chat(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_uusiadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await hallitus.lisaa_admin(
            context,
            update.effective_chat.id,
            update.message.text,
            update.effective_user.username or "",
        )

async def cmd_listaa_adminit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await hallitus.listaa_adminit(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_komennot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != "private":
        return
    user = update.effective_user.username or ""
    if user not in config.hallituksen_jasenet:
        await context.bot.send_message(update.effective_chat.id, "Sinulla ei ole oikeutta tähän komentoon")
        return
    await context.bot.send_message(
        update.effective_chat.id,
        "*Hallituksen komennot*\n"
        "/komennot — Listaa hallituslaisten komennot\n"
        "/hallitushaku — Liity hallituksen jäseneksi\n"
        "/hallituslaiset — Listaa hallituslaiset\n"
        "/kalenteri — Hallinnoi tapahtumakalenteria\n"
        "/pomppa — Pomppa-aika POJOING\\!\n"
        "/kahviakeittoonkiitos — Pyydä kahvinkeittoilmoitusta\n"
        "/killanovi — Tarkista killan oven tila\n"
        "/skilta — Soita skilta-ääni, se on harvinainen",
    )

async def cmd_adminkomennot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != "private":
        return
    user = update.effective_user.username or ""
    if user not in config.admins:
        await context.bot.send_message(update.effective_chat.id, "Sinulla ei ole oikeutta tähän komentoon")
        return
    await context.bot.send_message(
        update.effective_chat.id,
        "Admin-komennot\n"
        "/adminkomennot — Tämä lista\n"
        "/uusiadmin @username — Lisää admin\n"
        "/listaa_adminit — Listaa adminit\n"
        "/uusihallitus — Merkitse tämä chat hallituksen chatiksi\n"
        "/wipehallitus — Poista hallituksen jäseniä\n\n"
        "/logon — Käynnistä viestiloggauksen\n"
        "/logoff — Pysäytä viestiloggauksen\n"
        "Äänet\n"
        "/aanetpois — Poista äänet käytöstä\n"
        "/aanetpaalle — Ota äänet käyttöön\n"
        "/nytvittu — Pysäytä kaikki äänet\n\n"
        "Ovisensori\n"
        "/sensori_auki — Override: ovi auki (1h)\n"
        "/sensori_kiinni — Override: ovi kiinni (1h)\n"
        "/sensori_reset — Nollaa override\n\n"
        "Jyrkipasianssi\n"
        "/printdata — Tulosta jyrkipasianssi-data konsoliin\n"
        "Salaiset\n"
        "/salainekuusi — Soita kuusi\n"
        "/salaineseitseman — Soita seitsemän\n"
        "/pomppa — Pomppa-aika (kilta-koodi vaaditaan)",
    )

async def cmd_liuskaovi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.ilmoitus_kiltaan(context, update.effective_chat.id, "./audios/liuskaauki.mp3")

async def cmd_hissiovi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.ilmoitus_kiltaan(context, update.effective_chat.id, "./audios/hissiauki.mp3")

async def cmd_slaikkaaika(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.ilmoitus_kiltaan(context, update.effective_chat.id, "./audios/slaikka.mp3")

async def cmd_ninjaoviaukikiitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.ilmoitus_kiltaan(context, update.effective_chat.id, "./audios/ninjaauki.mp3")

async def cmd_skilta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.ilmoitus_kiltaan(context, update.effective_chat.id, "./audios/skilta.mp3")

async def cmd_nytvittu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.stop_all(context, update.effective_chat.id)

async def cmd_aanetpois(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.aanet_pois(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_aanetpaalle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await kilta.aanet_paalle(context, update.effective_chat.id, update.effective_user.username or "")

async def cmd_salainekuusi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        audio.queue("./audios/kuusi.mp3")

async def cmd_salaineseitseman(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        audio.queue("./audios/seitseman.mp3")

async def cmd_pomppa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != "private":
        return
    user = update.effective_user.username or ""
    if user not in config.hallituksen_jasenet:
        return
    chat_id = update.effective_chat.id
    if await kilta.tarkista_koodi(context, chat_id):
        audio.queue("./audios/pomppaaika.mp3")

async def cmd_testiviesti(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await context.bot.send_message(update.effective_chat.id, "Testiviesti onnistui! :3")

async def cmd_funtesti(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        chat_id = update.effective_chat.id
        if await kilta.tarkista_koodi(context, chat_id):
            await context.bot.send_message(chat_id, "Koodintarkistus onnistui!")

async def cmd_valot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == "private":
        await context.bot.send_message(
            update.effective_chat.id,
            "Valoanturi hävisi muutossa ja uusi komento tälle säädetään kesän aikana. "
            "Hiukkanen pahoittelee tästä aiheutuvaa haittaa.",
        )

# ---------------------------------------------------------------------------
# Tekstiviestien reititys (multi-step kyselyt)
# ---------------------------------------------------------------------------

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg or not msg.text or msg.edit_date:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user.username or ""
    viesti = msg.text.strip()

    if chat_id == config.hallitus_id:
        return

    if await kahvi.handle_viesti(context, chat_id, viesti):
        return
    if await hallitus.handle_haku_viesti(context, chat_id, user, viesti):
        return
    if await hallitus.handle_wipe_viesti(context, chat_id, user, viesti):
        return
    if await calendar_handler.handle_viesti(context, chat_id, user, viesti):
        return
    if await kilta.handle_koodi_viesti(context, chat_id, viesti):
        return
    if await jyrkipasianssi.handle_viesti(context, chat_id, user, viesti):
        return

    if update.effective_chat.type == "private":
        await context.bot.send_message(chat_id, "Virheellinen komento, kirjoita / nähdäksesi komennot :3")


# ---------------------------------------------------------------------------
# Inline-napin callback (ovenavaus)
# ---------------------------------------------------------------------------

async def on_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data == "oven_avaus":
        await ovi.callback_oven_avaus(update, context)
    else:
        await query.answer()


# ---------------------------------------------------------------------------
# Käynnistys
# ---------------------------------------------------------------------------

def main() -> None:
    if not audio.init():
        logging.error("Äänilaite ei käynnistynyt, jatketaan ilman ääniä...")

    if not config.load():
        logging.error("Konfiguraation lataus epäonnistui, lopetetaan.")
        return

    calendar_handler.get_service()

    app = Application.builder().token(config.bot_token).build()

    komennot = [
        ("start",               cmd_start),
        ("help",                cmd_start),
        ("h",                   cmd_start),
        ("oviaukikiitos",        cmd_oviaukikiitos),
        ("killanovi",            cmd_killanovi),
        ("sensori_auki",         cmd_sensori_auki),
        ("sensori_kiinni",       cmd_sensori_kiinni),
        ("sensori_reset",        cmd_sensori_reset),
        ("kahviakeittoonkiitos", cmd_kahviakeittoonkiitos),
        ("kalenteri",            cmd_kalenteri),
        ("hallitushaku",         cmd_hallitushaku),
        ("wipehallitus",         cmd_wipehallitus),
        ("hallituslaiset",       cmd_hallituslaiset),
        ("uusihallitus",         cmd_uusihallitus),
        ("uusiadmin",            cmd_uusiadmin),
        ("listaa_adminit",       cmd_listaa_adminit),
        ("komennot",             cmd_komennot),
        ("adminkomennot",        cmd_adminkomennot),
        ("liuskanoviaukikiitos", cmd_liuskaovi),
        ("hissinoviaukikiitos",  cmd_hissiovi),
        ("skilta",               cmd_skilta),
        ("nytvittu",             cmd_nytvittu),
        ("aanetpois",            cmd_aanetpois),
        ("aanetpaalle",          cmd_aanetpaalle),
        ("salainekuusi",         cmd_salainekuusi),
        ("salaineseitseman",     cmd_salaineseitseman),
        ("pomppa",               cmd_pomppa),
        ("testiviesti",          cmd_testiviesti),
        ("funtesti",             cmd_funtesti),
        ("valot",                cmd_valot),
        ("ninjaoviaukikiitos",   cmd_ninjaoviaukikiitos),
        ("jyrki",                cmd_jyrkipasianssi),
        ("slaikka",              cmd_slaikkaaika)
    ]

    for komento, funktio in komennot:
        app.add_handler(CommandHandler(komento, funktio))

    app.add_handler(MessageHandler(filters.TEXT, kirjaus_handler), group=-1)
    app.add_handler(MessageHandler(filters.TEXT, on_message))
    app.add_handler(CallbackQueryHandler(on_callback_query))

    logging.info("Botti käynnistyy... :3")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
