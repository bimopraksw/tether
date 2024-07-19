from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import requests
import time


with open('query.txt', 'r') as file:
    authorizations = [line.strip() for line in file.readlines()]

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Access-Control-Allow-Origin': '*',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Host': 'tap-tether.org',
    'Referer': 'https://tap-tether.org/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
}

def log_with_timestamp(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(
        f"{Fore.BLUE + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{message}"
    )

def format_balance(balance):
    value = float(balance) / 1000000
    return "{:.8f}".format(value)

def tt_login(token, index):
    url = 'https://tap-tether.org/server/login'
    headers.update({
        'Authorization': token
    })
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()['userData']
        first_name = data['firstName']
        balance = format_balance(data['balance'])
        remaining_clicks = data['remainingClicks']
        result = (
            f"{Fore.CYAN + Style.BRIGHT}[ {first_name} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT}[ USDT {balance} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}[ Remaining Clicks {remaining_clicks} ]{Style.RESET_ALL}"
        )
        return result, data['lastUpdateClicksTime']
    return None, None

def tt_clicks(token, last_click_time):
    url = f"https://tap-tether.org/server/clicks?clicks=1000&lastClickTime={last_click_time}"
    headers.update({
        'Authorization': token
    })
    response = requests.get(url=url, headers=headers)
    return response.status_code == 200

def tt_run(token, index):
    while True:
        try:
            time.sleep(1)
            result, last_click_time = tt_login(token, index)

            if result:
                tt_clicks(token, last_click_time)
                return result

        except Exception as e:
            log_with_timestamp(f"🍓 {Fore.RED + Style.BRIGHT}[ Account {index + 1} ] [ {e} ]")
            return
while True:
    init(autoreset=True)
    results = []
    with ThreadPoolExecutor(max_workers=len(authorizations)) as executor:
        futures = [executor.submit(tt_run, token, index) for index, token in enumerate(authorizations)]
        for future in futures:
            result = future.result()
            if result:
                results.append(result)

    if results:
        log_with_timestamp("\n".join(results))
    time.sleep(1)
