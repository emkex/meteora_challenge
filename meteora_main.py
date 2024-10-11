import asyncio
from playwright.async_api import async_playwright, expect
from solflare_wallet import add_solflare_wallet
from meteora_functions import open_position_meteora, close_position_meteora, sell_buy_jupiter
from meteora_settings import tokens, EXTENTION_PATH, meteora_website, jup_website


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='',
            headless=False,
            args=[
                f"--disable-extensions-except={EXTENTION_PATH}",
                f"--load-extension={EXTENTION_PATH}",
            ],
            # slow_mo=1000
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

        # Добавляю метеору
        page = await context.new_page()
        await page.goto(meteora_website)

        titles = [await p.title() for p in context.pages]

        print(f'Order of pages: {titles}')

        for index, title in enumerate(titles):
            if title == "Solflare":
                solflare_page = context.pages[index]
            elif title == "Home | Meteora":
                met_page = context.pages[index]
            elif title == "Home | Jupiter" or "Swap | Jupiter":
                jup_page = context.pages[index]

        # --------------------------- Add wallet --------------------------------

        await add_solflare_wallet(context, solflare_page)
        print('Кошелек подключен')

        # ------------------------  "Connect wallet" -----------------------------

        await met_page.bring_to_front()
        await met_page.wait_for_load_state(state='domcontentloaded')

        connect_wal_btn = met_page.get_by_role('button').filter(has_text="Connect").first
        await connect_wal_btn.click()
        # print('Пробую приконнектить кошель, нажимаю "Connect wallet"')

        solflare_choose = met_page.get_by_role('button').filter(has_text="Solflare")
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
        print('Кошелек привязан к сайту')

        # ------------------------------- ИЩУ ПАРУ JLP-USDT --------------------------------

        # Отслеживаю появление "старого" окна
        await met_page.bring_to_front()
        await met_page.wait_for_load_state(state='domcontentloaded')

        input_search_token = met_page.locator('//input[@class="flex-1 w-full placeholder:text-sm"]')
        await input_search_token.fill(tokens['JLP']['token_contract']) # Change to jlp-usdt
        # print('Вставил в поиск контракт токена')
        await met_page.keyboard.press("Enter")

        await met_page.wait_for_load_state(state='domcontentloaded')

        scroll_to_pair = met_page.locator('//img[@alt="USDT"]/ancestor::div[contains(@class, "flex")]/following-sibling::div/p[contains(text(), "JLP-USDT")]')
        await expect(scroll_to_pair.first).to_be_visible()
        await scroll_to_pair.scroll_into_view_if_needed()
        await scroll_to_pair.click()
        # print('Отыскал пару JLP-USDT')

        needed_pair = met_page.locator('//a[@href="/dlmm/C1e2EkjmKBqx8LPYr2Moyjyvba4Kxkrkrcy5KuTEYKRH"]')
        await needed_pair.click()
        print('Перешел во вкладку к паре JLP-USDT')

        await met_page.wait_for_load_state(state='domcontentloaded')

        # Поиск баланса sol на метеоре
        balance_sol_corner = met_page.locator('//div[@class="ml-2"]').first
        balance_sol_text = await balance_sol_corner.inner_text()
        sol_balance_meteora = float(balance_sol_text.split(' ')[0].replace(',', '.'))

        # -------------------------- DEX JUPITER OR NOT ???  ---------------------------

        # Estimate SOL balance on meteora web
        minimum_sol = 0.08

        if sol_balance_meteora < minimum_sol:
            # Go To DEX Jupiter
            await sell_buy_jupiter(context, jup_page)

        # ----------------------------- Isn't it logic ???  ---------------------------------

        # Нижнюю часть (opened_position - if-else) можно зациклить (после добавления foo_price_check())

        # Проверка наличия открытой позиции
        opened_position = met_page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]')

        if await opened_position.count() > 0:
            # if await foo_price_check():  # # HERE must be logic regarding price 95% max in pool
                print('SUDO')
                await close_position_meteora(context, met_page)
                await open_position_meteora(context, met_page)
        else:
            print('TUDO') # Если открытая позиция не найдена - открой
            await open_position_meteora(context, met_page)

        print('main() отработал')
        await asyncio.sleep(100000)

        await context.close()

if __name__ == '__main__':
    asyncio.run(main())