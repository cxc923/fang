# -*- coding: utf-8 -*-


import re

import scrapy
from fang.items import NewHouseItem,ESFHouseItem


class SfwSpiderSpider(scrapy.Spider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    start_urls = ['http://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None
        # 两个for控制一行一列
        for tr in trs:
            # 排除掉第一个td，剩下第二个和第三个td标签
            tds = tr.xpath(".//td[not(@class)]")
            province_td = tds[0]
            province_text = province_td.xpath(".//text()").get()
            # 如果第二个td里面是空值，则使用上个td的省份的值
            province_text = re.sub(r"\s", "", province_text)
            if province_text:
                province = province_text
            # 排除海外城市
            if province == '其它':
                continue

            city_td = tds[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                # print("省份：",province)
                # print("城市：",city)
                # print("城市链接：",city_url)
                # 构建新房链接
                url_module = city_url.split("//")
                # 协议
                scheme = url_module[0]
                # 域名
                domain = url_module[1]
                if 'bj' in domain:
                    newhouse_url = 'https://newhouse.fang.com/house/s/'
                    esf_url = 'https://esf.fang.com/'
                else:
                    newhouse_url = scheme + '//' + 'newhouse.' + domain + '/house/s/'

                    # 构建二手房链接
                    esf_url = scheme + '//' + "esf." + domain

                # print('城市: %s %s' % (province, city))
                # print('新房URL：%s' % newhouse_url)
                # print('二手房URL:%s' % esf_url)
                yield scrapy.Request(url=newhouse_url,callback=self.parse_newhouse,meta={"info":(province,city)})

                yield scrapy.Request(esf_url, callback=self.parse_esf, meta={"info": (province, city)})


    def parse_newhouse(self,response):
        province,city=response.meta.get('info')
        # 获取一页的所有信息
        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            # 小区名字
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            if name:

                # 几居
                house_type_list = li.xpath(".//div[contains(@class,'house_type clearfix')]/a/text()").getall()
                house_type_list = list(map(lambda x: re.sub(r"\s", "", x), house_type_list))
                rooms = list(filter(lambda x: x.endswith("居"), house_type_list))
                # 面积
                # 转化为字符串
                area = "".join(li.xpath(".//div[contains(@class,'house_type clearfix')]/text()").getall())
                area = re.sub(r"\s|－|/", "", area)
                # 地址
                address = li.xpath(".//div[@class='address']/a/@title").get()
                # 行政区
                district_text = "".join(li.xpath(".//div[@class='address']/a//text()").getall())
                district = re.search(r".\[(.+)\].*", district_text).group(1)
                # 是否在销售
                sale = li.xpath("//div[contains(@class,'fangyuan')]/span/text()").get()
                # 价格
                price = "".join(li.xpath("//div[@class='nhouse_price']//text()").getall())
                price = re.sub(r"\s|广告","",price)
                # 房天下的详情url
                origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
                item = NewHouseItem(
                    name=name,
                    rooms=rooms,
                    area=area,
                    address=address,
                    sale=sale,
                    price=price,
                    origin_url=origin_url,
                    province=province,
                    city=city
                )
                yield item

        # 下一页
        next_url = response.xpath("//div[@class='page']/a[@class='next']/@href").getall()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url),
                                 callback=self.parse_newhouse,
                                 meta={'info': (province, city)})




    def parse_esf(self,response):
        # 二手房
        provice, city = response.meta.get('info')
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            item = ESFHouseItem(provice=provice, city=city)
            name = dl.xpath(".//span[@class='tit_shop']/text()").get()
            if name:
                infos = dl.xpath(".//p[@class='tel_shop']/text()").getall()
                infos = list(map(lambda x: re.sub(r"\s", "", x), infos))
                for info in infos:
                    if "厅" in info:
                        item["rooms"] = info
                    elif '层' in info:
                        item["floor"] = info
                    elif '向' in info:
                        item['toward'] = info
                    elif '㎡' in info:
                        item['area'] = info
                    elif '年建' in info:
                        item['year'] = re.sub("年建", "", info)
                item['address'] = dl.xpath(".//p[@class='add_shop']/span/text()").get()
                # 总价
                item['price'] = "".join(dl.xpath(".//span[@class='red']//text()").getall())
                # 单价
                item['unit'] = dl.xpath(".//dd[@class='price_right']/span[2]/text()").get()
                item['name'] = name
                detail = dl.xpath(".//h4[@class='clearfix']/a/@href").get()
                item['origin_url'] = response.urljoin(detail)
                yield item
        # 下一页
        next_url = response.xpath("//div[@class='page_al']/p/a/@href").get()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url),
                                 callback=self.parse_esf,
                                 meta={'info': (provice, city)}
                                 )

