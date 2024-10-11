import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from settings_meteora import TURN_IT_ON, jlp_usdt_page


async def open_position_meteora(context: BrowserContext, page: Page):

    await page.bring_to_front()

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    bottom_of_page = page.locator('//div[contains(@class, "overflow-x-auto")]')
    # await expect(bottom_of_page).to_be_attached() # DELETE
    add_position_btn = bottom_of_page.locator('//div/span[text()="Add Position"]')
    await add_position_btn.scroll_into_view_if_needed()
    # await expect(add_position_btn).to_be_visible() # M/B DELETE
    await add_position_btn.click()
    # print("Open 'Add Position' stopka")

    # # Поиск баланса jlp на метеоре
    # balance_jlp_span = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[1]/div[2]/div[1]/div[2]/div[1]/div/span')
    # await expect(balance_jlp_span).to_be_visible()
    # balance_jlp_text = await balance_jlp_span.inner_text()
    # jlp_balance_meteora = float(balance_jlp_text)
    # print(f"\nJupiter Perps LP balance (from meteora web): {jlp_balance_meteora} JLP")

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
    await left_border.fill('0')

    await asyncio.sleep(2)

    right_border = page.locator('//input[@inputmode="numeric"]').nth(1)
    await expect(right_border).to_be_enabled()
    await right_border.click()
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')
    await right_border.fill('3')

    await asyncio.sleep(2)

    left_border = page.locator('//input[@inputmode="numeric"]').nth(0)
    await expect(left_border).to_be_enabled()
    await left_border.click()

    right_border = page.locator('//input[@inputmode="numeric"]').nth(1)
    await expect(right_border).to_be_enabled()
    await right_border.click()
    await page.keyboard.press('Control+A')
    await page.keyboard.press('Backspace')
    await right_border.fill('3')

    add_liquidity_btn = page.locator('//button[@type="submit"]').filter(has_text='Add Liquidity')
    await add_liquidity_btn.scroll_into_view_if_needed()
    await expect(add_liquidity_btn).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await add_liquidity_btn.click()
    # await page.keyboard.press('Enter')

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

        if TURN_IT_ON == 1: # код сработает
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