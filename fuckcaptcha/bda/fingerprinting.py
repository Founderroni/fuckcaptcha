from fuckcaptcha import cipher

import base64
import json
import secrets
import time


def get_browser_data(user_agent: str) -> str:
    ts = time.time()
    timeframe = int(ts - ts % 21600)
    key = user_agent + str(timeframe)
    data = cipher.encrypt(
        json.dumps(
            {secrets.token_hex(64): "Contact dort.#0001 on discord ur shits ass bruh"}
        ),
        key,
    )
    data = base64.b64encode(data.encode("utf-8")).decode("utf-8")
    return data
