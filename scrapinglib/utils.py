# -*- coding: utf-8 -*-

from lxml import etree, html


def getTreeElement(tree, expr, index=0):
    """根据表达式从 xmltree 中获取匹配值，默认 index 为 0"""
    if not isinstance(tree, (etree._Element, html.HtmlElement)) or not expr:
        return ''
    try:
        result = tree.xpath(expr)
        if result and len(result) > index:
            val = result[index]
            if hasattr(val, 'text') and val.text is not None:
                return str(val.text).strip()
            return str(val).strip()
        return ''
    except Exception:
        return ''


def getTreeAll(tree, expr):
    """根据表达式从 xmltree 中获取全部匹配值"""
    if not isinstance(tree, (etree._Element, html.HtmlElement)) or not expr:
        return []
    try:
        result = tree.xpath(expr)
        items = []
        for val in result:
            if hasattr(val, 'text') and val.text is not None:
                items.append(str(val.text).strip())
            else:
                items.append(str(val).strip())
        return items
    except Exception:
        return []
