# # --------------------------- BALANCES (SOLSCAN) --------------------------------
#
# # Добавляю solscan
# solscan_page = await context.new_page()
# await solscan_page.goto(solscan_wallet_website)
# await solscan_page.wait_for_load_state(state='domcontentloaded')
#
# sol_balance_text = solscan_page.locator('//*[@id="__next"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]')
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
# find_tokens_btn = solscan_page.locator('//div[@type="button"]').and_(solscan_page.locator('//div[@id="radix-:rn:"]'))
# await expect(find_tokens_btn).to_be_enabled(timeout=15000)
# await find_tokens_btn.click()
#
# await solscan_page.keyboard.insert_text(tokens['JLP']['token_contract'])
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
# await solscan_page.keyboard.insert_text(tokens['USDT']['token_contract'])
# usdt_balance_text = solscan_page.locator('//*[@id="radix-:ro:"]/div[2]/div/div/a/div[2]/div[1]')
# await expect(usdt_balance_text).to_be_visible()
# usdt_balance = await usdt_balance_text.inner_text()
#
# usdt_balance = float(usdt_balance.replace(' USDT', ''))
# print(f"Your USDT balance (from solscan web): {usdt_balance} USDT\n")
#
# await solscan_page.close()

# # --------------------------- Поиск баланса sol на юпитере --------------------------------

# await page.keyboard.press('Control+A')
# await page.keyboard.press('Backspace')
#
# await page.keyboard.insert_text(tokens['SOL']['token_contract'])
#
# token_sell_ready = page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/p') # copy xpath = //*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/p
# await expect(token_sell_ready).to_be_visible() # token_sell_ready = page.locator('//li').locator('//img[@alt="SOL"]').locator('//p')
# balance_sol_text = await token_sell_ready.inner_text()
# sol_balance_jupiter = float(balance_sol_text.replace('$', '').replace(',', '.'))
# print(f"\nYour SOL balance (from jupiter dex) in $: {sol_balance_jupiter} $")
#
# # Поиск баланса usdt на юпитере
# await page.keyboard.press('Control+A')
# await page.keyboard.press('Backspace')
#
# await page.keyboard.insert_text(tokens['USDT']['token_contract'])
#
# token_sell_ready = page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/p') # copy xpath = //*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/p
# await expect(token_sell_ready).to_be_visible()
# balance_usdt_text = await token_sell_ready.inner_text()
# usdt_balance_jupiter = float(balance_usdt_text.replace('$', '').replace(',', '.'))
# print(f"Your USDT balance (from jupiter dex) in $: {usdt_balance_jupiter} $")
#
# # Поиск баланса jlp на юпитере
# await page.keyboard.press('Control+A')
# await page.keyboard.press('Backspace')
#
# await page.keyboard.insert_text(tokens['JLP']['token_contract'])
#
# token_sell_ready = page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/p') # copy xpath = //*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[3]/p
# await expect(token_sell_ready).to_be_visible()
# balance_jlp_text = await token_sell_ready.inner_text()
# jlp_balance_jupiter = float(balance_jlp_text.replace('$', '').replace(',', '.'))
# print(f"Your JLP balance (from jupiter dex) in $: {jlp_balance_jupiter} $\n")




# tooltip = met_page.locator('//div[contains(@class, "popover-tooltip")]')
# if await tooltip.is_visible():
#     await tooltip.get_by_role('button')
#     await tooltip.click()
#     # print('Toolflip was closed')
# else:
#     print("Toolflip was not here")


# # HERE i'm going to check that i open only 1 pos!
# one_position_check = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[3]/div[2]/div/div[4]/div[1]/div[1]')
# await expect(one_position_check).to_be_attached()
# one_position_text = await one_position_check.inner_text()
# one_position_value = float(one_position_text.split('\n')[1].split(' ')[0])
#
# if one_position_value < 0.06:
#     pass
# else:
#     await asyncio.sleep(10000)


# dc_jlp_img = met_page.locator('//img[@alt="JLP"]').first
# dc_usdt_img = met_page.locator('//img[@alt="USDT"]').first
#
# if await dc_jlp_img.is_visible() and await dc_usdt_img.is_visible():
#     pass # print("Double-check that it's indeed JLP-USDT pair")
# else:
#     print('Double-check for jlp-usdt was fucked up')
#     await asyncio.sleep(100000)