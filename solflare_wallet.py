import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from private_wal import SOL_PASSWORD, seedka


async def add_solflare_wallet(context: BrowserContext, page: Page) -> None:
    
    await page.bring_to_front()

    i_have_wal_btn = page.locator('//button[@data-id="i_already_have_wallet_button"]')
    await expect(i_have_wal_btn).to_be_visible()
    await i_have_wal_btn.click()
    
    counter = 0
    for _ in seedka:
        element = page.locator(f'//input[@id="mnemonic-input-{counter}"]')
        await element.fill(seedka[counter])
        counter += 1
    
    continue_btn_last = page.get_by_role('button').last
    await expect(continue_btn_last).to_be_enabled()
    await continue_btn_last.click()
    # print("Вставляю сид-фразу в пропуски пословно и перехожу дальше")
    
    create_password_input = page.locator('//*[@id=":r1:"]')
    await expect(create_password_input).to_be_attached()
    await create_password_input.fill(SOL_PASSWORD)
    
    create_password_input_second = page.locator('//*[@id=":r2:"]')
    await create_password_input_second.fill(SOL_PASSWORD)
    # print("Пароль вставился оба раза")
    
    wal_continue_btn = page.locator('//*[@id="root"]/div/div[2]/div/div[2]/form/div[2]/button[2]')
    await expect(wal_continue_btn).to_be_enabled()
    await wal_continue_btn.click()
    # print("Продолжаем, далее")
    
    wal_continue_btn2 = page.get_by_role('button').nth(4)
    await expect(wal_continue_btn2).to_be_enabled(timeout=60000)
    await wal_continue_btn2.click()
    # print('Import all')
    
    # create_wal_continue_btn = page.locator('//button[@class="_1a406992 _1a406993 _1a406998 _16aew8t0 _16aew8ta _16aew8ti _16aew8tq _9rd95r0 _1a406990 _1a406991 btn-primary"]')
    create_wal_continue_btn = page.locator('//*[@id="root"]/div/div[1]/div[2]/div[2]/button')
    await expect(create_wal_continue_btn).to_be_enabled()
    await create_wal_continue_btn.click()
    # print("Продолжаем дальше...")
    
    show_sol_btn = page.get_by_role('button').last
    await expect(show_sol_btn).to_be_enabled()
    await show_sol_btn.click()

    print('Кошелек импортирован в браузер')
    
    # await page.wait_for_load_state(state='domcontentloaded')
    # balance0 = page.locator('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/h2/button')
    # await expect(balance0).to_be_visible()
    # why_zero = await balance0.inner_text()
    # print(f"Your balance: {why_zero}")


async def connect_wallet(context: BrowserContext, page: Page) -> None:

    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    connect_wal_btn = page.get_by_role('button').filter(has_text="Connect").first
    await connect_wal_btn.click()
    # print(f'Пробую приконнектить кошель, нажимаю "Connect wallet"')

    solflare_choose = page.get_by_role('button').filter(has_text="Solflare")
    await expect(solflare_choose).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await solflare_choose.click()
    # print('Выбираю коннектить Solflare')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await asyncio.sleep(3)
    await new_window.wait_for_load_state(state='domcontentloaded')

    solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[3]/div/button[2]')
    await expect(solflare_turn_on).to_be_enabled()
    await solflare_turn_on.click(click_count=2)
    print(f'Кошелек привязан к сайту {page}')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')


async def connect_wallet_jup(context: BrowserContext, page: Page) -> None:

    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    connect_wal_btn = page.get_by_role('button').filter(has_text="Connect").first
    await connect_wal_btn.click()
    # print(f'Пробую приконнектить кошель, нажимаю "Connect wallet"')

    solflare_choose = page.locator('//img[@alt="Solflare icon"]')
    await expect(solflare_choose).to_be_enabled()

    # ожидаю открытие нового окна
    wait_page = context.wait_for_event("page")

    await solflare_choose.click()
    # print('Выбираю коннектить Solflare')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление нового окна
    new_window = await wait_page
    await new_window.bring_to_front()
    await asyncio.sleep(3)
    await new_window.wait_for_load_state(state='domcontentloaded')

    solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[3]/div/button[2]')
    await expect(solflare_turn_on).to_be_enabled()
    await solflare_turn_on.click(click_count=2)
    print(f'Кошелек привязан к сайту {page}')

    # -------------------- Переключение на соседнее окно -----------------------------

    # Отслеживаю появление "старого" окна
    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')