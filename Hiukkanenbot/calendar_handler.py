"""
calendar_handler.py — Google Kalenterin hallinta.

Stepit tapahtuman lisäyksessä:
  0 = odotetaan /uusi tai /poista
  1-6 = tapahtuman tietojen keruu
  10 = odotetaan tapahtuman poistovalintaa
"""
import logging
import os
import re
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = os.environ.get(
    "HB_SERVICE_ACCOUNT",
    "/home/pi/hiukkanenbot/service_account.json",
)
CALENDAR_ID = os.environ.get(
    "HB_CALENDAR_ID",
    "c_02db97519df6747baaba282cdf0f78f83ac90cdd5f01a1b836b65230a8f060c9@group.calendar.google.com",
)

_service = None
_pending: dict[int, int] = {}
_data: dict[int, dict] = {}
_poisto_data: dict[int, list] = {}


def get_service():
    global _service
    if _service is not None:
        return _service
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        _service = build("calendar", "v3", credentials=creds)
        logging.info("calendar: palvelu alustettu")
    except FileNotFoundError:
        logging.error("calendar: service_account.json ei löydy")
    except Exception:
        logging.exception("calendar: palvelun alustus epäonnistui")
    return _service


async def kaynnista(context, chat_id: int, user: str) -> bool:
    if user not in config.hallituksen_jasenet:
        await context.bot.send_message(chat_id, "Sinulla ei ole oikeutta tähän komentoon.")
        return False
    _pending[chat_id] = 0
    _data[chat_id] = {}
    await context.bot.send_message(
        chat_id,
        "Tervetuloa hallinnoimaan tapahtumakalenteria!\n"
        "/uusi — Lisää uusi tapahtuma\n"
        "/poista — Poista tapahtuma\n"
        "/peru — Peruuta",
    )
    return True


async def handle_viesti(context, chat_id: int, user: str, viesti: str) -> bool:
    if chat_id not in _pending:
        return False

    step = _pending[chat_id]

    if step == 0:
        return await _handle_step0(context, chat_id, user, viesti)
    if step == 10:
        return await _handle_poisto(context, chat_id, user, viesti)
    if 1 <= step <= 6:
        return await _handle_lisays(context, chat_id, user, viesti, step)

    return False


async def _cancel(context, chat_id: int, viesti: str = "Peruttu.") -> bool:
    _pending.pop(chat_id, None)
    _data.pop(chat_id, None)
    _poisto_data.pop(chat_id, None)
    await context.bot.send_message(chat_id, viesti)
    return True


async def _handle_step0(context, chat_id: int, user: str, viesti: str) -> bool:
    if viesti == "/peru":
        return await _cancel(context, chat_id, "Kalenterin muokkaus peruttu.")
    elif viesti == "/uusi":
        _pending[chat_id] = 1
        _data[chat_id] = {}
        await context.bot.send_message(chat_id, "Anna tapahtuman nimi:")
        return True
    elif viesti == "/poista":
        _pending.pop(chat_id, None)
        await _kaynnista_poisto(context, chat_id, user)
        return True
    else:
        await context.bot.send_message(
            chat_id,
            "Virheellinen komento. Kirjoita /uusi lisätäksesi tai /peru peruuttaaksesi.",
        )
        return True


async def _handle_lisays(context, chat_id: int, user: str, viesti: str, step: int) -> bool:
    if user not in config.hallituksen_jasenet:
        await context.bot.send_message(chat_id, "Sinulla ei ole oikeutta tähän komentoon.")
        return False

    if viesti == "/peru":
        return await _cancel(context, chat_id, "Tapahtuman luonti peruttu.")

    if step == 1:
        _data[chat_id]["nimi"] = viesti
        _pending[chat_id] = 2
        await context.bot.send_message(chat_id, "Anna tapahtuman kuvaus (tai - jos ei kuvausta):")
        return True

    if step == 2:
        _data[chat_id]["kuvaus"] = "" if viesti == "-" else viesti
        _pending[chat_id] = 3
        await context.bot.send_message(chat_id, "Anna päivämäärä muodossa VVVV-KK-PP (esim. 2025-05-01):")
        return True

    if step == 3:
        try:
            datetime.strptime(viesti, "%Y-%m-%d")
            _data[chat_id]["pvm"] = viesti
            _pending[chat_id] = 4
            await context.bot.send_message(chat_id, "Anna alkamisaika muodossa TT:MM (esim. 14:00):")
        except ValueError:
            await context.bot.send_message(chat_id, "Virheellinen päivämäärä. Käytä muotoa VVVV-KK-PP:")
        return True

    if step == 4:
        if re.match(r"^\d{2}:\d{2}$", viesti):
            _data[chat_id]["alkaa"] = viesti
            _pending[chat_id] = 5
            await context.bot.send_message(chat_id, "Anna loppumisaika muodossa TT:MM (esim. 16:00):")
        else:
            await context.bot.send_message(chat_id, "Virheellinen aika. Käytä muotoa TT:MM:")
        return True

    if step == 5:
        if re.match(r"^\d{2}:\d{2}$", viesti):
            alkaa = datetime.strptime(_data[chat_id]["alkaa"], "%H:%M")
            loppuu = datetime.strptime(viesti, "%H:%M")
            if loppuu <= alkaa:
                await context.bot.send_message(
                    chat_id,
                    f"Loppumisaika ei voi olla ennen alkamisaikaa (alkaa {_data[chat_id]['alkaa']}). Anna uudelleen:",
                )
                return True
            _data[chat_id]["loppuu"] = viesti
            _pending[chat_id] = 6
            await context.bot.send_message(chat_id, "Anna paikka (tai - jos ei paikkaa):")
        else:
            await context.bot.send_message(chat_id, "Virheellinen aika. Käytä muotoa TT:MM:")
        return True

    if step == 6:
        _data[chat_id]["paikka"] = "" if viesti == "-" else viesti
        await _tallenna_tapahtuma(context, chat_id)
        return True

    return False


async def _tallenna_tapahtuma(context, chat_id: int) -> None:
    palvelu = get_service()
    if palvelu is None:
        await context.bot.send_message(chat_id, "Kalenteriin ei saada yhteyttä. Yritä myöhemmin.")
        _pending.pop(chat_id, None)
        _data.pop(chat_id, None)
        return

    d = _data[chat_id]
    kuvaus = d.get("kuvaus", "")
    if d.get("paikka"):
        kuvaus += f"\nPaikka: {d['paikka']}"

    event = {
        "summary": d["nimi"],
        "description": kuvaus,
        "location": d.get("paikka", ""),
        "start": {"dateTime": f"{d['pvm']}T{d['alkaa']}:00", "timeZone": "Europe/Helsinki"},
        "end": {"dateTime": f"{d['pvm']}T{d['loppuu']}:00", "timeZone": "Europe/Helsinki"},
    }

    try:
        palvelu.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        await context.bot.send_message(
            chat_id,
            f"✅ Tapahtuma lisätty!\n\n"
            f"📌 {d['nimi']}\n"
            f"📅 {d['pvm']} {d['alkaa']}–{d['loppuu']}\n"
            f"📍 {d.get('paikka') or 'Ei paikkaa'}\n"
            f"📝 {d.get('kuvaus') or 'Ei kuvausta'}",
        )
    except HttpError as e:
        logging.error("calendar: API virhe: %s", e)
        await context.bot.send_message(chat_id, f"❌ Kalenterivirhe: {e}")
    except Exception:
        logging.exception("calendar: tapahtuman tallennus epäonnistui")
        await context.bot.send_message(chat_id, "❌ Tapahtuman lisääminen epäonnistui.")
    finally:
        _pending.pop(chat_id, None)
        _data.pop(chat_id, None)


async def _kaynnista_poisto(context, chat_id: int, user: str) -> bool:
    if user not in config.hallituksen_jasenet:
        await context.bot.send_message(chat_id, "Sinulla ei ole oikeutta tähän komentoon.")
        return False

    palvelu = get_service()
    if palvelu is None:
        await context.bot.send_message(chat_id, "Kalenteriin ei saada yhteyttä.")
        return False

    try:
        nyt = datetime.utcnow().isoformat() + "Z"
        tulos = palvelu.events().list(
            calendarId=CALENDAR_ID,
            timeMin=nyt,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        tapahtumat = tulos.get("items", [])
        if not tapahtumat:
            await context.bot.send_message(chat_id, "Ei tulevia tapahtumia kalenterissa.")
            return True

        _poisto_data[chat_id] = tapahtumat
        _pending[chat_id] = 10

        viesti = "Tulevat tapahtumat — kirjoita numero poistaaksesi:\n\n"
        for i, t in enumerate(tapahtumat, 1):
            nimi = t.get("summary", "Nimetön tapahtuma")
            alku = t["start"].get("dateTime", t["start"].get("date", ""))
            try:
                alku_str = datetime.fromisoformat(alku).strftime("%d.%m.%Y %H:%M")
            except ValueError:
                alku_str = alku
            viesti += f"{i}. {nimi} — {alku_str}\n"
        viesti += "\n/peru — peruuta"

        await context.bot.send_message(chat_id, viesti)
        return True

    except HttpError as e:
        logging.error("calendar: API virhe: %s", e)
        await context.bot.send_message(chat_id, f"❌ Kalenterivirhe: {e}")
    except Exception:
        logging.exception("calendar: tapahtumien haku epäonnistui")
        await context.bot.send_message(chat_id, "❌ Tapahtumien haku epäonnistui.")
    return True


async def _handle_poisto(context, chat_id: int, user: str, viesti: str) -> bool:
    if viesti == "/peru":
        return await _cancel(context, chat_id, "Poisto peruttu.")

    tapahtumat = _poisto_data.get(chat_id, [])
    try:
        valinta = int(viesti)
        if not 1 <= valinta <= len(tapahtumat):
            raise ValueError
    except ValueError:
        await context.bot.send_message(
            chat_id, f"Kirjoita numero väliltä 1–{len(tapahtumat)} tai /peru peruuttaaksesi."
        )
        return True

    tapahtuma = tapahtumat[valinta - 1]
    nimi = tapahtuma.get("summary", "Nimetön tapahtuma")

    palvelu = get_service()
    try:
        palvelu.events().delete(calendarId=CALENDAR_ID, eventId=tapahtuma["id"]).execute()
        await context.bot.send_message(chat_id, f"🗑️ Tapahtuma poistettu:\n📌 {nimi}")
    except HttpError as e:
        logging.error("calendar: poisto API virhe: %s", e)
        await context.bot.send_message(chat_id, f"❌ Kalenterivirhe: {e}")
    except Exception:
        logging.exception("calendar: poisto epäonnistui")
        await context.bot.send_message(chat_id, "❌ Tapahtuman poistaminen epäonnistui.")

    _pending.pop(chat_id, None)
    _poisto_data.pop(chat_id, None)
    return True
