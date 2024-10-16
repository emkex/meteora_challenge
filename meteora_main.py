import asyncio
from playwright.async_api import async_playwright
from solflare_wallet import get_service_workers, add_solflare_wallet, connect_wallet_meteora
from jupiter_functions import prepare_jupiter, get_token_balances, swap_to_solana_jup, swap_to_jlp_jup
from meteora_functions import open_position_meteora, close_position_meteora, solana_balance, search_pool, \
    get_current_price, max_price_pool, get_position_balance
from settings import EXTENTION_PATH, meteora_website, jup_website


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='',
            headless=False,
            args=[
                f"--disable-extensions-except={EXTENTION_PATH}",
                f"--load-extension={EXTENTION_PATH}",
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

        # Estimate SOL balance on meteora web
        minimum_sol = 0.08

        if await solana_balance(context, met_page) < minimum_sol:

            await prepare_jupiter(context, jup_page)
            token_balances = await get_token_balances(context, jup_page)
            await swap_to_solana_jup(context, jup_page, token_balances)

        await prepare_jupiter(context, jup_page)
        token_balances = await get_token_balances(context, jup_page)
        await swap_to_jlp_jup(context, jup_page, token_balances)

        # ------------------------ Isn't it logic ???  ---------------------------

        await met_page.bring_to_front()

        while True:

            position_balance = await get_position_balance(context, met_page)

            if position_balance == 0:
                print('\nTUDOOOOoooooo, open position\n')
                await open_position_meteora(context, met_page)

            else:

                await met_page.reload()
                await connect_wallet_meteora(context, met_page)

                price_close_pos = await max_price_pool(context, met_page)

                while await get_current_price(context, met_page) < price_close_pos:
                    await asyncio.sleep(30)  # make more elegant logic :)
                    print('Pool did not reach the price of max limit to reopen it')

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

        # print('main() отработал')
        # await asyncio.sleep(10000)
        # await context.close()


async def restartable_main():
    while True:
        try:
            await main()
        except Exception as e:
            print(f"Error occurred: {e}. Restart the script...")
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(restartable_main())
