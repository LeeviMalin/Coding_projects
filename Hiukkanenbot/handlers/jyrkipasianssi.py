"""
Botin /jyrki komennolla saa syötettyä ja kysyttä tietoa jyrkipasianssi pelin tilastoista

Data struct: dict[chat_id, (int, int)]

Stepit
1 = kysely käynnistetty

"""

import logging

from handlers.utils import tarkista_slowdown
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import os
import logging 
import config

logging.basicConfig(level=logging.INFO)
_pending: dict[int, int] = {}

COLUMNS = list(range(1, 53))

filu= "jyrkipasianssi_data.json"
try:
    _jyrki_df = pd.read_json(filu, orient="index")
    #logging.info(f"Jyrkipasianssi datat haettu onnistuneesti :P")
except (FileNotFoundError, ValueError):
    logging.error(f"Jyrkipasianssi data file {filu} not found or invalid. Initializing empty DataFrame.")

async def kaynnista_kysely(context, user, chat_id: int) -> bool:
    if not await tarkista_slowdown(context, chat_id):
        return False
    # Alussa tarkistetaan onko df latautunut ja jos ei ole niin ei anneta komentojen mennä läpi
    if _jyrki_df.empty:
        await context.bot.send_message(chat_id, "Jyrkipasianssi data ei saatavilla. Ole yhteydessä ATK toimariin")
        return True
    # Varmistetaan että käyttäjällä on rivi df:ssä, jotta voidaan lisätä dataa myöhemmin. 
    # Jos ei ole, lisätään uusi rivi käyttäjälle. Näin tarkistuksia ei tarvitse tehdä myöhemmin
    if user not in _jyrki_df.index:
            _jyrki_df.loc[user] = [0] * len(COLUMNS)
    await context.bot.send_message(chat_id, "Tervetuloa Jyrkimodeen!\n"
    "\n"
    "Voit muokata pelitietojasi tai tarkastella tilastoja.\n"
    "Komennot: /uusipeli, /poistapeli, /omatstatsit, /killanstatsit, /omakuvaaja, /killankuvaaja.\n"
    "\n"
    "Jos et tiedä mitä on jyrkipasianssi niin ethän syötä virheellistä dataa :)\n"
    "Voit poistua Jyrkimodesta /poistu")
    _pending[chat_id] = 1
    return True

async def send_mid_info(context, chat_id: int) -> bool:
    await context.bot.send_message(chat_id, "Komennot: /uusipeli, /poistapeli, /omatstatsit, /killanstatsit, /omakuvaaja, /killankuvaaja.\n"
        "Voit poistua Jyrkimodesta /poistu")

async def handle_viesti(context, chat_id: int, user: str, viesti: str) -> bool:
    if chat_id not in _pending:
        return False
    if viesti == "/poistu":
        _pending.pop(chat_id, None)
        await context.bot.send_message(chat_id, "Poistuit Jyrkimodesta")
        return True

    elif _pending[chat_id] == 1:

        if viesti == "/uusipeli":
            await context.bot.send_message(chat_id, "Syötä jäljelle jäävien pakkojen määrä. Voit perua pyynnön /peru")
            _pending[chat_id] = 2
            return True
        elif viesti == "/poistapeli":
            await context.bot.send_message(chat_id, "Syötä poistettavan pelin pakkojen määrä. Voit perua pyynnön /peru")
            _pending[chat_id] = 3
            return True
        elif viesti == "/omatstatsit":
            if _jyrki_df.loc[user].sum() == 0:
                await context.bot.send_message(chat_id, "Sinulla ei ole pelattuja pelejä.")
                return True
            pelienLukumaara = _jyrki_df.loc[user].sum()
            suurinPeli = _jyrki_df.loc[user].ne(0)[::-1].idxmax()
            pieninPeli = _jyrki_df.loc[user].ne(0).idxmax()
            keskimaarainenPeli = _jyrki_df.loc[user].mul(_jyrki_df.columns).sum()/_jyrki_df.loc[user].sum()
            moodiPeli = _jyrki_df.loc[user].idxmax()
            await context.bot.send_message(chat_id,
                f"Käyttäjän {user} tilastoja:\n"
                f"Pelejä pelattu yhteensä: {pelienLukumaara}\n"
                f"Suurin peli: {suurinPeli} pakkaa\n"
                f"Pienin peli: {pieninPeli} pakkaa\n"
                f"Keskimääräinen peli: {keskimaarainenPeli:.2f} pakkaa\n"
                f"Yleisin lopputulos: {moodiPeli} pakkaa")
            await send_mid_info(context, chat_id)
            return True
        elif viesti == "/killanstatsit":
            kiltadf = _jyrki_df.sum(axis=0)
            pelienLukumaara = kiltadf.sum()
            suurinPeli = kiltadf.ne(0)[::-1].idxmax()
            yhdenPakanPelit = kiltadf.loc[1]
            keskimaarainenPeli = kiltadf.mul(kiltadf.index).sum()/kiltadf.sum()
            moodiPeli = kiltadf.idxmax()

            await context.bot.send_message(chat_id,
                f"Killan yhteisiä tilastoja:\n"
                f"Pelejä pelattu yhteensä: {pelienLukumaara}\n"
                f"Voittoja: {yhdenPakanPelit}\n"
                f"Suurin peli: {suurinPeli} pakkaa\n"
                f"Keskimääräinen peli: {keskimaarainenPeli:.2f} pakkaa\n"
                f"Yleisin lopputulos: {moodiPeli} pakkaa")
            await send_mid_info(context, chat_id)
            return True
        elif viesti == "/omakuvaaja":
            omadf = _jyrki_df.loc[user]
            plt.bar(omadf.index, omadf.values)
            plt.xlabel("Pakkaa jäljellä")
            plt.ylabel("Pelejä pelattu")
            plt.title(f"Käyttäjän {user} Jyrkipasianssi tilastot")
            plt.xlim(left=0.5)
            plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(1))
            filunimi = "Jyrkipasianssitilastot" + user + ".png"
            plt.savefig(filunimi)
            await context.bot.send_photo(chat_id, photo=open(filunimi, "rb"))
            plt.close()
            os.remove(filunimi)
            await send_mid_info(context, chat_id)
            return True
        elif viesti == "/killankuvaaja":
            kiltadf = _jyrki_df.sum(axis=0)
            plt.bar(kiltadf.index, kiltadf.values)
            plt.xlabel("Pakkaa jäljellä")
            plt.ylabel("Pelejä pelattu")
            plt.title("Killan Jyrkipasianssi tilastot")
            plt.xlim(left=0.5)
            plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(1))
            filunimi = "Jyrkipasianssitilastot_kilta.png"
            plt.savefig(filunimi)
            await context.bot.send_photo(chat_id, photo=open(filunimi, "rb"))
            plt.close()
            os.remove(filunimi)
            await send_mid_info(context, chat_id)
            return True
        elif viesti == "/printdata":
            if user in config.admins:
                await context.bot.send_message(chat_id, "Jyrkipasianssi data printattu konsoliin")
                logging.info(_jyrki_df)
            else:
                await context.bot.send_message(chat_id, "Sinulla ei ole oikeuksia käyttää tätä komentoa.")
            return True
        else:
            await context.bot.send_message(chat_id, "Väärä komento. Käytä /uusipeli, /omatstatsit tai /killanstatsit. Voit poistua pyynnöstä /poistu")
            return True

    if _pending[chat_id] == 2:

        if viesti == "/peru":
            _pending[chat_id] = 1
            await context.bot.send_message(chat_id, "Pyyntö peruttu.")
            await send_mid_info(context, chat_id)
            return True

        if not viesti.isdigit() or not (1 <= int(viesti) <= 52):
            await context.bot.send_message(chat_id, "Pakkojen määrä on kokonaisluku 1-52 -_- Voit perua pyynnön /peru")
            return True

        _jyrki_df.loc[user, int(viesti)] += 1
        _jyrki_df.to_json("jyrkipasianssi_data.json", orient="index")

        if int(viesti) > 25:
            await context.bot.send_message(chat_id, f"Yrittäisit edes :D Jyrkipasianssipeli lisätty käyttäjälle {user} pakkojen määrällä {viesti}.")
        elif int(viesti) < 4:
            await context.bot.send_message(chat_id, f"Oho :o Jyrkipasianssipeli lisätty käyttäjälle {user} pakkojen määrällä {viesti}.")
        else:
            await context.bot.send_message(chat_id, f"Jyrkipasianssipeli lisätty käyttäjälle {user} pakkojen määrällä {viesti}.")
        
        _pending[chat_id] = 1
        send_mid_info(context, chat_id)
        return True
        
     
    elif _pending[chat_id] == 3:

        if viesti == "/peru":
            _pending[chat_id] = 1
            await context.bot.send_message(chat_id, "Pyyntö peruttu.")
            await send_mid_info(context, chat_id)
            return True

        if not viesti.isdigit() or not (1 <= int(viesti) <= 52):
            await context.bot.send_message(chat_id, "Pakkojen määrä on kokonaisluku välillä 1-52 -_- Voit perua pyynnön /peru")
            return True
        if _jyrki_df.loc[user, int(viesti)] <= 0:
            await context.bot.send_message(chat_id, f"Sinulla ei ole kyseisellä pakkojen määrällä peliä pelattuna, syötä uusi numero. Voit perua pyynnön /peru")
            return True
        _jyrki_df.loc[user, int(viesti)] -= 1
        _jyrki_df.to_json("jyrkipasianssi_data.json", orient="index")
        await context.bot.send_message(chat_id, f"Jyrkipasianssipeli poistettu käyttäjältä {user} pakkojen määrällä {viesti}.")
        _pending[chat_id] = 1
        send_mid_info(context, chat_id)
        return True
    
    await context.bot.send_message(chat_id, "Virheellinen komento. Käytä /uusipeli, /poistapeli, /omatstatsit tai /killanstatsit. Voit poistua jyrkimodesta /peru")
    return True