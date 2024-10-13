import asyncio
from playwright.async_api import async_playwright
from solflare_wallet import add_solflare_wallet, connect_wallet
from jupiter_functions import prepare_jupiter, get_token_balances, swap_to_solana_jup, swap_to_jlp_jup
from meteora_functions import open_position_meteora, close_position_meteora, solana_balance, search_pool, \
    get_current_price, max_price_pool, tooltip_and_ratio
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

        # -----------------------  "Connect wallet" -----------------------------
        await connect_wallet(context, met_page)

        # -------------------------- Pair JLP-USDT -------------------------------
        await search_pool(context, met_page)

        # --------------------------- DEX JUPITER  -------------------------------

        # Estimate SOL balance on meteora web
        minimum_sol = 0.08

        if await solana_balance(context, met_page) < minimum_sol:
            # Go To DEX Jupiter
            await prepare_jupiter(context, jup_page)
            token_balances = await get_token_balances(context, jup_page)
            await swap_to_solana_jup(context, jup_page, token_balances)

        await prepare_jupiter(context, jup_page)
        token_balances = await get_token_balances(context, jup_page)
        await swap_to_jlp_jup(context, jup_page, token_balances)

        # ------------------------ Isn't it logic ???  ---------------------------

        await met_page.bring_to_front()

        while True:

            await asyncio.sleep(4)
            await met_page.wait_for_load_state(state='domcontentloaded')

            position_balance = await tooltip_and_ratio(context, met_page)

            if position_balance == 0:
                # here must be double check to deny opening if there is pos
                print('\nTUDOOOOoooooo, open position\n')
                await open_position_meteora(context, met_page)

            else:

                await met_page.reload()
                await connect_wallet(context, met_page)

                await asyncio.sleep(4)
                await met_page.wait_for_load_state(state='domcontentloaded')

                # here must be double check to deny opening if there is pos
                price_close_pos = await max_price_pool(context, met_page)

                while await get_current_price(context, met_page) < price_close_pos:
                    await asyncio.sleep(20)  # make more elegant logic :)
                    print('Pool did not reach the price of max limit to reopen it')

                print('\nSUDOOOOoooooo, reopen position\n')

                await close_position_meteora(context, met_page)

                # During closing position go to DEX Jupiter
                await prepare_jupiter(context, jup_page)
                token_balances = await get_token_balances(context, jup_page)
                await swap_to_jlp_jup(context, jup_page, token_balances)

                await met_page.bring_to_front()
                await asyncio.sleep(4)
                await met_page.wait_for_load_state(state='domcontentloaded')

                position_balance = await tooltip_and_ratio(context, met_page)

                if position_balance == 0:
                    # here must be double check to deny opening if there is pos
                    await open_position_meteora(context, met_page)

        # print('main() отработал')
        #
        # await asyncio.sleep(10000)
        # await context.close()


if __name__ == '__main__':
    asyncio.run(main())
