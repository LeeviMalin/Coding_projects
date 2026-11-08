"""
http_utils.py — HTTP-apufunktiot.
safe_get tekee uudelleenyrityksiä epäonnistuneille GET-pyynnöille.
"""
import logging
import time
import requests

_session: requests.Session | None = None


def get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def safe_get(url: str, timeout=(3, 10), retries: int = 3, **kwargs):
    """GET-pyyntö uudelleenyrityksillä. Palauttaa Response-objektin tai None."""
    #logging.info("safe_get: %s", url)
    for attempt in range(retries):
        t0 = time.time()
        try:
            resp = requests.get(url, timeout=timeout, **kwargs)
            #logging.info("safe_get: vastaus %.3fs status=%s", time.time() - t0, resp.status_code)
            resp.raise_for_status()
            return resp
        except requests.exceptions.ConnectTimeout:
            logging.warning("safe_get: yhteys aikakatkaisu yritys %d (%.3fs)", attempt + 1, time.time() - t0)
        except requests.exceptions.ReadTimeout:
            logging.warning("safe_get: luku aikakatkaisu yritys %d (%.3fs)", attempt + 1, time.time() - t0)
        except requests.exceptions.ConnectionError:
            logging.warning("safe_get: yhteysvirhe yritys %d (%.3fs)", attempt + 1, time.time() - t0)
        except Exception:
            logging.exception("safe_get: odottamaton virhe yritys %d (%.3fs)", attempt + 1, time.time() - t0)

        if attempt < retries - 1:
            time.sleep(0.5)

    logging.error("safe_get: kaikki yritykset epäonnistuivat url=%s", url)
    return None
