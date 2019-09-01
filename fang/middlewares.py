# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random


class UserAgentDownloadMiddleware(object):
    User_Agent = [
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 7.0; America Online Browser 1.1; Windows NT 5.1; (R1 1.5); .NET CLR 2.0.50727; InfoPath.1)',
        'Mozilla/5.0 (X11; U; Linux x86_64; es-ES; rv:1.9.0.12) Gecko/2009072711 CentOS/3.0.12-1.el5.centos Firefox/3.0.12',
        'Mozilla/5.0 (compatible; Konqueror/3.3; Linux) KHTML/3.3.2 (like Gecko)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'

    ]
    def process_request(self,request,spider):
        # choice方法随机选择一个
        user_agent = random.choice(self.User_Agent)
        request.headers['User-Agent'] = user_agent