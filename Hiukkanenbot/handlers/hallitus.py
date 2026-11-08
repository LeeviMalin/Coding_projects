"""
handlers/hallitus.py — Hallituksen jäsenyyden hallinta.
"""
import logging
import config

_pending_jasen: list[int] = []
_pending_wipe: list[int] = []


async def kaynnista_haku(context, chat_id: int, username: str) -> bool:
    if username in config.hallituksen_jasenet:
        await context.bot.send_message(chat_id, "Olet jo hallituksen jäsen :3")
        return False
    _pending_jasen.append(chat_id)
    await context.bot.send_message(chat_id, "Anna salasana")
    return True


async def handle_haku_viesti(context, chat_id: int, username: str, viesti: str) -> bool:
    if chat_id not in _pending_jasen:
        return False

    if viesti == "/peru":
        _pending_jasen.remove(chat_id)
        await context.bot.send_message(chat_id, "Hallitukseen pääsy peruttu. >:3")
        return True

    if viesti == config.hallituksen_salasana:
        _pending_jasen.remove(chat_id)
        config.hallituksen_jasenet.append(username)
        config.save()
        await context.bot.send_message(chat_id, "Olet nyt hallituksen jäsen :3")
        return True

    await context.bot.send_message(chat_id, "Väärä salasana. Yritä uudelleen tai kirjoita /peru peruuttaaksesi.")
    return True


async def kaynnista_wipe(context, chat_id: int, user: str) -> bool:
    if user not in config.admins:
        return False
    _pending_wipe.append(chat_id)
    await context.bot.send_message(
        chat_id, "kaikki = wipe kaikki, peru = peruuta, jäsenen_nikki = poista tietty jäsen."
    )
    return True


async def handle_wipe_viesti(context, chat_id: int, user: str, viesti: str) -> bool:
    if chat_id not in _pending_wipe:
        return False
    if user not in config.admins:
        return False

    if viesti == "kaikki":
        config.hallituksen_jasenet.clear()
        config.save()
        await context.bot.send_message(chat_id, "Hallituksen jäsenet on pyyhitty >:3")
        _pending_wipe.remove(chat_id)
    elif viesti == "peru":
        await context.bot.send_message(chat_id, "Hallituksen wipe peruttu.")
        _pending_wipe.remove(chat_id)
    elif viesti in config.hallituksen_jasenet:
        config.hallituksen_jasenet.remove(viesti)
        config.save()
        await context.bot.send_message(chat_id, f"Jäsen {viesti} on potkittu hallituksesta.")
        _pending_wipe.remove(chat_id)
    else:
        await context.bot.send_message(chat_id, "Virheellinen vastaus.")

    return True


async def listaa_jasenet(context, chat_id: int, user: str) -> None:
    if user not in config.hallituksen_jasenet:
        await context.bot.send_message(chat_id, "Sinulla ei ole oikeutta tähän komentoon")
        return
    if not config.hallituksen_jasenet:
        await context.bot.send_message(chat_id, "Hallituksessa ei ole jäseniä 3:")
    else:
        await context.bot.send_message(chat_id, f"Hallituksen jäsenet: {', '.join(config.hallituksen_jasenet)}")


async def listaa_adminit(context, chat_id: int, user: str) -> None:
    if user not in config.admins:
        await context.bot.send_message(chat_id, "Sinulla ei ole oikeutta tähän komentoon")
        return
    await context.bot.send_message(chat_id, ', '.join(config.admins))


async def lisaa_admin(context, chat_id: int, msg_text: str, user: str) -> None:
    if user not in config.admins:
        return
    osat = msg_text.split()
    if len(osat) < 2:
        await context.bot.send_message(chat_id, "Käyttö: /uusiadmin @username")
        return
    new_admin = osat[1]
    config.admins.append(new_admin)
    config.save()
    await context.bot.send_message(chat_id, f"Käyttäjä {new_admin} on nyt admin")


async def aseta_hallitus_chat(context, chat_id: int, user: str) -> None:
    if user not in config.admins:
        return
    config.hallitus_id = chat_id
    config.save()
    await context.bot.send_message(chat_id, "Tämä on merkattu hallituksen piilopaikaksi :3")
