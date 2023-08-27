# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UrlbruterItem(scrapy.Item):
    """���� UrlBruter

    Items:
        title: ��������� �����,
        meta_description: ����-��������,
        phone_number: �����(�) ��������,
        email: �����(�),
        inn: ���,
        url: ������ �� ����
    """

    title = scrapy.Field()  # ��������� �����
    meta_description = scrapy.Field()   # ����-��������
    phone_number = scrapy.Field()  # ��������� ������ ���������
    email = scrapy.Field()  # Email
    inn = scrapy.Field()    # ���
    url = scrapy.Field()    # ������ �� ����
