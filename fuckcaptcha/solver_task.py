import json
import random
import sys
import time
from urllib.parse import urlparse

import httpx

from fuckcaptcha import cipher
from fuckcaptcha.api import breakers
from fuckcaptcha.bda.browser_agent_fetcher import get_random_bda


def get_request_id(session_token):
    key = f"REQUESTED{session_token}ID"
    data = "{}"
    return cipher.encrypt(data, key)


class Solver:

    def __init__(self, surl, skey, url, agent, bda, proxies):
        self.proxies = proxies
        self.surl = urlparse(surl).hostname
        self.agent = agent
        self.bda = bda
        self.url = url
        self.skey = skey
        self.proxy = f"http://{next(proxies)}"
        self.api_url = "https://client-api.arkoselabs.com"
        self.answers = []
        self.client = httpx.Client(proxies=self.proxy)

    def get_site_token_data(self):
        url = f'{self.api_url}/fc/gt2/public_key/{self.skey}'
        return self.client.post(url, headers={
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://iframe.arkoselabs.com",
            "referer": "https://iframe.arkoselabs.com/",
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": self.agent
        }, data={
            'bda': self.bda,
            'public_key': self.skey,
            'site': self.url,
            'userbrowser': self.agent,
            'language': 'fr',
            'rnd': str(random.random()),
            'data[id]': 'null',
        }).json()

    def load_captcha(self, session_token, region):
        url = f'{self.api_url}/fc/a/'
        return self.client.post(url, headers={
            'accept': '*/*',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'accept-encoding': 'gzip, deflate, br',
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "accept-language": "en-US,en;q=0.9",
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://iframe.arkoselabs.com',
            'referer': 'https://iframe.arkoselabs.com/',
            'user-agent': self.agent,
            "x-newrelic-timestamp": str(int(time.time()) * 1000),
            # "X-Requested-With": "XMLHttpRequest",
            # "X-Requested-ID": get_request_id(session_token),
        }, data={
            'session_token': session_token,
            'sid': region,
            'analytics_tier': 40,
            'category': 'Site URL',
            'action': 'https://iframe.arkoselabs.com/',
            'render_type': 'canvas'
        }).json()

    def get_challenge(self, token, region):
        url = f'{self.api_url}/fc/gfct/'
        return self.client.post(url, headers={
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://client-api.arkoselabs.com',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'referer': 'https://client-api.arkoselabs.com/fc/gc/?token=' + token.replace("|", "&"),
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.agent,
            "Cookie": f"timestamp={str(int(time.time()) * 1000)}",
            "x-newrelic-timestamp": str(int(time.time()) * 1000),
            # "X-Requested-With": "XMLHttpRequest",
            # "X-Requested-ID": get_request_id(token)
        }, data={
            'data[status]': 'init',
            'render_type': 'canvas',
            'sid': region,
            'analytics_tier': 40,
            'lang': 'fr',
            'token': token,
        }).json()

    def answer_normal(self, api_breaker, region, session_token, challenge_token, input_answer):
        input_answer = breakers.get_location(input_answer)
        fixed_answer = breakers.fix_answer(api_breaker, input_answer)
        self.answers.append(fixed_answer)
        url = f'{self.api_url}/fc/ca/'
        return self.client.post(url, headers={
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'user-agent': self.agent,
            # "X-Requested-With": "XMLHttpRequest",
            # "X-Requested-ID": get_request_id(session_token),
        }, data={
            'game_token': challenge_token,
            'sid': region,
            'session_token': session_token,
            'guess': cipher.encrypt(json.dumps(self.answers), session_token),
            'analytics_tier': 40,
            'bio': "eyJtYmlvIjoiMzM3MCwwLDMwMCwzNjszNDA0LDAsMjk0LDM2OzM0MTAsMCwyODgsMzg7MzQxNywwLDI4MywzOTszNDIzLDAsMjc4LDQzOzM0MjgsMCwyNzQsNDg7MzQzMiwwLDI3Miw1MzszNDM1LDAsMjcwLDU4OzM0MzgsMCwyNjgsNjQ7MzQ0MSwwLDI2NCw2OTszNDQ1LDAsMjYzLDc2OzM0NDgsMCwyNjEsODI7MzQ1MiwwLDI1OSw4OTszNDU1LDAsMjU3LDk0OzM0NTcsMCwyNTcsMTAwOzM0NjAsMCwyNTUsMTA1OzM0NjMsMCwyNTEsMTExOzM0NjYsMCwyNTAsMTE3OzM0NjksMCwyNDgsMTIyOzM0NzMsMCwyNDYsMTI3OzM0ODAsMCwyNDQsMTMyOzM0ODksMCwyNDIsMTM3OzM1MDAsMCwyNDEsMTQyOzM1MTIsMCwyNDAsMTQ3OzM1MjAsMCwyNDAsMTU0OzM1MzAsMCwyNDEsMTYwOzM1NDIsMCwyNDMsMTY1OzM1NDgsMCwyNDYsMTcwOzM1NTYsMCwyNTAsMTc0OzM1NjksMCwyNTUsMTc5OzM1ODgsMCwyNjAsMTgyOzM3MDMsMCwyNTcsMTg3OzM3ODYsMSwyNTMsMTg5OzM5MjksMiwyNTMsMTg4OzQwNjgsMCwyNTIsMTg2OzQwODcsMCwyNDgsMTgxOzQxMTMsMCwyNDQsMTc3OzQxMzQsMCwyNDAsMTczOzQxNjcsMCwyMzUsMTcwOzQyMTAsMCwyMzIsMTY1OzQzODksMSwyMzEsMTYyOzQ0ODcsMiwyMzEsMTYyOyIsInRiaW8iOiIiLCJrYmlvIjoiIn0="
        }).json()

    def answer_rotate(self, answer, challenge, challenge_token, region, session_token):
        clr = challenge['game_data']['customGUI']['_guiTextColor']
        increment = int("28" if clr else clr.replace("#", "0x")[3:])
        increment = round(increment / 10, 2) if increment > 113 else increment
        new_answer = round(answer * increment) if 0.0 <= answer <= round(360 / 51.4) - 1 else answer
        self.answers.append(new_answer)
        url = f'{self.api_url}/fc/ca/'
        return self.client.post(url, headers={
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'user-agent': self.agent,
            "sec-fetch-site": "cross-site",
            "Accept-Language": "en-US,en;q=0.9",
            # "X-Requested-With": "XMLHttpRequest",
            # "X-Requested-ID": get_request_id(session_token),
        }, data={
            'game_token': challenge_token,
            'sid': region,
            'session_token': session_token,
            'guess': cipher.encrypt(json.dumps(self.answers), session_token),
            'analytics_tier': 40,
            'bio': "eyJtYmlvIjoiMzM3MCwwLDMwMCwzNjszNDA0LDAsMjk0LDM2OzM0MTAsMCwyODgsMzg7MzQxNywwLDI4MywzOTszNDIzLDAsMjc4LDQzOzM0MjgsMCwyNzQsNDg7MzQzMiwwLDI3Miw1MzszNDM1LDAsMjcwLDU4OzM0MzgsMCwyNjgsNjQ7MzQ0MSwwLDI2NCw2OTszNDQ1LDAsMjYzLDc2OzM0NDgsMCwyNjEsODI7MzQ1MiwwLDI1OSw4OTszNDU1LDAsMjU3LDk0OzM0NTcsMCwyNTcsMTAwOzM0NjAsMCwyNTUsMTA1OzM0NjMsMCwyNTEsMTExOzM0NjYsMCwyNTAsMTE3OzM0NjksMCwyNDgsMTIyOzM0NzMsMCwyNDYsMTI3OzM0ODAsMCwyNDQsMTMyOzM0ODksMCwyNDIsMTM3OzM1MDAsMCwyNDEsMTQyOzM1MTIsMCwyNDAsMTQ3OzM1MjAsMCwyNDAsMTU0OzM1MzAsMCwyNDEsMTYwOzM1NDIsMCwyNDMsMTY1OzM1NDgsMCwyNDYsMTcwOzM1NTYsMCwyNTAsMTc0OzM1NjksMCwyNTUsMTc5OzM1ODgsMCwyNjAsMTgyOzM3MDMsMCwyNTcsMTg3OzM3ODYsMSwyNTMsMTg5OzM5MjksMiwyNTMsMTg4OzQwNjgsMCwyNTIsMTg2OzQwODcsMCwyNDgsMTgxOzQxMTMsMCwyNDQsMTc3OzQxMzQsMCwyNDAsMTczOzQxNjcsMCwyMzUsMTcwOzQyMTAsMCwyMzIsMTY1OzQzODksMSwyMzEsMTYyOzQ0ODcsMiwyMzEsMTYyOyIsInRiaW8iOiIiLCJrYmlvIjoiIn0="
        }).json()

    def solve(self):
        data = self.get_site_token_data()
        original_token = data['token']
        split = original_token.split("|")
        session_token = split[0]
        region = split[1].replace("r=", "")
        if self.load_captcha(session_token, region)['logged']:
            challenge = self.get_challenge(session_token, region)
            challenge_id = challenge['challengeID']
            waves = challenge['game_data']['waves']
            if waves > 2:
                raise "Challenge too hard of. Not able of completer. Sir. Ofing. Ok"
            if challenge['game_data']['gameType'] == 3:
                api_breaker = challenge['game_data']['customGUI']['api_breaker']
                for _ in range(waves):
                    answered = self.answer_normal(api_breaker, region, session_token, challenge_id,
                                                  random.randint(0, 5))
                    if 'solved' in answered and answered['solved']:
                        return {
                            'solved': True,
                            'token': original_token,
                            'bda': {
                                "bda": self.bda,
                                "agent": self.agent
                            }
                        }
            elif challenge['game_data']['gameType'] == 1:
                for _ in range(waves):
                    answered = self.answer_rotate(random.randint(0, 360), challenge, challenge_id,
                                                  region, session_token)
                    if 'solved' in answered and answered['solved']:
                        return {
                            'solved': True,
                            'token': original_token,
                            'bda': {
                                "bda": self.bda,
                                "agent": self.agent
                            }
                        }

        else:
            return {
                "solved": False,
                "token": original_token
            }


def solve(surl, skey, url, proxies):
    while True:
        nigger = get_random_bda()
        agent = nigger['agent']
        bda = nigger['bda']
        solver = Solver(surl, skey, url, agent, bda, proxies)
        try:
            result = solver.solve()
            if result['solved']:
                return result['token']
        except Exception:
            pass
