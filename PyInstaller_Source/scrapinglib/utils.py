# -*- coding: utf-8 -*-

from lxml.html import HtmlElement

def getTreeElement(tree: HtmlElement, expr='', index=0):
    """ 根据表达式从`xmltree`中获取匹配值,默认 index 为 0
    :param tree (html.HtmlElement)
    :param expr 
    :param index
    """
    if expr == '':
        return ''
    result = tree.xpath(expr)
    try:
        return result[index]
    except:
        return ''

def getTreeAll(tree: HtmlElement, expr=''):
    """ 根据表达式从`xmltree`中获取全部匹配值
    :param tree (html.HtmlElement)
    :param expr 
    :param index
    """
    if expr == '':
        return []
    result = tree.xpath(expr)
    try:
        return result
    except:
        return []
