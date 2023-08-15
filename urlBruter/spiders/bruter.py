import os

from scrapy import Spider
from urllib.parse import urlparse
import re


class Bruter(Spider):
    name = 'bruter'

    start_urls = []

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_URI': 'brute.csv'
    }

    def __init__(self, **kwargs):
        # TODO: Добавить обработчики исключений
        # Присваиваем директорию папки с доменами для работы
        domains_directory = os.getcwd() + r'\urlBruter\domains'

        # Извлекаем ссылки из файла domains.txt
        super().__init__(**kwargs)
        with open(domains_directory + r'\domains.txt', 'r') as file:
            urls = [url.strip() for url in file.readlines()]

        # Извлекаем ссылки из файла block_domains.txt
        with open(domains_directory + r'\block_domains.txt', 'r') as file:
            blocked_urls = [url.strip() for url in file.readlines()]

        # Проверяем ссылки из urls и записываем в start_urls те, которые не содержатся в blocked_urls
        self.start_urls = [url for url in urls if url not in blocked_urls]
        # Если у ссылки нет схемы - добавляем
        self.start_urls = self.add_scheme(self.start_urls)

    def parse(self, response):
        # Описание сайта:
        # meta[@class="description"]//
        item = {}
        item['title'] = response.xpath('//title/text()').get()
        item['meta-description'] = response.xpath('//meta[@name="description"]'
                                                  '/@content').get()
        item['phone_numbers'] = self.find_phone_number(response=response.text)
        item['url'] = response.url
        yield item

    def add_scheme(self, urls: list) -> list:
        """
        Парсит ссылки, если отсутсвует схема - добавляет
        """
        parsed_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = 'http://' + url
            parsed_urls.append(url)
        return parsed_urls

    def find_phone_number(self, response: str) -> list:
        """
        Ищет номер телефона на странице
        """
        # TODO: Исправить захват "левых" номеров
        phone_number_patterns = [
            # r"((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}"
            r"(\+7|8|7)(\d){10}"
            # TODO: По-возможности добавить "другие" шаблоны для более вариативной выборки
        ]

        phone_numbers = []

        for pattern in phone_number_patterns:
            matches = re.finditer(pattern, response)
            for match in matches:
                phone_number = match.group(0)
                phone_numbers.append(phone_number)

        return phone_numbers
