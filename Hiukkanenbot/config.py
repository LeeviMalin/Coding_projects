"""
config.py — Lataa ja tallentaa botin asetukset config.json-tiedostoon.
Sisältää myös botin globaalin tilan (admins, hallitus, jne.)
"""
import json
import logging
import os

# ---------------------------------------------------------------------------
# Botin conffaus — muokataan vain tässä moduulissa, luetaan muualta
# ---------------------------------------------------------------------------

bot_token: str = ""
admins: list[str] = []
hallitus_id: int = 0               # Hallituksen ryhmächatin ID
hallituksen_jasenet: list[str] = []
hallituksen_salasana: str = ""

CONFIG_PATH = os.environ.get("HB_CONFIG_PATH", "config.json")

def load() -> bool:
    """Lukee config.json:n ja päivittää moduulin tilan. Palauttaa True jos onnistui."""
    global bot_token, admins, hallitus_id, hallituksen_jasenet, hallituksen_salasana
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)

        bot_token = data.get("bot_token", "")
        if not bot_token:
            logging.error("config: bot_token puuttuu")
            return False

        hallitus_id = int(data.get("hallitusid", 0))
        admins = data.get("admins", [])
        hallituksen_jasenet = data.get("hallituksen_jasenet", [])
        hallituksen_salasana = data.get("hallituksen_salasana", "")

        logging.info("config: ladattu onnistuneesti")
        return True

    except Exception:
        logging.exception("config: virhe tiedoston luvussa")
        return False


def save() -> None:
    """Tallentaa nykyisen tilan config.json:iin."""
    data = {
        "bot_token": bot_token,
        "admins": admins,
        "hallitusid": hallitus_id,
        "hallituksen_jasenet": hallituksen_jasenet,
        "hallituksen_salasana": hallituksen_salasana,
    }
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f)
        logging.info("config: tallennettu")
    except Exception:
        logging.exception("config: tallennus epäonnistui")
