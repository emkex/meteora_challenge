import asyncio
from playwright.async_api import async_playwright
from solflare_wallet import get_service_workers, add_solflare_wallet, connect_wallet_meteora
from jupiter_functions import prepare_jupiter, get_token_balances, swap_to_solana_jup, swap_to_jlp_jup
from meteora_functions import open_position_meteora, close_position_meteora, solana_balance, search_pool, \
    get_current_price, max_price_pool, get_position_balance, min_price_pool
from settings import get_latest_extension_path, meteora_website, jup_website, minimum_sol


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='',
            headless=False,
            args=[
                f"--disable-extensions-except={get_latest_extension_path()}",
                f"--load-extension={get_latest_extension_path()}",
            ],
            slow_mo=350
        )

        # Устанавливаем тайм-аут для всего контекста (применимо ко всем страницам)
        context.set_default_timeout(60000)

        # Проверка сервисных воркеров
        background = await get_service_workers(context)

        # Функция для открытия страницы и проверки navigator.webdriver
        async def open_page(url):
            page = await context.new_page()
            await page.goto(url)
            # Проверка значения navigator.webdriver:
            # True -> страница видит, что браузер запускается с помощью ботов;
            # False -> не видит
            is_webdriver = await page.evaluate("navigator.webdriver")
            # print(f'Page at {url}, navigator.webdriver: {is_webdriver}')
            return page

        jup_page = await open_page(jup_website)
        met_page = await open_page(meteora_website)

        titles = [await p.title() for p in context.pages]
        # print(f'Order of pages: {titles}')

        for index, title in enumerate(titles):
            if title == "Solflare":
                solflare_page = context.pages[index]
            elif title == "Home | Meteora":
                met_page = context.pages[index]
            elif title == "Home | Jupiter" or "Swap | Jupiter":
                jup_page = context.pages[index]

        # --------------------------- Add wallet --------------------------------
        await add_solflare_wallet(context, solflare_page)

        # -----------------------  "Connect wallet" -----------------------------
        await connect_wallet_meteora(context, met_page)

        # -------------------------- Pair JLP-USDT -------------------------------
        await search_pool(context, met_page)

        # --------------------------- DEX JUPITER  -------------------------------

        # Estimate SOL balance on meteora
        if await solana_balance(context, met_page) < minimum_sol:

            await prepare_jupiter(context, jup_page)
            token_balances = await get_token_balances(context, jup_page)
            await swap_to_solana_jup(context, jup_page, token_balances)

        await prepare_jupiter(context, jup_page)
        token_balances = await get_token_balances(context, jup_page)
        await swap_to_jlp_jup(context, jup_page, token_balances)

        # ------------------------ Isn't it logic ???  ---------------------------

        await met_page.bring_to_front()
        await met_page.reload()
        await connect_wallet_meteora(context, met_page)

        while True:

            position_balance = await get_position_balance(context, met_page) # first check of position

            price_close_pos = await max_price_pool(context, met_page) # second check of position

            if position_balance == 0:

                if price_close_pos == False:
                    print('\nTUDOOOOoooooo, open position\n')

                    await open_position_meteora(context, met_page)

                elif isinstance(price_close_pos, float):

                    await met_page.reload()
                    await connect_wallet_meteora(context, met_page)

                    if isinstance(max_price_pool(context, met_page), float) and await get_position_balance(context, met_page) == 0: # double-check that there is not closed EMPTY pos
                        print('\nStrange thing, close it (error on the meteora)\n')

                        await close_position_meteora(context, met_page)

                        # During closing position go to DEX Jupiter
                        await prepare_jupiter(context, jup_page)
                        token_balances = await get_token_balances(context, jup_page)
                        await swap_to_solana_jup(context, jup_page, token_balances)
                        await swap_to_jlp_jup(context, jup_page, token_balances)

                        position_balance = await get_position_balance(context, met_page)

                        if position_balance == 0:
                            await open_position_meteora(context, met_page)

            else:

                await met_page.reload()
                await connect_wallet_meteora(context, met_page)

                price_close_pos = await max_price_pool(context, met_page)

                price_close_pos_2 = await min_price_pool(context, met_page)                 # TEST-DRIVE ONLY
                current_price = await get_current_price(context, met_page)                  # TEST-DRIVE ONLY
                while current_price < price_close_pos and current_price > price_close_pos_2: # TEST-DRIVE ONLY
                    await asyncio.sleep(30)                                                 # TEST-DRIVE ONLY
                    print('Pool did not reach the price of max limit to reopen it')         # TEST-DRIVE ONLY
                    current_price = await get_current_price(context, met_page)              # TEST-DRIVE ONLY

                # while await get_current_price(context, met_page) < price_close_pos:         # CLOSE IF TEST-DRIVE
                #     await asyncio.sleep(30)  # make more elegant logic :)                   # CLOSE IF TEST-DRIVE
                #     print('Pool did not reach the price of max limit to reopen it')         # CLOSE IF TEST-DRIVE

                print('\nSUDOOOOoooooo, reopen position\n')

                await close_position_meteora(context, met_page)

                # During closing position go to DEX Jupiter
                await prepare_jupiter(context, jup_page)
                token_balances = await get_token_balances(context, jup_page)
                await swap_to_solana_jup(context, jup_page, token_balances)
                await swap_to_jlp_jup(context, jup_page, token_balances)

                position_balance = await get_position_balance(context, met_page)

                if position_balance == 0:
                    await open_position_meteora(context, met_page)


async def restartable_main():
    while True:
        try:
            await main()
        except Exception as e:
            print(f"Error occurred: {e}. Restart the script...")
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(restartable_main())
