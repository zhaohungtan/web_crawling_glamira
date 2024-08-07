import scrapy


class GlamiraFullSpider(scrapy.Spider):
    name = "glamira_full_auto_dynamic"
    allowed_domains = ["glamira.com"]
    start_urls = ["https://www.glamira.com/"]  # Start from the homepage

    custom_settings = {
        'CONCURRENT_REQUESTS': 32,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 5,
    }

    scraped_items = set()  # Set to track unique items

    def parse(self, response):
        # Extract category links from the main navigation or sitemap
        category_links = response.css('a::attr(href)').getall()
        category_links = [response.urljoin(link) for link in category_links if
                          "glamira.com" in link and "/product/" not in link]

        for link in category_links:
            yield scrapy.Request(url=link, callback=self.parse_category, meta={'category_url': link, 'page': 1})

    def parse_category(self, response):
        # Get the category name from the URL or page content
        category = response.url.split('/')[-2]

        # Scrape products on the category page
        products = response.css('h2.product-item-details.product-name::text').getall()
        products = [product.strip() for product in products]

        images = response.css('img.product-image-photo::attr(src)').getall()
        prices = response.css('span.price::text').getall()
        prices = [price.strip() for price in prices]

        descriptions = response.css('span.short-description::text').getall()
        descriptions = [description.strip() for description in descriptions]

        carats = response.css('span.carat::text').getall()
        carats = [carat.strip() for carat in carats]

        # Combine and yield the results
        for product, image, price, description, carat in zip(products, images, prices, descriptions, carats):
            # Create a unique identifier for each product
            pid = f"{product}-{price}"

            # Check if the product has already been scraped
            if pid not in self.scraped_items:
                self.scraped_items.add(pid)  # Add the unique identifier to the set

                yield {
                    'PID': pid,
                    'Product Name': product,
                    'Image': image,
                    'Price': price,
                    'Description': description,
                    'Carat': carat,
                    'Category': category,
                    'URL': response.url
                }

        # Pagination logic
        page = response.meta.get('page', 1)
        last_page = int(response.css('li[data-lastpage]::attr(data-lastpage)').get() or page)

        if page < last_page:  # Stop if the current page is the last one
            next_page = page + 1
            next_page_url = f"{response.meta['category_url']}?p={next_page}"
            yield scrapy.Request(url=next_page_url, callback=self.parse_category,
                                 meta={'category_url': response.meta['category_url'], 'page': next_page})
