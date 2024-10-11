import asyncio
from playwright.async_api import async_playwright, expect
from private_wal import seedka, SOL_PASSWORD, wallet_test
import settings_meteora

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir = '',
            headless=False,
            args=[
                f"--disable-extensions-except={EXTENTION_PATH}",
                f"--load-extension={EXTENTION_PATH}",
            ],
            # slow_mo = 400
        )

        # Проверяю, есть ли загруженные воркеры для солана-кошелька
        background = None
        if len(context.service_workers) == 0:
            background = await context.wait_for_event('serviceworker', timeout=60000)
        else:
            background = context.service_workers[0]

        # Добавляю JUPITER
        page = await context.new_page()
        await page.goto(jup_website)

        titles = [await p.title() for p in context.pages]

        print(f'Order of pages: {titles}')

        for index, title in enumerate(titles):
            if title == "Solflare":
                sol_page = context.pages[index]
            elif title == "Home | Jupiter" or "Swap | Jupiter":
                jup_page = context.pages[index]

        # --------------------------- Add wallet --------------------------------

        await sol_page.bring_to_front()
        i_have_wal_btn = sol_page.locator('//button[@data-id="i_already_have_wallet_button"]')
        await expect(i_have_wal_btn).to_be_visible()
        await i_have_wal_btn.click()

        counter = 0
        for i in seedka:
            element = sol_page.locator(f'//input[@id="mnemonic-input-{counter}"]')
            await element.fill(seedka[counter])
            counter += 1

        continue_btn_last = sol_page.get_by_role('button').last
        await expect(continue_btn_last).to_be_enabled()
        await continue_btn_last.click()

        print("Вставляю сид-фразу в пропуски пословно и перехожу дальше")

        create_password_input = sol_page.locator('//*[@id=":r1:"]')
        await expect(create_password_input).to_be_attached()
        await create_password_input.fill(SOL_PASSWORD)

        create_password_input_second = sol_page.locator('//*[@id=":r2:"]')
        await create_password_input_second.fill(SOL_PASSWORD)
        print("Пароль вставился оба раза")

        wal_continue_btn = sol_page.locator('//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary css-j38ge0"]')
        await expect(wal_continue_btn).to_be_enabled()
        await wal_continue_btn.click()
        print("Продолжаем, далее")

        wal_continue_btn2 = sol_page.get_by_role('button').nth(4)
        await expect(wal_continue_btn2).to_be_enabled(timeout=10000)
        await wal_continue_btn2.click()
        print('Import all')

        # please_create_wal_continue_btn = sol_page.locator('//button[@class="_1a406992 _1a406993 _1a406998 _16aew8t0 _16aew8ta _16aew8ti _16aew8tq _9rd95r0 _1a406990 _1a406991 btn-primary"]')
        please_create_wal_continue_btn = sol_page.locator('//*[@id="root"]/div/div[1]/div[2]/div[2]/button')
        await expect(please_create_wal_continue_btn).to_be_enabled()
        await please_create_wal_continue_btn.click()
        print("Продолжаем дальше...")

        show_sol_btn = sol_page.get_by_role('button').last
        await expect(show_sol_btn).to_be_enabled()
        await show_sol_btn.click()

        await sol_page.wait_for_load_state(state='domcontentloaded')

        balance0 = sol_page.locator('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/h2/button')
        await expect(balance0).to_be_visible()
        why_zero = await balance0.inner_text()
        print(f"Your balance: {why_zero}")

        # # --------------------------- BALANCES (SOLSCAN) --------------------------------
        #
        # # Добавляю solscan
        # solscan_page = await context.new_page()
        # await solscan_page.goto(solscan_wallet_website)
        # await solscan_page.wait_for_load_state(state='domcontentloaded')
        #
        # sol_balance_text = solscan_page.locator(
        #     '//*[@id="__next"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]')
        # await expect(sol_balance_text).to_be_visible()
        # sol_balance = await sol_balance_text.inner_text()
        # sol_balance = float(sol_balance.replace(' SOL', ''))
        #
        # minimum_sol = 0.08
        # if sol_balance <= minimum_sol:
        #     print(f"\nYour SOLANA balance: {sol_balance} SOL, ADD MORE SOL!")
        # else:
        #     print(f"\nYour SOLANA balance: {sol_balance} SOL, it's enough")
        #
        # find_tokens_btn = solscan_page.locator('//div[@type="button"]').and_(
        #     solscan_page.locator('//div[@id="radix-:rn:"]'))
        # await expect(find_tokens_btn).to_be_enabled(timeout=15000)
        # await find_tokens_btn.click()
        #
        # await solscan_page.keyboard.insert_text(jlp_adress)
        # jlp_balance_text = solscan_page.locator('//*[@id="radix-:ro:"]/div[2]/div/div/a/div[2]/div[1]')
        # await expect(jlp_balance_text).to_be_visible()
        # jlp_balance = await jlp_balance_text.inner_text()
        #
        # await solscan_page.keyboard.press('Control+A')
        # await solscan_page.keyboard.press('Backspace')
        #
        # jlp_balance = float(jlp_balance.replace(' JLP', ''))
        # print(f"Your Jupiter Perps LP balance (from solscan web): {jlp_balance} JLP")
        #
        # await solscan_page.keyboard.insert_text(usdt_adress)
        # usdt_balance_text = solscan_page.locator('//*[@id="radix-:ro:"]/div[2]/div/div/a/div[2]/div[1]')
        # await expect(usdt_balance_text).to_be_visible()
        # usdt_balance = await usdt_balance_text.inner_text()
        #
        # usdt_balance = float(usdt_balance.replace(' USDT', ''))
        # print(f"Your USDT balance (from solscan web): {usdt_balance} USDT\n")
        #
        # await solscan_page.close()

        # # --------------------------- ХОТЕЛ ПАРСЕРНУТЬ SOLFLARE, НЕ СТАЛ  ----------------------------

        # pars_table_balances = sol_page.get_by_test_id('virtuoso-item-list')
        # tokens = pars_table_balances.locator('tr')
        # print(tokens)

        # counter = await tokens.count()
        #
        # for i in range(counter):
        #     row = tokens.nth(i)
        #     first_td = await row.locator('td').first.inner_text()
        #     last_td = await row.locator('td').nth(4).inner_text()
        #     print(f'Token {i + 1}: First Token = {first_td}, Last TD = {last_td}')

        # -------------------- find "Connect wallet" -----------------------------

        await jup_page.bring_to_front()
        await jup_page.wait_for_load_state(state='domcontentloaded')

        connect_wal_btn = jup_page.get_by_role('button').filter(has_text="Connect").first
        await expect(connect_wal_btn).to_be_attached()
        await connect_wal_btn.click()
        print(f'Пробую приконнектить кошель на Jupiter DEX, нажимаю "Connect wallet"')

        solflare_choose = jup_page.locator('//img[@alt="Solflare icon"]') #/ancestor::button[contains(@class, "css-11b5aec")]'
        await expect(solflare_choose).to_be_enabled()

        # ожидаю открытие нового окна
        waiting = context.wait_for_event("page")

        await solflare_choose.click()
        print('Выбираю коннектить Solflare')

        # -------------------- Переключение на соседнее окно -----------------------------

        # Отслеживаю появление нового окна
        new_window = await waiting
        await new_window.bring_to_front()
        await new_window.wait_for_load_state(state='networkidle', timeout=20000)

        solflare_turn_on = new_window.locator('//body/div[2]/div[2]/div/div[3]/div/button[2]')
        await expect(solflare_turn_on).to_be_enabled()
        await solflare_turn_on.click()
        print('Подтверждаю и... приконнекчено!')

        # -------------------- Переключение на соседнее окно -----------------------------

        await asyncio.sleep(1000000)
        # Отслеживаю появление "старого" окна
        await jup_page.bring_to_front()
        await jup_page.wait_for_load_state(state='domcontentloaded')

        swap_choose = jup_page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/a[1]')
        await expect(swap_choose).to_be_visible()
        swap_text = await swap_choose.inner_text()

        if swap_text == 'Swap':
            await swap_choose.click()
            print("Push on mode 'SWAP' even if it's pushed")

        token_to_sell = jup_page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[2]/div/button')
        await expect(token_to_sell).to_be_enabled()
        await token_to_sell.click()

        await jup_page.keyboard.insert_text(usdt_adress)
        await jup_page.keyboard.press('Enter')

        token_sell_ready = jup_page.locator('//li').locator('//img[@alt="USDT"]')
        await expect(token_sell_ready).to_be_enabled()
        await token_sell_ready.click()
        print('Token for selling')

        token_to_buy = jup_page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[2]/div/button')
        await expect(token_to_buy).to_be_enabled()
        await token_to_buy.click()

        await jup_page.keyboard.insert_text(jlp_adress)
        await jup_page.keyboard.press('Enter')

        token_buy_ready = jup_page.locator('//li').locator('//img[@alt="JLP"]')
        await expect(token_buy_ready).to_be_enabled()
        await token_buy_ready.click()
        print('Token for buying')

        usdt_filled = 0 # for test it was 5$
        await asyncio.sleep(1000000)

        # тут надо будет добавить поиск балансов и тд

        amount_of_token_to_sell = jup_page.get_by_placeholder('0.00').first
        await expect(amount_of_token_to_sell).to_be_enabled()
        await amount_of_token_to_sell.click()
        await amount_of_token_to_sell.fill(str(usdt_filled))

        swap_btn = jup_page.locator('//button[@type="submit"]').filter(has_text='Swap')
        await expect(swap_btn).to_be_enabled(timeout=10000)

        # ожидаю открытие нового окна
        waiting = context.wait_for_event("page")

        await swap_btn.click()

        print('Ready for "SWAPchik"')
        # -------------------- Переключение на соседнее окно -----------------------------

        # Отслеживаю появление нового окна
        new_window = await waiting
        await new_window.bring_to_front()
        await new_window.wait_for_load_state(state='networkidle', timeout=20000)

        try:
            solflare_turn_on = new_window.get_by_role('button').last
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
        await sol_page.bring_to_front()
        await sol_page.wait_for_load_state(state='domcontentloaded')

        await asyncio.sleep(100000)

        await context.close()

if __name__ == '__main__':
    asyncio.run(main())