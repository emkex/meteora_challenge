import asyncio
from playwright.async_api import async_playwright, expect

DEFAULT_DELAY = 300
jlp_adress = '27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4'

async def main():
    async with async_playwright() as p: # init playwright
        browser = await p.chromium.launch(headless=False) # init browser
        context = await browser.new_context() # init session
        page = await context.new_page() # init page
        await page.goto('https://app.meteora.ag/')

        input = page.locator('xpath=//input[contains(@class, "flex-1") and contains(@class, "w-full") and contains(@class, "placeholder:text-sm")]')
        await input.fill(jlp_adress) # or type

        # attempt without long xpath
        locator_pair = page.get_by_text("JLP-USDT")
        try:
            await expect(locator_pair.first).to_be_visible(timeout=10000)
            await locator_pair.first.scroll_into_view_if_needed()
            await locator_pair.first.wait_for_element_state("stable", timeout=5000)
            await expect(locator_pair.first).to_be_visible()
            await locator_pair.first.click()
        except AssertionError as e:
            print("Element not found or not visible:", e)
            found = False
        except Exception as e:
            print(f"Unexpected error: {e}")
            found = False

        if not found:
            print("Refresh page and try again...")
            await page.reload()
            await input.fill(jlp_adress)

            try:
                await page.get_by_text("JLP-USDT", exact=True).first.scroll_into_view_if_needed()
                token_pair = page.locator(
                    '//*[@id="__next"]/div[1]/div[5]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div/div[3]/div[1]')
                await expect(token_pair).to_be_visible()
                await token_pair.click()
            except AssertionError as e:
                print("Element not found or not visible with long xpath:", e)
            except Exception as e:
                print("Unexpected error with long xpath:", e)

        total_liq = await page.locator('xpath=//p[@class="text-black-75 font-semibold text-xsm"]').first.inner_html()
        print(f'Got a total liquidity of pool equaled {total_liq} ')

        await asyncio.sleep(100)
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())