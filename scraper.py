import asyncio
from playwright.async_api import async_playwright

# crawlers
semaphore = asyncio.Semaphore(5)
async def crawler(context, page_num, semaphore): # returns links
    page = await context.new_page()
    await page.goto(f"https://www.amazon.com.br/s?k=celular&page={page_num}&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&xpid=epfafZntw_-NH&ref=sr_pg_{page_num}", 
                    wait_until="domcontentloaded")
    
    products_data = await page.locator("div[data-cy='title-recipe'] a.a-link-normal").all()
    
    links = []

    for product_data in products_data:
        link = await product_data.get_attribute("href")
        links.append("https://www.amazon.com.br" + link)
    
    links = {link for link in links if "/dp/" in link}

    print("produtos:", len(links))

    tasks = [crawler_products(context,  url, semaphore) for url in links]
    products = await asyncio.gather(*tasks)

    await page.close()

    return products

async def crawler_products(context, url, semaphore):
    print(url)
    async with semaphore:
        page = await context.new_page()

        product = {}

        await page.goto(url, wait_until="domcontentloaded")

        tittle = await page.locator("#productTitle").text_content()
        tittle = tittle.replace("\n", "").strip()
        tittle = " ".join(tittle.split())
        price = await page.locator(".a-price-whole").first.text_content()

        print(tittle, price)
        product[f"{tittle}"] = []

        espec = page.locator("table td[role='presentation']")
        print(type(espec.all()))
        for i in range(0, await espec.count(), 2):
            item1 = await espec.nth(i).locator("span").text_content()
            item2 = await espec.nth(i + 1).locator("span").text_content()

            print("1", item1, "2", item2)
            product[f"{tittle}"].append({item1: item2})

            print(product)

        await page.close()
        return product

async def main():
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        for i in range(1, 20):
            products = await asyncio.gather(crawler(context, i, semaphore))

        print(products)
        await browser.close()

asyncio.run(main())
