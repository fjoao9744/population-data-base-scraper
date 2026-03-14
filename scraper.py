from playwright.sync_api import sync_playwright
url_base = "https://www.amazon.com.br/s?k=celular&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.goto(url_base)
    
    products_data = page.locator("div[data-cy='title-recipe'] a.a-link-normal")
    
    links = []

    for product_data in products_data.all():
        link = product_data.get_attribute("href")
        links.append("https://www.amazon.com.br" + link)
    
    links = {link for link in links if "/dp/" in link}

    print("produtos:", len(links), products_data.count())
    products = {}

    for url in links:
        page.goto(url)

        tittle = page.locator("#productTitle").text_content().strip().replace("\n", "")
        tittle = text = " ".join(tittle.split())
        price = page.locator(".a-price-whole").first.text_content()

        print(tittle, price)
        products[f"{tittle}"] = []

        espec = page.locator("table td[role='presentation']")
        print(type(espec.all()))
        for i in range(0, espec.count(), 2):
            item1 = espec.nth(i).locator("span").text_content()
            item2 = espec.nth(i + 1).locator("span").text_content()

            print("1", item1, "2", item2)
            products[f"{tittle}"].append({item1: item2})

        print(products)
        

    browser.close()

# coleta -> modelagem -> armazenamento -> pesquisa -> analise -> mostra de resultado