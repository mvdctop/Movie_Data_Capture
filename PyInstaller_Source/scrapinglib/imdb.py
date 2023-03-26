# -*- coding: utf-8 -*-


from .parser import Parser


class Imdb(Parser):
    source = 'imdb'
    imagecut = 0

    expr_title = '//h1[@data-testid="hero-title-block__title"]/text()'
    expr_release = '//a[contains(text(),"Release date")]/following-sibling::div[1]/ul/li/a/text()'
    expr_cover = '//head/meta[@property="og:image"]/@content'
    expr_outline = '//head/meta[@property="og:description"]/@content'
    expr_actor = '//h3[contains(text(),"Top cast")]/../../../following-sibling::div[1]/div[2]/div/div/a/text()'
    expr_tags = '//div[@data-testid="genres"]/div[2]/a/ul/li/text()'

    def queryNumberUrl(self, number):
        """
        TODO 区分 ID 与 名称
        """
        id  = number
        movieUrl = "https://www.imdb.com/title/" + id
        return movieUrl
