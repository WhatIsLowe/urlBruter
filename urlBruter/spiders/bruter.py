import logging
import os

import scrapy.http
from scrapy import Spider
from urllib.parse import urlparse
from ..items import UrlbruterItem
import re


class Bruter(Spider):
    name = 'bruter'

    start_urls = []

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_URI': 'brute.csv',
        'LOG_FILE': 'brute.log',
        'LOG_LEVEL': "ERROR",
        'RETRY_TIMES': 1
    }

    # Вариации надписей кнопки для связи
    CONTACT_LABELS = [
        'Контакты',
        'Связаться',
        'Связаться с нами',
        'Обратная связь'
        # Можно добавить еще вариаций
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: Добавить обработчики исключений
        # Присваиваем директорию папки с доменами для работы
        domains_directory = os.getcwd() + r'\urlBruter\domains'

        # Извлекаем ссылки из файла domains.txt
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

        # ___ Ищем страницу с контактами ___
        # Ищем в теге header кнопку для перехода на страницу с контактами
        header = response.xpath('//header')
        # Ищем тег "button" или тег "a", содержащий текст из CONTACT_LABELS
        button_xpath = './/*[self::button or self::a][' + ' or '.join(
            f'contains(text(), "{label}")' for label in self.CONTACT_LABELS) + ']'
        button = header.xpath(button_xpath)
        if button:
            # Если кнопка найдена - переходим на страницу и парсим ее
            # Получаем ссылку на страницу из атрибута "href" и делаем новый запрос, после вызываем метод parse_contact_page
            contact_url = button.xpath('./@href').get()
            yield response.follow(contact_url, callback=self.parse_page)
        else:
            # Если страница с контактами не найдена, то парсим главную страницу
            yield from self.parse_page(response)

    def parse_page(self, response: scrapy.http.Response):
        item = UrlbruterItem()
        item['title'] = response.xpath('//title/text()').get() or 'н/д'
        item['meta-description'] = response.xpath('//meta[@name="description"]'
                                                   '/@content').get() or 'н/д'
        item['phone_numbers'] = self.find_phone_number(response=response.text) or 'н/д'
        item['email'] = self.find_email(response=response.text) or 'н/д'
        item['inn'] = self.find_inn(response=response.text) or 'н/д'
        item['url'] = response.url
        yield item

    def add_scheme(self, urls: list) -> list:
        """
        Парсит ссылки, если отсутствует схема - добавляет
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
        # Указываем шаблоны для поиска номера телефона
        phone_number_patterns = [
            # r"((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}"
            r"\b(\+7|8|7)(\d){10}\b"
            # TODO: По-возможности добавить "другие" шаблоны для более вариативной выборки
        ]

        phone_numbers = []

        # Проверяем страницу по каждому шаблону
        for pattern in phone_number_patterns:
            matches = re.finditer(pattern, response)
            for match in matches:
                phone_number = match.group(0)
                phone_numbers.append(phone_number)

        # Пропускаем список найденных номеров через функцию remove_duplicates
        return self.remove_duplicates(phone_numbers)

    def find_email(self, response: str) -> list:
        """
        Ищет почту на странице
        """
        emails = []
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.finditer(email_pattern, response)
        for match in matches:
            email = match.group(0)
            emails.append(email)

        return self.remove_duplicates(emails)

    def find_inn(self, response: str) -> str:
        """
        Ищет номер ИНН
        """
        inn_pattern = r'\b(\d{3}-\d{3}-\d{3}\s\d{2})\b'
        inn = re.search(inn_pattern, response)
        if inn is not None:
            return inn.group(0)
        else:
            return "н/д"

    def remove_duplicates(self, data_list: list) -> list:
        """
        Убирает дубли из списка
        """
        return list(set(data_list))

    def close(self, reason):
        logging.log(logging.CRITICAL, "Паук закончить работать. Паук устать. Паук идти спать. ;-)")
