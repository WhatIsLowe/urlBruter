# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UrlbruterItem(scrapy.Item):
    """Итем UrlBruter

    Items:
        title: Заголовок сайта,
        meta_description: Мета-описание,
        phone_number: Номер(а) телефона,
        email: Почта(ы),
        inn: ИНН,
        url: Ссылка на сайт
    """

    title = scrapy.Field()  # Заголовок сайта
    meta_description = scrapy.Field()   # Мета-описание
    phone_number = scrapy.Field()  # Найденные номера телефонов
    email = scrapy.Field()  # Email
    inn = scrapy.Field()    # ИНН
    url = scrapy.Field()    # Ссылка на сайт
