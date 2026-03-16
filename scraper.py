import asyncio
from playwright.async_api import async_playwright
from kafka import send_to_kafka, start_producer

# crawlers
semaphore = asyncio.Semaphore(5)
async def crawler(context, page_num, semaphore, producer): # returns links
    page = await context.new_page()
    await page.goto(f"https://www.amazon.com.br/s?k=celular&page={page_num}&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&xpid=epfafZntw_-NH&ref=sr_pg_{page_num}", 
                    wait_until="domcontentloaded")
    
    links = await page.eval_on_selector_all(
        "div[data-cy='title-recipe'] a",
        "elements => elements.map(e => e.href)"
    )
    
    links = {link for link in links if "/dp/" in link}

    print("produtos:", len(links))

    tasks = [crawler_products(context,  url, semaphore, producer) for url in links]
    products = await asyncio.gather(*tasks)

    await page.close()

    return products

async def crawler_products(context, url, semaphore, producer):
    async with semaphore:
        page = await context.new_page()

        product = {}

        await page.goto(url, wait_until="domcontentloaded")

        tittle = await page.locator("#productTitle").text_content()
        tittle = tittle.replace("\n", "").strip()
        tittle = " ".join(tittle.split())
        price = await page.locator(".a-price-whole").first.text_content()

        product[f"{tittle}"] = []

        espec = page.locator("table td[role='presentation']")
        spans = await espec.locator("span").all_text_contents()

        for i in range(0, len(spans), 2):
            item1 = spans[i]
            item2 = spans[i + 1]

            product[f"{tittle}"].append({item1: item2})

        await send_to_kafka(producer, "scraper-topic", {"tittle":tittle, "price": price})
        
        await page.close()
        return product

async def block_resources(route, request):
    if request.resource_type in ["image", "media", "font"]:
        await route.abort()
    else:
        await route.continue_()

async def main():
    producer = await start_producer()
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.route("**/*", block_resources)

        for i in range(1, 20):
            await asyncio.gather(crawler(context, i, semaphore, producer))
        
        await producer.stop()
        await browser.close()

asyncio.run(main())
