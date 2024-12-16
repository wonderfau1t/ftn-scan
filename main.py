import time
from math import ceil

import requests

TELEGRAM_BOT_TOKEN = '7663401015:AAEnpvk5PoMw1KXGWXnehfZUlvZ_PvPG7aE'
TELEGRAM_CHAT_IDS = ['717664582', '508884173']
# TELEGRAM_CHAT_IDS = ['508884173']

start_timestamp = ceil(time.time())
start_block = 4297057

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
        'sort': 'desc',
        'address': wallet_address,
        'startblock': start_block,
    }
    response = requests.get('https://api.ftnscan.com/api', params=params).json()
    transactions = response.get('result')
    if transactions:
        last_tx = transactions[0]

        if last_transactions.get(wallet_address) != last_tx['hash'] and last_tx['txreceipt_status'] == '1':
            last_transactions[wallet_address] = last_tx['hash']

            if wallet_address == hot_wallet_address:
                if last_tx['from'] == wallet_address.lower():
                    message = (
                        f"⬇️ <b>Вывод с MEXC</b>\n"
                        f"На адрес: <code>{last_tx['to']}</code>\n"
                        f"Сумма: {float(last_tx['value']) / 10 ** 18:.4f} FTN\n"
                        f"Хэш: <code>{last_tx['hash']}</code>\n"
                        f"Ссылка: <a href='https://www.ftnscan.com/tx/{last_tx['hash']}'>Посмотреть</a>"
                    )
                elif last_tx['to'] == wallet_address.lower():
                    message = (
                        f"⬆️ <b>Ввод на MEXC</b>\n"
                        f"С адреса: <code>{last_tx['from']}</code>\n"
                        f"Сумма: {float(last_tx['value']) / 10 ** 18:.4f} FTN\n"
                        f"Хэш: <code>{last_tx['hash']}</code>\n"
                        f"Ссылка: <a href='https://www.ftnscan.com/tx/{last_tx['hash']}'>Посмотреть</a>"
                    )
            elif wallet_address == contract_address and last_tx['input'].startswith('0x98dcef71'):
                amount = get_amount_of_ftn(last_tx['hash'])
                message = (
                    f"️⚠️ <b>С контракта разлочены FTN</b>\n"
                    f"Адрес: <code>{last_tx['from']}</code>\n"
                    f"Сумма: {amount:.4f} FTN\n"
                    f"Хэш: <code>{last_tx['hash']}</code>\n"
                    f"Ссылка: <a href='https://www.ftnscan.com/tx/{last_tx['hash']}'>Посмотреть</a>"
                )
            else:
                message = (
                    f"🔔 <b>Что-то на промежуточном адресе происходит</b>\n"
                    f"Адрес: <code>{wallet_address}</code>\n"
                    f"Хэш: <code>{last_tx['hash']}</code>\n"
                    f"Ссылка: <a href='https://www.ftnscan.com/tx/{last_tx['hash']}'>Посмотреть</a>"
                )
            send_telegram_notification(message)


def main():
    send_telegram_notification('Перезапуск...\nПока без фильтра на суммы выводов, надо потестить пока что это :)')
    print("Запуск цикла...")
    while True:
        check_transactions(hot_wallet_address)
        check_transactions(middle_wallet_address)
        check_transactions(contract_address)
        time.sleep(5)


def get_amount_of_ftn(tx_hash):
    amount = 0
    logs = requests.get("https://api.ftnscan.com/api", params={
        'module': 'transaction',
        'action': 'gettxinfo',
        'txhash': tx_hash
    }).json().get('result').get('logs')
    for log in logs:
        if log.get('topics')[0].startswith('0xddf252ad'):
            amount = int(log.get('data'), 16) / 10 ** 18
    return amount


if __name__ == '__main__':
    main()
