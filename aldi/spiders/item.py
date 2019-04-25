# -*- coding: utf-8 -*-
import scrapy


class ItemSpider(scrapy.Spider):
    name = 'item'
    allowed_domains = ['aldi.com.au']
    start_urls = ['https://www.aldi.com.au/']

    def parse(self, response):

        for nav in response.css('a.m-level-sub::attr(href)'):
            yield response.follow(nav, callback=self.parse_item)

    def parse_item(self, response):

        products = self.get_products(response)

        top_category, sub_category = self.parse_bread_crumb(response)

        for product in products:
            name, price, image_src, url = ItemSpider.extract_product_detail(product)

            yield {
                'top_category': top_category,
                'sub_category': sub_category,
                'product': name,
                'price': price,
                'image_url': image_src,
                'product_url': url
            }

    @staticmethod
    def extract_product_detail(product_html):
        url = product_html.css('::attr(href)').get()
        name = product_html.css('div.box--description--header::text').get().strip()
        val_part = product_html.css('div.box--price>span.box--value::text').getall()
        decimal_part = product_html.css('div.box--price>span.box--decimal::text').getall()
        price = ItemSpider.concatenate_price(val_part, decimal_part)
        image_src = product_html.css('div.box--image-container>::attr(src)').get()

        return ItemSpider.clean_product_name(name), price, image_src, url

    @staticmethod
    def clean_product_name(product_name):
        return product_name.replace('\u00a0', '').replace('\u2019', '')

    @staticmethod
    def concatenate_price(value, decimal):

        price_parts = value + decimal
        conc = ''.join(price_parts)

        if conc == '':
            return None

        if conc[0:1] == "$":
            return conc.replace('$', '').replace(',', '')

        return '0.' + conc.replace('c', '')

    def get_products(self, response):
        products = response.css('div.tx-aldi-products a.box--wrapper')
        return products

    def parse_bread_crumb(self, response):
        top_text = response.xpath('//*[@id="breadcrumb-nav"]/div/div/ul/li[2]/a/span[1]/text()').get()
        sub_text = response.xpath('//*[@id="breadcrumb-nav"]/div/div/ul/li[3]/span/text()').get()
        return top_text, sub_text
