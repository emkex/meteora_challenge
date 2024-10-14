import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from settings import tokens, TURN_IT_ON
from solflare_wallet import connect_wallet_jup


async def prepare_jupiter(context: BrowserContext, page: Page) -> None: # page: Page

    await page.bring_to_front()
    await page.reload()
    await page.wait_for_load_state(state='domcontentloaded')

    await connect_wallet_jup(context, page)

    swap_choose = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/a[1]')
    swap_text = await swap_choose.inner_text()

    if swap_text == 'Swap':
        await swap_choose.click()
        print("Push on mode 'SWAP' even if it's pushed")


async def get_token_balances(context: BrowserContext, page: Page) -> dict:  # page: Page

    # выбираю токен из стопки
    token_to_sell = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[2]/div/button')
    await expect(token_to_sell).to_be_enabled()
    await token_to_sell.click()

    token_balances = {}

    # Collect balances of 'tokens' (dictionary) : USDT, JLP, SOL
    for token in tokens:
        await page.keyboard.press('Control+A')
        await page.keyboard.press('Backspace')

        await page.keyboard.insert_text(tokens[token]['token_contract'])

        token_amount = page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/span')
        await expect(token_amount).to_be_visible()
        token_amount_text = await token_amount.inner_text()
        token_balances[token] = float(token_amount_text.replace(',', '.'))

    print('\n', token_balances, '\n')

    return token_balances


async def swap_to_solana_jup(context: BrowserContext, page: Page, token_balances: dict) -> None:

    minimum_sol = 0.08

    if token_balances['SOL'] < minimum_sol:

        if token_balances['USDT'] > 6:
            token_sell = tokens['USDT']
            token_buy = tokens['SOL']
            amount_to_sell = 5 # USDT i will sell for n SOL
            # print(f'Initialize swap of {amount_to_sell} USDT to SOL')

        elif token_balances['JLP'] > 3:
            token_sell = tokens['JLP']
            token_buy = tokens['SOL']
            amount_to_sell = 2 # JLP i will sell for n SOL
            # print(f'Initialize swap of {amount_to_sell} JLP to SOL')

        else:
            print('You do not have enough SOL, USDT and JLP')
            await asyncio.sleep(100000) # send me TG warning

    # Continue
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')

    token_insert_name1 = token_sell['name']
    await page.keyboard.insert_text(token_sell['token_contract'])
    token_sell_choose = page.locator('//li').locator(f'//img[@alt="{token_insert_name1}"]')
    await expect(token_sell_choose).to_be_enabled()
    await page.keyboard.press('Enter')
    # print(f'Token for selling is {token_sell["name"]}')

    token_buy_choose = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[2]/div/button')
    await expect(token_buy_choose).to_be_enabled()
    await token_buy_choose.click()

    token_insert_name2 = token_buy['name']
    await page.keyboard.insert_text(token_buy['token_contract'])
    token_buy_ready = page.locator('//li').locator(f'//img[@alt="{token_insert_name2}"]')
    await expect(token_buy_ready).to_be_enabled()
    await token_buy_ready.click()
    # print(f'Token for buying is {token_buy["name"]}')

    amount_token_sell = page.locator('//input[@inputmode="decimal"]').first
    await amount_token_sell.fill(str(amount_to_sell))

    swap_btn = page.locator('//button[@type="submit"]').filter(has_text='Swap')
    await swap_btn.scroll_into_view_if_needed()
    await expect(swap_btn).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await swap_btn.click()

    print(f'Ready for "SWAPchik" of {token_insert_name1} to {token_insert_name2}')
    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await asyncio.sleep(3)
    await new_window.wait_for_load_state(state='domcontentloaded')

    try:
        solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]').or_(new_window.get_by_role('button').last)
        await expect(solflare_turn_on).to_be_enabled()

        if TURN_IT_ON == 1:  # код сработает
            await solflare_turn_on.click(click_count=2)
            print('Подтверждаю и... ОДОБРЯЮ!\n')
        else:
            print('FREEZE')
            await asyncio.sleep(100000)

    except Exception as e:
        print(f'Что-то пошло не так: {e}, ожидаем...')

    # -------------------- Переключение на соседнее окно -----------------------------

    await asyncio.sleep(40) # wait for confirmation of trx


async def swap_to_jlp_jup(context: BrowserContext, page: Page, token_balances: dict) -> None:

    minimum_usdt = 4

    if token_balances['USDT'] >= minimum_usdt:
        token_sell = tokens['USDT'] # sell max USDT
        token_buy = tokens['JLP']

    else:
        return

    # Continue
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')

    token_insert_name1 = token_sell['name']
    await page.keyboard.insert_text(token_sell['token_contract'])
    token_sell_choose = page.locator('//li').locator(f'//img[@alt="{token_insert_name1}"]')
    await expect(token_sell_choose).to_be_enabled()
    await page.keyboard.press('Enter')
    # print(f'Token for selling is {token_sell["name"]}')

    token_buy_choose = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[2]/div/button')
    await expect(token_buy_choose).to_be_enabled()
    await token_buy_choose.click()

    token_insert_name2 = token_buy['name']
    await page.keyboard.insert_text(token_buy['token_contract'])
    token_buy_ready = page.locator('//li').locator(f'//img[@alt="{token_insert_name2}"]')
    await expect(token_buy_ready).to_be_enabled()
    await token_buy_ready.click()
    # print(f'Token for buying is {token_buy["name"]}')

    amount_token_sell = page.get_by_role('button').filter(has_text='MAX')
    await expect(amount_token_sell).to_be_enabled()
    await amount_token_sell.click()

    swap_btn = page.locator('//button[@type="submit"]').filter(has_text='Swap')
    await swap_btn.scroll_into_view_if_needed()
    await expect(swap_btn).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await swap_btn.click()

    print(f'Ready for "SWAPchik" of {token_insert_name1} to {token_insert_name2}')
    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await asyncio.sleep(3)
    await new_window.wait_for_load_state(state='domcontentloaded')

    try:
        solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]').or_(new_window.get_by_role('button').last)
        await expect(solflare_turn_on).to_be_enabled()

        if TURN_IT_ON == 1:  # код сработает
            await solflare_turn_on.click(click_count=2)
            print('Подтверждаю и... ОДОБРЯЮ!\n')
        else:
            print('FREEZE')
            await asyncio.sleep(100000)

    except Exception as e:
        print(f'Что-то пошло не так: {e}, ожидаем...')

    # -------------------- Переключение на соседнее окно -----------------------------

    await asyncio.sleep(40) # wait for confirmation of trx