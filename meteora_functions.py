import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from settings import tokens, TURN_IT_ON, jlp_usdt_page, percent_of_max
from solflare_wallet import confirm_transaction


async def search_pool(context: BrowserContext, page: Page) -> None:

    if await page.locator('button:has-text("Refresh")').is_visible(): # T
        await page.locator('button:has-text("Refresh")').click()

    input_search_token = page.locator('//input[@class="flex-1 w-full placeholder:text-sm"]') # css = 'input.flex-1.w-full.placeholder\\:text-sm'
    await input_search_token.fill(tokens['JLP']['token_contract'])  # Change to jlp-usdt
    await page.keyboard.press("Enter")
    # print('Вставил в поиск контракт токена')

    scroll_to_pair = page.locator('//img[@alt="USDT"]/ancestor::div[contains(@class, "flex")]/following-sibling::div/p[contains(text(), "JLP-USDT")]')
    await expect(scroll_to_pair.first).to_be_visible()
    await scroll_to_pair.scroll_into_view_if_needed()
    await scroll_to_pair.click()
    # print('Отыскал пару JLP-USDT')

    needed_pair = page.locator('//a[@href="/dlmm/C1e2EkjmKBqx8LPYr2Moyjyvba4Kxkrkrcy5KuTEYKRH"]')
    await expect(needed_pair).to_be_visible()
    await needed_pair.click()

    await page.wait_for_load_state(state='domcontentloaded')
    print('Перешел во вкладку к паре JLP-USDT')

    if await page.locator('button:has-text("Agree, let\'s go")').nth(1).is_visible(): # T (del)
        await page.locator('button:has-text("Agree, let\'s go")').nth(1).click()
        print('gang')

    return None
# Change to jlp-usdt + 1 del ! if needed (ready)
    
async def solana_balance(context: BrowserContext, page: Page) -> float:
    # Поиск баланса sol на метеоре
    balance_sol_corner = page.locator('//div[@class="ml-2"]').first
    balance_sol_text = await balance_sol_corner.inner_text()
    sol_balance_meteora = float(balance_sol_text.split(' ')[0].replace(',', '.'))

    return sol_balance_meteora
# ready

async def open_position_meteora(context: BrowserContext, page: Page) -> None:

    await page.bring_to_front()
    await asyncio.sleep(4)

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    add_liquidity_btn = page.get_by_role('button').filter(has_text="Add Liquidity") # copy xpath = //*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/div/div/button
    await add_liquidity_btn.scroll_into_view_if_needed()
    await add_liquidity_btn.click()
    # print("Open 'Add Position' stopka")

    auto_fill = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[1]/div[1]/div/div/button') # auto-fill button
    await expect(auto_fill).to_be_enabled()
    await auto_fill.click()
    # print('Turn OFF Auto-Fill button')

    jlp_max_add = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]')
    await expect(jlp_max_add).to_be_enabled()
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
            print('Retry to turn off Auto-Fill')
            await auto_fill.click()
            await asyncio.sleep(2)
            await usdt_input.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')

    left_border = page.locator('//input[@inputmode="numeric"]').nth(0)
    await expect(left_border).to_be_enabled()
    await left_border.click()
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')
    await left_border.type('0')

    click = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[3]/div[2]/div/div[4]/div[1]/div[1]/div[2]') # additional click for code to work
    await expect(click).to_be_enabled()
    await click.click()
    await asyncio.sleep(2)

    right_border = page.locator('//input[@inputmode="numeric"]').nth(1)
    await expect(right_border).to_be_enabled()
    await right_border.click()
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')
    await right_border.type('3')

    click = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[3]/div[2]/div/div[4]/div[1]/div[1]/div[2]') # additional click for code to work
    await expect(click).to_be_enabled()
    await click.click()
    await asyncio.sleep(2)

    add_liquidity_btn = page.locator('//button[@type="submit"]').filter(has_text='Add Liquidity')
    await add_liquidity_btn.scroll_into_view_if_needed()
    await expect(add_liquidity_btn).to_be_enabled()

    await add_liquidity_btn.click()

    print('Ready for "Add liquidity" to pool')

    while not await confirm_transaction(context, page):
        print('Retry in 20 sec')
        await asyncio.sleep(20)
        # await withdraw_btn.click()
        if await page.get_by_role('alert').nth(0).is_visible():
            await add_liquidity_btn.click()
            # if await confirm_transaction(context):
            #     break
        else:
            await add_liquidity_btn.click()
            # if await confirm_transaction(context):
            #     break

    await asyncio.sleep(40) # wait for confirmation of trx

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')
# ready

async def close_position_meteora(context: BrowserContext, page: Page) -> None:

    await page.bring_to_front()
    await asyncio.sleep(4)

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    if await page.locator('button:has-text("Refresh")').is_visible(): # T
        await page.locator('button:has-text("Refresh")').click()

    your_positions_btn = page.locator('//div/span[text()="Your Positions"]') # css = 'span:has-text("Your Positions")'
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

    await withdraw_and_close_btn.click()

    print('Ready for "Withdraw & Close Position"')

    while not await confirm_transaction(context, page): # T
        print('Retry in 20 sec')
        await asyncio.sleep(20)
        await withdraw_btn.click()
        if await page.get_by_role('alert').nth(0).is_visible():
            await withdraw_and_close_btn.click()
            # if await confirm_transaction(context):
            #     break
        else:
            await withdraw_and_close_btn.click()
            # if await confirm_transaction(context):
            #     break

    await asyncio.sleep(40) # wait for confirmation of trx

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')
# ready

async def get_current_price(context: BrowserContext, page: Page) -> float:

    await page.bring_to_front()

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    pool_price = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/button/div[1]/span')
    pool_price_text = await pool_price.inner_text()
    current_price = float(pool_price_text)
    print(f'Current pool price: {current_price} USDT/JLP')

    return current_price
# ready

async def max_price_pool(context: BrowserContext, page: Page) -> float:

    await asyncio.sleep(3)
    await page.wait_for_load_state(state='domcontentloaded')

    borders = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div/span')
    await expect(borders).to_be_attached()
    borders_text = await borders.inner_text()

    left_price_value = float(borders_text.split(' - ')[0])
    print(f'Left price border: {left_price_value} USDT/JLP')

    right_price_value = float(borders_text.split(' - ')[1])
    print(f'Right price border: {right_price_value} USDT/JLP')

    price_close_pos = left_price_value + percent_of_max/100 * (right_price_value - left_price_value)
    print(f'\nPrice when code will close position is {price_close_pos} USDT/JLP\n')

    return price_close_pos # max price
# ready

async def get_position_balance(context: BrowserContext, page: Page) -> float:

    await page.bring_to_front()
    await asyncio.sleep(4)
    await page.wait_for_load_state(state='domcontentloaded')

    if await page.locator('button:has-text("Agree, let\'s go")').nth(1).is_visible():
        await page.locator('button:has-text("Agree, let\'s go")').nth(1).click()

    if await page.locator('button:has-text("Go Back")').is_visible(): # T
        await page.locator('button:has-text("Go Back")').click()

    if await page.locator('button:has-text("Refresh")').is_visible(): # T
        await page.locator('button:has-text("Refresh")').click()

    if await page.locator('//img[@alt="tip"]').is_visible():
        tip_close = page.get_by_role('button').filter(has_text="Agree, let's go").last
        await tip_close.click()
        # print('Toolflip was closed')

    # if await page.get_by_alt_text('warning').is_visible(): # # WAS TAKEN FROM TIMA. I've never seen this before
    #     print('"WARNING" - расхождение цены')
    #     await asyncio.sleep(120)
    #     return None # перезаход на страницу надо добавить

    # if await page.locator('button', has_text='Connecting...').nth(0).is_visible():
    #     await connect_wallet(context=context)
    #
    # elif await page.locator('button', has_text='Connect Wallet').nth(0).is_visible():
    #     await page.locator('button', has_text='Connect Wallet').nth(0).click(click_count=2)
    #     await page.locator('button:has-text("Solflare")').click() # 3 верх. строчки есть и у меня
    #     await connect_wallet(context=context)

    change_ratio = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/button')
    await expect(change_ratio).to_be_enabled()
    change_ratio_text = await change_ratio.inner_text()
    ratio_pair = change_ratio_text.split('\n')[1]

    if ratio_pair == 'JLP/USDT':
        await change_ratio.click()  # it must be USDT/JLP
        # print('USDT/JLP was choosed')

    current_position_bal = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/div[2]/div[1]/div/span[2]')
    current_position_text = await current_position_bal.inner_text()
    position_balance = float(current_position_text.split(' ')[0])
    print(f'Current position balance: {position_balance} JLP')

    return position_balance
# warn + connecting are commented as I didn't come across with that yet (ready)