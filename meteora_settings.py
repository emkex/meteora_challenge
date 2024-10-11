EXTENTION_PATH = r'C:/Users/Asus/AppData/Local/Google/Chrome/User Data/Default/Extensions/bhhhlbepdkbapadjdnnojkbgioiodbic/1.72.1_0/' # path to the manifest

TURN_IT_ON = 1 # Если 1, то в самом конце пройдёт транзакция

DEFAULT_DELAY = 100

tokens = {
    'USDT': {'name':'USDT','token_contract':'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',},
    'JLP': {'name':'JLP','token_contract':'27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4',},
    'SOL': {'name':'SOL','token_contract':'So11111111111111111111111111111111111111112',},
}

meteora_website = 'https://app.meteora.ag'
jup_website = 'https://jup.ag/'
jlp_usdt_page = 'https://app.meteora.ag/dlmm/C1e2EkjmKBqx8LPYr2Moyjyvba4Kxkrkrcy5KuTEYKRH'

# solscan_wallet_website = f'https://solscan.io/account/1Eq9gcz9oZSq7EgZehHjgDkTB3Ha9f2QSW7e3Hzg7fp'
# jlp_usdt_pair = 'C1e2EkjmKBqx8LPYr2Moyjyvba4Kxkrkrcy5KuTEYKRH' # GET-запрос

# identificator for solflare: bhhhlbepdkbapadjdnnojkbgioiodbic (found through Win + X -> powershell -> Get-ChildItem -Path "$env:LOCALAPPDATA/Google/Chrome/User Data" -Recurse -Filter "bhhhlbepdkbapadjdnnojkbgioiodbic" | Select-Object FullName)