import asyncio
from playwright.async_api import async_playwright, expect, BrowserContext, Page
from private_wal import SOL_PASSWORD, seedka


async def add_solflare_wallet(context: BrowserContext, page: Page):
    
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
    
    # await page.wait_for_load_state(state='domcontentloaded')
    # balance0 = page.locator('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/h2/button')
    # await expect(balance0).to_be_visible()
    # why_zero = await balance0.inner_text()
    # print(f"Your balance: {why_zero}")