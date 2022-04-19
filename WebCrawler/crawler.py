from lxml import etree

class Crawler:
    def __init__(self,htmlcode):
        self.html = etree.HTML(htmlcode)

    def getString(self,_xpath):
        if _xpath == "":
            return ""
        result = self.html.xpath(_xpath)
        try:
            return result[0]
        except:
            return ""

    def getStrings(self,_xpath):
        result = self.html.xpath(_xpath)
        try:
            return result
        except:
            return ""

    def getOutline(self,_xpath):
        result = self.html.xpath(_xpath)
        try:
            return "\n".join(result)
        except:
            return ""