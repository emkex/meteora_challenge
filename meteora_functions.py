import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from meteora_settings import tokens, TURN_IT_ON, jlp_usdt_page, percent_of_max


async def open_position_meteora(context: BrowserContext, page: Page):

    await page.bring_to_front()

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    bottom_of_page = page.locator('//div[contains(@class, "overflow-x-auto")]')
    add_position_btn = bottom_of_page.locator('//div/span[text()="Add Position"]')
    await add_position_btn.scroll_into_view_if_needed()
    await add_position_btn.click()
    # print("Open 'Add Position' stopka")

    auto_fill = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[1]/div[1]/div/div/button') # auto-fill button
    await expect(auto_fill).to_be_enabled()
    await auto_fill.click()
    # print('Turn OFF Auto-Fill button')

    jlp_max_add = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]')
    await expect(jlp_max_add).to_be_attached()
    await jlp_max_add.click()
    # print(f'All JLP in pool...')

    for _ in range(3):

        usdt_input = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[1]/div[2]/div[2]/div[1]/input') # usdt_input = page.locator('//div[@class="h-8 w-8"]/ancestor::div//input[@placeholder="0.00"]').nth(1)
        await asyncio.sleep(2)
        usdt_value = await usdt_input.input_value() # Double-check that auto_fill is OFF: must be nothing

        if usdt_value == '':
            # print('Auto_fill was turned off')
            break

        else:
            # print('Retry to turn off Auto-Fill')
            await auto_fill.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')

    left_border = page.locator('//input[@inputmode="numeric"]').nth(0)
    await expect(left_border).to_be_enabled()
    await left_border.click()
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')
    await left_border.type('0')
    await asyncio.sleep(2)

    click = page.locator('//div[@type = "button"]').and_(page.locator('//div[@aria-controls="radix-:r0:"]')) # additional click for code to work
    await expect(click).to_be_enabled()
    await click.click()

    await asyncio.sleep(2)

    right_border = page.locator('//input[@inputmode="numeric"]').nth(1)
    await expect(right_border).to_be_enabled()
    await right_border.click()
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')
    await right_border.type('3')

    click = page.locator('//div[@type = "button"]').and_(page.locator('//div[@aria-controls="radix-:r0:"]')) # additional click for code to work
    await expect(click).to_be_enabled()
    await click.click()

    await asyncio.sleep(2)

    add_liquidity_btn = page.locator('//button[@type="submit"]').filter(has_text='Add Liquidity')
    await add_liquidity_btn.scroll_into_view_if_needed()
    await expect(add_liquidity_btn).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await add_liquidity_btn.click()

    print('Ready for "Add liquidity" to pool')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await asyncio.sleep(3)
    await new_window.wait_for_load_state(state='domcontentloaded')

    try:
        solflare_approve = new_window.locator('//body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]').or_(new_window.get_by_role('button').last)
        await expect(solflare_approve).to_be_enabled()

        if TURN_IT_ON == 1: # код сработает если 1 в settings
            await solflare_approve.click(click_count=2)
            print('Подтверждаю и... ОДОБРЯЮ транзакцию!')
        else:
            print('FREEZE')
            await asyncio.sleep(100000)

    except Exception as e:
        print(f'Что-то пошло не так: {e}, ожидаем...')

    # ---------------------- Переключение на соседнее окно ---------------------------

    await asyncio.sleep(40) # wait for confirmation of trx

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    return


async def close_position_meteora(context: BrowserContext, page: Page):

    await page.bring_to_front()

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    bottom_of_page = page.locator('//div[contains(@class, "overflow-x-auto")]')
    your_positions_btn = bottom_of_page.locator('//div/span[text()="Your Positions"]')
    await your_positions_btn.scroll_into_view_if_needed()
    await your_positions_btn.click()
    # print("Open 'Your Positions' stopka")

    my_position_btn = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]')
    await expect(my_position_btn).to_be_enabled()
    await my_position_btn.click()

    withdraw_btn = page.locator('//div[text() = "Withdraw"]')
    await expect(withdraw_btn).to_be_enabled()
    await withdraw_btn.click()

    withdraw_and_close_btn = page.locator('//button[@type="submit"]').filter(has_text='Withdraw & Close Position')
    await withdraw_and_close_btn.scroll_into_view_if_needed()
    await expect(withdraw_and_close_btn).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await withdraw_and_close_btn.click()

    print('Ready for "Withdraw & Close Position"')
    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await asyncio.sleep(3)
    await new_window.wait_for_load_state(state='domcontentloaded')

    try:
        solflare_approve = new_window.locator('//body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]').or_(new_window.get_by_role('button').last)
        await expect(solflare_approve).to_be_enabled()

        if TURN_IT_ON == 1:  # код сработает
            await solflare_approve.click(click_count=2)
            print('Подтверждаю и... ОДОБРЯЮ транзакцию!')
        else:
            print('FREEZE')
            await asyncio.sleep(100000)

    except Exception as e:
        print(f'Что-то пошло не так: {e}, ожидаем...')

    # -------------------- Переключение на соседнее окно -----------------------------

    await asyncio.sleep(40) # wait for confirmation of trx

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')


async def sell_buy_jupiter(context: BrowserContext, page: Page): # page: Page

    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    # ------------------------  "Connect wallet" -----------------------------

    connect_wal_btn = page.get_by_role('button').filter(has_text="Connect").first
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
    await asyncio.sleep(3)
    await new_window.wait_for_load_state(state='domcontentloaded')

    solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[3]/div/button[2]')
    await expect(solflare_turn_on).to_be_enabled()
    await solflare_turn_on.click(click_count=2)
    print('Кошелек привязан к сайту')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    # режим swap выбран
    swap_choose = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/a[1]')
    swap_text = await swap_choose.inner_text()

    if swap_text == 'Swap':
        await swap_choose.click()
        print("Push on mode 'SWAP' even if it's pushed")

    # выбираю токен из стопки, чтобы продать
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

    print(f'Ready for "SWAPchik" of {amount_to_sell} {token_insert_name1} to SOL ')
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


async def pool_price_check(context: BrowserContext, page: Page):

    await page.bring_to_front()

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    pool_price = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/button/div[1]/span')
    pool_price_text = await pool_price.inner_text()
    pool_price_value = float(pool_price_text)
    print(f'Current pool price: {pool_price_value} USDT/JLP')

    return pool_price_value


async def max_price_pool(context: BrowserContext, page: Page):

    borders = page.locator('//*[@id="__next"]/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div/span')
    await expect(borders).to_be_attached()
    borders_text = await borders.inner_text()

    left_price_value = float(borders_text.split(' - ')[0])
    print(f'Left price border: {left_price_value} USDT/JLP')

    right_price_value = float(borders_text.split(' - ')[1])
    print(f'Right price border: {right_price_value} USDT/JLP')

    price_close_pos = left_price_value + percent_of_max/100 * (right_price_value - left_price_value)
    print(f'\nPrice when code will close position is {price_close_pos} USDT/JLP\n')

    return price_close_pos # max price