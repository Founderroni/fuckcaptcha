from fuckcaptcha.bda import fingerprinting
import random


def shart() -> str:
    return f"Mozilla/5.0 (Windows NT 10.0); rv:{str(random.randint(1, 480000))}" \
           f".0) Gecko/{str(random.randint(1, 4800))}.0 xXxNiceCaptchaFucktardsPvPYTHDxXx" \
           f"/{str(random.randint(1, 480000))}.0 KAIOS/2.0 Nigger/4.20 Jew/4.4 StiffSock/1.5.0"


def get_random_bda():
    agent = shart()
    return {
        "bda": fingerprinting.get_browser_data(agent),
        "agent": agent
    }
