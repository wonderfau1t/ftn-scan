import time
from math import ceil

import requests

TELEGRAM_BOT_TOKEN = '7663401015:AAEnpvk5PoMw1KXGWXnehfZUlvZ_PvPG7aE'
TELEGRAM_CHAT_IDS = ['717664582', '508884173']

start_timestamp = ceil(time.time())
start_block = 4296576

hot_wallet_address = '0x04950aaAc4f1896A0385C85415904677CE770303'
middle_wallet_address = '0xb63A33e7b5d5004245fd27a4Fbecd0F02d286e22'
contract_address = '0x0CA83dD56aF172A1E04B667D6E64446d0B88c4a4'

last_transactions = {
    hot_wallet_address: None,
    middle_wallet_address: None,
    contract_address: None
}


def send_telegram_notification(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Ошибка при отправке в Telegram: {response.text}")


def check_transactions(wallet_address):
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet_address,
        # 'start_timestamp': start_timestamp,
        'start_block': start_block
    }
    response = requests.get('https://api.ftnscan.com/api', params=params).json()
    transactions = response.get('result')
    if transactions:
        latest_hash = transactions[0]['hash']
        if last_transactions.get(wallet_address) != latest_hash:
            last_transactions[wallet_address] = latest_hash
            message = (
                f"🔔 <b>Новая транзакция!</b>\n"
                f"Кошелек: <code>{wallet_address}</code>\n"
                f"Hash: <code>{latest_hash}</code>\n"
                f"Ссылка: <a href='https://www.ftnscan.com/tx/{latest_hash}'>Посмотреть</a>"
            )
            send_telegram_notification(message)


def main():
    print("Запуск цикла...")
    while True:
        check_transactions(hot_wallet_address)
        check_transactions(middle_wallet_address)
        check_transactions(contract_address)
        time.sleep(5)


if __name__ == '__main__':
    main()
