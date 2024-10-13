import asyncio
from playwright.async_api import async_playwright, expect
from solflare_wallet import add_solflare_wallet, connect_wallet
from jupiter_functions import swap_jupiter
from meteora_functions import open_position_meteora, close_position_meteora, search_pool, get_current_price, max_price_pool
from settings import tokens, EXTENTION_PATH, meteora_website, jup_website


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

        # ------------------------  "Connect wallet" -----------------------------
        await connect_wallet(context, met_page)

        # -------------------------- Pair JLP-USDT -------------------------------
        await search_pool(context, met_page)

        # ---------------------- DEX JUPITER OR NOT ???  -------------------------

        # Поиск баланса sol на метеоре
        balance_sol_corner = met_page.locator('//div[@class="ml-2"]').first
        balance_sol_text = await balance_sol_corner.inner_text()
        sol_balance_meteora = float(balance_sol_text.split(' ')[0].replace(',', '.'))

        # Estimate SOL balance on meteora web
        minimum_sol = 0.08

        if sol_balance_meteora < minimum_sol:
            # Go To DEX Jupiter
            await swap_jupiter(context, jup_page)

        # ----------------------------- Isn't it logic ???  ---------------------------------

        await asyncio.sleep(4)
        await met_page.wait_for_load_state(state='domcontentloaded')

        tooltip = met_page.locator('//img[@alt="tip"]')

        if await tooltip.is_visible():
            tip_close = met_page.get_by_role('button').filter(has_text="Agree, let's go").last
            await tip_close.click()
            print('Toolflip was closed')

        change_ratio = met_page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/button')
        await expect(change_ratio).to_be_enabled()
        change_ratio_text = await change_ratio.inner_text()
        ratio_pair = change_ratio_text.split('\n')[1]

        if ratio_pair == 'JLP/USDT':
            await change_ratio.click()  # it must be USDT/JLP
            print('USDT/JLP was choosed')

        current_position_bal = met_page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/div[2]/div[1]/div/span[2]')
        current_position_text = await current_position_bal.inner_text()
        position_balance = float(current_position_text.split(' ')[0])
        print(f'Current position balance (if there is opened one): {position_balance} JLP')

        if position_balance == 0:
            # here must be double check to deny opening if there is pos
            print('TUDOOOOoooooo, open position')
            await open_position_meteora(context, met_page)

        else:
            await met_page.reload()
            await connect_wallet(context, met_page)

            tooltip = met_page.locator('//img[@alt="tip"]')

            if await tooltip.is_visible():
                tip_close = met_page.get_by_role('button').filter(has_text="Agree, let's go").last
                await tip_close.click()
                # print('Toolflip was closed')

            change_ratio = met_page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/button')
            await expect(change_ratio).to_be_enabled()
            change_ratio_text = await change_ratio.inner_text()
            ratio_pair = change_ratio_text.split('\n')[1]

            if ratio_pair == 'JLP/USDT':
                await change_ratio.click() # it must be USDT/JLP

            # here must be double check to deny opening if there is pos
            price_close_pos = await max_price_pool(context, met_page)

            while await get_current_price(context, met_page) < price_close_pos:
                await asyncio.sleep(30) # make more elegant logic :)
                print('Pool did not reach the price of max limit to reopen it')

            # if True: # было if await get_current_price(context, met_page) >= price_close_pos:
            print('SUDOOOOoooooo, reopen position')
            await close_position_meteora(context, met_page)
            await open_position_meteora(context, met_page)

        print('main() отработал')

        await asyncio.sleep(10000)
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())