import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from private_wal import SOL_PASSWORD, seedka
from settings import TURN_IT_ON


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

    return None
# ready

async def connect_wallet(context: BrowserContext, page: Page) -> bool:

    await asyncio.sleep(3)
    all_pages = context.pages
    new_window = all_pages[-1]  # Последняя страница
    await new_window.bring_to_front()
    await new_window.reload()
    await new_window.wait_for_load_state(state='domcontentloaded')

    solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[3]/div/button[2]')

    try:
        await expect(solflare_turn_on).to_be_enabled()
        if TURN_IT_ON == 1:  # код сработает
            await solflare_turn_on.click(click_count=2)
            print(f'Кошелек привязан к сайту {page}')

            # Отслеживаю появление "старого" окна
            await page.bring_to_front()
            await asyncio.sleep(3)
            await page.wait_for_load_state(state='domcontentloaded')

            return True

        else:
            print('FREEZE')
            await asyncio.sleep(100000)

    except AssertionError:
        print(f'Кнопка была не доступна. Кошелек не подключен')
        # Отслеживаю появление "старого" окна
        # if not new_window.is_closed() and new_window != page:
        #     await new_window.close()
        await page.bring_to_front()
        await asyncio.sleep(5)

        return False

    except TimeoutError:
        print(f'Кнопка была не доступна. Кошелек не подключен')
        # Отслеживаю появление "старого" окна
        # if not new_window.is_closed() and new_window != page:
        #     await new_window.close()
        await page.bring_to_front()
        await asyncio.sleep(5)

        return False
# ready

async def connect_wallet_meteora(context: BrowserContext, page: Page) -> None:

    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    connect_wal_btn = page.get_by_role('button').filter(has_text="Connect Wallet").first

    # if await connect_wal_btn.is_visible():
    await connect_wal_btn.click(click_count=2)
    # print(f'Пробую приконнектить кошель, нажимаю "Connect wallet"')

    solflare_choose = page.get_by_role('button').filter(has_text="Solflare")
    await expect(solflare_choose).to_be_enabled()

    await solflare_choose.click()
    # print('Выбираю коннектить Solflare')

    while not await connect_wallet(context, page):
        print('Retry in 20 sec')
        await asyncio.sleep(20)
        connecting_btn = page.get_by_role('button').filter(has_text="Connecting").first
        if await connecting_btn.is_visible():
            await connecting_btn.click(click_count=2)
            await solflare_choose.click()
        else:
            await connect_wal_btn.click(click_count=2)
            await solflare_choose.click()

    return None
# ready

async def connect_wallet_jup(context: BrowserContext, page: Page) -> None:

    await page.bring_to_front()
    await page.wait_for_load_state(state='domcontentloaded')

    connect_wal_btn = page.get_by_role('button').filter(has_text="Connect Wallet").first
    await connect_wal_btn.click(click_count=2)
    # print(f'Пробую приконнектить кошель, нажимаю "Connect wallet"')

    solflare_choose = page.locator('span:has-text("Solflare")').first # '//img[@alt="Solflare icon"]'
    await expect(solflare_choose).to_be_enabled()

    await solflare_choose.click(click_count=2)
    # print('Выбираю коннектить Solflare')

    while not await connect_wallet(context, page):
        print('Retry in 20 sec')
        await asyncio.sleep(20)
        connecting_btn = page.get_by_role('button').filter(has_text="Connecting").first
        if await connecting_btn.is_visible():
            await connecting_btn.click(click_count=2)
            await solflare_choose.click()
        else:
            await connect_wal_btn.click(click_count=2)
            await solflare_choose.click()

    return None
# ready

async def confirm_transaction(context: BrowserContext, page: Page) -> bool:

    await asyncio.sleep(3)
    all_pages = context.pages
    new_window = all_pages[-1]  # Последняя страница
    await new_window.bring_to_front()
    await new_window.reload()
    await new_window.wait_for_load_state(state='domcontentloaded')

    solflare_approve = new_window.locator('button:has-text("Утвердить")')

    try:
        await expect(solflare_approve).to_be_enabled()
        if TURN_IT_ON == 1:
            await solflare_approve.click(click_count=2)
            print('Подтверждаю и... ОДОБРЯЮ транзакцию!')

            return True

        else:
            print('FREEZE')
            await asyncio.sleep(100000)

    except AssertionError:
        print(f'Транзакция отклонена. Причина: кнопка была не доступна ')
        # Отслеживаю появление "старого" окна
        # if not new_window.is_closed() and new_window != page:
        #     await new_window.close()
        await page.bring_to_front()
        await asyncio.sleep(5)

        return False

    except TimeoutError:
        print(f'Транзакция отклонена. Причина: кнопка была не доступна ')
        # Отслеживаю появление "старого" окна
        # if not new_window.is_closed() and new_window != page:
        #     await new_window.close()
        await page.bring_to_front()
        await asyncio.sleep(5)

        return False
# ready

async def get_service_workers(context) -> None:
    if len(context.service_workers) == 0:
        return await context.wait_for_event('serviceworker', timeout=60000)
    return context.service_workers[0]
# ready