import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from settings_meteora import TURN_IT_ON, jlp_usdt_page


async def close_position_meteora(context: BrowserContext, page: Page):

    await page.bring_to_front()

    current_url = page.url  # смотрю, где я

    titles = [await p.title() for p in context.pages]

    if current_url != jlp_usdt_page:
        for index, title in enumerate(titles):
            if title == "JLP-USDT | Meteora":
                page = context.pages[index]

    bottom_of_page = page.locator('//div[contains(@class, "overflow-x-auto")]')
    # await expect(bottom_of_page).to_be_attached() # DELETE
    your_positions_btn = bottom_of_page.locator('//div/span[text()="Your Positions"]')
    await your_positions_btn.scroll_into_view_if_needed()
    # await expect(your_positions_btn).to_be_visible() # DELETE
    await your_positions_btn.click()
    # print("Open 'Your Positions' stopka")

    my_position_btn = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]')
    await expect(my_position_btn).to_be_enabled()
    await my_position_btn.click()

    withdraw_btn = page.locator('//div[text() = "Withdraw"]') # copy xpath = //*[@id="radix-:r1:"]/div[2]/div[1]/div/div[2]
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