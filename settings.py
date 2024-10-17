def get_latest_extension_path():
    import os
    # Исправляем путь
    base_path_for_solflare_wallet = os.path.join('C:\\', 'Users', 'Asus', 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Extensions', 'bhhhlbepdkbapadjdnnojkbgioiodbic')

    # Проверяем, существует ли директория
    if not os.path.exists(base_path_for_solflare_wallet):
        raise FileNotFoundError(f"Указанный путь не существует: {base_path_for_solflare_wallet}")

    # Получаем список версий расширений
    versions = [d for d in os.listdir(base_path_for_solflare_wallet) if os.path.isdir(os.path.join(base_path_for_solflare_wallet, d))]

    if not versions:
        raise FileNotFoundError(f"Не найдены версии расширений в {base_path_for_solflare_wallet}")

    # Находим последнюю версию
    latest_version = sorted(versions)[-1]
    latest_extension_path = os.path.join(base_path_for_solflare_wallet, latest_version)

    # Проверяем наличие manifest.json
    manifest_path = os.path.join(latest_extension_path, 'manifest.json')
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Файл манифеста не найден в {latest_extension_path}")

    return latest_extension_path

TURN_IT_ON = 1 # Если 1, то всё работает

tokens = {
    'USDT': {'name':'USDT','token_contract':'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',},
    'JLP': {'name':'JLP','token_contract':'27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4',},
    'SOL': {'name':'SOL','token_contract':'So11111111111111111111111111111111111111112',},
}

minimum_sol = 0.08 # for fees of bchain
minimum_usdt = 4 # for swap USDT to JLP

# for opening position
open_min_percent = 0
open_max_percent = 2.75

# for closing position
percent_of_max = 15
percent_of_min = 15

meteora_website = 'https://app.meteora.ag'
jup_website = 'https://jup.ag/'
jlp_usdt_page = 'https://app.meteora.ag/dlmm/C1e2EkjmKBqx8LPYr2Moyjyvba4Kxkrkrcy5KuTEYKRH'

# solscan_wallet_website = f'https://solscan.io/account/1Eq9gcz9oZSq7EgZehHjgDkTB3Ha9f2QSW7e3Hzg7fp'
# jlp_usdt_pair = 'C1e2EkjmKBqx8LPYr2Moyjyvba4Kxkrkrcy5KuTEYKRH' # GET-запрос

# identificator for solflare: bhhhlbepdkbapadjdnnojkbgioiodbic (found through Win + X -> powershell -> Get-ChildItem -Path "$env:LOCALAPPDATA/Google/Chrome/User Data" -Recurse -Filter "bhhhlbepdkbapadjdnnojkbgioiodbic" | Select-Object FullName)