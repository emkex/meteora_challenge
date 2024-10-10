import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from settings_meteora import tokens, EXTENTION_PATH, meteora_website, jup_website, TURN_IT_ON


async def sell_buy_function(context: BrowserContext, page: Page): # page: Page

    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    # ------------------------  "Connect wallet" -----------------------------

    connect_wal_btn = page.get_by_role('button').filter(has_text="Connect").first
    await expect(connect_wal_btn).to_be_attached()
    await connect_wal_btn.click()
    # print(f'Пробую приконнектить кошель на Jupiter DEX, нажимаю "Connect wallet"')

    solflare_choose = page.locator('//img[@alt="Solflare icon"]')
    await expect(solflare_choose).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await solflare_choose.click()
    # print('Выбираю коннектить Solflare на Jupiter DEX')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await new_window.wait_for_load_state(state='networkidle', timeout=20000)

    solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[3]/div/button[2]')
    await expect(solflare_turn_on).to_be_enabled()
    await solflare_turn_on.click()
    print('Кошелек привязан к сайту')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    # режим swap выбран
    swap_choose = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/a[1]')
    await expect(swap_choose).to_be_visible()
    swap_text = await swap_choose.inner_text()

    if swap_text == 'Swap':
        await swap_choose.click()
        print("Push on mode 'SWAP' even if it's pushed")

    # выбираю токен из стопки, чтобы продать
    token_to_sell = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[2]/div/button')
    await expect(token_to_sell).to_be_enabled()
    await token_to_sell.click()

    # Ниже цикл для сбора количества токенов и сколько они сейчас стоят в $
    current_token_amounts = {}
    current_token_balances_in_dollars = {}

    for token in tokens:
        await page.keyboard.press('Control+A')
        await page.keyboard.press('Backspace')

        await page.keyboard.insert_text(tokens[token]['token_contract'])

        token_dollars = page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/p')
        await expect(token_dollars).to_be_visible()  # token_dollars = page.locator('//li').locator('//img[@alt="SOL"]').locator('//p')
        balance_of_token_text = await token_dollars.inner_text()
        current_token_balances_in_dollars[f'{token}_in_dollars'] = float(balance_of_token_text.replace('$', '').replace(',', '.'))
        print(f"\n{tokens[token]['name']} balance (from jupiter dex) in $: {current_token_balances_in_dollars[f'{token}_in_dollars']} $")

        token_amount = page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/span')
        await expect(token_amount).to_be_visible()
        amounts_of_token_text = await token_amount.inner_text()
        current_token_amounts[f'amount_{token}'] = float(amounts_of_token_text.replace(',', '.'))
        print(f"\n{tokens[token]['name']} balance (from jupiter dex): {current_token_amounts[f'amount_{token}']} {tokens[token]['name']}")

    print('\n', current_token_amounts)
    print(current_token_balances_in_dollars)

    # Estimate SOL balance on Jupiter DEX
    minimum_sol = 0.08

    if current_token_amounts['amount_SOL'] < minimum_sol and current_token_amounts['amount_USDT'] > current_token_balances_in_dollars['JLP_in_dollars']:
        print(f"\nSolana balance (from jupiter dex): {current_token_amounts['amount_SOL']} SOL. Not enough!")
        token_sell = tokens['USDT']
        token_buy = tokens['SOL']
        amount_to_buy = 0.04

    elif current_token_amounts['amount_SOL'] < minimum_sol and current_token_balances_in_dollars['JLP_in_dollars'] > current_token_balances_in_dollars['USDT_in_dollars']:
        print(f"\nSolana balance (from jupiter dex): {current_token_amounts['amount_SOL']} SOL. Not enough!")
        token_sell = tokens['JLP']
        token_buy = tokens['SOL']
        amount_to_buy = 0.04

    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')

    await page.keyboard.insert_text(token_sell['token_contract'])
    token_sell_ready = page.locator('//li').locator(f'//img[@alt="{token_sell['name']}"]')
    await expect(token_sell_ready).to_be_enabled()
    await page.keyboard.press('Enter')
    print(f'Token for selling is {token_sell['name']}')

    token_to_buy = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[2]/div/button')
    await expect(token_to_buy).to_be_enabled()
    await token_to_buy.click()

    await page.keyboard.insert_text(token_buy['token_contract'])
    token_buy_ready = page.locator('//li').locator(f'//img[@alt="{token_buy['name']}"]')
    await expect(token_buy_ready).to_be_enabled()
    await page.keyboard.press('Enter')
    print(f'Token for buying is {token_buy['name']}')

    amount_of_token_to_buy = page.locator('//input[@inputmode="decimal"]').last
    await expect(amount_of_token_to_buy).to_be_enabled()
    await amount_of_token_to_buy.fill(str(amount_to_buy))

    # Добавитьсценарий, если надо вписать не сколько чего купить, а сколько чего продать (скорее всего, вместо купить сол)

    swap_btn = page.locator('//button[@type="submit"]').filter(has_text='Swap')
    await swap_btn.scroll_into_view_if_needed()
    await expect(swap_btn).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await swap_btn.click()

    print('Ready for "SWAPchik"')
    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await new_window.wait_for_load_state(state='networkidle', timeout=20000)

    try:
        solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]').or_(new_window.get_by_role('button').last)
        await expect(solflare_turn_on).to_be_enabled()

        if TURN_IT_ON == 1:  # код сработает
            pass
        else:
            print('FREEZE')
            await asyncio.sleep(100000)

        await solflare_turn_on.click()
        print('Подтверждаю и... ОДОБРЯЮ!')
    except Exception as e:
        print(f'Что-то пошло не так: {e}, ожидаем...')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')