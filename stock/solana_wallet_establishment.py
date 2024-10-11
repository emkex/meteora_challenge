import asyncio
import os
import shutil
from playwright.async_api import async_playwright, expect


EXTENTION_PATH = r'C:/Users/Asus/AppData/Local/Google/Chrome/User Data/Default/Extensions/bhhhlbepdkbapadjdnnojkbgioiodbic/1.71.0_0/' # path to the manifest
SOL_PASSWORD = 'YALEGENDA12345'
user_data_dir = r"C:/Users/Asus/AppData/Local/Google/Chrome/User Data/PlaywrightProfile"

def clear_user_data():
    if os.path.exists(user_data_dir):
        try:
            shutil.rmtree(user_data_dir)  # Удаляем папку с данными
            print("Папка с данными пользователя успешно удалена.")
        except Exception as e:
            print(f"Не удалось удалить папку с данными: {e}")

# identificator for solflare: bhhhlbepdkbapadjdnnojkbgioiodbic (found through Win + X -> powershell -> Get-ChildItem -Path "$env:LOCALAPPDATA/Google/Chrome/User Data" -Recurse -Filter "bhhhlbepdkbapadjdnnojkbgioiodbic" | Select-Object FullName)

async def main():
    clear_user_data()
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                f"--disable-extensions-except={EXTENTION_PATH}",
                f"--load-extension={EXTENTION_PATH}",
            ],
            slow_mo = 200
        )

        # Проверяю, есть ли загруженные воркеры
        background = None
        if len(context.service_workers) == 0:
            background = await context.wait_for_event('serviceworker', timeout=60000)
            print("Service worker загружен")
        else:
            background = context.service_workers[0]
            print("Service worker загружен")

        # # Пытаемся получить ID расширения, если background загружен
        # if background:
        #     extension_id = background.url.split("/")[2]
        # else:
        #     extension_id = "bhhhlbepdkbapadjdnnojkbgioiodbic"
        # print(f"ID расширения: {extension_id}")
        #
        # # # Открываю страницу SolFlare
        # # solflare_url = f"chrome-extension://{extension_id}/wallet.html"
        # # print(f"Открытие SolFlare по адресу: {solflare_url}")
        # # sol_page = await context.new_page()
        # # await sol_page.goto(solflare_url)
        # #
        # # await sol_page.wait_for_load_state()
        # # print("SolFlare страница загружена")

        titles = [await p.title() for p in context.pages]
        while 'Solflare' not in titles:
            titles = [await p.title() for p in context.pages]

        # await context.close()

        sol_page = context.pages[1]
        await sol_page.wait_for_load_state()

        # -------------------- создать новый кошелек --------------------

        create_new_btn = sol_page.locator('//button[@data-id="i_need_a_wallet_button"]')
        await expect(create_new_btn).to_be_enabled()
        await create_new_btn.click()
        print("Создаю новый кошель")

        # -------------------- копирую сидку -----------------------------

        seed = []
        for i in range(12):
            seed.append(await sol_page.locator('//p[@class="MuiTypography-root MuiTypography-body1 jssSolrise19 css-1362g6f"]').and_(sol_page.locator((f'//p[@data-index="{i+1}"]'))).inner_text())

        print(f'My seed phrase: {seed}')

        # -------------------- подтверждаю сохранение сидки -------------

        confirm_seed_btn = sol_page.locator('//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary css-j38ge0"]')
        await expect(confirm_seed_btn).to_be_enabled()
        await confirm_seed_btn.click()
        print("Подтвердил её сохранение")

        # -------------------- вставляю сидку --------------------

        # await asyncio.sleep(10000)

        counter = 0
        for i in seed:
            element = sol_page.locator(f'//input[@id="mnemonic-input-{counter}"]')
            await element.fill(seed[counter])
            counter += 1
        print("Проверил сидку - вставляется в пропуски пословно")

        # -------------------- нажимаю "продолжить" --------------------

        continue_btn = sol_page.locator('//button[@data-id="continue_button"]')
        await expect(continue_btn).to_be_enabled()
        await continue_btn.click()
        print("Продолжаем...")

        # -------------------- Создаю новый пароль для кошеля ----------

        create_password_input = sol_page.locator('//*[@id=":r1:"]')
        await expect(create_password_input).to_be_attached()
        await create_password_input.fill(SOL_PASSWORD)

        create_password_input_second = sol_page.locator('//*[@id=":r2:"]')
        await create_password_input_second.fill(SOL_PASSWORD)
        print("Пароль вставился оба раза")

        create_wal_continue_btn = sol_page.locator('//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary css-j38ge0"]')
        await expect(create_wal_continue_btn).to_be_enabled()
        await create_wal_continue_btn.click()
        print("Продолжаем ещё...")

        # await asyncio.sleep(10000)
        please_create_wal_continue_btn = sol_page.locator('//button[@class="_1a406992 _1a406993 _1a406998 _16aew8t0 _16aew8ta _16aew8ti _16aew8tq _9rd95r0 _1a406990 _1a406991 btn-primary"]')
        await expect(please_create_wal_continue_btn).to_be_enabled()
        await please_create_wal_continue_btn.click()
        print("Продолжаем дальше...")

        # await asyncio.sleep(10000)
        show_sol_btn = sol_page.locator('//button[@class="_1a406992 _1a406993 _1a406998 _16aew8t0 _16aew8ta _16aew8ti _16aew8tq _9rd95r0 _1a406990 _1a406991 btn-primary"]')
        await expect(show_sol_btn).to_be_enabled()
        await show_sol_btn.click()

        # await asyncio.sleep(10000)
        balance0 = sol_page.locator('//button[@class="css-eo255b"]')
        await expect(balance0).to_be_visible()
        why_zero = await balance0.inner_text()
        print(f"Your balance: {why_zero}")

        # -------------------- закрыть страничку --------------------
        await sol_page.close()

        await asyncio.sleep(50)

if __name__ == '__main__':
    asyncio.run(main())