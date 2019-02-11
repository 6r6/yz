#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 6r6

import os
import time
import random
import hmac
import hashlib
import binascii
import base64
import json
import logging
import re
import requests

# (*)腾讯优图配置
app_id = os.environ.get('app_id')
secret_id = os.environ.get('secret_id')
secret_key = os.environ.get('secret_key')

# Server酱V3配置
sckey = ''

logger = logging.getLogger()

class Youtu(object):

    def __init__(self, app_id, secret_id, secret_key, qq=10000):
        self.app_id = app_id
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.qq = qq

    def cal_sig(self):
        timestamp = int(time.time())
        expired = str(timestamp + 2592000)
        rdm = str(random.randint(0, 999999999))
        plain_text = 'a={appid}&k={secret_id}&e={expired}&t={timestamp}&r={rdm}&u={qq}&f='
        plain_text = plain_text.format(appid=self.app_id,
                                       secret_id=self.secret_id,
                                       timestamp=timestamp,
                                       rdm=rdm, qq=self.qq,
                                       expired=expired)
        bin = hmac.new(self.secret_key.encode(), plain_text.encode(), hashlib.sha1).hexdigest()
        s = binascii.unhexlify(bin)
        s = s + plain_text.encode('ascii')
        signature = base64.b64encode(s).rstrip().decode()
        return signature

    def get_text(self, image_raw):
        signature = self.cal_sig()
        headers = {'Host': 'api.youtu.qq.com', 'Content-Type': 'text/json', 'Authorization': signature}
        data = {'app_id': self.app_id, 'image': ''}
        data['image'] = base64.b64encode(image_raw).rstrip().decode('utf-8')
        resp = requests.post('https://api.youtu.qq.com/youtu/ocrapi/generalocr',
                             data=json.dumps(data),
                             headers=headers)
        if 'items' in resp.text:
            return resp.content.decode('utf-8')
        else:
            return '0'

class SocreQuery:

    def __init__(self, xm, id, ksbh):
        self.xm = xm
        self.id = id
        self.ksbh = ksbh
        self.cookies = requests.cookies.RequestsCookieJar()
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control':'max-age=0',
            'Content-Type':'application/x-www-form-urlencoded',
            'DNT':'1',
            'Host':'yz.chsi.com.cn',
            'Origin':'https://yz.chsi.com.cn',
            'Referer':'https://yz.chsi.com.cn/apply/cjcx/',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/70.0.3537.110 Safari/537.37'
        }

    def get_cookies(self):
        base_url = 'https://yz.chsi.com.cn/apply/cjcx'
        session = requests.session()
        base_resp = session.get(base_url, headers=self.headers)
        self.cookies = base_resp.cookies

    def get_checkcode(self):
        pic_url = 'https://yz.chsi.com.cn/apply/cjcx/image.do'
        resp = requests.get(pic_url, headers=self.headers, cookies=self.cookies).content
        ocr = Youtu(app_id, secret_id, secret_key)
        try:
            resp = ocr.get_text(resp)
            resp = eval(resp)
            return resp['items'][0]['itemstring']
        except:
            return '0'

    def get_score_page(self):
        self.get_cookies()
        checkcode = self.get_checkcode().replace(' ','')
        post_url = 'https://yz.chsi.com.cn/apply/cjcx/cjcx.do'
        data = {
            'xm': self.xm,
            'zjhm':self.id,
            'ksbh':self.ksbh,
            'bkdwdm':None,
            'checkcode':checkcode
        }
        post_resp = requests.post(post_url,data=data, headers=self.headers).text
        return post_resp

    @staticmethod
    def get_mid_text(w1, w2, text):
        pat = re.compile(w1+'(.*?)'+w2,re.S)
        result_dict = pat.findall(text)
        return result_dict

    @staticmethod
    def notice(key, title, desp):
        url = 'https://sc.ftqq.com/{}.send'.format(key)
        payload = {'text':title,'desp':desp}
        r = requests.get(url,params=payload)
        return r.text


def main_handler(event, context):
    data = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {"Content-Type":"application/json"},
    "body": ""}
    try:
        rid = context["request_id"]
        xm = event['queryString']['xm']
        id = event['queryString']['id']
        kh = event['queryString']['kh']
        query = SocreQuery(xm,id,kh)
        page = query.get_score_page()
        if '无查询结果' in page:
            logging.info('成绩还没出')
            data['body'] = json.dumps({"Code":101,"Msg":"Score not released yet","Request_id":rid})
            return data
        elif '总分' in page:
            score_content = query.get_mid_text('<tbody>','</tbody>',page)[0]
            logging.info('成绩查询成功')
            data['headers']['Content-Type'] = 'text/html'
            data['body'] = score_content
            #query.notice(sckey,'成绩出了',page)
            return data
        else:
            data['body'] = json.dumps({"Code":103,"Msg":"Unexpected page contents","Request_id":rid})
            return data
    except:
        data['body'] = json.dumps({"Code":102,"Msg":"Unexpected url parameters","Request_id":rid})
        return data
