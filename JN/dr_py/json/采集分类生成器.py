#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : 采集分类生成器.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Date  : 2024/6/21

import os
import json
import gzip
import base64

from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import requests

import warnings

# 关闭警告
warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

pool = ThreadPoolExecutor(max_workers=20)  # 初始化线程池内线程数量为20

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Connection': 'close'  # 设置为关闭长连接
}

timeout = 5  # 5秒

use_gzip = False


def compress_and_encode(data: str):
    # 压缩数据
    compressed_data = gzip.compress(data.encode('utf-8'))
    # 对压缩数据进行Base64编码
    encoded_data = base64.b64encode(compressed_data).decode('utf-8')
    return encoded_data


def get_classes(rec):
    classes = None
    if rec.get('url') and str(rec['url']).startswith('http'):
        _class_api = rec.get('api') or '/api.php/provide/vod/'
        _api = urljoin(str(rec['url']).rstrip('/'), _class_api)
        # _api = urljoin(rec['url'], '/api.php/provide/vod/at/json')
        print(_api)
        try:
            r = requests.get(_api, headers=headers, timeout=timeout, verify=False)
            ret = r.json()
            if rec.get('name') == '乐视资源':
                print('=======乐视=========')
                print(ret)
            # print(ret)
            classes = ret.get('class')
        except Exception as e:
            print(f'获取资源【{rec["name"]}】({_api})分类发生错误:{e}')

    return classes


def convert_class(classes, name=None):
    """
    获取的分类转静态分类格式
    @param classes:
    @return:
    """
    if name is None:
        name = ''
    if not classes:
        return {
            "name": "",
            "class_name": "",
            "class_url": "",
        }
    class_names = []
    class_urls = []
    for cls in classes:
        if cls.get('type_name') and cls.get('type_id'):
            class_urls.append(str(cls['type_id']))
            class_names.append(str(cls['type_name']))
    global use_gzip
    return {
        "name": name,
        "class_name": compress_and_encode('&'.join(class_names)) if use_gzip else '&'.join(class_names),
        "class_url": '&'.join(class_urls),
    }


def get_convert_classes(rec):
    classes = get_classes(rec)
    classes = convert_class(classes, rec.get('name'))
    return classes


def main(fname='采集'):
    file_path = f'./{fname}.json'
    out_file_path = file_path.replace('.json', '静态.json')
    if not os.path.exists(file_path):
        exit(f'不存在采集文件路径:{file_path}')
    with open(file_path, encoding='utf-8') as f:
        data = f.read()
    records = json.loads(data)
    print(records)
    # for rec in records:
    #     ret = get_convert_classes(rec)
    #     pprint(ret)
    tasks = [pool.submit(get_convert_classes, rec) for rec in records]  # 构造一个列表，循环向线程池内submit提交执行的方法
    pool.shutdown(wait=True)  # 线程数等待所有线程结束，这里 卡住主线程
    results = [task.result() for task in tasks]
    pprint(results)
    new_records = []
    for record in records:
        rec_name = record["name"]
        if rec_name:
            has_name = [ret for ret in results if ret.get("name") == rec_name]
            if has_name:
                record.update(has_name[-1])
                new_records.append(record)
    pprint(new_records)
    with open(out_file_path, mode='w+', encoding='utf-8') as f:
        f.write(json.dumps(new_records, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    use_gzip = True
    fname = str(input('请输入文件名,留空默认为采集:\n'))
    fname = fname or '采集'
    main(fname)
