"""
audio.py — Pygame-äänien hallinta.
Sisältää äänen soittamisen, jonotuksen ja pysäyttämisen.
"""
import logging
import time
import pygame


def init(retries: int = 5, delay: int = 2) -> bool:
    """Alustaa pygame.mixer:n. Palauttaa True jos onnistui."""
    for attempt in range(retries):
        try:
            pygame.mixer.init()
            logging.info("audio: mixer alustettu onnistuneesti <3")
            return True
        except pygame.error:
            if attempt < retries - 1:
                logging.warning("audio: laite varattuna, yritetään uudelleen %ds kuluttua (yritys %d)", delay, attempt + 1)
                time.sleep(delay)
            else:
                logging.exception("audio: alustus epäonnistui %d yrityksellä", retries)
    return False


def play(path: str, loops: int = 0) -> bool:
    """Soittaa äänen suoraan (keskeyttää nykyisen)."""
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loops)
        return True
    except Exception:
        logging.exception("audio: soitto epäonnistui: %s", path)
        return False


def queue(path: str, loops: int = 0) -> bool:
    """Lisää äänen jonoon. Jos ei soi mitään, soittaa suoraan."""
    try:
        if not pygame.mixer.music.get_busy():
            return play(path, loops)
        pygame.mixer.music.queue(path, loops=loops)
        return True
    except Exception:
        logging.exception("audio: jonoon lisääminen epäonnistui: %s", path)
        return False


def stop() -> bool:
    """Pysäyttää kaiken äänen."""
    try:
        pygame.mixer.music.stop()
        return True
    except Exception:
        logging.exception("audio: pysäytys epäonnistui")
        return False


def disable() -> bool:
    """Sammuttaa mixerin kokonaan."""
    try:
        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        return True
    except Exception:
        logging.exception("audio: poistaminen käytöstä epäonnistui")
        return False


def enable() -> bool:
    """Käynnistää mixerin uudelleen."""
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        return True
    except Exception:
        logging.exception("audio: käyttöön ottaminen epäonnistui")
        return False


def is_ready() -> bool:
    """Tarkistaa onko mixer käytössä."""
    return pygame.mixer.get_init() is not None
