import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CcapfedItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CcapfedSpider(scrapy.Spider):
	name = 'capfed'
	start_urls = ['https://www.capfed.com/community/point-of-blue-blog?offset=0']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="pagination__list-item pagination__list-item--next"]/a[@class="pagination__link"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="article__dateline"]/br/following-sibling::text()').get().strip()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="article__content"]//text()[not (ancestor::p[@class="article__back-link"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CcapfedItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
