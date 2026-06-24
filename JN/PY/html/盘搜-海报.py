# -*- coding: utf-8 -*-
import sys
import json
import time
import base64
import random
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.append('..')
from base.spider import Spider


class PanSouSpider(Spider):
    """
    PanSou 网盘搜索爬虫
    适用于 OK影视 / PG 本地包

    默认行为：
    1. 只调用 /api/search 显示搜索结果
    2. 不调用 /api/check/links
    3. 检测代码保留，后续可通过 ext 开启
    """

    DEFAULT_BASE_URL = "https://so.252035.xyz"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    SEARCH_PAGE_SIZE = 60
    REQUEST_TIMEOUT = 30
    CHECK_TIMEOUT = 15
    MAX_RETRIES = 2
    BACKOFF_FACTOR = 0.5

    PAN_CONFIG = {
        "quark": {
            "api_type": "quark",
            "name": "夸克",
            "keywords": ["pan.quark.cn"],
            "icon": "quark.png"
        },
        "a115": {
            "api_type": "115",
            "name": "115",
            "keywords": ["115.com", "115cdn.com", "anxia.com"],
            "icon": "115.png"
        },
        "ali": {
            "api_type": "aliyun",
            "name": "阿里",
            "keywords": ["alipan.com", "aliyundrive.com"],
            "icon": "ali.png"
        },
        "baidu": {
            "api_type": "baidu",
            "name": "百度",
            "keywords": ["pan.baidu.com", "baidu"],
            "icon": "baidu.png"
        },
        "uc": {
            "api_type": "uc",
            "name": "UC",
            "keywords": ["drive.uc.cn"],
            "icon": "uc.png"
        },
        "tianyi": {
            "api_type": "tianyi",
            "name": "天翼",
            "keywords": ["cloud.189.cn"],
            "icon": "189.png"
        },
        "mobile": {
            "api_type": "mobile",
            "name": "移动",
            "keywords": ["caiyun.139.com"],
            "icon": "139.png"
        },
        "xunlei": {
            "api_type": "xunlei",
            "name": "迅雷",
            "keywords": ["xunlei", "pan.xunlei.com", "thunder"],
            "icon": "xunlei.png"
        },
        "a123": {
            "api_type": "123",
            "name": "123",
            "keywords": [
                "123pan.com",
                "123pan.cn",
                "123684.com",
                "123685.com",
                "123912.com",
                "123592.com"
            ],
            "icon": "123.png"
        },
        "pikpak": {
            "api_type": "pikpak",
            "name": "PikPak",
            "keywords": ["pikpak"],
            "icon": "pikpak.png"
        },
        "magnet": {
            "api_type": "magnet",
            "name": "磁力",
            "keywords": ["magnet:"],
            "icon": "cili.png"
        },
        "ed2k": {
            "api_type": "ed2k",
            "name": "电驴",
            "keywords": ["ed2k://"],
            "icon": ""
        }
    }

    REVERSE_PAN_MAP = {
        v["api_type"]: k for k, v in PAN_CONFIG.items()
    }

    def __init__(self):
        super().__init__()

        # API 地址
        self.base_url = self.DEFAULT_BASE_URL
        self.token = ""
        self.proxy = ""

        # 搜索参数
        self.src = "all"
        self.refresh = False
        self.channels = []
        self.plugins = []
        self.cloud_types = []
        self.search_ext = {}
        self.search_filter = {}

        # 排序配置
        self.pan_order = ""
        self.pan_priority = ""

        # 检测配置
        # 默认关闭，只显示搜索结果
        self.check_enable = False
        self.check_types = ["quark", "115"]
        self.check_hide_bad = False

        # requests session
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

        retries = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=self.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )

        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def init(self, extend):
        """
        PG ext 示例：

        推荐先关闭检测：
        {
            "server": "https://so.252035.xyz",
            "src": "all",
            "check_enable": false
        }

        后续开启检测：
        {
            "server": "https://so.252035.xyz",
            "src": "all",
            "check_enable": true,
            "check_types": ["quark", "115"]
        }
        """

        try:
            if not extend:
                cfg = {}
            elif isinstance(extend, dict):
                cfg = extend
            elif isinstance(extend, str):
                cfg = json.loads(extend)
            else:
                cfg = {}

            self.base_url = cfg.get(
                "server",
                cfg.get("api", self.DEFAULT_BASE_URL)
            ).rstrip("/")

            self.token = cfg.get("token", "")
            self.proxy = cfg.get("proxy", "")

            self.src = cfg.get("src", self.src)
            self.refresh = self._to_bool(cfg.get("refresh", self.refresh))

            self.channels = self._to_list(cfg.get("channels", self.channels))
            self.plugins = self._to_list(cfg.get("plugins", self.plugins))
            self.cloud_types = self._to_list(cfg.get("cloud_types", self.cloud_types))

            self.search_ext = cfg.get(
                "search_ext",
                cfg.get("ext_params", {})
            ) or {}

            self.search_filter = cfg.get("filter", {}) or {}

            self.pan_order = cfg.get("pan_order", "")
            self.pan_priority = cfg.get("pan_priority", "")

            # 默认关闭检测，只有 ext 里明确 check_enable=true 才开启
            self.check_enable = self._to_bool(
                cfg.get("check_enable", self.check_enable)
            )

            self.check_types = self._to_list(
                cfg.get("check_types", self.check_types)
            ) or ["quark", "115"]

            self.check_hide_bad = self._to_bool(
                cfg.get("check_hide_bad", self.check_hide_bad)
            )

            if self.proxy:
                self.session.proxies = {
                    "http": self.proxy,
                    "https": self.proxy
                }

            self.session.headers.update(self._headers())

            print("PanSou init ok:", self.base_url)

        except Exception as e:
            print("PanSou init error:", e)

    def getName(self):
        return "PanSou"

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        return {
            "class": [
                {
                    "type_id": "search",
                    "type_name": "PanSou|网盘搜索"
                }
            ],
            "list": []
        }

    def homeVideoContent(self):
        return {
            "list": []
        }

    def categoryContent(self, cid, page, filter, ext):
        return {
            "list": [
                {
                    "vod_id": "tips",
                    "vod_name": "请使用搜索功能搜索资源",
                    "vod_pic": "",
                    "vod_remarks": "PanSou"
                }
            ],
            "page": 1,
            "pagecount": 1,
            "limit": 1,
            "total": 1
        }

    def searchContent(self, key, quick, pg="1"):
        return self._perform_search(key, pg)

    def searchContentPage(self, key, quick, page):
        return self._perform_search(key, page)

    def _perform_search(self, keywords, page_str):
        """
        搜索主流程：
        默认只显示搜索结果。
        检测代码保留，但 check_enable 默认为 False。
        """

        try:
            page = int(page_str)
        except Exception:
            page = 1

        result = {
            "list": [],
            "page": page,
            "pagecount": 1,
            "limit": self.SEARCH_PAGE_SIZE,
            "total": 0
        }

        if not keywords:
            return result

        try:
            search_data = self._request_search(keywords)
            all_items = self._parse_search_results(search_data, keywords)
            all_items = self._sort_results(all_items)

            total_count = len(all_items)
            start = (page - 1) * self.SEARCH_PAGE_SIZE
            end = start + self.SEARCH_PAGE_SIZE
            page_items = all_items[start:end]

            # 默认不会执行检测。
            # 只有配置 check_enable=true 时才会检测当前页的夸克、115。
            if self.check_enable and page_items:
                page_items = self._apply_check_results(page_items)

            all_images = self._collect_all_images(page_items)

            seed = int(hashlib.md5(keywords.encode("utf-8")).hexdigest(), 16)
            rng = random.Random(seed)

            vod_list = []

            for item in page_items:
                vod_list.append(
                    self._build_vod_item(item, all_images, rng)
                )

            result.update({
                "list": vod_list,
                "total": total_count,
                "pagecount": max(
                    1,
                    (total_count + self.SEARCH_PAGE_SIZE - 1) // self.SEARCH_PAGE_SIZE
                )
            })

        except Exception as e:
            print("PanSou search error:", e)

        return result

    def _request_search(self, keywords):
        """
        使用 GET 搜索。
        你的接口已验证：
        https://so.252035.xyz/api/search?kw=庆余年&res=merge
        """

        url = self.base_url + "/api/search"

        params = {
            "kw": keywords,
            "res": "merge",
            "src": self.src
        }

        if self.refresh:
            params["refresh"] = "true"

        if self.channels:
            params["channels"] = ",".join(self.channels)

        if self.plugins:
            params["plugins"] = ",".join(self.plugins)

        if self.cloud_types:
            params["cloud_types"] = ",".join(self.cloud_types)

        if isinstance(self.search_ext, dict) and self.search_ext:
            params["ext"] = json.dumps(
                self.search_ext,
                ensure_ascii=False
            )

        if isinstance(self.search_filter, dict) and self.search_filter:
            params["filter"] = json.dumps(
                self.search_filter,
                ensure_ascii=False
            )

        response = self.session.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=self.REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    def _parse_search_results(self, data, keywords):
        """
        兼容接口格式：

        {
            "code": 0,
            "message": "success",
            "data": {
                "total": 179,
                "merged_by_type": {}
            }
        }

        也兼容：
        {
            "merged_by_type": {}
        }
        """

        items = []

        if not isinstance(data, dict):
            return items

        if isinstance(data.get("data"), dict):
            merged = data.get("data", {}).get("merged_by_type", {}) or {}
        else:
            merged = data.get("merged_by_type", {}) or {}

        if not isinstance(merged, dict):
            return items

        for api_type, links in merged.items():
            if not isinstance(links, list):
                continue

            pan_type = self.REVERSE_PAN_MAP.get(api_type, api_type)
            pan_name = self._pan_name(api_type)

            for link in links:
                if not isinstance(link, dict):
                    continue

                resource_url = link.get("url") or ""

                if not resource_url:
                    continue

                item = {
                    "api_type": api_type,
                    "pan_type": pan_type,
                    "pan_name": pan_name,
                    "url": resource_url,
                    "password": link.get("password") or "",
                    "normalized_url": "",
                    "note": link.get("note") or keywords,
                    "datetime": link.get("datetime") or "",
                    "source": link.get("source") or "PanSou",
                    "images": link.get("images") or [],
                    "state": "",
                    "summary": "",
                    "_timestamp": self._timestamp(link.get("datetime"))
                }

                item["id"] = self._encode_id(item)

                items.append(item)

        return self._dedupe_items(items)

    # ==========================================================
    # 检测功能：默认不执行，但代码保留
    # ==========================================================

    def _apply_check_results(self, items):
        """
        只检测当前页中的 check_types。
        默认 check_enable=False，所以此函数默认不会被调用。
        """

        check_items = []

        for item in items:
            api_type = item.get("api_type", "")

            if api_type not in self.check_types:
                continue

            url = item.get("url", "")

            if not url:
                continue

            check_items.append({
                "disk_type": api_type,
                "url": url,
                "password": item.get("password", "")
            })

        if not check_items:
            return items

        check_map = self._request_check_links(check_items)

        output = []

        for item in items:
            key = self._check_key(
                item.get("api_type", ""),
                item.get("url", "")
            )

            if key in check_map:
                checked = check_map[key]

                item["state"] = checked.get("state", "")
                item["summary"] = checked.get("summary", "")
                item["normalized_url"] = checked.get("normalized_url", "")
                item["id"] = self._encode_id(item)

                if self.check_hide_bad and item["state"] == "bad":
                    continue

            output.append(item)

        return output

    def _request_check_links(self, check_items):
        """
        调用 /api/check/links
        默认不调用，除非 check_enable=true。
        """

        url = self.base_url + "/api/check/links"

        payload = {
            "items": check_items,
            "view_token": "ok-pg-%s" % int(time.time() * 1000)
        }

        try:
            response = self.session.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=self.CHECK_TIMEOUT
            )

            response.raise_for_status()

            data = response.json()

            output = {}

            for item in data.get("results", []) or []:
                api_type = item.get("disk_type", "")
                raw_url = item.get("url", "")

                output[self._check_key(api_type, raw_url)] = {
                    "state": item.get("state", ""),
                    "summary": item.get("summary", ""),
                    "normalized_url": item.get("normalized_url", "")
                }

            return output

        except Exception as e:
            print("PanSou check error:", e)
            return {}

    # ==========================================================
    # OK影视详情与播放
    # ==========================================================

    def _build_vod_item(self, item, all_images, rng):
        pan_name = item.get("pan_name", "网盘")
        note = self._clean_title(
            item.get("note") or "网盘资源"
        )
        source = item.get("source") or ""
        password = item.get("password") or ""
        state = item.get("state") or ""

        pan_type = item.get("pan_type", "")
        pan_config = self.PAN_CONFIG.get(pan_type, {})
        icon = self._get_icon_url(
            pan_config.get("icon", "")
        )

        vod_pic = self._get_best_image(
            item,
            all_images,
            icon,
            rng
        )

        dt = self._to_datetime(
            item.get("datetime")
        )

        time_str = dt.strftime("%m-%d") if dt else ""

        remarks = [pan_name]

        if time_str:
            remarks.append(time_str)

        if password:
            remarks.append("码:%s" % password)

        if state:
            remarks.append(
                self._state_name(state)
            )

        if source:
            remarks.append(
                source.replace("plugin:", "").replace("tg:", "")
            )

        return {
            "vod_id": item.get("id") or self._encode_id(item),
            "vod_name": note,
            "vod_pic": vod_pic,
            "vod_remarks": "|".join(remarks)
        }

    def detailContent(self, did):
        result = {
            "list": []
        }

        if not did or not did[0]:
            return result

        try:
            item = self._decode_id(did[0])
        except Exception:
            raw_url = did[0]
            api_type = self._extract_api_type_from_url(raw_url)

            item = {
                "api_type": api_type,
                "pan_type": self.REVERSE_PAN_MAP.get(api_type, api_type),
                "pan_name": self._pan_name(api_type),
                "url": raw_url,
                "password": "",
                "normalized_url": "",
                "note": "网盘资源",
                "datetime": "",
                "source": "PanSou",
                "images": [],
                "state": "",
                "summary": ""
            }

        api_type = item.get("api_type", "")
        pan_type = item.get("pan_type", "")
        pan_name = item.get("pan_name") or self._pan_name(api_type)

        title = self._clean_title(
            item.get("note") or "%s资源" % pan_name
        )

        raw_url = item.get("url") or ""
        password = item.get("password") or ""
        normalized_url = item.get("normalized_url") or ""

        final_url = self._build_final_url(
            api_type,
            normalized_url or raw_url,
            password
        )

        state = item.get("state") or ""
        summary = item.get("summary") or ""
        source = item.get("source") or ""
        datetime_text = item.get("datetime") or ""

        content = [
            "资源名称：%s" % title,
            "网盘类型：%s" % pan_name,
            "资源链接：%s" % raw_url
        ]

        if normalized_url and normalized_url != raw_url:
            content.append(
                "规范链接：%s" % normalized_url
            )

        if password:
            content.append(
                "提取码：%s" % password
            )

        if state:
            content.append(
                "检测状态：%s" % self._state_name(state)
            )

        if summary:
            content.append(
                "检测说明：%s" % summary
            )

        if source:
            content.append(
                "来源：%s" % source
            )

        if datetime_text:
            content.append(
                "时间：%s" % datetime_text
            )

        play_name = pan_name

        if password:
            play_name += " 提取码:%s" % password

        if state:
            play_name += " %s" % self._state_name(state)

        play_id = self._encode_id({
            "api_type": api_type,
            "url": final_url,
            "password": password
        })

        icon = self._get_icon_url(
            self.PAN_CONFIG.get(pan_type, {}).get("icon", "")
        )

        result["list"].append({
            "vod_id": did[0],
            "vod_name": title,
            "vod_pic": icon,
            "type_name": pan_name,
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": self._state_name(state) if state else pan_name,
            "vod_actor": source,
            "vod_director": "PanSou",
            "vod_content": "\n".join(content),
            "vod_play_from": pan_name,
            "vod_play_url": "%s$%s" % (play_name, play_id)
        })

        return result

    def playerContent(self, flag, pid, vipFlags):
        """
        不使用 push:
        直接返回网盘链接、磁力链接或 ed2k。
        """

        result = {
            "parse": 0,
            "playUrl": "",
            "url": "",
            "header": self._headers()
        }

        if not pid:
            return result

        try:
            data = self._decode_id(pid)

            api_type = data.get("api_type", "")
            url = data.get("url", "")
            password = data.get("password", "")

            result["url"] = self._build_final_url(
                api_type,
                url,
                password
            )

            return result

        except Exception:
            result["url"] = str(pid)
            return result

    def localProxy(self, param):
        return None

    # ==========================================================
    # 工具函数
    # ==========================================================

    def _headers(self):
        headers = dict(self.HEADERS)

        if self.token:
            headers["Authorization"] = "Bearer " + self.token

        return headers

    def _to_list(self, value):
        if value is None:
            return []

        if isinstance(value, list):
            return [
                str(x).strip()
                for x in value
                if str(x).strip()
            ]

        if isinstance(value, tuple):
            return [
                str(x).strip()
                for x in value
                if str(x).strip()
            ]

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return []

            return [
                x.strip()
                for x in value.split(",")
                if x.strip()
            ]

        return []

    def _to_bool(self, value):
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            return value != 0

        if isinstance(value, str):
            value = value.strip().lower()

            if value in [
                "true",
                "1",
                "yes",
                "y",
                "on"
            ]:
                return True

            if value in [
                "false",
                "0",
                "no",
                "n",
                "off",
                ""
            ]:
                return False

        return bool(value)

    def _encode_id(self, data):
        text = json.dumps(
            data,
            ensure_ascii=False
        )
        raw = text.encode("utf-8")
        code = base64.urlsafe_b64encode(raw).decode("utf-8")
        return code.rstrip("=")

    def _decode_id(self, text):
        text = str(text)
        padding = "=" * (-len(text) % 4)
        raw = base64.urlsafe_b64decode(
            (text + padding).encode("utf-8")
        )
        return json.loads(
            raw.decode("utf-8")
        )

    def _dedupe_items(self, items):
        seen = set()
        output = []

        for item in items:
            key = self._check_key(
                item.get("api_type", ""),
                item.get("url", "")
            )

            if key in seen:
                continue

            seen.add(key)
            output.append(item)

        return output

    def _check_key(self, api_type, url):
        return "%s|%s" % (
            str(api_type).strip().lower(),
            str(url).strip().replace(" ", "")
        )

    def _pan_name(self, api_type):
        for config in self.PAN_CONFIG.values():
            if config.get("api_type") == api_type:
                return config.get("name", api_type)

        return api_type or "网盘"

    def _state_name(self, state):
        mapping = {
            "ok": "有效",
            "bad": "失效",
            "locked": "需密码",
            "unsupported": "不支持检测",
            "uncertain": "检测失败"
        }

        return mapping.get(
            str(state),
            str(state)
        )

    def _sort_results(self, items):
        order_text = self.pan_order or self.pan_priority

        if order_text:
            enabled = [
                x.strip()
                for x in order_text.split(",")
                if x.strip()
            ]
        else:
            enabled = []

        if enabled:
            filtered = []

            for item in items:
                if (
                    item.get("pan_type") in enabled
                    or item.get("api_type") in enabled
                ):
                    filtered.append(item)

            items = filtered

            order_map = {
                pan: idx
                for idx, pan in enumerate(enabled)
            }

            items.sort(
                key=lambda x: (
                    order_map.get(
                        x.get("pan_type"),
                        order_map.get(
                            x.get("api_type"),
                            len(enabled)
                        )
                    ),
                    -x.get("_timestamp", 0)
                )
            )
        else:
            items.sort(
                key=lambda x: -x.get("_timestamp", 0)
            )

        return items

    def _collect_all_images(self, items):
        images = []

        for item in items:
            for img in item.get("images") or []:
                if img:
                    images.append(img)

        return images

    def _get_best_image(self, item, all_images, icon, rng):
        images = item.get("images") or []

        if images:
            return images[0]

        if all_images:
            return rng.choice(all_images)

        return icon

    def _get_icon_url(self, icon_name):
        if not icon_name:
            return ""

        return "http://127.0.0.1:9978/file/Download/lib/icon/%s" % icon_name

    def _clean_title(self, title):
        if not title:
            return "网盘资源"

        title = str(title)
        title = title.replace("\n", " ")
        title = title.replace("\r", " ")
        title = " ".join(title.split())

        if len(title) > 90:
            title = title[:90] + "..."

        return title

    def _timestamp(self, time_str):
        dt = self._to_datetime(time_str)

        if not dt:
            return 0

        try:
            return dt.timestamp()
        except Exception:
            return 0

    def _to_datetime(self, time_str):
        if not time_str:
            return None

        if time_str == "0001-01-01T00:00:00Z":
            return None

        try:
            clean = str(time_str).replace("Z", "+00:00")
            return datetime.fromisoformat(clean)
        except Exception:
            pass

        try:
            return datetime.strptime(
                str(time_str),
                "%Y-%m-%d %H:%M:%S"
            )
        except Exception:
            return None

    def _extract_api_type_from_url(self, url):
        if not url:
            return "unknown"

        url_lower = str(url).lower()

        if url_lower.startswith("magnet:"):
            return "magnet"

        if url_lower.startswith("ed2k://"):
            return "ed2k"

        try:
            host = urlparse(url).netloc.lower()
        except Exception:
            host = url_lower

        for config in self.PAN_CONFIG.values():
            for keyword in config.get("keywords", []):
                if keyword.lower() in host or keyword.lower() in url_lower:
                    return config.get("api_type", "unknown")

        return "unknown"

    def _build_final_url(self, api_type, url, password=""):
        if not url:
            return ""

        api_type = str(api_type)

        if api_type in ["magnet", "ed2k"]:
            return url

        if not password:
            return url

        lower_url = url.lower()

        if (
            "pwd=" in lower_url
            or "password=" in lower_url
            or "passcode=" in lower_url
        ):
            return url

        if "?" in url:
            return url + "&pwd=" + password

        return url + "?pwd=" + password


Spider = PanSouSpider

# ===== PANSOU_QIWEI_STYLE_PATCH_BEGIN =====
# PanSou 七味式二级/三级目录补丁
# 追加在 py_pansou.py 文件末尾即可生效

import re as _psq_re
import json as _psq_json
import time as _psq_time
import html as _psq_html
import base64 as _psq_base64
from urllib.parse import unquote as _psq_unquote


try:
    _PSQ_ORIG_INIT = PanSouSpider.init
    _PSQ_ORIG_SEARCH = PanSouSpider.searchContent
    _PSQ_ORIG_SEARCH_PAGE = PanSouSpider.searchContentPage
    _PSQ_ORIG_CATEGORY = PanSouSpider.categoryContent
    _PSQ_ORIG_DETAIL = PanSouSpider.detailContent
    _PSQ_ORIG_PLAYER = PanSouSpider.playerContent
except Exception:
    _PSQ_ORIG_INIT = None
    _PSQ_ORIG_SEARCH = None
    _PSQ_ORIG_SEARCH_PAGE = None
    _PSQ_ORIG_CATEGORY = None
    _PSQ_ORIG_DETAIL = None
    _PSQ_ORIG_PLAYER = None


# ============================================================
# 基础 ID 编解码
# ============================================================

def _psq_b64e(obj):
    try:
        txt = _psq_json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        return _psq_base64.urlsafe_b64encode(txt.encode("utf-8")).decode("utf-8").rstrip("=")
    except Exception:
        return ""


def _psq_b64d(s):
    try:
        s = str(s or "")
        s += "=" * (-len(s) % 4)
        return _psq_json.loads(
            _psq_base64.urlsafe_b64decode(s.encode("utf-8")).decode("utf-8")
        )
    except Exception:
        return {}


def _psq_make_id(vtype, data):
    return "psq|" + str(vtype) + "|" + _psq_b64e(data or {})


def _psq_parse_id(vod_id):
    try:
        vod_id = str(vod_id or "")
        if not vod_id.startswith("psq|"):
            return "", {}
        arr = vod_id.split("|", 2)
        if len(arr) < 3:
            return "", {}
        return arr[1], _psq_b64d(arr[2])
    except Exception:
        return "", {}


def _psq_raw_b64e(text):
    try:
        return _psq_base64.urlsafe_b64encode(
            str(text or "").encode("utf-8")
        ).decode("utf-8").rstrip("=")
    except Exception:
        return ""


def _psq_raw_b64d(text):
    try:
        text = str(text or "")
        text += "=" * (-len(text) % 4)
        return _psq_base64.urlsafe_b64decode(
            text.encode("utf-8")
        ).decode("utf-8")
    except Exception:
        return ""


def _psq_std_b64e(obj):
    try:
        txt = _psq_json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        return _psq_base64.b64encode(txt.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""


def _psq_std_b64d(text):
    try:
        text = str(text or "")
        text += "=" * (-len(text) % 4)
        return _psq_json.loads(
            _psq_base64.b64decode(text.encode("utf-8")).decode("utf-8")
        )
    except Exception:
        return []


def _psq_clean_name(self, text, limit=160):
    try:
        text = str(text or "")
        text = _psq_html.unescape(text)
        text = text.replace("#", "＃").replace("$", "＄")
        text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        text = _psq_re.sub(r"\s+", " ", text).strip()
        if not text:
            text = "资源"
        return text[:limit]
    except Exception:
        return "资源"


def _psq_wait_url(self):
    try:
        u = getattr(self, "wait_video_url", "") or ""
        if u:
            return u
        u = getattr(self, "ack_mp4", "") or ""
        if u:
            return u
        return "https://vd2.bdstatic.com/mda-nj5kxa8kr7wgq6ie/sc/cae_h264_nowatermark/1653272065989267185/mda-nj5kxa8kr7wgq6ie.mp4"
    except Exception:
        return ""


def _psq_ack(self):
    try:
        pic = getattr(self, "last_vod_pic", "") or ""
        ret = {
            "parse": 0,
            "playUrl": "",
            "url": _psq_wait_url(self),
            "header": {
                "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
            }
        }
        if pic:
            ret["pic"] = pic
            ret["poster"] = pic
        return ret
    except Exception:
        return {
            "parse": 1,
            "playUrl": "",
            "url": ""
        }


# ============================================================
# 类型 / 显示 / 排序
# ============================================================

_PSQ_GROUP_ORDER = [
    "quark",
    "115",
    "magnet",
    "baidu",
    "uc",
    "aliyun",
    "xunlei",
    "123",
    "mobile",
    "tianyi",
    "pikpak",
    "ed2k",
    "other"
]

_PSQ_GROUP_NAME = {
    "quark": "🟢 夸克",
    "115": "🟡 115",
    "magnet": "🧲 磁力资源",
    "baidu": "📘 百度",
    "uc": "📱 UC",
    "aliyun": "☁️ 阿里",
    "xunlei": "⚡ 迅雷",
    "123": "📦 123盘",
    "mobile": "☁️ 移动云",
    "tianyi": "☎️ 天翼",
    "pikpak": "📦 PikPak",
    "ed2k": "🔗 电驴",
    "other": "📦 其他网盘"
}

_PSQ_GROUP_ICON = {
    "quark": "🟢",
    "115": "🟡",
    "magnet": "🧲",
    "baidu": "📘",
    "uc": "📱",
    "aliyun": "☁️",
    "xunlei": "⚡",
    "123": "📦",
    "mobile": "☁️",
    "tianyi": "☎️",
    "pikpak": "📦",
    "ed2k": "🔗",
    "other": "📦"
}


def _psq_group_key(api_type):
    api_type = str(api_type or "").strip().lower()

    if api_type in ["115", "a115"]:
        return "115"

    if api_type in ["ali", "aliyun", "alipan"]:
        return "aliyun"

    if api_type in ["123", "a123", "123pan"]:
        return "123"

    if api_type in ["tianyi", "189"]:
        return "tianyi"

    if api_type in ["mobile", "139"]:
        return "mobile"

    if api_type in _PSQ_GROUP_NAME:
        return api_type

    return "other"


def _psq_group_rank(api_type):
    key = _psq_group_key(api_type)
    try:
        return _PSQ_GROUP_ORDER.index(key)
    except Exception:
        return 99


def _psq_extract_size_text(text):
    try:
        text = str(text or "")
        m = _psq_re.search(r"(?i)(\d+(?:\.\d+)?)\s*(TB|GB|MB|KB|T|G|M|K)\b", text)
        if not m:
            return ""
        num = m.group(1)
        unit = m.group(2).upper()
        unit = {
            "T": "TB",
            "G": "GB",
            "M": "MB",
            "K": "KB"
        }.get(unit, unit)
        return "%s%s" % (num, unit)
    except Exception:
        return ""


def _psq_size_gb(text):
    try:
        size = _psq_extract_size_text(text)
        if not size:
            return 0.0

        m = _psq_re.search(r"(?i)(\d+(?:\.\d+)?)(TB|GB|MB|KB)", size)
        if not m:
            return 0.0

        num = float(m.group(1))
        unit = m.group(2).upper()

        if unit == "TB":
            return num * 1024.0
        if unit == "GB":
            return num
        if unit == "MB":
            return num / 1024.0
        if unit == "KB":
            return num / 1024.0 / 1024.0

        return 0.0
    except Exception:
        return 0.0


def _psq_quality_score(text):
    try:
        raw = str(text or "")
        low = raw.lower()

        score = 0

        if "杜比" in raw or "dolby" in low or "dovi" in low:
            score += 120000

        if _psq_re.search(r"(?i)(^|[\s._\-\[\]()【】])dv($|[\s._\-\[\]()【】])", low):
            score += 100000

        if "高码" in raw or "high bitrate" in low or "hbr" in low or "hq" in low:
            score += 90000

        if "hdr10+" in low:
            score += 85000
        elif "hdr10" in low:
            score += 80000
        elif _psq_re.search(r"(?i)(^|[\s._\-\[\]()【】])hdr($|[\s._\-\[\]()【】])", low):
            score += 75000

        if "4k" in low or "2160p" in low or "2160" in low or "uhd" in low:
            score += 65000

        if "原盘" in raw or "remux" in low or "bluray" in low or "blu-ray" in low or "bdmv" in low:
            score += 55000

        if "60fps" in low or "60帧" in raw:
            score += 35000

        if "1080p" in low or "1080" in low:
            score += 15000

        if "web-dl" in low or "webdl" in low:
            score += 3000

        if any(x in raw for x in ["枪版", "抢先", "预告", "花絮", "解说"]):
            score -= 1000000

        if _psq_re.search(r"(?i)(^|[\s._\-\[\]()【】])(tc|ts|cam|trailer)($|[\s._\-\[\]()【】])", low):
            score -= 1000000

        return score
    except Exception:
        return 0


def _psq_date_value(item):
    try:
        dt = str(item.get("datetime") or item.get("date") or item.get("time") or "")

        if not dt or dt.startswith("0001-"):
            return 0

        m = _psq_re.search(r"((?:19|20)\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})", dt)
        if m:
            y = int(m.group(1))
            mo = int(m.group(2))
            d = int(m.group(3))
            return y * 10000 + mo * 100 + d

        return int(item.get("_timestamp") or 0)

    except Exception:
        return 0


def _psq_sort_items(items):
    def key_func(item):
        text = " ".join([
            str(item.get("note") or ""),
            str(item.get("name") or ""),
            str(item.get("url") or ""),
            str(item.get("source") or "")
        ])

        return (
            -_psq_quality_score(text),
            -_psq_date_value(item),
            -_psq_size_gb(text),
            str(item.get("note") or "")
        )

    try:
        arr = list(items or [])
        arr.sort(key=key_func)
        return arr
    except Exception:
        return items or []


def _psq_magnet_btih(magnet):
    try:
        magnet = str(magnet or "")
        m = _psq_re.search(r"xt=urn:btih:([a-zA-Z0-9]+)", magnet, _psq_re.I)
        return m.group(1).lower() if m else ""
    except Exception:
        return ""


def _psq_normalize_magnet(self, url):
    try:
        if hasattr(self, "_normalize_magnet"):
            return self._normalize_magnet(url)

        url = str(url or "").strip()
        url = _psq_html.unescape(url)
        url = _psq_unquote(url)
        url = url.replace("&amp;", "&")

        m = _psq_re.search(r"(magnet:\?[^\s\"'<>]+)", url, _psq_re.I)
        if m:
            url = m.group(1)

        url = _psq_re.sub(r"\s+", "", url)

        if not url.startswith("magnet:?"):
            return ""

        if "urn:btih:" not in url:
            return ""

        return url

    except Exception:
        return ""


def _psq_extract_dn(url):
    try:
        url = str(url or "")
        m = _psq_re.search(r"[?&]dn=([^&]+)", url, _psq_re.I)
        if not m:
            return ""
        return _psq_unquote(m.group(1)).strip()
    except Exception:
        return ""


def _psq_clean_magnet_name(self, item):
    try:
        name = str(item.get("note") or item.get("name") or "").strip()
        url = str(item.get("url") or "")

        bad = [
            "",
            "磁力",
            "磁力链接",
            "磁力资源",
            "资源",
            "下载",
            "链接",
            "magnet",
            "magnetlink"
        ]

        if name.strip().lower() in [x.lower() for x in bad]:
            dn = _psq_extract_dn(url)
            if dn:
                name = dn
            else:
                btih = _psq_magnet_btih(url)
                if btih:
                    name = "磁力%s" % btih[:8].upper()
                else:
                    name = "磁力资源"

        return _psq_clean_name(self, name, 150)
    except Exception:
        return "磁力资源"


def _psq_remark(item, status="未检测"):
    try:
        note = str(item.get("note") or item.get("name") or "")
        url = str(item.get("url") or "")
        source = str(item.get("source") or "")

        date_text = "时间未知"
        dt = str(item.get("datetime") or "")
        if dt and not dt.startswith("0001-"):
            m = _psq_re.search(r"((?:19|20)\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})", dt)
            if m:
                date_text = "%s-%02d-%02d" % (
                    m.group(1),
                    int(m.group(2)),
                    int(m.group(3))
                )
            else:
                date_text = dt[:10]

        size = _psq_extract_size_text(" ".join([note, url])) or "大小未知"

        kws = []
        text = " ".join([note, url])
        low = text.lower()

        def add(x):
            if x and x not in kws:
                kws.append(x)

        if "杜比" in text or "dolby" in low or "dovi" in low:
            add("杜比")
        if "4k" in low or "2160p" in low or "2160" in low:
            add("4K")
        if "1080p" in low or "1080" in low:
            add("1080P")
        if "hdr10+" in low:
            add("HDR10+")
        elif "hdr10" in low:
            add("HDR10")
        elif "hdr" in low:
            add("HDR")
        if "remux" in low:
            add("REMUX")
        if "原盘" in text:
            add("原盘")
        if "60fps" in low or "60帧" in text:
            add("60FPS")
        if "web-dl" in low or "webdl" in low:
            add("WEB-DL")

        kw_text = "/".join(kws) if kws else "无关键词"

        src = source.replace("plugin:", "").replace("tg:", "")

        parts = [status, date_text, size, kw_text]

        if src:
            parts.append(src)

        return " · ".join(parts)

    except Exception:
        return "%s · 时间未知 · 大小未知 · 无关键词" % status


# ============================================================
# 搜索缓存
# ============================================================

def _psq_cache(self):
    if not hasattr(self, "_psq_search_cache"):
        self._psq_search_cache = {}
    return self._psq_search_cache


def _psq_fetch_search_items(self, keyword):
    keyword = str(keyword or "").strip()

    if not keyword:
        return []

    cache = _psq_cache(self)
    ttl = int(getattr(self, "psq_cache_ttl", 600) or 600)
    now = _psq_time.time()
    ck = "kw|" + keyword

    old = cache.get(ck)

    if old:
        ts, arr = old
        if now - ts < ttl:
            return arr

    try:
        data = self._request_search(keyword)
        arr = self._parse_search_results(data, keyword)

        try:
            arr = self._dedupe_items(arr)
        except Exception:
            pass

        cache[ck] = (now, arr)

        return arr

    except Exception as e:
        print("[PSQ] fetch search error:", e)
        return []


def _psq_group_items(items):
    groups = {}

    for item in items or []:
        try:
            api_type = item.get("api_type") or ""
            key = _psq_group_key(api_type)
            groups.setdefault(key, [])
            groups[key].append(item)
        except Exception:
            pass

    return groups


# ============================================================
# init 包装
# ============================================================

def _psq_init(self, extend=""):
    ret = None

    if _PSQ_ORIG_INIT:
        ret = _PSQ_ORIG_INIT(self, extend)

    self.psq_cache_ttl = getattr(self, "psq_cache_ttl", 600)

    self.wait_video_url = getattr(self, "wait_video_url", "")
    self.ack_mp4 = getattr(
        self,
        "ack_mp4",
        "https://vd2.bdstatic.com/mda-nj5kxa8kr7wgq6ie/sc/cae_h264_nowatermark/1653272065989267185/mda-nj5kxa8kr7wgq6ie.mp4"
    )

    # 115/OpenList 配置入口，保留
    self.pan_115_cookie = getattr(self, "pan_115_cookie", "")
    self.confirm_115 = getattr(self, "confirm_115", False)
    self.confirm_cache = getattr(self, "confirm_cache", set())

    self.openlist_url = getattr(self, "openlist_url", "")
    self.openlist_token = getattr(self, "openlist_token", "")
    self.openlist_parent = getattr(self, "openlist_parent", "/云下载")
    self.openlist_test_stream = getattr(self, "openlist_test_stream", False)
    self.test_m3u8 = getattr(self, "test_m3u8", "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8")

    try:
        if extend and isinstance(extend, str) and extend.strip().startswith("{"):
            ext = _psq_json.loads(extend)

            self.psq_cache_ttl = int(ext.get("psq_cache_ttl", self.psq_cache_ttl))
            self.wait_video_url = str(ext.get("wait_video_url", self.wait_video_url) or "").strip()
            self.ack_mp4 = str(ext.get("ack_mp4", self.ack_mp4) or "").strip()

            self.pan_115_cookie = str(ext.get("pan_115_cookie", self.pan_115_cookie) or "").strip()
            self.confirm_115 = str(ext.get("confirm_115", "0")).lower() in [
                "1", "true", "yes", "on"
            ]

            self.openlist_url = str(ext.get("openlist_url", self.openlist_url) or "").strip().rstrip("/")
            self.openlist_token = str(ext.get("openlist_token", self.openlist_token) or "").strip()
            self.openlist_parent = str(ext.get("openlist_parent", self.openlist_parent) or "/云下载").strip()

            if self.openlist_parent and not self.openlist_parent.startswith("/"):
                self.openlist_parent = "/" + self.openlist_parent

            self.openlist_test_stream = str(ext.get("openlist_test_stream", "0")).lower() in [
                "1", "true", "yes", "on"
            ]

            self.test_m3u8 = str(ext.get("test_m3u8", self.test_m3u8) or "").strip()

    except Exception as e:
        print("[PSQ] init patch ext error:", e)

    print("[PANSOU QIWEI STYLE PATCH] enabled")

    return ret if ret is not None else {}


# ============================================================
# 搜索结果：二级目录
# ============================================================

def _psq_searchContent(self, key, quick=False, pg="1"):
    try:
        page = int(pg) if str(pg).isdigit() else 1
    except Exception:
        page = 1

    keyword = str(key or "").strip()

    if not keyword:
        return {
            "list": [],
            "page": page,
            "pagecount": 1,
            "limit": 0,
            "total": 0
        }

    items = _psq_fetch_search_items(self, keyword)
    groups = _psq_group_items(items)

    videos = []

    for gkey in _PSQ_GROUP_ORDER:
        arr = groups.get(gkey) or []

        if not arr:
            continue

        cover = ""

        for x in arr:
            imgs = x.get("images") or []
            if imgs:
                cover = imgs[0]
                break

        if not cover:
            try:
                pan_type = self.REVERSE_PAN_MAP.get(gkey, gkey)
                icon = self.PAN_CONFIG.get(pan_type, {}).get("icon", "")
                cover = self._get_icon_url(icon)
            except Exception:
                cover = ""

        vod_id = _psq_make_id("group", {
            "kw": keyword,
            "group": gkey
        })

        videos.append({
            "vod_id": vod_id,
            "vod_name": _PSQ_GROUP_NAME.get(gkey, gkey),
            "vod_pic": cover,
            "vod_remarks": "%s条资源" % len(arr),
            "vod_content": "搜索词：%s\n资源类型：%s\n点击进入具体资源列表。" % (
                keyword,
                _PSQ_GROUP_NAME.get(gkey, gkey)
            ),
            "vod_tag": "folder"
        })

    for gkey, arr in groups.items():
        if gkey in _PSQ_GROUP_ORDER:
            continue

        if not arr:
            continue

        vod_id = _psq_make_id("group", {
            "kw": keyword,
            "group": gkey
        })

        videos.append({
            "vod_id": vod_id,
            "vod_name": "📦 %s" % gkey,
            "vod_pic": "",
            "vod_remarks": "%s条资源" % len(arr),
            "vod_content": "搜索词：%s\n资源类型：%s" % (keyword, gkey),
            "vod_tag": "folder"
        })

    return {
        "list": videos,
        "page": page,
        "pagecount": 1,
        "limit": len(videos),
        "total": len(videos)
    }


def _psq_searchContentPage(self, key, quick, page):
    return _psq_searchContent(self, key, quick, page)


# ============================================================
# 分类：二级目录进入三级资源
# ============================================================

def _psq_categoryContent(self, tid, pg, filter, extend):
    try:
        tid_s = str(tid or "")

        if tid_s.startswith("psq|"):
            vtype, data = _psq_parse_id(tid_s)

            if vtype == "group":
                return _psq_build_third_category(self, data, pg)

        if _PSQ_ORIG_CATEGORY:
            return _PSQ_ORIG_CATEGORY(self, tid, pg, filter, extend)

    except Exception as e:
        print("[PSQ] categoryContent error:", e)

    return {
        "list": [],
        "page": 1,
        "pagecount": 1,
        "limit": 0,
        "total": 0
    }


def _psq_build_third_category(self, data, pg=1):
    try:
        page = int(pg) if str(pg).isdigit() else 1
    except Exception:
        page = 1

    if page < 1:
        page = 1

    keyword = str(data.get("kw") or "").strip()
    group = str(data.get("group") or "").strip()

    items = _psq_fetch_search_items(self, keyword)
    groups = _psq_group_items(items)
    current = groups.get(group) or []

    current = _psq_sort_items(current)

    page_size = int(getattr(self, "SEARCH_PAGE_SIZE", 60) or 60)

    if page_size <= 0:
        page_size = 60

    total = len(current)
    pagecount = max(1, int((total + page_size - 1) / page_size))

    if page > pagecount:
        page = pagecount

    start = (page - 1) * page_size
    page_items = current[start:start + page_size]

    videos = []
    width = max(2, len(str(total))) if total else 2

    cover_fallback = ""

    for x in current:
        imgs = x.get("images") or []
        if imgs:
            cover_fallback = imgs[0]
            break

    for idx, item in enumerate(page_items):
        real_idx = start + idx + 1

        note = item.get("note") or item.get("url") or "资源"
        url = item.get("url") or ""
        password = item.get("password") or ""
        api_type = item.get("api_type") or group
        gkey = _psq_group_key(api_type)

        imgs = item.get("images") or []
        pic = imgs[0] if imgs else cover_fallback

        if gkey == "magnet":
            clean_title = _psq_clean_magnet_name(self, item)
            icon = "⚪"
            vod_id = _psq_make_id("magnetplay", {
                "kw": keyword,
                "group": gkey,
                "name": clean_title,
                "url": url,
                "pic": pic
            })
            remark = _psq_remark(item, "未检测")
            content = "%s\n点击后进入磁力播放页。" % clean_title

        elif gkey == "ed2k":
            clean_title = _psq_clean_name(self, note, 150)
            icon = "⚪"
            vod_id = _psq_make_id("ed2kplay", {
                "kw": keyword,
                "group": gkey,
                "name": clean_title,
                "url": url,
                "pic": pic
            })
            remark = _psq_remark(item, "未检测")
            content = "%s\n点击后推送电驴链接。" % clean_title

        else:
            clean_title = _psq_clean_name(self, note, 150)
            icon = "⚪"
            vod_id = _psq_make_id("panplay", {
                "kw": keyword,
                "group": gkey,
                "api_type": api_type,
                "name": clean_title,
                "url": url,
                "password": password,
                "pic": pic
            })
            remark = _psq_remark(item, "未检测")
            content = "%s\n点击后自动推送网盘链接。" % clean_title

        show_name = "%s. %s %s" % (
            str(real_idx).zfill(width),
            icon,
            clean_title
        )

        videos.append({
            "vod_id": vod_id,
            "vod_name": _psq_clean_name(self, show_name, 160),
            "vod_pic": pic,
            "vod_remarks": remark,
            "vod_content": content,
            "vod_tag": "file"
        })

    if not videos:
        videos.append({
            "vod_id": "empty",
            "vod_name": "%s 暂无资源" % _PSQ_GROUP_NAME.get(group, group),
            "vod_pic": cover_fallback,
            "vod_remarks": "空"
        })

    return {
        "list": videos,
        "page": page,
        "pagecount": pagecount,
        "limit": page_size,
        "total": total
    }


# ============================================================
# 详情：三级资源点击处理
# ============================================================

def _psq_detailContent(self, ids):
    try:
        vod_id = ids[0] if isinstance(ids, list) and ids else ids
        vod_id_s = str(vod_id or "")

        if vod_id_s.startswith("psq|"):
            vtype, data = _psq_parse_id(vod_id_s)

            if vtype == "panplay":
                return _psq_build_panplay_detail(self, data)

            if vtype == "ed2kplay":
                return _psq_build_ed2kplay_detail(self, data)

            if vtype == "magnetplay":
                return _psq_build_magnetplay_detail(self, data)

            if vtype == "group":
                return {
                    "list": [{
                        "vod_id": vod_id_s,
                        "vod_name": _PSQ_GROUP_NAME.get(data.get("group"), "资源分类"),
                        "vod_pic": "",
                        "vod_remarks": "分类入口",
                        "vod_content": "当前客户端未识别 folder，请返回后重新进入。",
                        "vod_play_from": "提示",
                        "vod_play_url": "无可播放资源$__ACK__"
                    }]
                }

        if _PSQ_ORIG_DETAIL:
            return _PSQ_ORIG_DETAIL(self, ids)

    except Exception as e:
        print("[PSQ] detailContent error:", e)

    return {
        "list": []
    }


def _psq_build_panplay_detail(self, data):
    title = data.get("name") or "网盘资源"
    pic = data.get("pic") or getattr(self, "last_vod_pic", "") or ""
    url = data.get("url") or ""
    password = data.get("password") or ""
    api_type = data.get("api_type") or data.get("group") or ""

    if pic:
        self.last_vod_pic = pic

    try:
        final_url = self._build_final_url(api_type, url, password)
    except Exception:
        final_url = url

    payload = self._encode_id({
        "type": "pan",
        "api_type": api_type,
        "url": final_url,
        "password": password,
        "pic": pic
    })

    content = [
        "资源名称：%s" % title,
        "资源链接：%s" % url
    ]

    if password:
        content.append("提取码：%s" % password)

    return {
        "list": [{
            "vod_id": "psq_panplay",
            "vod_name": title,
            "vod_pic": pic,
            "vod_remarks": "自动推送",
            "vod_content": "\n".join(content),
            "vod_play_from": "推送",
            "vod_play_url": "自动推送$%s" % payload
        }]
    }


def _psq_build_ed2kplay_detail(self, data):
    title = data.get("name") or "电驴资源"
    pic = data.get("pic") or getattr(self, "last_vod_pic", "") or ""
    url = data.get("url") or ""

    if pic:
        self.last_vod_pic = pic

    payload = self._encode_id({
        "type": "ed2k",
        "url": url,
        "pic": pic
    })

    return {
        "list": [{
            "vod_id": "psq_ed2kplay",
            "vod_name": title,
            "vod_pic": pic,
            "vod_remarks": "电驴资源",
            "vod_content": "点击后推送电驴链接。",
            "vod_play_from": "推送",
            "vod_play_url": "%s$%s" % (title, payload)
        }]
    }


def _psq_build_115_cloud_items(self, magnets):
    items = []

    try:
        mg_list = [x.get("url") for x in magnets if x.get("url")]
        mg_b64 = _psq_std_b64e(mg_list)
        items.append("下载状态$__115_STATUS_ALL__|%s" % mg_b64)
    except Exception as e:
        print("[PSQ 115] build status error:", e)

    for x in magnets or []:
        try:
            mg = x.get("url") or ""
            name = x.get("name") or "磁力资源"
            enc = _psq_raw_b64e(mg)
            items.append("%s$%s" % (_psq_clean_name(self, name, 120), enc))
        except Exception:
            pass

    return "#".join(items)


def _psq_build_cached_playlist(self, magnets):
    """
    简化版播放列表：
    如果后续你加入完整 115/OpenList 补丁，可以覆盖这里。
    """
    try:
        if hasattr(self, "build115CachedFilePlayItems"):
            return self.build115CachedFilePlayItems(magnets)
    except Exception:
        pass

    return "暂无115缓存，请先点115云下载-下载状态$__ACK__"


def _psq_build_query_items(self, title):
    """
    简化版查询线路。
    如果配置了 OpenList，并且后续你加入完整 OpenList 逻辑，可以继续扩展。
    """
    try:
        if hasattr(self, "buildOpenlistPlayItems"):
            return self.buildOpenlistPlayItems(title)
    except Exception:
        pass

    title_b64 = _psq_base64.b64encode(
        str(title or "").encode("utf-8")
    ).decode("utf-8")

    items = [
        "刷新OpenList$__OPENLIST_REFRESH__|%s" % title_b64
    ]

    for n in range(2, 14):
        items.append("搜%s$__OPENLIST_SEARCH__|%s|%s" % (n, n, title_b64))

    return "#".join(items)


def _psq_build_magnetplay_detail(self, data):
    title = data.get("name") or "磁力资源"
    pic = data.get("pic") or getattr(self, "last_vod_pic", "") or ""
    url = data.get("url") or ""

    if pic:
        self.last_vod_pic = pic

    mu = _psq_normalize_magnet(self, url)

    if not mu:
        return {
            "list": [{
                "vod_id": "psq_bad_magnet",
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": "磁力无效",
                "vod_content": "磁力链接解析失败。",
                "vod_play_from": "0",
                "vod_play_url": "等待视频$__ACK__"
            }]
        }

    play_from = []
    play_url = []

    # 0线路固定第一，防止自动触发云下载
    play_from.append("0")
    play_url.append("等待视频$__ACK__")

    magnets = [{
        "name": title,
        "url": mu,
        "key": _psq_magnet_btih(mu) or mu.lower()
    }]

    # 115云下载
    cloud_items = _psq_build_115_cloud_items(self, magnets)
    if cloud_items:
        play_from.append("115云下载")
        play_url.append(cloud_items)

    # 播放列表
    cached_list = _psq_build_cached_playlist(self, magnets)
    play_from.append("播放列表")
    play_url.append(cached_list)

    # 查询
    if getattr(self, "openlist_url", "") and getattr(self, "openlist_token", ""):
        play_from.append("查询")
        play_url.append(_psq_build_query_items(self, title))

    # 磁力播放
    payload = self._encode_id({
        "type": "magnet",
        "url": mu,
        "pic": pic
    })

    play_from.append("磁力播放")
    play_url.append("%s$%s" % (title, payload))

    return {
        "list": [{
            "vod_id": "psq_magnetplay",
            "vod_name": title,
            "vod_pic": pic,
            "vod_remarks": "磁力资源",
            "vod_content": "%s\n\n0线路为等待视频，用于防止壳自动跳到云下载。" % title,
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url)
        }]
    }


# ============================================================
# 115 / OpenList 简化兼容
# ============================================================

def _psq_115_status_all(self, pid):
    """
    简化实现：
    点击 115云下载-下载状态 时返回等待视频。
    如果你后续接入完整 115 API，可覆盖此函数。
    """
    return _psq_ack(self)


def _psq_115_submit_magnet(self, magnet):
    """
    简化实现：
    当前只返回等待视频，不真正提交 115。
    完整 115 离线逻辑可继续接你参考代码里的补丁。
    """
    return _psq_ack(self)


def _psq_openlist_player(self, pid):
    """
    简化实现：
    如果开启 openlist_test_stream，则返回测试流；
    否则返回等待视频。
    """
    try:
        if getattr(self, "openlist_test_stream", False):
            ret = {
                "parse": 0,
                "playUrl": "",
                "url": getattr(self, "test_m3u8", ""),
                "header": {
                    "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
                }
            }

            pic = getattr(self, "last_vod_pic", "") or ""
            if pic:
                ret["pic"] = pic
                ret["poster"] = pic

            return ret
    except Exception:
        pass

    return _psq_ack(self)


# ============================================================
# 播放
# ============================================================

def _psq_playerContent(self, flag, pid, vipFlags):
    try:
        flag = str(flag or "")
        pid = str(pid or "")

        if pid in ["__ACK__", "__WAIT_VIDEO__", "__QW_WAIT_VIDEO__", "__BTL_WAIT_VIDEO__"]:
            return _psq_ack(self)

        if flag == "0" or flag == "提示":
            return _psq_ack(self)

        if flag == "115云下载":
            if pid.startswith("__115_STATUS_ALL__|"):
                return _psq_115_status_all(self, pid)

            real_mag = _psq_raw_b64d(pid)
            real_mag = _psq_normalize_magnet(self, real_mag)

            if real_mag:
                return _psq_115_submit_magnet(self, real_mag)

            return _psq_ack(self)

        if flag == "播放列表" or pid.startswith("__115_FILE__|"):
            try:
                if hasattr(self, "_115CachedFilePlayerContent"):
                    return self._115CachedFilePlayerContent(pid)
            except Exception:
                pass
            return _psq_ack(self)

        if flag == "查询" or pid.startswith("__OPENLIST_"):
            return _psq_openlist_player(self, pid)

        # 先尝试解析本补丁/原代码的 JSON payload
        try:
            data = self._decode_id(pid)

            if isinstance(data, dict):
                typ = data.get("type", "")
                url = data.get("url", "")
                pic = data.get("pic") or getattr(self, "last_vod_pic", "")

                if typ == "pan":
                    ret = {
                        "parse": 0,
                        "playUrl": "",
                        "url": "push://" + url,
                        "pic": pic,
                        "poster": pic,
                        "header": {
                            "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
                        }
                    }
                    return ret

                if typ == "magnet":
                    mu = _psq_normalize_magnet(self, url)

                    if mu:
                        return {
                            "parse": 0,
                            "playUrl": "",
                            "url": "push://" + mu,
                            "pic": pic,
                            "poster": pic,
                            "header": {
                                "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
                            }
                        }

                    return {
                        "parse": 1,
                        "playUrl": "",
                        "url": url,
                        "pic": pic,
                        "poster": pic
                    }

                if typ == "ed2k":
                    return {
                        "parse": 0,
                        "playUrl": "",
                        "url": "push://" + url,
                        "pic": pic,
                        "poster": pic,
                        "header": {
                            "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
                        }
                    }

        except Exception:
            pass

        # 原始 push
        if pid.startswith("push://"):
            return {
                "parse": 0,
                "playUrl": "",
                "url": pid,
                "pic": getattr(self, "last_vod_pic", ""),
                "poster": getattr(self, "last_vod_pic", "")
            }

        # 原始磁力
        mu = _psq_normalize_magnet(self, pid)

        if mu:
            return {
                "parse": 0,
                "playUrl": "",
                "url": "push://" + mu,
                "pic": getattr(self, "last_vod_pic", ""),
                "poster": getattr(self, "last_vod_pic", ""),
                "header": {
                    "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
                }
            }

        # 原始 ed2k
        if pid.lower().startswith("ed2k://"):
            return {
                "parse": 0,
                "playUrl": "",
                "url": "push://" + pid,
                "pic": getattr(self, "last_vod_pic", ""),
                "poster": getattr(self, "last_vod_pic", ""),
                "header": {
                    "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
                }
            }

        # 原始网盘链接
        if _psq_re.search(r"(pan\.quark\.cn|115\.com|115cdn\.com|pan\.baidu\.com|drive\.uc\.cn|aliyundrive\.com|alipan\.com|cloud\.189\.cn|caiyun\.139\.com|123pan|xunlei)", pid, _psq_re.I):
            return {
                "parse": 0,
                "playUrl": "",
                "url": "push://" + pid,
                "pic": getattr(self, "last_vod_pic", ""),
                "poster": getattr(self, "last_vod_pic", ""),
                "header": {
                    "User-Agent": self.HEADERS.get("User-Agent", "Mozilla/5.0")
                }
            }

        if _PSQ_ORIG_PLAYER:
            return _PSQ_ORIG_PLAYER(self, flag, pid, vipFlags)

        return {
            "parse": 1,
            "playUrl": "",
            "url": pid
        }

    except Exception as e:
        print("[PSQ] playerContent error:", e)
        return _psq_ack(self)


# ============================================================
# 绑定
# ============================================================

PanSouSpider.init = _psq_init
PanSouSpider.searchContent = _psq_searchContent
PanSouSpider.searchContentPage = _psq_searchContentPage
PanSouSpider.categoryContent = _psq_categoryContent
PanSouSpider.detailContent = _psq_detailContent
PanSouSpider.playerContent = _psq_playerContent

Spider = PanSouSpider

print("[PANSOU QIWEI STYLE PATCH] loaded")
# ===== PANSOU_QIWEI_STYLE_PATCH_END =====

# ===== PANSOU_QIWEI_FIX_V2_BEGIN =====
# PanSou 七味式补丁 v2
# 修复：
# 1. 二级分类重复显示；
# 2. 0线路默认等待视频路径；
# 3. ext 支持 wait_video_url；
# 4. quickSearch 默认返回空，避免 OK/PG 双搜索合并造成重复。

import json as _psqfix_json
import re as _psqfix_re

try:
    _PSQ_FIX_PREV_INIT = PanSouSpider.init
    _PSQ_FIX_PREV_SEARCH = PanSouSpider.searchContent
    _PSQ_FIX_PREV_SEARCH_PAGE = PanSouSpider.searchContentPage
except Exception:
    _PSQ_FIX_PREV_INIT = None
    _PSQ_FIX_PREV_SEARCH = None
    _PSQ_FIX_PREV_SEARCH_PAGE = None


_PSQ_FIX_DEFAULT_WAIT_VIDEO = "/storage/emulated/0/Download/2026/太阳之子"


def _psqfix_to_bool(v, default=False):
    try:
        if isinstance(v, bool):
            return v
        if isinstance(v, int):
            return v != 0
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off", ""]:
                return False
        return bool(v)
    except Exception:
        return default


def _psqfix_parse_ext(extend):
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str) and extend.strip().startswith("{"):
            return _psqfix_json.loads(extend)
        return {}
    except Exception:
        return {}


def _psqfix_normalize_wait_video_url(url):
    """
    支持：
    1. http://xxx
    2. https://xxx
    3. file:///xxx
    4. /storage/xxx
    5. /sdcard/xxx
    """

    try:
        u = str(url or "").strip()

        if not u:
            return ""

        if u.startswith(("http://", "https://", "file://", "content://")):
            return u

        if u.startswith(("/storage/", "/sdcard/", "/mnt/", "/data/")):
            return "file://" + u

        if u.startswith("/"):
            return "file://" + u

        return u

    except Exception:
        return str(url or "")


def _psqfix_init(self, extend=""):
    ret = None

    if _PSQ_FIX_PREV_INIT:
        ret = _PSQ_FIX_PREV_INIT(self, extend)

    try:
        ext = _psqfix_parse_ext(extend)

        # 默认等待视频路径
        default_wait = _PSQ_FIX_DEFAULT_WAIT_VIDEO

        wait_video_url = (
            ext.get("wait_video_url")
            or ext.get("psq_wait_video_url")
            or getattr(self, "wait_video_url", "")
            or default_wait
        )

        self.wait_video_url = _psqfix_normalize_wait_video_url(wait_video_url)

        # 是否让 quickSearch 返回空。
        # 默认 True，防止 OK/PG 同时合并 quickSearch + searchContent 造成二级目录重复。
        self.psq_quick_empty = _psqfix_to_bool(
            ext.get("psq_quick_empty", True),
            True
        )

        print("[PANSOU QIWEI FIX V2] wait_video_url =", self.wait_video_url)
        print("[PANSOU QIWEI FIX V2] psq_quick_empty =", self.psq_quick_empty)

    except Exception as e:
        print("[PANSOU QIWEI FIX V2] init error:", e)

    return ret if ret is not None else {}


def _psqfix_empty_search(page=1):
    try:
        page = int(page)
    except Exception:
        page = 1

    return {
        "list": [],
        "page": page,
        "pagecount": 1,
        "limit": 0,
        "total": 0
    }


def _psqfix_dedupe_videos(videos):
    """
    二级目录去重。
    按 vod_id 优先去重；
    如果 vod_id 不可靠，则按 vod_name 去重。
    """

    out = []
    seen = set()

    for v in videos or []:
        try:
            vid = str(v.get("vod_id") or "")
            name = str(v.get("vod_name") or "")

            # 对 psq group 目录，按 group 类型去重。
            key = ""

            if vid.startswith("psq|group|"):
                key = vid
            elif name:
                key = "name|" + name
            else:
                key = vid or repr(v)

            if key in seen:
                continue

            seen.add(key)
            out.append(v)

        except Exception:
            out.append(v)

    return out


def _psqfix_searchContent(self, key, quick=False, pg="1"):
    """
    包装搜索：
    1. 如果 quick=True 且 psq_quick_empty=True，则返回空，避免重复；
    2. 调用原搜索；
    3. 对二级目录再次去重。
    """

    try:
        page = int(pg) if str(pg).isdigit() else 1
    except Exception:
        page = 1

    try:
        quick_bool = _psqfix_to_bool(quick, False)

        if quick_bool and getattr(self, "psq_quick_empty", True):
            return _psqfix_empty_search(page)

        if _PSQ_FIX_PREV_SEARCH:
            ret = _PSQ_FIX_PREV_SEARCH(self, key, quick, pg)
        else:
            ret = {
                "list": [],
                "page": page,
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

        if isinstance(ret, dict) and isinstance(ret.get("list"), list):
            ret["list"] = _psqfix_dedupe_videos(ret.get("list") or [])
            ret["limit"] = len(ret["list"])
            ret["total"] = len(ret["list"])

        return ret

    except Exception as e:
        print("[PANSOU QIWEI FIX V2] searchContent error:", e)
        return _psqfix_empty_search(page)


def _psqfix_searchContentPage(self, key, quick, page):
    return _psqfix_searchContent(self, key, quick, page)


# 覆盖全局 _psq_wait_url。
# 原 _psq_ack 会动态读取这个函数，所以这里重定义后 0线路会生效。
def _psq_wait_url(self):
    try:
        u = getattr(self, "wait_video_url", "") or _PSQ_FIX_DEFAULT_WAIT_VIDEO
        return _psqfix_normalize_wait_video_url(u)
    except Exception:
        return _psqfix_normalize_wait_video_url(_PSQ_FIX_DEFAULT_WAIT_VIDEO)


# 如果之前补丁里有 _psq_get_wait_video_url，也一起覆盖。
def _psq_get_wait_video_url(self):
    return _psq_wait_url(self)


PanSouSpider.init = _psqfix_init
PanSouSpider.searchContent = _psqfix_searchContent
PanSouSpider.searchContentPage = _psqfix_searchContentPage

Spider = PanSouSpider

print("[PANSOU QIWEI FIX V2] loaded")
# ===== PANSOU_QIWEI_FIX_V2_END =====

# ===== PANSOU_QIWEI_FIX_V3_BEGIN =====
# PanSou 七味式补丁 v3
# 解决 quickSearch=0 后仍然二级分类显示两遍的问题。
# 原因通常是壳层同时调用 searchContent/searchContentPage 并合并结果。
# 本补丁会在短时间窗口内拦截重复搜索。

import time as _psqv3_time
import json as _psqv3_json
import re as _psqv3_re

try:
    _PSQV3_PREV_INIT = PanSouSpider.init
    _PSQV3_PREV_SEARCH = PanSouSpider.searchContent
    _PSQV3_PREV_SEARCH_PAGE = PanSouSpider.searchContentPage
except Exception:
    _PSQV3_PREV_INIT = None
    _PSQV3_PREV_SEARCH = None
    _PSQV3_PREV_SEARCH_PAGE = None


def _psqv3_to_bool(v, default=False):
    try:
        if isinstance(v, bool):
            return v
        if isinstance(v, int):
            return v != 0
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off", ""]:
                return False
        return bool(v)
    except Exception:
        return default


def _psqv3_parse_ext(extend):
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str) and extend.strip().startswith("{"):
            return _psqv3_json.loads(extend)
        return {}
    except Exception:
        return {}


def _psqv3_empty(page=1):
    try:
        page = int(page)
    except Exception:
        page = 1

    return {
        "list": [],
        "page": page,
        "pagecount": 1,
        "limit": 0,
        "total": 0
    }


def _psqv3_normalize_key(key):
    try:
        return str(key or "").strip().lower().replace(" ", "")
    except Exception:
        return str(key or "")


def _psqv3_is_psq_group_item(v):
    try:
        vid = str(v.get("vod_id") or "")
        name = str(v.get("vod_name") or "")
        if vid.startswith("psq|group|"):
            return True
        if any(x in name for x in [
            "夸克",
            "115",
            "磁力资源",
            "百度",
            "UC",
            "阿里",
            "迅雷",
            "123盘",
            "移动云",
            "天翼",
            "PikPak",
            "电驴",
            "其他网盘"
        ]):
            return True
        return False
    except Exception:
        return False


def _psqv3_group_dedupe_key(v):
    """
    二级分类强制去重 key。
    不依赖 vod_id，因为有些壳/补丁生成的 vod_id 不完全相同。
    """
    try:
        name = str(v.get("vod_name") or "").strip()

        # 去掉数量、空白、emoji差异后按资源类型归一。
        raw = name

        if "夸克" in raw:
            return "group|quark"
        if "115" in raw:
            return "group|115"
        if "磁力" in raw:
            return "group|magnet"
        if "百度" in raw:
            return "group|baidu"
        if "UC" in raw or "uc" in raw.lower():
            return "group|uc"
        if "阿里" in raw:
            return "group|aliyun"
        if "迅雷" in raw:
            return "group|xunlei"
        if "123" in raw:
            return "group|123"
        if "移动" in raw:
            return "group|mobile"
        if "天翼" in raw:
            return "group|tianyi"
        if "PikPak" in raw or "pikpak" in raw.lower():
            return "group|pikpak"
        if "电驴" in raw or "ed2k" in raw.lower():
            return "group|ed2k"
        if "其他" in raw:
            return "group|other"

        vid = str(v.get("vod_id") or "")
        if vid:
            return "id|" + vid

        return "name|" + name
    except Exception:
        return repr(v)


def _psqv3_dedupe_list(lst):
    out = []
    seen = set()

    for v in lst or []:
        try:
            if not isinstance(v, dict):
                continue

            if _psqv3_is_psq_group_item(v):
                key = _psqv3_group_dedupe_key(v)
            else:
                key = str(v.get("vod_id") or "") or str(v.get("vod_name") or "") or repr(v)

            if key in seen:
                continue

            seen.add(key)
            out.append(v)

        except Exception:
            out.append(v)

    return out


def _psqv3_init(self, extend=""):
    ret = None

    if _PSQV3_PREV_INIT:
        ret = _PSQV3_PREV_INIT(self, extend)

    try:
        ext = _psqv3_parse_ext(extend)

        # 防双调用开关，默认开启。
        # 如果某个壳出现第一次搜索为空，可以在 ext 设置 "psq_anti_double": false。
        self.psq_anti_double = _psqv3_to_bool(
            ext.get("psq_anti_double", True),
            True
        )

        # 重复调用拦截时间窗口，默认 2.5 秒。
        try:
            self.psq_anti_double_window = float(
                ext.get("psq_anti_double_window", 2.5)
            )
        except Exception:
            self.psq_anti_double_window = 2.5

        if not hasattr(self, "_psqv3_last_search"):
            self._psqv3_last_search = {}

        print("[PANSOU QIWEI FIX V3] psq_anti_double =", self.psq_anti_double)
        print("[PANSOU QIWEI FIX V3] window =", self.psq_anti_double_window)

    except Exception as e:
        print("[PANSOU QIWEI FIX V3] init error:", e)

    return ret if ret is not None else {}


def _psqv3_should_block_duplicate(self, key, page, quick):
    """
    短时间内同关键词、同页的第二次搜索返回空。
    用来防止：
    - searchContent 调一次
    - searchContentPage 又调一次
    - 壳层把两次结果合并
    """
    try:
        if not getattr(self, "psq_anti_double", True):
            return False

        k = _psqv3_normalize_key(key)
        p = str(page or "1")

        # quick 参数不参与 key。
        # 因为有些壳第一次 quick=False，第二次 quick=0 或 None。
        call_key = "search|" + k + "|page|" + p

        now = _psqv3_time.time()
        window = float(getattr(self, "psq_anti_double_window", 2.5) or 2.5)

        if not hasattr(self, "_psqv3_last_search"):
            self._psqv3_last_search = {}

        last = self._psqv3_last_search.get(call_key)

        self._psqv3_last_search[call_key] = now

        if last and now - last < window:
            print("[PANSOU QIWEI FIX V3] block duplicated search:", call_key)
            return True

        return False

    except Exception:
        return False


def _psqv3_searchContent(self, key, quick=False, pg="1"):
    try:
        page = int(pg) if str(pg).isdigit() else 1
    except Exception:
        page = 1

    try:
        if _psqv3_should_block_duplicate(self, key, page, quick):
            return _psqv3_empty(page)

        if _PSQV3_PREV_SEARCH:
            ret = _PSQV3_PREV_SEARCH(self, key, quick, pg)
        else:
            ret = _psqv3_empty(page)

        if isinstance(ret, dict) and isinstance(ret.get("list"), list):
            ret["list"] = _psqv3_dedupe_list(ret.get("list") or [])

            # 注意：二级分类 total 就按目录数量返回。
            ret["limit"] = len(ret["list"])
            ret["total"] = len(ret["list"])

        return ret

    except Exception as e:
        print("[PANSOU QIWEI FIX V3] searchContent error:", e)
        return _psqv3_empty(page)


def _psqv3_searchContentPage(self, key, quick, page):
    try:
        page_i = int(page) if str(page).isdigit() else 1
    except Exception:
        page_i = 1

    try:
        if _psqv3_should_block_duplicate(self, key, page_i, quick):
            return _psqv3_empty(page_i)

        if _PSQV3_PREV_SEARCH_PAGE:
            ret = _PSQV3_PREV_SEARCH_PAGE(self, key, quick, page)
        elif _PSQV3_PREV_SEARCH:
            ret = _PSQV3_PREV_SEARCH(self, key, quick, page)
        else:
            ret = _psqv3_empty(page_i)

        if isinstance(ret, dict) and isinstance(ret.get("list"), list):
            ret["list"] = _psqv3_dedupe_list(ret.get("list") or [])
            ret["limit"] = len(ret["list"])
            ret["total"] = len(ret["list"])

        return ret

    except Exception as e:
        print("[PANSOU QIWEI FIX V3] searchContentPage error:", e)
        return _psqv3_empty(page_i)


PanSouSpider.init = _psqv3_init
PanSouSpider.searchContent = _psqv3_searchContent
PanSouSpider.searchContentPage = _psqv3_searchContentPage

Spider = PanSouSpider

print("[PANSOU QIWEI FIX V3] loaded")
# ===== PANSOU_QIWEI_FIX_V3_END =====

# ===== PANSOU_QIWEI_FIX_MAGNET_SIZE_BEGIN =====
# PanSou 七味式补丁：磁力大小显示修复
# 只增强 _psq_extract_size_text，全局 _psq_remark 会自动调用新函数。

import re as _psqms_re
from urllib.parse import unquote as _psqms_unquote


def _psqms_format_bytes(n):
    try:
        n = int(float(n))
        if n <= 0:
            return ""

        tb = 1024 ** 4
        gb = 1024 ** 3
        mb = 1024 ** 2
        kb = 1024

        if n >= tb:
            return "%.2fTB" % (n / tb)

        if n >= gb:
            return "%.2fGB" % (n / gb)

        if n >= mb:
            return "%.2fMB" % (n / mb)

        if n >= kb:
            return "%.2fKB" % (n / kb)

        return "%sB" % n

    except Exception:
        return ""


def _psqms_normalize_size(num, unit):
    try:
        num = str(num or "").strip()
        unit = str(unit or "").strip().upper()

        unit_map = {
            "T": "TB",
            "TB": "TB",
            "G": "GB",
            "GB": "GB",
            "M": "MB",
            "MB": "MB",
            "K": "KB",
            "KB": "KB",
            "TIB": "TB",
            "GIB": "GB",
            "MIB": "MB",
            "KIB": "KB"
        }

        unit = unit_map.get(unit, unit)

        if not num or unit not in ["TB", "GB", "MB", "KB"]:
            return ""

        # 去掉无意义的 .00
        if "." in num:
            try:
                f = float(num)
                if f.is_integer():
                    num = str(int(f))
            except Exception:
                pass

        return "%s%s" % (num, unit)

    except Exception:
        return ""


def _psq_extract_size_text(text):
    """
    覆盖前面补丁里的 _psq_extract_size_text。

    支持：
    1. 29.5G / 29.5GB
    2. 1.2T / 1.2TB
    3. 800M / 800MB
    4. [74.8G]
    5. xl=42125203739
    6. &xl=42125203739
    """

    try:
        text = str(text or "")

        if not text:
            return ""

        raw = text

        try:
            raw = _psqms_unquote(raw)
        except Exception:
            pass

        # 1. 优先识别明确单位
        # 注意：
        # - 支持 G/T/M/K 简写；
        # - 支持 GB/TB/MB/KB；
        # - 支持 GiB/TiB；
        # - 避免把 4K 当成 4KB，所以 K 单位要谨慎。
        patterns = [
            # 74.8GB / 74.8G / 1.2TB / 1.2T
            r"(?i)(\d+(?:\.\d+)?)\s*(TB|TIB|GB|GIB|MB|MIB|KB|KIB)\b",
            r"(?i)(\d+(?:\.\d+)?)\s*(T|G|M)\b"
        ]

        for p in patterns:
            m = _psqms_re.search(p, raw)

            if m:
                size = _psqms_normalize_size(m.group(1), m.group(2))

                if size:
                    return size

        # 2. 兼容 [] 中的简写，比如 [29.5G]
        m = _psqms_re.search(
            r"(?i)[\[\(（【]\s*(\d+(?:\.\d+)?)\s*(T|G|M|TB|GB|MB)\s*[\]\)）】]",
            raw
        )

        if m:
            size = _psqms_normalize_size(m.group(1), m.group(2))

            if size:
                return size

        # 3. 从磁力链接 xl=字节数 中解析
        # magnet:?xt=xxx&dn=xxx&xl=42125203739
        m = _psqms_re.search(r"(?i)(?:[?&]|\\u0026)xl=(\d{6,})", raw)

        if m:
            size = _psqms_format_bytes(m.group(1))

            if size:
                return size

        # 4. 有些 JSON 会转义成 \u0026xl=数字
        m = _psqms_re.search(r"(?i)xl[=:](\d{6,})", raw)

        if m:
            size = _psqms_format_bytes(m.group(1))

            if size:
                return size

        return ""

    except Exception:
        return ""


print("[PANSOU QIWEI FIX MAGNET SIZE] loaded")
# ===== PANSOU_QIWEI_FIX_MAGNET_SIZE_END =====

# ===== PANSOU_QIWEI_FIX_V6_SEARCH_PAGE_BEGIN =====
# PanSou 七味式补丁 v6
# 搜索二级分类只允许第一页返回，page > 1 返回空，防止下滑追加重复二级目录。

import re as _psqv6_re


try:
    _PSQV6_PREV_SEARCH = PanSouSpider.searchContent
    _PSQV6_PREV_SEARCH_PAGE = PanSouSpider.searchContentPage
except Exception:
    _PSQV6_PREV_SEARCH = None
    _PSQV6_PREV_SEARCH_PAGE = None


def _psqv6_empty(page=1):
    try:
        page = int(page)
    except Exception:
        page = 1

    return {
        "list": [],
        "page": page,
        "pagecount": 1,
        "limit": 0,
        "total": 0
    }


def _psqv6_to_page(pg):
    try:
        p = int(pg)
    except Exception:
        p = 1

    if p < 1:
        p = 1

    return p


def _psqv6_is_second_group_item(v):
    try:
        if not isinstance(v, dict):
            return False

        vid = str(v.get("vod_id") or "")
        name = str(v.get("vod_name") or "")

        if vid.startswith("psq|group|"):
            return True

        words = [
            "夸克",
            "115",
            "磁力",
            "百度",
            "UC",
            "阿里",
            "迅雷",
            "123",
            "移动",
            "天翼",
            "PikPak",
            "电驴",
            "其他网盘"
        ]

        return any(w in name for w in words)

    except Exception:
        return False


def _psqv6_group_key(v):
    try:
        name = str(v.get("vod_name") or "")
        low = name.lower()

        if "夸克" in name or "quark" in low:
            return "group|quark"

        if "115" in name:
            return "group|115"

        if "磁力" in name or "magnet" in low:
            return "group|magnet"

        if "百度" in name or "baidu" in low:
            return "group|baidu"

        if "UC" in name or "uc" in low:
            return "group|uc"

        if "阿里" in name or "aliyun" in low or "alipan" in low:
            return "group|aliyun"

        if "迅雷" in name or "xunlei" in low:
            return "group|xunlei"

        if "123" in name:
            return "group|123"

        if "移动" in name or "mobile" in low or "139" in low:
            return "group|mobile"

        if "天翼" in name or "tianyi" in low or "189" in low:
            return "group|tianyi"

        if "pikpak" in low:
            return "group|pikpak"

        if "电驴" in name or "ed2k" in low:
            return "group|ed2k"

        if "其他" in name:
            return "group|other"

        vid = str(v.get("vod_id") or "")
        if vid:
            return "id|" + vid

        return "name|" + name

    except Exception:
        return repr(v)


def _psqv6_dedupe_second_groups(lst):
    """
    对第一页二级分类再做一次保险去重。
    """

    out = []
    seen = set()

    for v in lst or []:
        try:
            if not isinstance(v, dict):
                continue

            if _psqv6_is_second_group_item(v):
                key = _psqv6_group_key(v)
            else:
                key = str(v.get("vod_id") or "") or str(v.get("vod_name") or "") or repr(v)

            if key in seen:
                continue

            seen.add(key)
            out.append(v)

        except Exception:
            out.append(v)

    return out


def _psqv6_fix_ret_page1(ret):
    """
    page=1 返回结果修正：
    1. 二级分类去重；
    2. 强制 pagecount=1；
    3. total/limit 等于二级分类数量。
    """

    try:
        if not isinstance(ret, dict):
            return ret

        lst = ret.get("list")

        if not isinstance(lst, list):
            return ret

        new_list = _psqv6_dedupe_second_groups(lst)

        ret["list"] = new_list
        ret["page"] = 1
        ret["pagecount"] = 1
        ret["limit"] = len(new_list)
        ret["total"] = len(new_list)

        return ret

    except Exception:
        return ret


def _psqv6_searchContent(self, key, quick=False, pg="1"):
    """
    搜索入口：
    只允许 page=1 返回二级分类。
    page>1 返回空，避免壳层下滑追加重复二级目录。
    """

    page = _psqv6_to_page(pg)

    if page > 1:
        print("[PANSOU QIWEI FIX V6] block search page >", page)
        return _psqv6_empty(page)

    try:
        if _PSQV6_PREV_SEARCH:
            ret = _PSQV6_PREV_SEARCH(self, key, quick, "1")
        else:
            ret = _psqv6_empty(1)

        return _psqv6_fix_ret_page1(ret)

    except Exception as e:
        print("[PANSOU QIWEI FIX V6] searchContent error:", e)
        return _psqv6_empty(page)


def _psqv6_searchContentPage(self, key, quick, page):
    """
    搜索翻页入口：
    page=1 返回二级分类；
    page>1 返回空。
    """

    page_i = _psqv6_to_page(page)

    if page_i > 1:
        print("[PANSOU QIWEI FIX V6] block searchContentPage page >", page_i)
        return _psqv6_empty(page_i)

    try:
        # 注意这里不要调用 PREV_SEARCH_PAGE。
        # 因为 PREV_SEARCH_PAGE 有可能又走旧翻页逻辑。
        # 直接调用 PREV_SEARCH 且固定 pg=1。
        if _PSQV6_PREV_SEARCH:
            ret = _PSQV6_PREV_SEARCH(self, key, quick, "1")
        elif _PSQV6_PREV_SEARCH_PAGE:
            ret = _PSQV6_PREV_SEARCH_PAGE(self, key, quick, "1")
        else:
            ret = _psqv6_empty(1)

        return _psqv6_fix_ret_page1(ret)

    except Exception as e:
        print("[PANSOU QIWEI FIX V6] searchContentPage error:", e)
        return _psqv6_empty(page_i)


PanSouSpider.searchContent = _psqv6_searchContent
PanSouSpider.searchContentPage = _psqv6_searchContentPage

Spider = PanSouSpider

print("[PANSOU QIWEI FIX V6 SEARCH PAGE] loaded")
# ===== PANSOU_QIWEI_FIX_V6_SEARCH_PAGE_END =====

# ===== PANSOU_FINAL_MAGNET_115_OPENLIST_PATCH_BEGIN =====
# PanSou 最终磁力/ed2k增强补丁
# 功能：
# 1. 115云下载：提交 magnet / ed2k 到115离线；
# 2. 下载状态：查询115离线任务、解析文件、写入本地缓存；
# 3. 播放列表：读取115缓存生成播放项，按剧集/自然顺序排列；
# 4. 播放列表点击：优先用完整文件名搜索 OpenList，失败回退115播放；
# 5. OpenList 查询：刷新、搜N、取直链播放；
# 6. 磁力播放 / ed2k播放：push:// 推送；
# 7. 覆盖七味补丁里的空壳函数。
import os as _pf_os
import re as _pf_re
import ssl as _pf_ssl
import json as _pf_json
import time as _pf_time
import base64 as _pf_base64
import hashlib as _pf_hashlib
import threading as _pf_threading
import requests as _pf_requests
from urllib.parse import quote as _pf_quote, unquote as _pf_unquote
from requests.adapters import HTTPAdapter as _pf_HTTPAdapter

try:
    import urllib3 as _pf_urllib3
    _pf_urllib3.disable_warnings()
except Exception:
    pass


class _PF_SSLAdapter(_pf_HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        ctx = _pf_ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = _pf_ssl.CERT_NONE
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(connections, maxsize, block=block, **kwargs)

    def proxy_manager_for(self, proxy, **kwargs):
        ctx = _pf_ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = _pf_ssl.CERT_NONE
        kwargs["ssl_context"] = ctx
        return super().proxy_manager_for(proxy, **kwargs)


try:
    _PF_TARGET = PanSouSpider
except Exception:
    _PF_TARGET = globals().get("Spider")

if _PF_TARGET is None:
    print("[PANSOU FINAL PATCH] no target class, skip")
else:
    try:
        _PF_PREV_INIT = _PF_TARGET.init
    except Exception:
        _PF_PREV_INIT = None

    try:
        _PF_PREV_PLAYER = _PF_TARGET.playerContent
    except Exception:
        _PF_PREV_PLAYER = None

    # ============================================================
    # 基础工具
    # ============================================================
    def _pf_parse_ext(extend):
        try:
            if not extend:
                return {}
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _pf_json.loads(extend)
            return {}
        except Exception:
            return {}

    def _pf_bool(v, default=False):
        try:
            if isinstance(v, bool):
                return v
            if isinstance(v, int):
                return v != 0
            if isinstance(v, str):
                s = v.strip().lower()
                if s in ["1", "true", "yes", "y", "on"]:
                    return True
                if s in ["0", "false", "no", "n", "off", ""]:
                    return False
            return bool(v)
        except Exception:
            return default

    def _pf_ua(self):
        try:
            if hasattr(self, "HEADERS"):
                return self.HEADERS.get("User-Agent", "Mozilla/5.0")
            if hasattr(self, "headers"):
                return self.headers.get("User-Agent", "Mozilla/5.0")
        except Exception:
            pass
        return "Mozilla/5.0"

    def _pf_clean_name(self, name, limit=160):
        try:
            if hasattr(self, "_clean_name"):
                return self._clean_name(name, limit)
        except Exception:
            pass
        try:
            name = str(name or "")
            name = name.replace("#", "＃").replace("$", "＄")
            name = _pf_re.sub(r"\s+", " ", name).strip()
            if not name:
                name = "资源"
            return name[:limit]
        except Exception:
            return "资源"

    def _pf_b64e_text(text):
        try:
            return _pf_base64.urlsafe_b64encode(str(text or "").encode("utf-8")).decode("utf-8").rstrip("=")
        except Exception:
            return ""

    def _pf_b64d_text(text):
        try:
            text = str(text or "")
            text += "=" * (-len(text) % 4)
            return _pf_base64.urlsafe_b64decode(text.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""

    def _pf_b64e_json(obj):
        try:
            return _pf_base64.b64encode(_pf_json.dumps(obj, ensure_ascii=False).encode("utf-8")).decode("utf-8")
        except Exception:
            return ""

    def _pf_b64d_json(text):
        try:
            text = str(text or "")
            text += "=" * (-len(text) % 4)
            return _pf_json.loads(_pf_base64.b64decode(text.encode("utf-8")).decode("utf-8"))
        except Exception:
            return []

    def _pf_decode_payload(self, pid):
        try:
            if hasattr(self, "_decode_id"):
                return self._decode_id(pid)
        except Exception:
            pass
        try:
            s = str(pid or "")
            s += "=" * (-len(s) % 4)
            return _pf_json.loads(_pf_base64.urlsafe_b64decode(s.encode("utf-8")).decode("utf-8"))
        except Exception:
            return {}

    def _pf_encode_payload(self, obj):
        try:
            if hasattr(self, "_encode_id"):
                return self._encode_id(obj)
        except Exception:
            pass
        try:
            txt = _pf_json.dumps(obj, ensure_ascii=False)
            return _pf_base64.urlsafe_b64encode(txt.encode("utf-8")).decode("utf-8").rstrip("=")
        except Exception:
            return ""

    def _pf_normalize_magnet(self, url):
        try:
            if hasattr(self, "_normalize_magnet"):
                x = self._normalize_magnet(url)
                if x:
                    return x
        except Exception:
            pass
        try:
            url = str(url or "").strip()
            url = url.replace("&amp;", "&")
            if url.startswith("push://"):
                url = url.replace("push://", "", 1).replace("#0agent", "")
            if "%3A" in url or "%3F" in url or "%26" in url:
                url = _pf_unquote(url)
            m = _pf_re.search(r"(magnet:\?[^\s\"'<>]+)", url, _pf_re.I)
            if m:
                url = m.group(1)
            url = _pf_re.sub(r"\s+", "", url)
            if not url.startswith("magnet:"):
                return ""
            if "urn:btih:" not in url.lower():
                return ""
            return url
        except Exception:
            return ""

    def _pf_normalize_ed2k(url):
        try:
            url = str(url or "").strip()
            url = url.replace("&amp;", "&")
            if url.startswith("push://"):
                url = url.replace("push://", "", 1).replace("#0agent", "")
            if "%3A" in url or "%2F" in url:
                url = _pf_unquote(url)
            m = _pf_re.search(r"(ed2k://[^\s\"'<>]+)", url, _pf_re.I)
            if m:
                url = m.group(1)
            if url.lower().startswith("ed2k://"):
                return url
            return ""
        except Exception:
            return ""

    def _pf_extract_btih(text):
        try:
            text = str(text or "")
            m = _pf_re.search(r"btih:([a-fA-F0-9]{40})", text, _pf_re.I)
            if m:
                return m.group(1).lower()
            m = _pf_re.search(r"btih:([A-Z2-7]{32})", text, _pf_re.I)
            if m:
                return m.group(1).lower()
            m = _pf_re.search(r"\b([a-fA-F0-9]{40})\b", text)
            if m:
                return m.group(1).lower()
        except Exception:
            pass
        return ""

    def _pf_link_key(link):
        try:
            h = _pf_extract_btih(link)
            if h:
                return h
            return _pf_hashlib.md5(str(link or "").encode("utf-8")).hexdigest()
        except Exception:
            return _pf_hashlib.md5(str(link or "").encode("utf-8")).hexdigest()

    def _pf_extract_dn(link):
        try:
            m = _pf_re.search(r"[?&]dn=([^&]+)", str(link or ""), _pf_re.I)
            if m:
                return _pf_unquote(m.group(1)).strip()
        except Exception:
            pass
        return ""

    def _pf_new_session():
        s = _pf_requests.Session()
        s.verify = False
        try:
            s.mount("http://", _PF_SSLAdapter(max_retries=2))
            s.mount("https://", _PF_SSLAdapter(max_retries=2))
        except Exception:
            pass
        return s

    def _pf_ack(self):
        try:
            url = (
                getattr(self, "wait_video_url", "")
                or getattr(self, "qw_wait_video_url", "")
                or getattr(self, "ack_mp4", "")
                or "https://vd2.bdstatic.com/mda-nj5kxa8kr7wgq6ie/sc/cae_h264_nowatermark/1653272065989267185/mda-nj5kxa8kr7wgq6ie.mp4"
            )
            ret = {
                "parse": 0,
                "playUrl": "",
                "url": url,
                "header": {
                    "User-Agent": _pf_ua(self)
                }
            }
            pic = getattr(self, "last_vod_pic", "") or ""
            if pic:
                ret["pic"] = pic
                ret["poster"] = pic
            return ret
        except Exception:
            return {
                "parse": 1,
                "playUrl": "",
                "url": ""
            }

    # ============================================================
    # init
    # ============================================================
    def _pf_init(self, extend=""):
        ret = None
        if _PF_PREV_INIT:
            try:
                ret = _PF_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU FINAL INIT] prev init error:", e)

        ext = _pf_parse_ext(extend)

        try:
            self.pan_115_cookie = str(ext.get("pan_115_cookie", getattr(self, "pan_115_cookie", "")) or "").strip()
            self.confirm_115 = _pf_bool(ext.get("confirm_115", getattr(self, "confirm_115", False)), False)
            if not hasattr(self, "confirm_cache"):
                self.confirm_cache = set()

            self.cache_115_file = str(
                ext.get(
                    "cache_115_file",
                    getattr(self, "cache_115_file", "/storage/emulated/0/Download/115api_cache/115_cache.json")
                )
            ).strip()

            self.pan_115_save_cid = str(ext.get("pan_115_save_cid", getattr(self, "pan_115_save_cid", "")) or "").strip()

            try:
                self.offline_115_timeout = max(30, int(ext.get("offline_115_timeout", getattr(self, "offline_115_timeout", 180))))
            except Exception:
                self.offline_115_timeout = 180

            try:
                self.offline_115_poll_interval = max(3, int(ext.get("offline_115_poll_interval", getattr(self, "offline_115_poll_interval", 5))))
            except Exception:
                self.offline_115_poll_interval = 5

            try:
                self.min_115_video_size = int(ext.get("min_115_video_size", getattr(self, "min_115_video_size", 100 * 1024 * 1024)))
            except Exception:
                self.min_115_video_size = 100 * 1024 * 1024

            self.openlist_url = str(ext.get("openlist_url", getattr(self, "openlist_url", "")) or "").strip().rstrip("/")
            if self.openlist_url and not self.openlist_url.startswith(("http://", "https://")):
                self.openlist_url = "http://" + self.openlist_url.lstrip("/")

            self.openlist_token = str(ext.get("openlist_token", getattr(self, "openlist_token", "")) or "").strip()

            self.openlist_parent = str(ext.get("openlist_parent", getattr(self, "openlist_parent", "/云下载")) or "/云下载").strip()
            if self.openlist_parent and not self.openlist_parent.startswith("/"):
                self.openlist_parent = "/" + self.openlist_parent

            self.openlist_force_dav = _pf_bool(ext.get("openlist_force_dav", getattr(self, "openlist_force_dav", False)), False)
            self.openlist_test_stream = _pf_bool(ext.get("openlist_test_stream", getattr(self, "openlist_test_stream", False)), False)
            self.test_m3u8 = str(ext.get("test_m3u8", getattr(self, "test_m3u8", "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8")) or "").strip()

            try:
                self.openlist_search_cache_ttl = max(0, int(ext.get("openlist_search_cache_ttl", getattr(self, "openlist_search_cache_ttl", 300))))
            except Exception:
                self.openlist_search_cache_ttl = 300

            try:
                self.openlist_refresh_latest_n = max(1, int(ext.get("openlist_refresh_latest_n", getattr(self, "openlist_refresh_latest_n", 3))))
            except Exception:
                self.openlist_refresh_latest_n = 3

            self.ack_mp4 = str(
                ext.get(
                    "ack_mp4",
                    getattr(
                        self,
                        "ack_mp4",
                        "https://vd2.bdstatic.com/mda-nj5kxa8kr7wgq6ie/sc/cae_h264_nowatermark/1653272065989267185/mda-nj5kxa8kr7wgq6ie.mp4"
                    )
                )
            ).strip()

            self.wait_video_url = str(
                ext.get("wait_video_url", ext.get("qw_wait_video_url", getattr(self, "wait_video_url", self.ack_mp4)))
                or self.ack_mp4
            ).strip()

            if not hasattr(self, "_openlist_search_cache"):
                self._openlist_search_cache = {}
            if not hasattr(self, "_openlist_recent_files"):
                self._openlist_recent_files = []

            self.openlist_session = _pf_requests.Session()
            self.openlist_session.verify = False
            self.openlist_session.headers.clear()
            try:
                self.openlist_session.mount("http://", _PF_SSLAdapter(max_retries=2))
                self.openlist_session.mount("https://", _PF_SSLAdapter(max_retries=2))
            except Exception:
                pass

            print("[PANSOU FINAL PATCH] enabled")
            print("[PANSOU FINAL PATCH] 115 cookie:", "已配置" if self.pan_115_cookie else "未配置")
            print("[PANSOU FINAL PATCH] OpenList:", self.openlist_url or "未配置")
            print("[PANSOU FINAL PATCH] 115 cache:", self.cache_115_file)
        except Exception as e:
            print("[PANSOU FINAL INIT] error:", e)

        return ret if ret is not None else {}

    # ============================================================
    # 115 缓存
    # ============================================================
    def _pf_115_cache_paths(self):
        paths = []
        candidates = [
            getattr(self, "cache_115_file", "") or "",
            "/storage/emulated/0/Download/115api_cache/115_cache.json",
            "/sdcard/Download/115api_cache/115_cache.json",
            "/storage/emulated/0/Download/115_cache.json",
            "/sdcard/Download/115_cache.json",
            "/sdcard/115_cache.json",
            "/tmp/okys_115_offline_cache.json",
        ]
        for p in candidates:
            p = str(p or "").strip()
            if p and p not in paths:
                paths.append(p)
        return paths

    def _pf_115_cache_load(self):
        for p in _pf_115_cache_paths(self):
            try:
                if _pf_os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        data = _pf_json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                    if "magnets" not in data or not isinstance(data.get("magnets"), dict):
                        data["magnets"] = {}
                    if "files" not in data or not isinstance(data.get("files"), dict):
                        data["files"] = {}
                    self.cache_115_file = p
                    return data
            except Exception as e:
                print("[115 cache] load error:", p, e)
        return {
            "magnets": {},
            "files": {}
        }

    def _pf_115_cache_save(self, data):
        for p in _pf_115_cache_paths(self):
            try:
                d = _pf_os.path.dirname(p)
                if d:
                    _pf_os.makedirs(d, exist_ok=True)
                tmp = p + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    _pf_json.dump(data, f, ensure_ascii=False, indent=2)
                try:
                    _pf_os.replace(tmp, p)
                except Exception:
                    with open(p, "w", encoding="utf-8") as f:
                        _pf_json.dump(data, f, ensure_ascii=False, indent=2)
                self.cache_115_file = p
                print("[115 cache] save ok:", p)
                return True
            except Exception as e:
                print("[115 cache] save error:", p, e)
        return False

    # ============================================================
    # 115 API
    # ============================================================
    def _pf_115_headers(self):
        return {
            "User-Agent": _pf_ua(self),
            "Cookie": getattr(self, "pan_115_cookie", ""),
            "Origin": "https://115.com",
            "Referer": "https://115.com/web/lixian/",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

    def _pf_115_add_task(self, link):
        if not getattr(self, "pan_115_cookie", ""):
            return {
                "state": False,
                "msg": "missing 115 cookie"
            }

        link = str(link or "").strip()
        if not link:
            return {
                "state": False,
                "msg": "empty link"
            }

        mg = _pf_normalize_magnet(self, link)
        ed = _pf_normalize_ed2k(link)
        if mg:
            link = mg
        elif ed:
            link = ed

        try:
            s = _pf_new_session()
            headers = _pf_115_headers(self)

            sign_resp = s.get("https://115.com/?ct=offline&ac=space", headers=headers, timeout=10)
            try:
                sign_json = sign_resp.json()
            except Exception:
                return {
                    "state": False,
                    "msg": "sign non-json",
                    "raw": sign_resp.text[:200]
                }

            if not sign_json.get("state"):
                print("[115 add] sign failed:", sign_json)
                return {
                    "state": False,
                    "msg": "sign fail",
                    "raw": sign_json
                }

            sign = sign_json.get("sign", "")
            req_time = sign_json.get("time", "")

            uid = ""
            m = _pf_re.search(r"UID=(\d+)", getattr(self, "pan_115_cookie", ""))
            if m:
                uid = m.group(1)

            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"

            post_data = {
                "url": link,
                "uid": uid,
                "sign": sign,
                "time": req_time
            }

            if getattr(self, "pan_115_save_cid", ""):
                post_data["wp_path_id"] = getattr(self, "pan_115_save_cid", "")

            add_resp = s.post(
                "https://115.com/web/lixian/?ct=lixian&ac=add_task_url",
                data=post_data,
                headers=headers,
                timeout=15
            )

            try:
                add_json = add_resp.json()
            except Exception:
                return {
                    "state": False,
                    "msg": "add non-json",
                    "raw": add_resp.text[:200]
                }

            ok = bool(add_json.get("state") or add_json.get("errcode") == 0)
            print("[115 add]", "success" if ok else "failed", add_json)

            return {
                "state": ok,
                "btih": _pf_extract_btih(link),
                "task": add_json,
                "raw": add_json
            }
        except Exception as e:
            print("[115 add] error:", e)
            return {
                "state": False,
                "msg": str(e)
            }

    def _pf_115_task_list(self, page=1):
        if not getattr(self, "pan_115_cookie", ""):
            return []

        urls = [
            "https://115.com/web/lixian/?ct=lixian&ac=task_lists",
            "https://115.com/web/lixian/?ct=lixian&ac=task_list",
        ]

        headers = _pf_115_headers(self)
        params = {
            "page": int(page or 1),
            "limit": 100
        }

        for url in urls:
            try:
                s = _pf_new_session()
                r = s.get(url, headers=headers, params=params, timeout=15)
                data = r.json()
                tasks = data.get("tasks") or data.get("data") or data.get("list") or []
                if isinstance(tasks, dict):
                    tasks = tasks.get("tasks") or tasks.get("list") or []
                if isinstance(tasks, list):
                    return tasks
            except Exception as e:
                print("[115 task list] error:", e)
        return []

    def _pf_115_find_task_by_link(self, link):
        key = _pf_link_key(link)
        btih = _pf_extract_btih(link)
        raw_link = str(link or "").lower()

        tasks = _pf_115_task_list(self, 1)
        for t in tasks:
            try:
                raw = _pf_json.dumps(t, ensure_ascii=False).lower()
                if btih and btih in raw:
                    return t
                if raw_link and raw_link in raw:
                    return t
                h = t.get("info_hash") or t.get("hash") or t.get("bt_hash") or t.get("sha1") or ""
                if h and str(h).lower() in [btih, key]:
                    return t
            except Exception:
                pass
        return None

    def _pf_115_task_done(task):
        if not task:
            return False

        raw = _pf_json.dumps(task, ensure_ascii=False).lower()
        if any(w in raw for w in ["完成", "已完成", "success", "finished", "done"]):
            return True

        status = task.get("status") or task.get("state") or task.get("percentDone") or task.get("percent") or task.get("progress")
        try:
            if str(status).lower() in ["2", "100", "done", "success", "finished"]:
                return True
            if float(status) >= 100:
                return True
        except Exception:
            pass

        return False

    def _pf_115_task_failed(task):
        if not task:
            return False

        raw = _pf_json.dumps(task, ensure_ascii=False).lower()
        if any(w in raw for w in ["失败", "error", "failed", "fail"]):
            return True

        status = task.get("status") or task.get("state")
        if str(status).lower() in ["-1", "failed", "error"]:
            return True

        return False

    def _pf_115_task_cid(self, task):
        if not task:
            return str(getattr(self, "pan_115_save_cid", "") or "")

        keys = ["cid", "save_cid", "wp_path_id", "file_id", "to_cid", "target_cid", "parent_id"]
        for k in keys:
            v = task.get(k)
            if v:
                return str(v)

        for k in ["file", "folder", "data", "info"]:
            sub = task.get(k)
            if isinstance(sub, dict):
                for kk in keys:
                    v = sub.get(kk)
                    if v:
                        return str(v)

        return str(getattr(self, "pan_115_save_cid", "") or "")

    def _pf_parse115_file(item, parent_cid=""):
        try:
            name = item.get("n") or item.get("name") or item.get("file_name") or item.get("fname") or ""
            fid = item.get("fid") or item.get("file_id") or item.get("id") or ""
            cid = item.get("cid") or item.get("parent_id") or parent_cid or ""
            pc = item.get("pc") or item.get("pick_code") or item.get("pickcode") or item.get("pickCode") or ""
            size = int(item.get("s") or item.get("size") or item.get("file_size") or 0)
            sha1 = item.get("sha") or item.get("sha1") or item.get("file_sha1") or ""
            return {
                "fid": str(fid),
                "cid": str(cid),
                "name": str(name),
                "size": size,
                "pickcode": str(pc),
                "sha1": str(sha1)
            }
        except Exception:
            return {
                "fid": "",
                "cid": str(parent_cid or ""),
                "name": "",
                "size": 0,
                "pickcode": "",
                "sha1": ""
            }

    def _pf_is_video_file(name):
        try:
            name = str(name or "").lower()
            return name.endswith((
                ".mp4", ".mkv", ".iso", ".avi", ".mov", ".wmv", ".flv",
                ".webm", ".m4v", ".rmvb", ".ts", ".m2ts", ".vob", ".f4v",
                ".3gp", ".mpg", ".mpeg", ".m3u8"
            ))
        except Exception:
            return False

    def _pf_choose_video_files(self, files, min_size=None, parent_cid=""):
        if min_size is None:
            min_size = int(getattr(self, "min_115_video_size", 100 * 1024 * 1024) or 0)

        bad_words = ["sample", "trailer", "preview", "预告", "样片", "花絮", "广告"]
        out = []
        seen = set()

        for it in files or []:
            info = _pf_parse115_file(it, parent_cid)
            name = info.get("name") or ""
            size = int(info.get("size") or 0)
            low = name.lower()

            if not name:
                continue
            if not _pf_is_video_file(name):
                continue
            if size < min_size:
                continue
            if any(w in low for w in bad_words):
                continue

            k = info.get("fid") or info.get("pickcode") or name
            if k in seen:
                continue
            seen.add(k)
            out.append(info)

        out.sort(key=lambda x: int(x.get("size") or 0), reverse=True)
        return out

    def _pf_115_list_files(self, cid="0", limit=500):
        if not getattr(self, "pan_115_cookie", ""):
            return []

        try:
            limit = max(20, min(500, int(limit)))
        except Exception:
            limit = 500

        headers = _pf_115_headers(self)
        params = {
            "cid": str(cid or "0"),
            "offset": 0,
            "limit": limit,
            "show_dir": 1,
            "format": "json"
        }

        try:
            s = _pf_new_session()
            r = s.get("https://webapi.115.com/files", headers=headers, params=params, timeout=15)
            data = r.json()
            files = data.get("data") or data.get("files") or []
            if isinstance(files, list):
                return files
        except Exception as e:
            print("[115 files] error:", e)

        return []

    def _pf_115_submit_only(self, link):
        try:
            mg = _pf_normalize_magnet(self, link)
            ed = _pf_normalize_ed2k(link)
            if mg:
                link = mg
            elif ed:
                link = ed

            key = _pf_link_key(link)
            btih = _pf_extract_btih(link)
            cache = _pf_115_cache_load(self)
            rec = cache.get("magnets", {}).get(key)

            if rec:
                print("[115 submit] cache exists:", rec.get("status"))
                return rec

            task = _pf_115_find_task_by_link(self, link)

            if task:
                rec = {
                    "magnet": link,
                    "key": key,
                    "btih": btih,
                    "status": "done" if _pf_115_task_done(task) else "downloading",
                    "task": task,
                    "cid": _pf_115_task_cid(self, task),
                    "files": [],
                    "best": None,
                    "update_time": int(_pf_time.time())
                }
                cache["magnets"][key] = rec
                _pf_115_cache_save(self, cache)
                return rec

            add = _pf_115_add_task(self, link)
            rec = {
                "magnet": link,
                "key": key,
                "btih": btih,
                "status": "submitted" if add.get("state") else "add_failed",
                "task": add.get("task") or add.get("raw") or {},
                "cid": "",
                "files": [],
                "best": None,
                "update_time": int(_pf_time.time())
            }

            cache["magnets"][key] = rec
            _pf_115_cache_save(self, cache)
            return rec
        except Exception as e:
            print("[115 submit only] error:", e)
            return None

    def _pf_115_resolve_files(self, link, wait=False):
        try:
            mg = _pf_normalize_magnet(self, link)
            ed = _pf_normalize_ed2k(link)
            if mg:
                link = mg
            elif ed:
                link = ed

            key = _pf_link_key(link)
            btih = _pf_extract_btih(link)

            cache = _pf_115_cache_load(self)
            rec = cache.get("magnets", {}).get(key)

            if isinstance(rec, dict) and rec.get("status") == "done" and (rec.get("files") or rec.get("best")):
                return rec

            task = _pf_115_find_task_by_link(self, link)

            if not task:
                if rec and rec.get("task"):
                    task = rec.get("task")
                else:
                    rec = rec or {
                        "magnet": link,
                        "key": key,
                        "btih": btih,
                        "status": "not_found",
                        "cid": "",
                        "task": {},
                        "files": [],
                        "best": None,
                        "update_time": int(_pf_time.time())
                    }
                    cache["magnets"][key] = rec
                    _pf_115_cache_save(self, cache)
                    return rec

            done = _pf_115_task_done(task)
            failed = _pf_115_task_failed(task)
            cid = _pf_115_task_cid(self, task)

            videos = []

            if done and cid:
                raw_files = _pf_115_list_files(self, cid, limit=500)
                videos = _pf_choose_video_files(self, raw_files, getattr(self, "min_115_video_size", 0), parent_cid=cid)

            if done and not videos:
                inner = task.get("files") or task.get("file_list") or task.get("filelist") or []
                if isinstance(inner, list):
                    videos = _pf_choose_video_files(self, inner, getattr(self, "min_115_video_size", 0), parent_cid=cid)

            best = videos[0] if videos else None
            status = "done" if done else ("failed" if failed else "downloading")

            rec = {
                "magnet": link,
                "key": key,
                "btih": btih,
                "status": status,
                "cid": cid,
                "task": task or {},
                "files": videos,
                "best": best,
                "update_time": int(_pf_time.time())
            }

            cache["magnets"][key] = rec

            for f in videos:
                fid = f.get("fid") or ""
                pc = f.get("pickcode") or ""
                fk = fid or pc
                if fk:
                    cache["files"][fk] = {
                        "fid": fid,
                        "pickcode": pc,
                        "cid": f.get("cid") or cid,
                        "name": f.get("name"),
                        "size": f.get("size"),
                        "sha1": f.get("sha1"),
                        "magnet_key": key,
                        "btih": btih,
                        "update_time": int(_pf_time.time())
                    }

            _pf_115_cache_save(self, cache)

            print("[115 resolve] status=%s cid=%s videos=%s best=%s" % (
                status,
                cid,
                len(videos),
                (best or {}).get("name")
            ))

            return rec
        except Exception as e:
            print("[115 resolve] error:", e)
            return None

    # ============================================================
    # 播放列表
    # ============================================================
    def _pf_nat_parts(text):
        try:
            parts = _pf_re.split(r"(\d+)", str(text or "").lower())
            out = []
            for p in parts:
                out.append(int(p) if p.isdigit() else p)
            return out
        except Exception:
            return [str(text or "").lower()]

    def _pf_episode_key(name):
        try:
            raw = str(name or "")
            s = raw.lower()

            m = _pf_re.search(r"\bs(\d{1,2})e(\d{1,4})\b", s, _pf_re.I)
            if m:
                return (int(m.group(1)), int(m.group(2)), _pf_nat_parts(raw))

            m = _pf_re.search(r"\b(\d{1,2})x(\d{1,4})\b", s, _pf_re.I)
            if m:
                return (int(m.group(1)), int(m.group(2)), _pf_nat_parts(raw))

            m = _pf_re.search(r"\b(?:ep|e)(\d{1,4})\b", s, _pf_re.I)
            if m:
                return (1, int(m.group(1)), _pf_nat_parts(raw))

            m = _pf_re.search(r"第\s*(\d{1,4})\s*集", raw)
            if m:
                return (1, int(m.group(1)), _pf_nat_parts(raw))

            return (999, 999999, _pf_nat_parts(raw))
        except Exception:
            return (999, 999999, _pf_nat_parts(name))

    def _pf_build115CachedFilePlayItems(self, links):
        try:
            if not links:
                return ""

            raw_links = []
            for x in links:
                if isinstance(x, dict):
                    raw_links.append(x.get("url") or x.get("magnet") or "")
                else:
                    raw_links.append(str(x or ""))

            cache = _pf_115_cache_load(self)
            items_data = []
            seen = set()

            for link in raw_links:
                key = _pf_link_key(link)
                rec = cache.get("magnets", {}).get(key)
                if not rec:
                    continue

                for f in rec.get("files") or []:
                    name = f.get("name") or ""
                    size = int(f.get("size") or 0)
                    fid = f.get("fid") or ""
                    pc = f.get("pickcode") or ""
                    fk = fid or pc

                    if not name or not fk:
                        continue
                    if not _pf_is_video_file(name):
                        continue
                    if size < int(getattr(self, "min_115_video_size", 0) or 0):
                        continue
                    if fk in seen:
                        continue

                    seen.add(fk)
                    items_data.append({
                        "name": name,
                        "size": size,
                        "fk": fk
                    })

            if not items_data:
                return ""

            items_data.sort(key=lambda x: _pf_episode_key(x.get("name") or ""))

            items = []
            for f in items_data:
                name = f.get("name") or ""
                size = int(f.get("size") or 0)
                fk = f.get("fk") or ""
                size_gb = size / 1024 / 1024 / 1024
                show = _pf_clean_name(self, "%s [%.2fG]" % (name, size_gb), 180)
                items.append("%s$__115_FILE__|%s" % (show, fk))

            print("[115 playlist] items =", len(items))
            return "#".join(items)
        except Exception as e:
            print("[115 playlist] error:", e)
            return ""

    # ============================================================
    # 115 播放
    # ============================================================
    def _pf_json_find_video_urls(obj):
        urls = []

        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if isinstance(v, str):
                        sv = v.strip()
                        low = sv.lower()
                        if sv.startswith(("http://", "https://")) and any(t in low for t in [".m3u8", ".mp4", ".ts", "download", "video"]):
                            urls.append(sv)
                    walk(v)
            elif isinstance(x, list):
                for i in x:
                    walk(i)
            elif isinstance(x, str):
                sv = x.strip()
                low = sv.lower()
                if sv.startswith(("http://", "https://")) and any(t in low for t in [".m3u8", ".mp4", ".ts", "download", "video"]):
                    urls.append(sv)

        walk(obj)

        out = []
        seen = set()
        for u in urls:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out

    def _pf_best_video_url(urls):
        if not urls:
            return ""
        for u in urls:
            if ".m3u8" in u.lower():
                return u
        for u in urls:
            if ".mp4" in u.lower():
                return u
        for u in urls:
            if ".ts" in u.lower():
                return u
        return urls[0]

    def _pf_115_get_play_url_by_pickcode(self, pickcode):
        if not pickcode or not getattr(self, "pan_115_cookie", ""):
            return "", {}

        headers = {
            "User-Agent": _pf_ua(self),
            "Cookie": getattr(self, "pan_115_cookie", ""),
            "Referer": "https://115.com/",
            "Origin": "https://115.com",
            "Accept": "application/json, text/plain, */*",
        }

        reqs = [
            {
                "url": "https://webapi.115.com/files/video",
                "params": {
                    "pickcode": pickcode
                }
            },
            {
                "url": "https://webapi.115.com/files/video_info",
                "params": {
                    "pickcode": pickcode
                }
            },
            {
                "url": "https://webapi.115.com/files/download",
                "params": {
                    "pickcode": pickcode
                }
            },
            {
                "url": "https://proapi.115.com/android/2.0/ufile/download",
                "params": {
                    "pickcode": pickcode
                }
            },
        ]

        s = _pf_new_session()

        for req in reqs:
            try:
                r = s.get(req["url"], headers=headers, params=req["params"], timeout=15)
                text = r.text or ""

                if r.status_code != 200:
                    print("[115 play] HTTP", r.status_code, req["url"], text[:120])
                    continue

                try:
                    data = r.json()
                except Exception:
                    if text.startswith(("http://", "https://")):
                        return text.strip(), headers
                    continue

                urls = _pf_json_find_video_urls(data)
                play_url = _pf_best_video_url(urls)

                if play_url:
                    print("[115 play] hit:", req["url"])
                    return play_url, headers
            except Exception as e:
                print("[115 play] candidate error:", req["url"], e)

        return "", headers

    def _pf_115_play_file_info(self, f):
        if not f:
            return _pf_ack(self)

        pc = f.get("pickcode") or ""
        if pc:
            play_url, headers = _pf_115_get_play_url_by_pickcode(self, pc)
            if play_url:
                ret = {
                    "parse": 0,
                    "playUrl": "",
                    "url": play_url,
                    "header": headers
                }
                pic = getattr(self, "last_vod_pic", "") or ""
                if pic:
                    ret["pic"] = pic
                    ret["poster"] = pic
                return ret

        print("[115 play] failed:", f.get("name"))
        return _pf_ack(self)

    def _pf_115_status_all(self, pid):
        try:
            parts = str(pid or "").split("|", 1)
            if len(parts) < 2:
                return _pf_ack(self)

            links = _pf_b64d_json(parts[1])
            if not isinstance(links, list) or not links:
                return _pf_ack(self)

            best_file = None
            updated = 0

            for link in links:
                link = str(link or "").strip()
                if not link:
                    continue

                rec = _pf_115_resolve_files(self, link, wait=False)
                if rec:
                    updated += 1

                best = rec.get("best") if isinstance(rec, dict) else None
                if best:
                    if not best_file:
                        best_file = best
                    else:
                        try:
                            if int(best.get("size") or 0) > int(best_file.get("size") or 0):
                                best_file = best
                        except Exception:
                            pass

            print("[115 status all] updated=%s best=%s" % (updated, (best_file or {}).get("name")))

            if best_file:
                return _pf_115_play_file_info(self, best_file)

            return _pf_ack(self)
        except Exception as e:
            print("[115 status all] error:", e)
            return _pf_ack(self)

    def _pf_get_115_file_by_pid(self, pid):
        try:
            pid = str(pid or "")
            if not pid.startswith("__115_FILE__|"):
                return None

            fk = pid.split("|", 1)[1].strip()
            if not fk:
                return None

            cache = _pf_115_cache_load(self)
            files_map = cache.get("files", {}) or {}

            f = files_map.get(fk)
            if isinstance(f, dict):
                return f

            for _, item in files_map.items():
                if str(item.get("fid") or "") == fk:
                    return item
                if str(item.get("pickcode") or "") == fk:
                    return item

            for _, rec in (cache.get("magnets", {}) or {}).items():
                for item in rec.get("files") or []:
                    if str(item.get("fid") or "") == fk:
                        return item
                    if str(item.get("pickcode") or "") == fk:
                        return item
        except Exception as e:
            print("[115 get file] error:", e)
        return None

    # ============================================================
    # OpenList
    # ============================================================
    def _pf_ol_headers(self):
        return {
            "Authorization": (getattr(self, "openlist_token", "") or "").strip(),
            "Content-Type": "application/json",
            "User-Agent": _pf_ua(self)
        }

    def _pf_ol_api_post(self, api_path, payload, timeout=15):
        if not getattr(self, "openlist_url", ""):
            return {}

        url = getattr(self, "openlist_url", "").rstrip("/") + api_path

        try:
            headers = _pf_ol_headers(self)
            s = getattr(self, "openlist_session", None)
            if s is None:
                s = _pf_requests.Session()
                s.verify = False
                self.openlist_session = s

            r = s.post(url, headers=headers, json=payload, timeout=timeout, verify=False)

            if r.status_code != 200:
                print("[OpenList API]", api_path, "HTTP", r.status_code, r.text[:200])
                return {}

            data = r.json()
            if data.get("code") != 200:
                print("[OpenList API]", api_path, "code=", data.get("code"), "msg=", data.get("message"))
            return data
        except Exception as e:
            print("[OpenList API]", api_path, "error:", e)
            return {}

    def _pf_ol_norm_path(path):
        path = str(path or "/").strip()
        path = "/" + path.lstrip("/")
        if path != "/":
            path = path.rstrip("/")
        return path

    def _pf_ol_join(parent, name):
        parent = _pf_ol_norm_path(parent)
        name = str(name or "").strip("/")
        if parent == "/":
            return "/" + name
        return parent + "/" + name

    def _pf_ol_under_parent(self, path):
        try:
            parent = _pf_ol_norm_path(getattr(self, "openlist_parent", "/"))
            path = _pf_ol_norm_path(path)
            if parent == "/":
                return True
            return path == parent or path.startswith(parent.rstrip("/") + "/")
        except Exception:
            return False

    def _pf_norm_search(text):
        try:
            text = str(text or "").lower()
            text = _pf_unquote(text)
            text = _pf_re.sub(r"[\s\-_.,，。:：;；!！?？'\"“”‘’\[\]【】()（）{}《》<>「」『』/\\|&@]+", "", text)
            return text.strip()
        except Exception:
            return ""

    def _pf_ol_list_dir(self, path, per_page=200, refresh=False):
        result = []

        if not getattr(self, "openlist_url", ""):
            return result

        path = _pf_ol_norm_path(path)
        if not _pf_ol_under_parent(self, path):
            return result

        try:
            per_page = max(20, min(500, int(per_page)))
        except Exception:
            per_page = 200

        data = _pf_ol_api_post(
            self,
            "/api/fs/list",
            {
                "path": path,
                "password": "",
                "page": 1,
                "per_page": per_page,
                "refresh": bool(refresh)
            },
            25
        )

        if data.get("code") != 200:
            return result

        content = (data.get("data", {}) or {}).get("content") or []

        for it in content:
            try:
                name = str(it.get("name") or "").strip()
                if not name:
                    continue

                full_path = _pf_ol_join(path, name)
                if not _pf_ol_under_parent(self, full_path):
                    continue

                is_dir = bool(it.get("is_dir") or it.get("isDir") or it.get("type") == 1)

                try:
                    size = int(it.get("size") or 0)
                except Exception:
                    size = 0

                result.append({
                    "name": name,
                    "path": full_path,
                    "size": size,
                    "sign": it.get("sign", ""),
                    "is_dir": is_dir,
                    "parent": path,
                    "time": 0
                })
            except Exception:
                pass

        return result

    def _pf_ol_collect_depth(self, dir_path, max_depth=4, per_page=300):
        videos = []
        seen_files = set()
        seen_dirs = set()

        def walk(path, depth_left):
            if depth_left <= 0:
                return

            p = _pf_ol_norm_path(path)
            if p in seen_dirs:
                return
            seen_dirs.add(p)

            items = _pf_ol_list_dir(self, p, per_page=per_page, refresh=False)

            for it in items:
                try:
                    name = it.get("name") or ""
                    path2 = _pf_ol_norm_path(it.get("path") or "")
                    if not name or not path2:
                        continue

                    if it.get("is_dir"):
                        walk(path2, depth_left - 1)
                        continue

                    if not _pf_is_video_file(name):
                        continue

                    if path2 in seen_files:
                        continue

                    seen_files.add(path2)
                    videos.append(it)
                except Exception:
                    pass

        walk(dir_path, int(max_depth or 4))
        return videos

    def _pf_ol_search_files(self, keyword, page=1, per_page=100):
        results = []

        if not getattr(self, "openlist_url", ""):
            return results

        keyword = str(keyword or "").strip()
        if not keyword:
            return results

        try:
            page = max(1, int(page))
        except Exception:
            page = 1

        try:
            per_page = max(20, min(200, int(per_page)))
        except Exception:
            per_page = 100

        data = _pf_ol_api_post(
            self,
            "/api/fs/search",
            {
                "parent": _pf_ol_norm_path(getattr(self, "openlist_parent", "/")),
                "keywords": keyword,
                "scope": 0,
                "page": page,
                "per_page": per_page,
                "password": ""
            },
            20
        )

        if data.get("code") != 200:
            return results

        content = (data.get("data", {}) or {}).get("content") or []
        seen = set()

        for it in content:
            try:
                name = str(it.get("name") or "").strip()
                if not name:
                    continue

                parent = str(it.get("parent") or "").strip()
                path = str(it.get("path") or "").strip()
                full_path = _pf_ol_norm_path(path) if path else _pf_ol_join(parent, name)

                if not _pf_ol_under_parent(self, full_path):
                    continue

                is_dir = bool(it.get("is_dir") or it.get("isDir") or it.get("type") == 1)

                if is_dir:
                    children = _pf_ol_collect_depth(self, full_path, max_depth=4, per_page=300)
                    for c in children:
                        cp = _pf_ol_norm_path(c.get("path") or "")
                        if not cp or cp in seen:
                            continue
                        seen.add(cp)
                        results.append(c)
                    continue

                if not _pf_is_video_file(name):
                    continue

                if full_path in seen:
                    continue
                seen.add(full_path)

                try:
                    size = int(it.get("size") or 0)
                except Exception:
                    size = 0

                results.append({
                    "name": name,
                    "path": full_path,
                    "size": size,
                    "sign": it.get("sign", ""),
                    "parent": parent,
                    "is_dir": False,
                    "time": 0
                })
            except Exception as e:
                print("[OpenList search item] error:", e)

        return results

    def _pf_ol_search_by_api(self, keywords, max_pages=2, per_page=100):
        result = []
        seen = set()

        if isinstance(keywords, str):
            keywords = [keywords]

        keywords = [str(x or "").strip() for x in keywords if str(x or "").strip()]

        for kw in keywords:
            for page in range(1, int(max_pages or 2) + 1):
                files = _pf_ol_search_files(self, kw, page=page, per_page=per_page)
                if not files:
                    break
                for f in files:
                    p = _pf_ol_norm_path(f.get("path") or "")
                    if not p or p in seen:
                        continue
                    seen.add(p)
                    result.append(f)

        return result

    def _pf_score_ol_candidate(c, keywords):
        try:
            name = str(c.get("name") or "")
            path = str(c.get("path") or "")
            size = int(c.get("size") or 0)
            name_n = _pf_norm_search(name)
            path_n = _pf_norm_search(path)

            score = 0

            for k in keywords or []:
                nk = _pf_norm_search(k)
                if not nk:
                    continue
                if nk in name_n:
                    score += 10000
                elif nk in path_n:
                    score += 5000

            all_l = (name + " " + path).lower()

            if any(x in all_l for x in ["4k", "2160p", "2160", "uhd"]):
                score += 50000
            elif any(x in all_l for x in ["1080p", "1080"]):
                score += 10000
            elif any(x in all_l for x in ["720p", "720"]):
                score += 3000

            score += min(size // (100 * 1024 * 1024), 5000)

            if name.lower().endswith((".mp4", ".mkv", ".iso")):
                score += 8
            elif name.lower().endswith((".ts", ".m2ts")):
                score += 3

            return score
        except Exception:
            return 0

    def _pf_ol_keywords(title, n=5):
        title = str(title or "").strip()

        try:
            n = int(n)
        except Exception:
            n = 5

        n = max(1, min(30, n))
        keys = []

        raw = _pf_re.sub(r"\s+", "", title)
        if raw:
            keys.append(raw[:n])

        compact = _pf_re.sub(r"[\[\]【】()（）{}《》<>「」『』]", "", title)
        compact = _pf_re.sub(r"[\/\\\|\-_.,，。:：;；!！?？'\"“”‘’&@]+", "", compact)
        compact = _pf_re.sub(r"\s+", "", compact)
        if compact:
            keys.append(compact[:n])

        tokens = _pf_re.split(r"[\s\-_.,，。:：;；!！?？\[\]【】()（）{}<>/\\|]+", title)
        tokens = [x for x in tokens if len(x) >= 2]
        keys.extend(tokens[:8])

        out = []
        seen = set()
        for k in keys:
            k = str(k or "").strip()
            if k and k not in seen:
                seen.add(k)
                out.append(k)

        return out

    def _pf_ol_search_best(self, keywords):
        try:
            if isinstance(keywords, str):
                keywords = [keywords]

            keywords = [str(x or "").strip() for x in keywords if str(x or "").strip()]
            if not keywords:
                return None

            norm_keys = [_pf_norm_search(x) for x in keywords if x]
            norm_keys = [x for x in norm_keys if x]

            recent = getattr(self, "_openlist_recent_files", []) or []
            if recent:
                hits = []
                for c in recent:
                    text_n = _pf_norm_search(str(c.get("name") or "") + " " + str(c.get("path") or ""))
                    if any(k and k in text_n for k in norm_keys):
                        hits.append(c)

                if hits:
                    hits.sort(key=lambda x: (_pf_score_ol_candidate(x, keywords), int(x.get("size") or 0)), reverse=True)
                    best = hits[0]
                    print("[OpenList recent] hit:", best.get("name"), best.get("path"))
                    return best

            candidates = _pf_ol_search_by_api(self, keywords, max_pages=2, per_page=100)
            if not candidates:
                print("[OpenList search] no candidates:", keywords)
                return None

            filtered = []
            for c in candidates:
                text_n = _pf_norm_search(str(c.get("name") or "") + " " + str(c.get("path") or ""))
                if any(k and k in text_n for k in norm_keys):
                    filtered.append(c)

            if not filtered:
                print("[OpenList search] no filtered:", keywords)
                return None

            filtered.sort(key=lambda x: (_pf_score_ol_candidate(x, keywords), int(x.get("size") or 0)), reverse=True)
            best = filtered[0]
            print("[OpenList search] hit:", best.get("name"), best.get("path"))
            return best
        except Exception as e:
            print("[OpenList search best] error:", e)
            return None

    def _pf_ol_normalize_url(self, url):
        url = str(url or "").strip()
        if not url:
            return ""
        if url.startswith("//"):
            return "https:" + url
        if url.startswith(("http://", "https://")):
            return url
        if url.startswith("/"):
            return getattr(self, "openlist_url", "").rstrip("/") + url
        return getattr(self, "openlist_url", "").rstrip("/") + "/" + url.lstrip("/")

    def _pf_ol_download_url(self, full_path, sign=""):
        p = "/" + str(full_path or "").lstrip("/")
        url = getattr(self, "openlist_url", "").rstrip("/") + "/d" + _pf_quote(p, safe="/")
        if sign:
            url += ("&" if "?" in url else "?") + "sign=" + _pf_quote(str(sign))
        return url

    def _pf_ol_dav_url(self, full_path):
        p = "/" + str(full_path or "").lstrip("/")
        return getattr(self, "openlist_url", "").rstrip("/") + "/dav" + _pf_quote(p, safe="/")

    def _pf_ol_get_playable(self, file_path):
        try:
            if str(file_path or "").startswith("__115CACHE__|"):
                fk = str(file_path).split("|", 1)[1].strip()
                cache = _pf_115_cache_load(self)
                f = cache.get("files", {}).get(fk)
                if f and f.get("pickcode"):
                    return _pf_115_get_play_url_by_pickcode(self, f.get("pickcode"))
                return "", {}
        except Exception:
            pass

        file_path = _pf_ol_norm_path(file_path)

        if not _pf_ol_under_parent(self, file_path):
            return "", {}

        headers = {
            "User-Agent": _pf_ua(self)
        }

        data = _pf_ol_api_post(
            self,
            "/api/fs/get",
            {
                "path": file_path,
                "password": ""
            },
            15
        )

        if data.get("code") == 200:
            d = data.get("data", {}) or {}

            extra = d.get("header") or d.get("headers") or {}
            if isinstance(extra, dict):
                for k, v in extra.items():
                    if k and v:
                        headers[str(k)] = str(v)

            raw = d.get("raw_url") or d.get("rawUrl") or d.get("url") or ""
            if raw:
                return _pf_ol_normalize_url(self, raw), headers

            sign = d.get("sign") or ""
            return _pf_ol_download_url(self, file_path, sign), headers

        if getattr(self, "openlist_force_dav", False):
            headers["Referer"] = getattr(self, "openlist_url", "").rstrip("/") + "/"
            return _pf_ol_dav_url(self, file_path), headers

        return _pf_ol_download_url(self, file_path), headers

    def _pf_ol_decode_title(pid):
        try:
            parts = str(pid or "").split("|")
            if len(parts) >= 2:
                if parts[0] == "__OPENLIST_SEARCH__" and len(parts) >= 3:
                    b64 = parts[2]
                else:
                    b64 = parts[1]
                b64 += "=" * (-len(b64) % 4)
                return _pf_base64.b64decode(b64.encode("utf-8")).decode("utf-8")
        except Exception:
            pass
        return ""

    def _pf_ol_refresh_latest(self, title=""):
        try:
            n = max(1, int(getattr(self, "openlist_refresh_latest_n", 3) or 3))
        except Exception:
            n = 3

        parent = _pf_ol_norm_path(getattr(self, "openlist_parent", "/"))
        print("[OpenList refresh] parent=%s latest_n=%s title=%s" % (parent, n, title))

        try:
            self._openlist_search_cache.clear()
        except Exception:
            pass

        items = _pf_ol_list_dir(self, parent, per_page=100, refresh=True)
        if not items:
            self._openlist_recent_files = []
            return 0

        latest = items[:n]
        videos = []
        seen = set()

        for it in latest:
            try:
                name = str(it.get("name") or "")
                path = _pf_ol_norm_path(it.get("path") or "")
                if not name or not path:
                    continue

                if not it.get("is_dir") and _pf_is_video_file(name):
                    if path not in seen:
                        seen.add(path)
                        videos.append(it)
                    continue

                if it.get("is_dir"):
                    children = _pf_ol_collect_depth(self, path, max_depth=4, per_page=300)
                    for c in children:
                        cp = _pf_ol_norm_path(c.get("path") or "")
                        cn = str(c.get("name") or "")
                        if not cp or not cn:
                            continue
                        if cp in seen:
                            continue
                        if not _pf_is_video_file(cn):
                            continue
                        seen.add(cp)
                        videos.append(c)
            except Exception as e:
                print("[OpenList refresh item] error:", e)

        self._openlist_recent_files = videos
        print("[OpenList refresh] recent videos:", len(videos))
        return len(videos)

    def _pf_ol_build_items(self, title):
        try:
            title = str(title or "").strip()
            b64 = _pf_base64.b64encode(title.encode("utf-8")).decode("utf-8")
            items = ["刷新OpenList$__OPENLIST_REFRESH__|%s" % b64]
            for n in range(2, 14):
                items.append("搜%s$__OPENLIST_SEARCH__|%s|%s" % (n, n, b64))
            return "#".join(items)
        except Exception:
            return "刷新OpenList$__OPENLIST_REFRESH__"

    def _pf_ol_player(self, pid):
        try:
            pid = str(pid or "")

            if not getattr(self, "openlist_url", "") or not getattr(self, "openlist_token", ""):
                return _pf_ack(self)

            if getattr(self, "openlist_test_stream", False):
                ret = {
                    "parse": 0,
                    "playUrl": "",
                    "url": getattr(self, "test_m3u8", ""),
                    "header": {
                        "User-Agent": _pf_ua(self)
                    }
                }
                pic = getattr(self, "last_vod_pic", "") or ""
                if pic:
                    ret["pic"] = pic
                    ret["poster"] = pic
                return ret

            if pid.startswith("__OPENLIST_REFRESH__"):
                title = _pf_ol_decode_title(pid)
                cnt = _pf_ol_refresh_latest(self, title)
                print("[OpenList refresh] clicked, cached =", cnt)
                return _pf_ack(self)

            if pid.startswith("__OPENLIST_SEARCH__"):
                parts = pid.split("|")
                try:
                    n = int(parts[1])
                except Exception:
                    n = 5

                title = _pf_ol_decode_title(pid)
                keys = _pf_ol_keywords(title, n)
                if not keys:
                    return _pf_ack(self)

                info = _pf_ol_search_best(self, keys)
                if not info or not info.get("path"):
                    return _pf_ack(self)

                play_url, headers = _pf_ol_get_playable(self, info.get("path"))
                if not play_url:
                    return _pf_ack(self)

                ret = {
                    "parse": 0,
                    "playUrl": "",
                    "url": play_url,
                    "header": headers
                }
                pic = getattr(self, "last_vod_pic", "") or ""
                if pic:
                    ret["pic"] = pic
                    ret["poster"] = pic
                return ret

            return _pf_ack(self)
        except Exception as e:
            print("[OpenList player] error:", e)
            return _pf_ack(self)

    # ============================================================
    # 播放列表点击优先 OpenList 精确文件名播放
    # ============================================================
    def _pf_file_stem(name):
        try:
            name = str(name or "").strip()
            name = name.replace("\\", "/").rsplit("/", 1)[-1]
            name = _pf_re.sub(
                r"\.(mp4|mkv|iso|avi|mov|wmv|flv|webm|m4v|rmvb|ts|m2ts|vob|f4v|3gp|mpg|mpeg|m3u8)$",
                "",
                name,
                flags=_pf_re.I
            )
            return name.strip()
        except Exception:
            return str(name or "")

    def _pf_exact_ol_match(c, target_name):
        try:
            cand_name = str(c.get("name") or "")
            cand_path = str(c.get("path") or "")
            if not cand_name or not cand_path:
                return False

            target_name = str(target_name or "").strip()
            t_norm = _pf_norm_search(target_name)
            ts_norm = _pf_norm_search(_pf_file_stem(target_name))
            cn_norm = _pf_norm_search(cand_name)
            cs_norm = _pf_norm_search(_pf_file_stem(cand_name))
            cp_norm = _pf_norm_search(cand_path)

            if cn_norm == t_norm:
                return True
            if ts_norm and cs_norm == ts_norm:
                return True
            if t_norm and t_norm in cp_norm:
                return True
            if ts_norm and ts_norm in cp_norm:
                return True
            return False
        except Exception:
            return False

    def _pf_exact_ol_score(c, target_name):
        try:
            cand_name = str(c.get("name") or "")
            cand_path = str(c.get("path") or "")
            size = int(c.get("size") or 0)

            t_norm = _pf_norm_search(target_name)
            ts_norm = _pf_norm_search(_pf_file_stem(target_name))
            cn_norm = _pf_norm_search(cand_name)
            cs_norm = _pf_norm_search(_pf_file_stem(cand_name))
            cp_norm = _pf_norm_search(cand_path)

            score = 0
            if cn_norm == t_norm:
                score += 100000000
            if ts_norm and cs_norm == ts_norm:
                score += 80000000
            if t_norm and t_norm in cp_norm:
                score += 50000000
            if ts_norm and ts_norm in cp_norm:
                score += 30000000
            score += min(size // (100 * 1024 * 1024), 5000)
            return score
        except Exception:
            return 0

    def _pf_exact_ol_search(self, target_name):
        try:
            target_name = str(target_name or "").strip()
            if not target_name:
                return None
            if not getattr(self, "openlist_url", "") or not getattr(self, "openlist_token", ""):
                return None

            keys = [target_name]
            stem = _pf_file_stem(target_name)
            if stem and stem != target_name:
                keys.append(stem)

            final_keys = []
            seen = set()
            for k in keys:
                nk = _pf_norm_search(k)
                if nk and nk not in seen:
                    seen.add(nk)
                    final_keys.append(k)

            recent = getattr(self, "_openlist_recent_files", []) or []
            if recent:
                hits = [c for c in recent if _pf_exact_ol_match(c, target_name)]
                if hits:
                    hits.sort(key=lambda x: (_pf_exact_ol_score(x, target_name), int(x.get("size") or 0)), reverse=True)
                    best = hits[0]
                    print("[Exact OpenList recent] hit:", best.get("name"), best.get("path"))
                    return best

            candidates = _pf_ol_search_by_api(self, final_keys, max_pages=2, per_page=100)
            if candidates:
                hits = [c for c in candidates if _pf_exact_ol_match(c, target_name)]
                if hits:
                    hits.sort(key=lambda x: (_pf_exact_ol_score(x, target_name), int(x.get("size") or 0)), reverse=True)
                    best = hits[0]
                    print("[Exact OpenList api] hit:", best.get("name"), best.get("path"))
                    return best

            return None
        except Exception as e:
            print("[Exact OpenList] error:", e)
            return None

    def _pf_115_cached_file_player(self, pid):
        try:
            pid = str(pid or "")
            if not pid.startswith("__115_FILE__|"):
                return _pf_ack(self)

            # 优先 OpenList 精确播放
            try:
                f = _pf_get_115_file_by_pid(self, pid)
                if f and f.get("name"):
                    info = _pf_exact_ol_search(self, f.get("name"))
                    if info and info.get("path"):
                        play_url, headers = _pf_ol_get_playable(self, info.get("path"))
                        if play_url:
                            ret = {
                                "parse": 0,
                                "playUrl": "",
                                "url": play_url,
                                "header": headers
                            }
                            pic = getattr(self, "last_vod_pic", "") or ""
                            if pic:
                                ret["pic"] = pic
                                ret["poster"] = pic
                            print("[playlist] use OpenList:", info.get("path"))
                            return ret
            except Exception as e:
                print("[playlist exact OpenList] error:", e)

            # 回退 115 播放
            f = _pf_get_115_file_by_pid(self, pid)
            if not f:
                print("[playlist] 115 cache miss:", pid)
                return _pf_ack(self)

            return _pf_115_play_file_info(self, f)
        except Exception as e:
            print("[playlist player] error:", e)
            return _pf_ack(self)

    # ============================================================
    # 构造云下载项
    # ============================================================
    def _pf_build_cloud_items(self, links):
        items = []
        clean_links = []

        for x in links or []:
            if isinstance(x, dict):
                u = x.get("url") or x.get("magnet") or ""
                n = x.get("name") or ""
            else:
                u = str(x or "")
                n = ""
            if not u:
                continue
            clean_links.append({
                "url": u,
                "name": n
            })

        try:
            all_urls = [x["url"] for x in clean_links]
            b64 = _pf_b64e_json(all_urls)
            items.append("下载状态$__115_STATUS_ALL__|%s" % b64)
        except Exception as e:
            print("[cloud items] status build error:", e)

        for x in clean_links:
            u = x.get("url") or ""
            n = x.get("name") or ""

            if not n:
                dn = _pf_extract_dn(u)
                if dn:
                    n = dn
                else:
                    btih = _pf_extract_btih(u)
                    if btih:
                        n = "磁力%s" % btih[:8].upper()
                    elif u.lower().startswith("ed2k://"):
                        n = "电驴资源"
                    else:
                        n = "离线资源"

            items.append("%s$%s" % (_pf_clean_name(self, n, 120), _pf_b64e_text(u)))

        return "#".join(items)

    # ============================================================
    # ed2k 详情页增强：和磁力一样拥有 115 / 状态 / 播放列表 / 查询 / 推送
    # ============================================================
    def _pf_build_ed2kplay_detail(self, data):
        title = data.get("name") or "电驴资源"
        pic = data.get("pic") or getattr(self, "last_vod_pic", "") or ""
        url = _pf_normalize_ed2k(data.get("url") or "")

        if pic:
            self.last_vod_pic = pic

        if not url:
            return {
                "list": [{
                    "vod_id": "psq_bad_ed2k",
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": "ed2k无效",
                    "vod_content": "ed2k链接解析失败。",
                    "vod_play_from": "0",
                    "vod_play_url": "等待视频$__ACK__"
                }]
            }

        play_from = []
        play_url = []

        play_from.append("0")
        play_url.append("等待视频$__ACK__")

        links = [{
            "name": title,
            "url": url
        }]

        play_from.append("115云下载")
        play_url.append(_pf_build_cloud_items(self, links))

        cached = _pf_build115CachedFilePlayItems(self, [url])
        if not cached:
            cached = "暂无115缓存，请先点115云下载-下载状态$__ACK__"
        play_from.append("播放列表")
        play_url.append(cached)

        if getattr(self, "openlist_url", "") and getattr(self, "openlist_token", ""):
            play_from.append("查询")
            play_url.append(_pf_ol_build_items(self, title))

        payload = _pf_encode_payload(self, {
            "type": "ed2k",
            "url": url,
            "pic": pic
        })
        play_from.append("电驴播放")
        play_url.append("%s$%s" % (title, payload))

        return {
            "list": [{
                "vod_id": "psq_ed2kplay",
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": "电驴资源",
                "vod_content": "%s\n\n0线路为等待视频，用于防止壳自动跳转。" % title,
                "vod_play_from": "$$$".join(play_from),
                "vod_play_url": "$$$".join(play_url)
            }]
        }

    # ============================================================
    # playerContent 覆盖
    # ============================================================
    def _pf_playerContent(self, flag, pid, vipFlags):
        try:
            flag = str(flag or "")
            pid = str(pid or "")

            if pid in ["__ACK__", "__WAIT_VIDEO__", "__QW_WAIT_VIDEO__", "__BTL_WAIT_VIDEO__"]:
                return _pf_ack(self)

            if flag in ["0", "提示"]:
                return _pf_ack(self)

            # OpenList 查询
            if flag in ["查询", "115播放"] or pid.startswith("__OPENLIST_"):
                return _pf_ol_player(self, pid)

            # 播放列表
            if flag == "播放列表" or pid.startswith("__115_FILE__|"):
                return _pf_115_cached_file_player(self, pid)

            # 115 云下载
            if flag == "115云下载":
                if pid.startswith("__115_STATUS_ALL__|"):
                    return _pf_115_status_all(self, pid)

                real_link = _pf_b64d_text(pid)
                mg = _pf_normalize_magnet(self, real_link)
                ed = _pf_normalize_ed2k(real_link)

                if mg:
                    real_link = mg
                elif ed:
                    real_link = ed
                else:
                    return _pf_ack(self)

                if not getattr(self, "pan_115_cookie", ""):
                    print("[115] 未配置 pan_115_cookie")
                    return _pf_ack(self)

                if getattr(self, "confirm_115", False) and real_link not in getattr(self, "confirm_cache", set()):
                    self.confirm_cache.add(real_link)
                    print("[115] confirm_115 开启，首次点击仅确认，二次点击提交")
                    return _pf_ack(self)

                _pf_threading.Thread(
                    target=_pf_115_submit_only,
                    args=(self, real_link),
                    daemon=True
                ).start()

                return _pf_ack(self)

            # payload
            data = _pf_decode_payload(self, pid)
            if isinstance(data, dict) and data:
                typ = data.get("type", "")
                url = data.get("url", "")
                pic = data.get("pic") or getattr(self, "last_vod_pic", "")

                if typ == "pan":
                    return {
                        "parse": 0,
                        "playUrl": "",
                        "url": "push://" + url,
                        "pic": pic,
                        "poster": pic,
                        "header": {
                            "User-Agent": _pf_ua(self)
                        }
                    }

                if typ == "magnet":
                    mu = _pf_normalize_magnet(self, url)
                    if mu:
                        return {
                            "parse": 0,
                            "playUrl": "",
                            "url": "push://" + mu,
                            "pic": pic,
                            "poster": pic,
                            "header": {
                                "User-Agent": _pf_ua(self)
                            }
                        }
                    return {
                        "parse": 1,
                        "url": url,
                        "pic": pic,
                        "poster": pic
                    }

                if typ == "ed2k":
                    ed = _pf_normalize_ed2k(url)
                    if ed:
                        return {
                            "parse": 0,
                            "playUrl": "",
                            "url": "push://" + ed,
                            "pic": pic,
                            "poster": pic,
                            "header": {
                                "User-Agent": _pf_ua(self)
                            }
                        }
                    return {
                        "parse": 1,
                        "url": url,
                        "pic": pic,
                        "poster": pic
                    }

            if pid.startswith("push://"):
                return {
                    "parse": 0,
                    "playUrl": "",
                    "url": pid,
                    "pic": getattr(self, "last_vod_pic", ""),
                    "poster": getattr(self, "last_vod_pic", "")
                }

            mu = _pf_normalize_magnet(self, pid)
            if mu:
                return {
                    "parse": 0,
                    "playUrl": "",
                    "url": "push://" + mu,
                    "pic": getattr(self, "last_vod_pic", ""),
                    "poster": getattr(self, "last_vod_pic", ""),
                    "header": {
                        "User-Agent": _pf_ua(self)
                    }
                }

            ed = _pf_normalize_ed2k(pid)
            if ed:
                return {
                    "parse": 0,
                    "playUrl": "",
                    "url": "push://" + ed,
                    "pic": getattr(self, "last_vod_pic", ""),
                    "poster": getattr(self, "last_vod_pic", ""),
                    "header": {
                        "User-Agent": _pf_ua(self)
                    }
                }

            if _PF_PREV_PLAYER:
                return _PF_PREV_PLAYER(self, flag, pid, vipFlags)

            return {
                "parse": 1,
                "playUrl": "",
                "url": pid
            }
        except Exception as e:
            print("[PANSOU FINAL playerContent] error:", e)
            return _pf_ack(self)

    # ============================================================
    # 覆盖七味补丁里的空壳函数 / 构造函数
    # ============================================================
    def _pf_psq_115_status_all(self, pid):
        return _pf_115_status_all(self, pid)

    def _pf_psq_115_submit_magnet(self, magnet):
        if not getattr(self, "pan_115_cookie", ""):
            print("[115] 未配置 pan_115_cookie")
            return _pf_ack(self)
        _pf_threading.Thread(
            target=_pf_115_submit_only,
            args=(self, magnet),
            daemon=True
        ).start()
        return _pf_ack(self)

    def _pf_psq_openlist_player(self, pid):
        return _pf_ol_player(self, pid)

    def _pf_psq_build_cached_playlist(self, magnets):
        ret = _pf_build115CachedFilePlayItems(self, magnets)
        if not ret:
            return "暂无115缓存，请先点115云下载-下载状态$__ACK__"
        return ret

    def _pf_psq_build_query_items(self, title):
        return _pf_ol_build_items(self, title)

    def _pf_psq_build_115_cloud_items(self, magnets):
        return _pf_build_cloud_items(self, magnets)

    globals()["_psq_115_status_all"] = _pf_psq_115_status_all
    globals()["_psq_115_submit_magnet"] = _pf_psq_115_submit_magnet
    globals()["_psq_openlist_player"] = _pf_psq_openlist_player
    globals()["_psq_build_cached_playlist"] = _pf_psq_build_cached_playlist
    globals()["_psq_build_query_items"] = _pf_psq_build_query_items
    globals()["_psq_build_115_cloud_items"] = _pf_psq_build_115_cloud_items
    globals()["_psq_build_ed2kplay_detail"] = _pf_build_ed2kplay_detail

    # ============================================================
    # 绑定到类
    # ============================================================
    _PF_TARGET.init = _pf_init
    _PF_TARGET.playerContent = _pf_playerContent

    _PF_TARGET._115_cache_paths = _pf_115_cache_paths
    _PF_TARGET._115_cache_load = _pf_115_cache_load
    _PF_TARGET._115_cache_save = _pf_115_cache_save
    _PF_TARGET._115_headers = _pf_115_headers
    _PF_TARGET._115_add_task = _pf_115_add_task
    _PF_TARGET._115_task_list = _pf_115_task_list
    _PF_TARGET._115_find_task_by_link = _pf_115_find_task_by_link
    _PF_TARGET._115_list_files = _pf_115_list_files
    _PF_TARGET._115_submit_only = _pf_115_submit_only
    _PF_TARGET._115_resolve_files = _pf_115_resolve_files
    _PF_TARGET.build115CachedFilePlayItems = _pf_build115CachedFilePlayItems
    _PF_TARGET._115StatusAllPlayerContent = _pf_115_status_all
    _PF_TARGET._115CachedFilePlayerContent = _pf_115_cached_file_player
    _PF_TARGET._115_get_play_url_by_pickcode = _pf_115_get_play_url_by_pickcode
    _PF_TARGET._115_play_file_info = _pf_115_play_file_info

    _PF_TARGET.openlistHeaders = _pf_ol_headers
    _PF_TARGET.openlistApiPost = _pf_ol_api_post
    _PF_TARGET.openlistNormalizePath = staticmethod(_pf_ol_norm_path)
    _PF_TARGET.openlistJoinPath = staticmethod(_pf_ol_join)
    _PF_TARGET.isPathUnderOpenlistParent = _pf_ol_under_parent
    _PF_TARGET.isOpenlistVideoFile = staticmethod(_pf_is_video_file)
    _PF_TARGET.normalizeSearchText = staticmethod(_pf_norm_search)
    _PF_TARGET.openlistListDirOnce = _pf_ol_list_dir
    _PF_TARGET.openlistApiSearchFiles = _pf_ol_search_files
    _PF_TARGET.searchOpenlistByApi = _pf_ol_search_by_api
    _PF_TARGET.searchOpenlistBestVideo = _pf_ol_search_best
    _PF_TARGET.buildOpenlistPlayItems = _pf_ol_build_items
    _PF_TARGET.buildOpenlistSearchKeywords = staticmethod(_pf_ol_keywords)
    _PF_TARGET.normalizeOpenlistUrl = _pf_ol_normalize_url
    _PF_TARGET.buildOpenlistDownloadUrl = _pf_ol_download_url
    _PF_TARGET.buildOpenlistDavUrl = _pf_ol_dav_url
    _PF_TARGET.getPlayableUrlFromOpenlist = _pf_ol_get_playable
    _PF_TARGET.refreshOpenlistLatest3ToMemory = _pf_ol_refresh_latest
    _PF_TARGET.openlistPlayerContent = _pf_ol_player

    Spider = _PF_TARGET

    print("[PANSOU FINAL MAGNET 115 OPENLIST PATCH] loaded")

# ===== PANSOU_FINAL_MAGNET_115_OPENLIST_PATCH_END =====
# ===== PANSOU_CLICK_QUARK_115_CHECK_TOPN_BEGIN =====
# 点击二级分类夸克/115后，对排序后的前 N 条进行有效性检测。
# 默认：
#   psq_click_check_enable = true
#   psq_click_check_top_n = 20
#   psq_click_check_types = ["quark", "115"]
#   psq_click_check_hide_bad = true
#
# ext 示例：
# {
#   "psq_click_check_enable": true,
#   "psq_click_check_top_n": 20,
#   "psq_click_check_types": ["quark", "115"],
#   "psq_click_check_hide_bad": true
# }

import json as _psqcc_json
import time as _psqcc_time

try:
    _PSQCC_PREV_INIT = PanSouSpider.init
except Exception:
    _PSQCC_PREV_INIT = None


def _psqcc_to_bool(v, default=False):
    try:
        if isinstance(v, bool):
            return v
        if isinstance(v, int):
            return v != 0
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off", ""]:
                return False
        return bool(v)
    except Exception:
        return default


def _psqcc_to_list(v):
    try:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, tuple):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            return [x.strip() for x in v.split(",") if x.strip()]
        return []
    except Exception:
        return []


def _psqcc_parse_ext(extend):
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str) and extend.strip().startswith("{"):
            return _psqcc_json.loads(extend)
        return {}
    except Exception:
        return {}


def _psqcc_init(self, extend=""):
    ret = None
    if _PSQCC_PREV_INIT:
        try:
            ret = _PSQCC_PREV_INIT(self, extend)
        except Exception as e:
            print("[PSQ CLICK CHECK] prev init error:", e)

    try:
        ext = _psqcc_parse_ext(extend)

        # 是否开启点击二级分类后的检测
        self.psq_click_check_enable = _psqcc_to_bool(
            ext.get(
                "psq_click_check_enable",
                getattr(self, "psq_click_check_enable", True)
            ),
            True
        )

        # 检测排序后的前多少条，默认 20
        try:
            self.psq_click_check_top_n = int(
                ext.get(
                    "psq_click_check_top_n",
                    getattr(self, "psq_click_check_top_n", 20)
                )
            )
        except Exception:
            self.psq_click_check_top_n = 20

        if self.psq_click_check_top_n < 0:
            self.psq_click_check_top_n = 0

        # 检测类型，默认 quark 和 115
        types = _psqcc_to_list(
            ext.get(
                "psq_click_check_types",
                getattr(self, "psq_click_check_types", ["quark", "115"])
            )
        )
        if not types:
            types = ["quark", "115"]

        # 统一一下 115 的写法
        fixed_types = []
        for x in types:
            x = str(x).strip().lower()
            if x in ["a115", "115"]:
                x = "115"
            if x in ["quark", "115"] and x not in fixed_types:
                fixed_types.append(x)

        self.psq_click_check_types = fixed_types or ["quark", "115"]

        # 是否隐藏 bad，默认隐藏
        self.psq_click_check_hide_bad = _psqcc_to_bool(
            ext.get(
                "psq_click_check_hide_bad",
                getattr(self, "psq_click_check_hide_bad", True)
            ),
            True
        )

        print("[PSQ CLICK CHECK] enable =", self.psq_click_check_enable)
        print("[PSQ CLICK CHECK] top_n =", self.psq_click_check_top_n)
        print("[PSQ CLICK CHECK] types =", self.psq_click_check_types)
        print("[PSQ CLICK CHECK] hide_bad =", self.psq_click_check_hide_bad)

    except Exception as e:
        print("[PSQ CLICK CHECK] init error:", e)

    return ret if ret is not None else {}


def _psqcc_group_key(api_type):
    try:
        if "_psq_group_key" in globals():
            return _psq_group_key(api_type)
    except Exception:
        pass

    api_type = str(api_type or "").strip().lower()
    if api_type in ["115", "a115"]:
        return "115"
    if api_type in ["quark"]:
        return "quark"
    return api_type


def _psqcc_state_name(self, state):
    try:
        return self._state_name(state)
    except Exception:
        mapping = {
            "ok": "有效",
            "bad": "失效",
            "locked": "需密码",
            "unsupported": "不支持检测",
            "uncertain": "检测失败"
        }
        return mapping.get(str(state), str(state))


def _psqcc_check_key(self, api_type, url):
    try:
        return self._check_key(api_type, url)
    except Exception:
        return "%s|%s" % (
            str(api_type).strip().lower(),
            str(url).strip().replace(" ", "")
        )


def _psqcc_request_check_links(self, check_items):
    """
    优先使用原脚本已有的 _request_check_links。
    如果失败，则返回空，避免误删。
    """
    try:
        if hasattr(self, "_request_check_links"):
            return self._request_check_links(check_items) or {}
    except Exception as e:
        print("[PSQ CLICK CHECK] self._request_check_links error:", e)

    # 兜底：直接请求 /api/check/links
    try:
        base_url = getattr(self, "base_url", "https://so.252035.xyz").rstrip("/")
        url = base_url + "/api/check/links"
        payload = {
            "items": check_items,
            "view_token": "psq-click-check-%s" % int(_psqcc_time.time() * 1000)
        }

        headers = {}
        try:
            headers = self._headers()
        except Exception:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json"
            }

        session = getattr(self, "session", None)
        if session:
            r = session.post(url, headers=headers, json=payload, timeout=20)
        else:
            import requests as _psqcc_requests
            r = _psqcc_requests.post(url, headers=headers, json=payload, timeout=20)

        r.raise_for_status()
        data = r.json()

        out = {}
        for item in data.get("results", []) or []:
            disk_type = item.get("disk_type", "")
            raw_url = item.get("url", "")
            out[_psqcc_check_key(self, disk_type, raw_url)] = {
                "state": item.get("state", ""),
                "summary": item.get("summary", ""),
                "normalized_url": item.get("normalized_url", "")
            }

        return out
    except Exception as e:
        print("[PSQ CLICK CHECK] direct check error:", e)
        return {}


def _psqcc_apply_click_check(self, items, group):
    """
    对排序后的 items 前 N 条做检测。
    只检测 quark / 115。
    bad 隐藏，其他状态保留。
    """
    try:
        if not getattr(self, "psq_click_check_enable", True):
            return items or []

        group = str(group or "").strip().lower()
        if group == "a115":
            group = "115"

        check_types = getattr(self, "psq_click_check_types", ["quark", "115"]) or ["quark", "115"]

        if group not in check_types:
            return items or []

        try:
            top_n = int(getattr(self, "psq_click_check_top_n", 20) or 0)
        except Exception:
            top_n = 20

        if top_n <= 0:
            return items or []

        arr = list(items or [])
        if not arr:
            return arr

        # 只取排序后的前 N 条检测
        check_part = arr[:top_n]
        rest_part = arr[top_n:]

        check_items = []
        check_index = {}

        for idx, item in enumerate(check_part):
            try:
                api_type = item.get("api_type") or group
                api_group = _psqcc_group_key(api_type)

                if api_group != group:
                    continue

                # check 接口 disk_type 要用接口类型：
                # quark -> quark
                # 115 -> 115
                if api_group == "115":
                    disk_type = "115"
                else:
                    disk_type = "quark"

                url = item.get("url") or ""
                if not url:
                    continue

                key = _psqcc_check_key(self, disk_type, url)

                check_items.append({
                    "disk_type": disk_type,
                    "url": url,
                    "password": item.get("password", "") or ""
                })

                check_index[key] = idx
            except Exception:
                pass

        if not check_items:
            return arr

        print("[PSQ CLICK CHECK] checking group=%s top=%s count=%s" % (
            group,
            top_n,
            len(check_items)
        ))

        check_map = _psqcc_request_check_links(self, check_items)

        if not check_map:
            print("[PSQ CLICK CHECK] no check result, keep all")
            return arr

        output_checked = []

        hide_bad = bool(getattr(self, "psq_click_check_hide_bad", True))

        for item in check_part:
            try:
                api_type = item.get("api_type") or group
                api_group = _psqcc_group_key(api_type)
                disk_type = "115" if api_group == "115" else "quark"
                url = item.get("url") or ""

                key = _psqcc_check_key(self, disk_type, url)

                if key in check_map:
                    checked = check_map[key] or {}
                    state = checked.get("state", "") or ""
                    summary = checked.get("summary", "") or ""
                    normalized_url = checked.get("normalized_url", "") or ""

                    item["state"] = state
                    item["summary"] = summary
                    if normalized_url:
                        item["normalized_url"] = normalized_url

                    # bad 直接隐藏
                    if hide_bad and state == "bad":
                        print("[PSQ CLICK CHECK] hide bad:", url)
                        continue

                    # 有检测结果但不是 bad，保留
                    output_checked.append(item)
                else:
                    # 没有返回结果，保留，避免误删
                    output_checked.append(item)

            except Exception:
                output_checked.append(item)

        return output_checked + rest_part

    except Exception as e:
        print("[PSQ CLICK CHECK] apply error:", e)
        return items or []


def _psqcc_remark_with_state(self, item, default_status="未检测"):
    """
    生成三级列表 remarks。
    如果 item 里有检测状态，则显示 有效/失效/需密码/检测失败 等。
    """
    try:
        state = item.get("state") or ""
        if state:
            status = _psqcc_state_name(self, state)
        else:
            status = default_status

        if "_psq_remark" in globals():
            return _psq_remark(item, status)

        return status
    except Exception:
        return default_status


def _psqcc_build_third_category(self, data, pg=1):
    """
    覆盖原 _psq_build_third_category：
    只在 quark / 115 二级分类点击后，
    对排序后的前 N 条做检测，无效链接不显示。
    """
    try:
        page = int(pg) if str(pg).isdigit() else 1
    except Exception:
        page = 1

    if page < 1:
        page = 1

    keyword = str(data.get("kw") or "").strip()
    group = str(data.get("group") or "").strip()
    group = "115" if group in ["a115", "115"] else group

    items = _psq_fetch_search_items(self, keyword)
    groups = _psq_group_items(items)
    current = groups.get(group) or []

    # 先排序
    current = _psq_sort_items(current)

    # 再对排序后的前 N 条做检测
    current = _psqcc_apply_click_check(self, current, group)

    page_size = int(getattr(self, "SEARCH_PAGE_SIZE", 60) or 60)
    if page_size <= 0:
        page_size = 60

    total = len(current)
    pagecount = max(1, int((total + page_size - 1) / page_size))

    if page > pagecount:
        page = pagecount

    start = (page - 1) * page_size
    page_items = current[start:start + page_size]

    videos = []
    width = max(2, len(str(total))) if total else 2

    cover_fallback = ""
    for x in current:
        imgs = x.get("images") or []
        if imgs:
            cover_fallback = imgs[0]
            break

    for idx, item in enumerate(page_items):
        real_idx = start + idx + 1
        note = item.get("note") or item.get("url") or "资源"
        url = item.get("url") or ""
        password = item.get("password") or ""
        api_type = item.get("api_type") or group
        gkey = _psq_group_key(api_type)

        imgs = item.get("images") or []
        pic = imgs[0] if imgs else cover_fallback

        if gkey == "magnet":
            clean_title = _psq_clean_magnet_name(self, item)
            icon = "⚪"
            vod_id = _psq_make_id("magnetplay", {
                "kw": keyword,
                "group": gkey,
                "name": clean_title,
                "url": url,
                "pic": pic
            })
            remark = _psq_remark(item, "未检测")
            content = "%s\n点击后进入磁力播放页。" % clean_title

        elif gkey == "ed2k":
            clean_title = _psq_clean_name(self, note, 150)
            icon = "⚪"
            vod_id = _psq_make_id("ed2kplay", {
                "kw": keyword,
                "group": gkey,
                "name": clean_title,
                "url": url,
                "pic": pic
            })
            remark = _psq_remark(item, "未检测")
            content = "%s\n点击后进入电驴播放页。" % clean_title

        else:
            clean_title = _psq_clean_name(self, note, 150)

            # 根据检测状态显示不同图标
            state = item.get("state") or ""
            if state == "ok":
                icon = "🟢"
            elif state == "locked":
                icon = "🟡"
            elif state in ["uncertain", "unsupported"]:
                icon = "🟠"
            else:
                icon = "⚪"

            vod_id = _psq_make_id("panplay", {
                "kw": keyword,
                "group": gkey,
                "api_type": api_type,
                "name": clean_title,
                "url": item.get("normalized_url") or url,
                "password": password,
                "pic": pic
            })

            remark = _psqcc_remark_with_state(self, item, "未检测")
            content = "%s\n点击后自动推送网盘链接。" % clean_title

        show_name = "%s. %s %s" % (
            str(real_idx).zfill(width),
            icon,
            clean_title
        )

        videos.append({
            "vod_id": vod_id,
            "vod_name": _psq_clean_name(self, show_name, 160),
            "vod_pic": pic,
            "vod_remarks": remark,
            "vod_content": content,
            "vod_tag": "file"
        })

    if not videos:
        videos.append({
            "vod_id": "empty",
            "vod_name": "%s 暂无可用资源" % _PSQ_GROUP_NAME.get(group, group),
            "vod_pic": cover_fallback,
            "vod_remarks": "空"
        })

    return {
        "list": videos,
        "page": page,
        "pagecount": pagecount,
        "limit": page_size,
        "total": total
    }


# 绑定 init
try:
    PanSouSpider.init = _psqcc_init
    Spider = PanSouSpider
except Exception as e:
    print("[PSQ CLICK CHECK] bind init error:", e)

# 覆盖全局三级分类构造函数。
# _psq_categoryContent 会在运行时查找 _psq_build_third_category，
# 所以这里直接重定义即可生效。
try:
    _psq_build_third_category = _psqcc_build_third_category
    print("[PANSOU CLICK QUARK/115 CHECK TOPN] loaded")
except Exception as e:
    print("[PANSOU CLICK CHECK] bind third category error:", e)

# ===== PANSOU_CLICK_QUARK_115_CHECK_TOPN_END =====
# ===== PANSOU_CLICK_CHECK_SORT_AND_PASSWORD_FIX_BEGIN =====
# 功能：
# 1. 点击夸克/115后，检测结果排序：
#    ok 有效              -> 最前
#    locked 需要密码       -> 有效后面，但仍算可用
#    uncertain/unsupported/单条无返回 -> 检测失败区
#    未检测资源             -> 最后
#    bad                  -> 隐藏
#
# 2. 需要密码的网盘链接，在点击推送时自动补上密码：
#    https://xxx.com/s/abc + password=1234
#    -> https://xxx.com/s/abc?pwd=1234
#
# 3. 同时兼容：
#    pwd=
#    password=
#    passcode=
#    code=
#    提取码已经存在时不重复追加。

import re as _psqcpf_re


def _psqcpf_state_rank(state, has_result=True):
    """
    状态排序。
    数字越小越靠前。

    0: 有效 ok
    1: 需要密码 locked，也属于可用
    2: 检测失败/未知/不支持/单条无返回
    3: 未检测
    """
    try:
        state = str(state or "").strip().lower()

        if state == "ok":
            return 0

        if state == "locked":
            return 1

        if state in ["uncertain", "unsupported", ""]:
            return 2

        if not has_result:
            return 2

        return 2
    except Exception:
        return 2


def _psqcpf_url_has_password(url):
    try:
        low = str(url or "").lower()
        return (
            "pwd=" in low
            or "password=" in low
            or "passcode=" in low
            or "code=" in low
            or "提取码" in low
        )
    except Exception:
        return False


def _psqcpf_add_password_to_url(url, password):
    """
    给网盘链接自动补密码。
    如果链接里已经有 pwd/password/passcode/code，则不重复追加。
    """
    try:
        url = str(url or "").strip()
        password = str(password or "").strip()

        if not url or not password:
            return url

        if _psqcpf_url_has_password(url):
            return url

        # magnet / ed2k 不拼密码
        low = url.lower()
        if low.startswith("magnet:") or low.startswith("ed2k://"):
            return url

        # 优先调用原始 _build_final_url
        try:
            if hasattr(self, "_build_final_url"):
                # api_type 不确定时给 unknown，内部只要不是 magnet/ed2k 都会拼 pwd
                fixed = self._build_final_url("unknown", url, password)
                if fixed:
                    return fixed
        except Exception:
            pass

        sep = "&" if "?" in url else "?"
        return url + sep + "pwd=" + password

    except Exception:
        return str(url or "")


def _psqcpf_apply_click_check(self, items, group):
    """
    覆盖 _psqcc_apply_click_check。

    对排序后的前 N 条检测：
      bad 隐藏；
      ok 排前；
      locked 排 ok 后；
      检测失败排 locked 后；
      未检测 rest_part 排最后。
    """
    try:
        if not getattr(self, "psq_click_check_enable", True):
            return items or []

        group = str(group or "").strip().lower()
        if group in ["a115", "115"]:
            group = "115"

        check_types = getattr(
            self,
            "psq_click_check_types",
            ["quark", "115"]
        ) or ["quark", "115"]

        check_types = [
            "115" if str(x).lower() in ["115", "a115"] else str(x).lower()
            for x in check_types
        ]

        if group not in check_types:
            return items or []

        try:
            top_n = int(getattr(self, "psq_click_check_top_n", 20) or 0)
        except Exception:
            top_n = 20

        if top_n <= 0:
            return items or []

        arr = list(items or [])
        if not arr:
            return arr

        # 前 N 条参与检测
        check_part = arr[:top_n]

        # N 之后是未检测区，最后显示
        rest_part = arr[top_n:]

        check_items = []

        for idx, item in enumerate(check_part):
            try:
                item["_psqcpf_original_index"] = idx

                api_type = item.get("api_type") or group

                try:
                    api_group = _psqcc_group_key(api_type)
                except Exception:
                    api_group = str(api_type or "").lower()
                    if api_group in ["a115", "115"]:
                        api_group = "115"

                if api_group != group:
                    continue

                if api_group == "115":
                    disk_type = "115"
                elif api_group == "quark":
                    disk_type = "quark"
                else:
                    continue

                url = item.get("url") or ""
                if not url:
                    continue

                check_items.append({
                    "disk_type": disk_type,
                    "url": url,
                    "password": item.get("password", "") or ""
                })

            except Exception:
                pass

        if not check_items:
            return arr

        print("[PSQ CLICK CHECK SORT/PWD] checking group=%s top_n=%s count=%s" % (
            group,
            top_n,
            len(check_items)
        ))

        try:
            check_map = _psqcc_request_check_links(self, check_items)
        except Exception as e:
            print("[PSQ CLICK CHECK SORT/PWD] request check error:", e)
            check_map = {}

        # 如果接口整体失败，不改变原排序，避免误处理
        if not check_map:
            print("[PSQ CLICK CHECK SORT/PWD] no check result, keep original order")
            return arr

        hide_bad = bool(getattr(self, "psq_click_check_hide_bad", True))

        checked_output = []

        for item in check_part:
            try:
                api_type = item.get("api_type") or group

                try:
                    api_group = _psqcc_group_key(api_type)
                except Exception:
                    api_group = str(api_type or "").lower()
                    if api_group in ["a115", "115"]:
                        api_group = "115"

                if api_group == "115":
                    disk_type = "115"
                elif api_group == "quark":
                    disk_type = "quark"
                else:
                    item["_psqcpf_state_rank"] = 2
                    checked_output.append(item)
                    continue

                url = item.get("url") or ""

                try:
                    key = _psqcc_check_key(self, disk_type, url)
                except Exception:
                    key = "%s|%s" % (
                        str(disk_type).lower(),
                        str(url).strip().replace(" ", "")
                    )

                checked = check_map.get(key)

                # 单条没有返回检测结果：算检测失败区，排在有效后面、未检测前面
                if not checked:
                    item["state"] = item.get("state") or "uncertain"
                    item["summary"] = item.get("summary") or "检测无返回"
                    item["_psqcpf_state_rank"] = 2
                    checked_output.append(item)
                    continue

                state = checked.get("state", "") or ""
                summary = checked.get("summary", "") or ""
                normalized_url = checked.get("normalized_url", "") or ""

                item["state"] = state
                item["summary"] = summary

                if normalized_url:
                    item["normalized_url"] = normalized_url

                # bad 隐藏
                if hide_bad and state == "bad":
                    print("[PSQ CLICK CHECK SORT/PWD] hide bad:", url)
                    continue

                item["_psqcpf_state_rank"] = _psqcpf_state_rank(
                    state,
                    True
                )

                checked_output.append(item)

            except Exception as e:
                print("[PSQ CLICK CHECK SORT/PWD] item check error:", e)
                try:
                    item["state"] = item.get("state") or "uncertain"
                    item["summary"] = item.get("summary") or "检测异常"
                    item["_psqcpf_state_rank"] = 2
                    checked_output.append(item)
                except Exception:
                    pass

        # 检测区内部排序：
        # ok -> locked -> 检测失败
        # 同一状态保留原质量排序顺序
        try:
            checked_output.sort(
                key=lambda x: (
                    int(x.get("_psqcpf_state_rank", 2)),
                    int(x.get("_psqcpf_original_index", 999999))
                )
            )
        except Exception:
            pass

        # 未检测区标记为 rank 3，但是不参与 checked_output 排序
        for item in rest_part:
            try:
                item["_psqcpf_state_rank"] = 3
            except Exception:
                pass

        # 清理临时字段
        for item in checked_output + rest_part:
            try:
                item.pop("_psqcpf_state_rank", None)
                item.pop("_psqcpf_original_index", None)
            except Exception:
                pass

        # 关键顺序：
        # 检测区 ok/locked/失败 -> 未检测区
        return checked_output + rest_part

    except Exception as e:
        print("[PSQ CLICK CHECK SORT/PWD] apply error:", e)
        return items or []


def _psqcpf_build_panplay_detail(self, data):
    """
    覆盖 _psq_build_panplay_detail。

    目的：
    需要密码的夸克/115链接，点击推送时自动补密码。
    """
    try:
        title = data.get("name") or "网盘资源"
        pic = data.get("pic") or getattr(self, "last_vod_pic", "") or ""
        url = data.get("url") or ""
        password = data.get("password") or ""
        api_type = data.get("api_type") or data.get("group") or ""

        if pic:
            self.last_vod_pic = pic

        # 优先使用 normalized_url 或原始 url，并确保补密码
        final_url = _psqcpf_add_password_to_url(url, password)

        try:
            payload = self._encode_id({
                "type": "pan",
                "api_type": api_type,
                "url": final_url,
                "password": password,
                "pic": pic
            })
        except Exception:
            import json as _psqcpf_json
            import base64 as _psqcpf_base64
            payload = _psqcpf_base64.urlsafe_b64encode(
                _psqcpf_json.dumps({
                    "type": "pan",
                    "api_type": api_type,
                    "url": final_url,
                    "password": password,
                    "pic": pic
                }, ensure_ascii=False).encode("utf-8")
            ).decode("utf-8").rstrip("=")

        content = [
            "资源名称：%s" % title,
            "资源链接：%s" % url
        ]

        if final_url != url:
            content.append("推送链接：%s" % final_url)

        if password:
            content.append("提取码：%s" % password)

        state = data.get("state") or ""
        if state:
            content.append("检测状态：%s" % state)

        return {
            "list": [{
                "vod_id": "psq_panplay",
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": "自动推送",
                "vod_content": "\n".join(content),
                "vod_play_from": "推送",
                "vod_play_url": "自动推送$%s" % payload
            }]
        }

    except Exception as e:
        print("[PSQ CLICK CHECK SORT/PWD] build panplay detail error:", e)
        try:
            if "_psq_build_panplay_detail" in globals():
                return _psq_build_panplay_detail(self, data)
        except Exception:
            pass

        return {
            "list": []
        }


def _psqcpf_playerContent(self, flag, pid, vipFlags):
    """
    包一层 playerContent，专门确保 pan payload 推送时再次补密码。
    防止前面某些 detail 构造漏拼 password。
    """
    try:
        flag_s = str(flag or "")
        pid_s = str(pid or "")

        # 只处理 payload 型 pan
        try:
            data = self._decode_id(pid_s)
        except Exception:
            data = None

        if isinstance(data, dict) and data.get("type") == "pan":
            url = data.get("url") or ""
            password = data.get("password") or ""
            pic = data.get("pic") or getattr(self, "last_vod_pic", "")

            final_url = _psqcpf_add_password_to_url(url, password)

            return {
                "parse": 0,
                "playUrl": "",
                "url": "push://" + final_url,
                "pic": pic,
                "poster": pic,
                "header": {
                    "User-Agent": getattr(self, "HEADERS", {}).get("User-Agent", "Mozilla/5.0")
                }
            }

    except Exception as e:
        print("[PSQ CLICK CHECK SORT/PWD] player pre-handle error:", e)

    # 其他情况走上一层 playerContent
    try:
        if "_PSQCPF_PREV_PLAYER" in globals() and _PSQCPF_PREV_PLAYER:
            return _PSQCPF_PREV_PLAYER(self, flag, pid, vipFlags)
    except Exception:
        pass

    try:
        if "_PSQ_ORIG_PLAYER" in globals() and _PSQ_ORIG_PLAYER:
            return _PSQ_ORIG_PLAYER(self, flag, pid, vipFlags)
    except Exception:
        pass

    return {
        "parse": 1,
        "playUrl": "",
        "url": pid
    }


# ============================================================
# 绑定覆盖
# ============================================================

try:
    # 覆盖检测排序函数
    _psqcc_apply_click_check = _psqcpf_apply_click_check
    print("[PSQ CLICK CHECK SORT/PWD] override _psqcc_apply_click_check ok")
except Exception as e:
    print("[PSQ CLICK CHECK SORT/PWD] override check apply error:", e)


try:
    # 覆盖网盘详情构造函数。
    # _psq_detailContent 会运行时查找这个全局函数，所以直接覆盖即可。
    _psq_build_panplay_detail = _psqcpf_build_panplay_detail
    print("[PSQ CLICK CHECK SORT/PWD] override _psq_build_panplay_detail ok")
except Exception as e:
    print("[PSQ CLICK CHECK SORT/PWD] override panplay detail error:", e)


try:
    _PSQCPF_PREV_PLAYER = PanSouSpider.playerContent
    PanSouSpider.playerContent = _psqcpf_playerContent
    Spider = PanSouSpider
    print("[PSQ CLICK CHECK SORT/PWD] playerContent bind ok")
except Exception as e:
    print("[PSQ CLICK CHECK SORT/PWD] playerContent bind error:", e)


print("[PANSOU CLICK CHECK SORT AND PASSWORD FIX] loaded")
# ===== PANSOU_CLICK_CHECK_SORT_AND_PASSWORD_FIX_END =====
# ===== PANSOU_PASSWORD_PARAM_115_FIX_BEGIN =====
# 修复 115 补密码参数：
# 115 / 115cdn / anxia 使用 password=
# 夸克 / 百度 / 其他默认使用 pwd=
#
# 例如：
# https://115cdn.com/s/swf29473zrk + t58d
# ->
# https://115cdn.com/s/swf29473zrk?password=t58d

from urllib.parse import urlparse as _psqpwd_urlparse
from urllib.parse import urlencode as _psqpwd_urlencode
from urllib.parse import parse_qsl as _psqpwd_parse_qsl
from urllib.parse import urlunparse as _psqpwd_urlunparse


def _psqpwd_detect_pan_type_from_url(url):
    """
    根据 URL 判断网盘类型。
    """
    try:
        u = str(url or "").strip().lower()
        host = _psqpwd_urlparse(u).netloc.lower()

        if "115.com" in host or "115cdn.com" in host or "anxia.com" in host:
            return "115"

        if "pan.quark.cn" in host:
            return "quark"

        if "pan.baidu.com" in host:
            return "baidu"

        if "drive.uc.cn" in host:
            return "uc"

        if "aliyundrive.com" in host or "alipan.com" in host:
            return "aliyun"

        if "cloud.189.cn" in host:
            return "tianyi"

        if "caiyun.139.com" in host:
            return "mobile"

        if "123pan.com" in host or "123pan.cn" in host:
            return "123"

        if "xunlei" in host or "pan.xunlei.com" in host:
            return "xunlei"

        return ""
    except Exception:
        return ""


def _psqpwd_password_param_name(url, api_type=""):
    """
    不同网盘使用不同密码参数。
    """
    try:
        api_type = str(api_type or "").strip().lower()

        if api_type in ["115", "a115"]:
            return "password"

        pan_type = _psqpwd_detect_pan_type_from_url(url)

        if pan_type == "115":
            return "password"

        # 夸克常见 pwd=
        if pan_type == "quark":
            return "pwd"

        # 百度常见 pwd=
        if pan_type == "baidu":
            return "pwd"

        # 默认 pwd=
        return "pwd"

    except Exception:
        return "pwd"


def _psqpwd_url_has_any_password(url):
    """
    判断链接是否已经带有密码参数，避免重复追加。
    """
    try:
        low = str(url or "").lower()

        return (
            "pwd=" in low
            or "password=" in low
            or "passcode=" in low
            or "code=" in low
            or "提取码" in low
        )
    except Exception:
        return False


def _psqpwd_add_password_to_url(url, password, api_type=""):
    """
    给网盘链接补密码。
    115 使用 password=
    其他默认 pwd=
    """
    try:
        url = str(url or "").strip()
        password = str(password or "").strip()

        if not url or not password:
            return url

        low = url.lower()

        # 磁力 / ed2k 不处理
        if low.startswith("magnet:") or low.startswith("ed2k://"):
            return url

        # 已经有密码参数，不重复追加
        if _psqpwd_url_has_any_password(url):
            return url

        param_name = _psqpwd_password_param_name(url, api_type)

        parsed = _psqpwd_urlparse(url)

        # 非标准 URL，直接字符串拼接
        if not parsed.scheme or not parsed.netloc:
            sep = "&" if "?" in url else "?"
            return url + sep + param_name + "=" + password

        query = dict(_psqpwd_parse_qsl(parsed.query, keep_blank_values=True))
        query[param_name] = password

        new_query = _psqpwd_urlencode(query)

        return _psqpwd_urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

    except Exception:
        try:
            sep = "&" if "?" in str(url or "") else "?"
            return str(url or "") + sep + "password=" + str(password or "")
        except Exception:
            return str(url or "")


# 覆盖上一版密码补全函数。
# 上一版 _psqcpf_build_panplay_detail / _psqcpf_playerContent 会运行时调用这个名字，
# 所以这里重新定义即可生效。
def _psqcpf_add_password_to_url(url, password):
    try:
        # 尽量从 URL 判断类型。
        return _psqpwd_add_password_to_url(url, password, "")
    except Exception:
        return str(url or "")


# 再额外覆盖 panplay detail，确保能把 api_type 也传进去判断。
def _psqpwd_build_panplay_detail(self, data):
    try:
        title = data.get("name") or "网盘资源"
        pic = data.get("pic") or getattr(self, "last_vod_pic", "") or ""
        url = data.get("url") or ""
        password = data.get("password") or ""
        api_type = data.get("api_type") or data.get("group") or ""

        if pic:
            self.last_vod_pic = pic

        final_url = _psqpwd_add_password_to_url(url, password, api_type)

        try:
            payload = self._encode_id({
                "type": "pan",
                "api_type": api_type,
                "url": final_url,
                "password": password,
                "pic": pic
            })
        except Exception:
            import json as _psqpwd_json
            import base64 as _psqpwd_base64
            payload = _psqpwd_base64.urlsafe_b64encode(
                _psqpwd_json.dumps({
                    "type": "pan",
                    "api_type": api_type,
                    "url": final_url,
                    "password": password,
                    "pic": pic
                }, ensure_ascii=False).encode("utf-8")
            ).decode("utf-8").rstrip("=")

        content = [
            "资源名称：%s" % title,
            "资源链接：%s" % url
        ]

        if final_url != url:
            content.append("推送链接：%s" % final_url)

        if password:
            content.append("提取码：%s" % password)

        state = data.get("state") or ""
        if state:
            content.append("检测状态：%s" % state)

        return {
            "list": [{
                "vod_id": "psq_panplay",
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": "自动推送",
                "vod_content": "\n".join(content),
                "vod_play_from": "推送",
                "vod_play_url": "自动推送$%s" % payload
            }]
        }

    except Exception as e:
        print("[PANSOU PASSWORD 115 FIX] build panplay detail error:", e)
        try:
            if "_psqcpf_build_panplay_detail" in globals():
                return _psqcpf_build_panplay_detail(self, data)
        except Exception:
            pass
        return {
            "list": []
        }


# 再额外覆盖 playerContent，确保最终 push 前也按 115=password 规则补一次。
def _psqpwd_playerContent(self, flag, pid, vipFlags):
    try:
        pid_s = str(pid or "")

        try:
            data = self._decode_id(pid_s)
        except Exception:
            data = None

        if isinstance(data, dict) and data.get("type") == "pan":
            url = data.get("url") or ""
            password = data.get("password") or ""
            api_type = data.get("api_type") or ""
            pic = data.get("pic") or getattr(self, "last_vod_pic", "")

            final_url = _psqpwd_add_password_to_url(url, password, api_type)

            return {
                "parse": 0,
                "playUrl": "",
                "url": "push://" + final_url,
                "pic": pic,
                "poster": pic,
                "header": {
                    "User-Agent": getattr(self, "HEADERS", {}).get("User-Agent", "Mozilla/5.0")
                }
            }

    except Exception as e:
        print("[PANSOU PASSWORD 115 FIX] player pre-handle error:", e)

    try:
        if "_PSQPWD_PREV_PLAYER" in globals() and _PSQPWD_PREV_PLAYER:
            return _PSQPWD_PREV_PLAYER(self, flag, pid, vipFlags)
    except Exception:
        pass

    try:
        if "_PSQCPF_PREV_PLAYER" in globals() and _PSQCPF_PREV_PLAYER:
            return _PSQCPF_PREV_PLAYER(self, flag, pid, vipFlags)
    except Exception:
        pass

    try:
        if "_PF_PREV_PLAYER" in globals() and _PF_PREV_PLAYER:
            return _PF_PREV_PLAYER(self, flag, pid, vipFlags)
    except Exception:
        pass

    return {
        "parse": 1,
        "playUrl": "",
        "url": pid
    }


try:
    _psq_build_panplay_detail = _psqpwd_build_panplay_detail
    print("[PANSOU PASSWORD 115 FIX] override _psq_build_panplay_detail ok")
except Exception as e:
    print("[PANSOU PASSWORD 115 FIX] override detail error:", e)


try:
    _PSQPWD_PREV_PLAYER = PanSouSpider.playerContent
    PanSouSpider.playerContent = _psqpwd_playerContent
    Spider = PanSouSpider
    print("[PANSOU PASSWORD 115 FIX] playerContent bind ok")
except Exception as e:
    print("[PANSOU PASSWORD 115 FIX] playerContent bind error:", e)


print("[PANSOU PASSWORD PARAM 115 FIX] loaded")
# ===== PANSOU_PASSWORD_PARAM_115_FIX_END =====
# ===== PANSOU_MAGNET_ONLY_115_ORIGINAL_PLAY_PATCH_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou 磁力三级详情页专用：新增“115原画播放”线路
#
# 作用范围：
#   只作用于点击三级目录里的“磁力链接资源”后生成的播放详情页。
#
# 不影响：
#   1. 网盘资源详情页 panplay；
#   2. ed2k 详情页；
#   3. 原 115云下载；
#   4. 原 播放列表；
#   5. 原 OpenList 查询；
#   6. 原 推送 / 磁力播放；
#   7. 原密码补全和检测逻辑。
#
# 线路规则：
#   1. 始终显示“115原画播放”；
#   2. 优先插入到“115云下载”后；
#   3. 没有“115云下载”时插到“0”后；
#   4. 复制原“播放列表”中的 __115_FILE__|xxx 项；
#   5. 没有缓存文件时显示占位提示；
#   6. 点击“115原画播放”时才构造 type=dwnz 原画播放地址。
# ============================================================

import json as _ps115op_json
import base64 as _ps115op_base64
import re as _ps115op_re
from urllib.parse import urlencode as _ps115op_urlencode
from urllib.parse import quote as _ps115op_quote

try:
    _PS115OP_TARGET = PanSouSpider
except Exception:
    _PS115OP_TARGET = globals().get("Spider")

try:
    _PS115OP_PREV_INIT = _PS115OP_TARGET.init
except Exception:
    _PS115OP_PREV_INIT = None

try:
    _PS115OP_PREV_PLAYER = _PS115OP_TARGET.playerContent
except Exception:
    _PS115OP_PREV_PLAYER = None

try:
    _PS115OP_PREV_MAGNET_DETAIL_BUILDER = globals().get("_psq_build_magnetplay_detail")
except Exception:
    _PS115OP_PREV_MAGNET_DETAIL_BUILDER = None


_PS115OP_DEFAULT_HOST = "127.0.0.1"
_PS115OP_DEFAULT_OK_PORT = "10078"
_PS115OP_DEFAULT_GO_PORT = "9978"
_PS115OP_DEFAULT_REFERER = "https://anxia.com/"
_PS115OP_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/138.0.0.0 Safari/537.36"
)


def _ps115op_parse_ext(extend):
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str) and extend.strip().startswith("{"):
            return _ps115op_json.loads(extend)
        return {}
    except Exception:
        return {}


def _ps115op_init(self, extend=""):
    """
    包装 init，只新增 115原画播放配置，不改原逻辑。
    """
    ret = None
    if _PS115OP_PREV_INIT:
        try:
            ret = _PS115OP_PREV_INIT(self, extend)
        except Exception as e:
            print("[PanSou 115原画播放 init] prev init error:", e)

    try:
        ext = _ps115op_parse_ext(extend)

        self.ps115op_host = str(
            ext.get(
                "ps115op_host",
                ext.get(
                    "jmv115op_host",
                    ext.get(
                        "jb115op_host",
                        getattr(self, "ps115op_host", _PS115OP_DEFAULT_HOST)
                    )
                )
            ) or _PS115OP_DEFAULT_HOST
        ).strip()

        self.ps115op_ok_port = str(
            ext.get(
                "ps115op_ok_port",
                ext.get(
                    "jmv115op_ok_port",
                    ext.get(
                        "jb115op_ok_port",
                        getattr(self, "ps115op_ok_port", _PS115OP_DEFAULT_OK_PORT)
                    )
                )
            ) or _PS115OP_DEFAULT_OK_PORT
        ).strip()

        self.ps115op_go_port = str(
            ext.get(
                "ps115op_go_port",
                ext.get(
                    "jmv115op_go_port",
                    ext.get(
                        "jb115op_go_port",
                        getattr(self, "ps115op_go_port", _PS115OP_DEFAULT_GO_PORT)
                    )
                )
            ) or _PS115OP_DEFAULT_GO_PORT
        ).strip()

        self.ps115op_referer = str(
            ext.get(
                "ps115op_referer",
                ext.get(
                    "jmv115op_referer",
                    ext.get(
                        "jb115op_referer",
                        getattr(self, "ps115op_referer", _PS115OP_DEFAULT_REFERER)
                    )
                )
            ) or _PS115OP_DEFAULT_REFERER
        ).strip()

        self.ps115op_ua = str(
            ext.get(
                "ps115op_ua",
                ext.get(
                    "jmv115op_ua",
                    ext.get(
                        "jb115op_ua",
                        getattr(self, "ps115op_ua", _PS115OP_DEFAULT_UA)
                    )
                )
            ) or _PS115OP_DEFAULT_UA
        ).strip()

        if "Chrome/138.0.0.0" not in self.ps115op_ua:
            self.ps115op_ua = _PS115OP_DEFAULT_UA

        print("[PanSou 115原画播放 init] host=%s ok_port=%s go_port=%s" % (
            self.ps115op_host,
            self.ps115op_ok_port,
            self.ps115op_go_port
        ))

    except Exception as e:
        print("[PanSou 115原画播放 init] error:", e)

    return ret if ret is not None else {}


def _ps115op_ack(self):
    try:
        if "_pf_ack" in globals():
            return _pf_ack(self)
    except Exception:
        pass
    try:
        if "_psq_ack" in globals():
            return _psq_ack(self)
    except Exception:
        pass
    return {
        "parse": 0,
        "playUrl": "",
        "url": getattr(self, "wait_video_url", "") or getattr(self, "ack_mp4", "") or "",
        "header": {
            "User-Agent": getattr(self, "HEADERS", {}).get("User-Agent", "Mozilla/5.0")
        }
    }


def _ps115op_get_pic(self, pid=""):
    try:
        return getattr(self, "last_vod_pic", "") or ""
    except Exception:
        return ""


def _ps115op_uid_from_cookie(cookie):
    try:
        m = _ps115op_re.search(r"(?:^|;\s*)UID=([^;]+)", str(cookie or ""))
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return ""


def _ps115op_ext(name):
    try:
        name = str(name or "").strip()
        if "." in name:
            ext = name.rsplit(".", 1)[-1].strip().lower()
            if ext:
                return ext
    except Exception:
        pass
    return "mp4"


def _ps115op_load_cache(self):
    try:
        if hasattr(self, "_115_cache_load"):
            return self._115_cache_load()
    except Exception as e:
        print("[PanSou 115原画播放 cache] _115_cache_load error:", e)

    try:
        if "_pf_115_cache_load" in globals():
            return _pf_115_cache_load(self)
    except Exception as e:
        print("[PanSou 115原画播放 cache] _pf_115_cache_load error:", e)

    return {
        "magnets": {},
        "files": {}
    }


def _ps115op_load_file_from_cache(self, fk):
    """
    fk 可以是 fid 或 pickcode。
    来源：
      播放列表里的 __115_FILE__|fk
    """
    fk = str(fk or "").strip()
    if not fk:
        return None

    try:
        # 优先调用最终补丁里已有的函数
        if "_pf_get_115_file_by_pid" in globals():
            f = _pf_get_115_file_by_pid(self, "__115_FILE__|" + fk)
            if isinstance(f, dict):
                return f
    except Exception:
        pass

    try:
        cache = _ps115op_load_cache(self)
        files_map = cache.get("files", {}) or {}

        if isinstance(files_map, dict):
            # 1. key 直接命中
            f = files_map.get(fk)
            if isinstance(f, dict):
                return f

            # 2. fid / pickcode 反查
            for _, v in files_map.items():
                if not isinstance(v, dict):
                    continue

                fid = str(
                    v.get("fid")
                    or v.get("file_id")
                    or v.get("id")
                    or ""
                ).strip()

                pc = str(
                    v.get("pickcode")
                    or v.get("pick_code")
                    or v.get("pickCode")
                    or v.get("pc")
                    or ""
                ).strip()

                if fk == fid or fk == pc:
                    return v

        # 3. magnets.records.files 兜底
        magnets_map = cache.get("magnets", {}) or {}
        if isinstance(magnets_map, dict):
            for _, rec in magnets_map.items():
                if not isinstance(rec, dict):
                    continue
                for v in rec.get("files") or []:
                    if not isinstance(v, dict):
                        continue
                    fid = str(v.get("fid") or v.get("file_id") or v.get("id") or "").strip()
                    pc = str(v.get("pickcode") or v.get("pick_code") or v.get("pickCode") or v.get("pc") or "").strip()
                    if fk == fid or fk == pc:
                        return v

    except Exception as e:
        print("[PanSou 115原画播放 cache] lookup error:", e)

    return None


def _ps115op_build_original_url(self, file_info):
    """
    构造 115 原画播放地址。

    内层 Go 代理：
      http://127.0.0.1:9978/proxy?do=115&type=dwnz&file_id=...&share_id=self&share_pwd=...&file_size=...&content_hash=...&file_name=ext

    外层 OK/PG：
      http://127.0.0.1:10078/p/32/null/{base64}/{ext}?header={HeaderJSON}
    """
    try:
        if not isinstance(file_info, dict):
            return "", {}

        fid = str(
            file_info.get("fid")
            or file_info.get("file_id")
            or file_info.get("id")
            or ""
        ).strip()

        pickcode = str(
            file_info.get("pickcode")
            or file_info.get("pick_code")
            or file_info.get("pickCode")
            or file_info.get("pc")
            or ""
        ).strip()

        name = str(
            file_info.get("name")
            or file_info.get("file_name")
            or file_info.get("fname")
            or ""
        ).strip()

        size = str(
            file_info.get("size")
            or file_info.get("file_size")
            or file_info.get("s")
            or "0"
        ).strip()

        sha1 = str(
            file_info.get("sha1")
            or file_info.get("sha")
            or file_info.get("file_sha1")
            or file_info.get("content_hash")
            or ""
        ).strip().upper()

        if not fid or not pickcode:
            print("[PanSou 115原画播放] missing fid/pickcode:", file_info)
            return "", {}

        ext = _ps115op_ext(name)

        host = str(getattr(self, "ps115op_host", _PS115OP_DEFAULT_HOST) or _PS115OP_DEFAULT_HOST).strip()
        ok_port = str(getattr(self, "ps115op_ok_port", _PS115OP_DEFAULT_OK_PORT) or _PS115OP_DEFAULT_OK_PORT).strip()
        go_port = str(getattr(self, "ps115op_go_port", _PS115OP_DEFAULT_GO_PORT) or _PS115OP_DEFAULT_GO_PORT).strip()
        referer = str(getattr(self, "ps115op_referer", _PS115OP_DEFAULT_REFERER) or _PS115OP_DEFAULT_REFERER).strip()
        ua = str(getattr(self, "ps115op_ua", _PS115OP_DEFAULT_UA) or _PS115OP_DEFAULT_UA).strip()

        if "Chrome/138.0.0.0" not in ua:
            ua = _PS115OP_DEFAULT_UA

        cookie = str(getattr(self, "pan_115_cookie", "") or "").strip()
        uid = _ps115op_uid_from_cookie(cookie)

        if not cookie:
            print("[PanSou 115原画播放] warning: pan_115_cookie empty")

        inner_params = [
            ("do", "115"),
            ("type", "dwnz"),
            ("file_id", fid),
            ("share_id", "self"),
            ("share_pwd", pickcode),
            ("file_size", size),
            ("content_hash", sha1),
            ("file_name", ext),
        ]

        inner_url = "http://%s:%s/proxy?%s" % (
            host,
            go_port,
            _ps115op_urlencode(inner_params)
        )

        inner_b64 = _ps115op_base64.b64encode(
            inner_url.encode("utf-8")
        ).decode("utf-8").rstrip("=")

        header_obj = {
            "cookie": cookie,
            "User-Agent": ua,
            "Referer": referer,
            "p115uid": uid,
            "SPEEDLIMIT": "0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        header_json = _ps115op_json.dumps(
            header_obj,
            ensure_ascii=False,
            separators=(",", ":")
        )

        header_encoded = _ps115op_quote(header_json, safe="()")

        final_url = (
            "http://%s:%s/p/32/null/%s/%s?header=%s"
            % (
                host,
                ok_port,
                inner_b64,
                ext,
                header_encoded
            )
        )

        try:
            self._ps115op_last_inner = inner_url
            self._ps115op_last_url = final_url
            self._ps115op_last_header = header_obj
        except Exception:
            pass

        print("[PanSou 115原画播放] build ok")
        print("[PanSou 115原画播放] name=%s" % name)
        print("[PanSou 115原画播放] fid=%s" % fid)
        print("[PanSou 115原画播放] pickcode=%s" % pickcode)
        print("[PanSou 115原画播放] size=%s" % size)
        print("[PanSou 115原画播放] sha1=%s" % sha1)
        print("[PanSou 115原画播放] inner=%s" % inner_url)
        print("[PanSou 115原画播放] final=%s" % final_url)

        return final_url, header_obj

    except Exception as e:
        print("[PanSou 115原画播放] build url error:", e)
        return "", {}


def _ps115op_is_115_file_item(play_item):
    try:
        s = str(play_item or "")
        if "$" not in s:
            return False
        _, pid = s.split("$", 1)
        return str(pid or "").strip().startswith("__115_FILE__|")
    except Exception:
        return False


def _ps115op_filter_115_file_items(source_url):
    """
    从原“播放列表”线路中提取 __115_FILE__ 项。
    """
    out = []
    try:
        for it in str(source_url or "").split("#"):
            it = str(it or "").strip()
            if not it:
                continue
            if _ps115op_is_115_file_item(it):
                out.append(it)
    except Exception:
        pass
    return "#".join(out)


def _ps115op_find_line(flags, name):
    try:
        name = str(name or "").strip()
        for i, f in enumerate(flags or []):
            if str(f or "").strip() == name:
                return i
    except Exception:
        pass
    return -1


def _ps115op_add_original_line_to_magnet_detail(self, ret):
    """
    只给磁力三级详情页增加“115原画播放”。
    """
    try:
        if not isinstance(ret, dict):
            return ret

        lst = ret.get("list") or []
        if not isinstance(lst, list) or not lst:
            return ret

        vod = lst[0]
        if not isinstance(vod, dict):
            return ret

        # 防止误加到非磁力详情：
        # 你的磁力详情 vod_id 固定是 psq_magnetplay，vod_remarks 是 磁力资源。
        vod_id = str(vod.get("vod_id") or "")
        remarks = str(vod.get("vod_remarks") or "")
        if vod_id != "psq_magnetplay" and "磁力" not in remarks:
            return ret

        play_from_raw = str(vod.get("vod_play_from", "") or "")
        play_url_raw = str(vod.get("vod_play_url", "") or "")

        flags = play_from_raw.split("$$$") if play_from_raw else []
        urls = play_url_raw.split("$$$") if play_url_raw else []

        max_len = max(len(flags), len(urls))
        while len(flags) < max_len:
            flags.append("")
        while len(urls) < max_len:
            urls.append("")

        # 已存在则不重复添加
        if "115原画播放" in [str(x or "").strip() for x in flags]:
            return ret

        # 从原“播放列表”复制 __115_FILE__ 项
        playlist_idx = _ps115op_find_line(flags, "播放列表")
        original_items = ""

        if playlist_idx >= 0 and playlist_idx < len(urls):
            original_items = _ps115op_filter_115_file_items(urls[playlist_idx])

        # 始终显示
        if not original_items:
            original_items = "暂无115原画缓存，请先点115云下载-下载状态$__ACK__"

        # 顺序：
        #   1. 优先 115云下载 后；
        #   2. 否则 0 后；
        #   3. 否则最前。
        cloud_idx = _ps115op_find_line(flags, "115云下载")
        zero_idx = _ps115op_find_line(flags, "0")

        if cloud_idx >= 0:
            insert_idx = cloud_idx + 1
        elif zero_idx >= 0:
            insert_idx = zero_idx + 1
        else:
            insert_idx = 0

        flags.insert(insert_idx, "115原画播放")
        urls.insert(insert_idx, original_items)

        vod["vod_play_from"] = "$$$".join(flags)
        vod["vod_play_url"] = "$$$".join(urls)

        print("[PanSou 115原画播放] magnet detail line added, insert_idx=%s, has_file=%s" % (
            insert_idx,
            "__115_FILE__|" in original_items
        ))

        return ret

    except Exception as e:
        print("[PanSou 115原画播放] add line error:", e)
        return ret


def _ps115op_build_magnetplay_detail(self, data):
    """
    包装原 _psq_build_magnetplay_detail。
    只对磁力三级详情页追加 115原画播放。
    """
    try:
        old = _PS115OP_PREV_MAGNET_DETAIL_BUILDER
        if old:
            ret = old(self, data)
        else:
            ret = {
                "list": []
            }
        return _ps115op_add_original_line_to_magnet_detail(self, ret)
    except Exception as e:
        print("[PanSou 115原画播放] magnet detail wrapper error:", e)
        try:
            if _PS115OP_PREV_MAGNET_DETAIL_BUILDER:
                return _PS115OP_PREV_MAGNET_DETAIL_BUILDER(self, data)
        except Exception:
            pass
        return {
            "list": []
        }


def _ps115op_playerContent(self, flag, pid, vipFlags):
    """
    只接管 flag == 115原画播放。
    其他所有播放逻辑原样交回上一层。
    """
    try:
        flag_s = str(flag or "").strip()
        pid_s = str(pid or "").strip()

        if flag_s == "115原画播放":
            pic = _ps115op_get_pic(self, pid_s)

            if not pid_s.startswith("__115_FILE__|"):
                print("[PanSou 115原画播放] invalid pid:", pid_s)
                ret = _ps115op_ack(self)
                if pic and isinstance(ret, dict):
                    ret["pic"] = ret.get("pic") or pic
                    ret["poster"] = ret.get("poster") or pic
                return ret

            fk = pid_s.split("|", 1)[1].strip()
            if not fk:
                ret = _ps115op_ack(self)
                if pic and isinstance(ret, dict):
                    ret["pic"] = ret.get("pic") or pic
                    ret["poster"] = ret.get("poster") or pic
                return ret

            f = _ps115op_load_file_from_cache(self, fk)
            if not f:
                print("[PanSou 115原画播放] cache miss:", fk)
                ret = _ps115op_ack(self)
                if pic and isinstance(ret, dict):
                    ret["pic"] = ret.get("pic") or pic
                    ret["poster"] = ret.get("poster") or pic
                return ret

            final_url, header_obj = _ps115op_build_original_url(self, f)
            if not final_url:
                ret = _ps115op_ack(self)
                if pic and isinstance(ret, dict):
                    ret["pic"] = ret.get("pic") or pic
                    ret["poster"] = ret.get("poster") or pic
                return ret

            ret = {
                "parse": 0,
                "playUrl": "",
                "url": final_url,
                "header": header_obj
            }

            if pic:
                ret["pic"] = pic
                ret["poster"] = pic

            print("[PanSou 115原画播放] player ret ok")
            return ret

        # 其他线路完全走原逻辑
        if _PS115OP_PREV_PLAYER:
            return _PS115OP_PREV_PLAYER(self, flag, pid, vipFlags)

        return {
            "parse": 1,
            "playUrl": "",
            "url": pid_s,
            "header": getattr(self, "HEADERS", {})
        }

    except Exception as e:
        print("[PanSou 115原画播放] playerContent error:", e)
        try:
            if _PS115OP_PREV_PLAYER:
                return _PS115OP_PREV_PLAYER(self, flag, pid, vipFlags)
        except Exception:
            pass
        return _ps115op_ack(self)


try:
    if _PS115OP_TARGET is not None:
        _PS115OP_TARGET.init = _ps115op_init
        _PS115OP_TARGET.playerContent = _ps115op_playerContent

        # 关键：只覆盖全局磁力详情构造函数。
        # _psq_detailContent 运行时查找 _psq_build_magnetplay_detail，
        # 所以只重定义这个函数即可只影响磁力三级详情页。
        globals()["_psq_build_magnetplay_detail"] = _ps115op_build_magnetplay_detail

        # 调试方法挂到类上
        _PS115OP_TARGET._ps115op_build_original_url = _ps115op_build_original_url
        _PS115OP_TARGET._ps115op_load_file_from_cache = _ps115op_load_file_from_cache

        Spider = _PS115OP_TARGET

        print("[PANSOU MAGNET ONLY 115 ORIGINAL PLAY PATCH] loaded")
        print("[PANSOU MAGNET ONLY 115 ORIGINAL PLAY PATCH] 仅磁力三级详情页新增：115原画播放")
        print("[PANSOU MAGNET ONLY 115 ORIGINAL PLAY PATCH] 位置：115云下载后，否则0线路后")
        print("[PANSOU MAGNET ONLY 115 ORIGINAL PLAY PATCH] 点击时构造 type=dwnz 原画地址")
except Exception as e:
    print("[PANSOU MAGNET ONLY 115 ORIGINAL PLAY PATCH] load error:", e)

# ===== PANSOU_MAGNET_ONLY_115_ORIGINAL_PLAY_PATCH_END =====
# ===== PANSOU_115_QUARK_SHARE_ORIGINAL_FULL_V2_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou 115/夸克 分享原画播放完整 V2 补丁
#
# 可直接追加在原代码末尾，不依赖任何旧补丁。
#
# 功能：
#   1. 三级目录 115网盘资源 -> 115分享原画播放
#   2. 三级目录 夸克网盘资源 -> 夸克分享原画播放
#   3. 分享文件列表按文件名自然排序
#
# 地址分离：
#   outer OK代理：播放器访问
#     默认 http://127.0.0.1:10078
#
#   inner Go代理：OK代理内部访问
#     默认 http://127.0.0.1:9978
#
# 推荐 ext：
#   {
#     "psgo_ok_host": "192.168.10.245",
#     "psgo_ok_port": "10078",
#     "psgo_go_host": "127.0.0.1",
#     "psgo_go_port": "9978"
#   }
#
# 115 inner：
#   http://127.0.0.1:9978/proxy?do=115&type=dwnz
#     &file_id=fid
#     &share_id=share_code
#     &share_pwd=receive_code
#     &file_size=size
#     &content_hash=sha1
#     &file_name=ext
#
# 115 outer：
#   http://OK_HOST:10078/p/32/null/{base64(inner)}/{ext}?header={HeaderJSON}
#
# 夸克 inner，按你验证成功格式：
#   http://127.0.0.1:9978/proxy?do=quark&type=dwnz
#     &file_id=fid_share_fid_token
#     &share_id=pwd_id
#     &pass_code=提取码
#     &file_name=完整文件名
#
# 夸克 outer：
#   http://OK_HOST:10078/p/32/null/262144/{base64(inner)}/{完整文件名}
#
# 夸克 CK：
#   不需要在 ext 里配置，交给 PG本地包/Go代理自行处理。
# ============================================================

import re as _psgv2_re
import json as _psgv2_json
import base64 as _psgv2_base64
import requests as _psgv2_requests
from urllib.parse import (
    urlparse as _psgv2_urlparse,
    parse_qsl as _psgv2_parse_qsl,
    urlencode as _psgv2_urlencode,
    quote as _psgv2_quote,
)

try:
    _PSGV2_TARGET = PanSouSpider
except Exception:
    _PSGV2_TARGET = globals().get("Spider")

try:
    _PSGV2_PREV_INIT = _PSGV2_TARGET.init
except Exception:
    _PSGV2_PREV_INIT = None

try:
    _PSGV2_PREV_PLAYER = _PSGV2_TARGET.playerContent
except Exception:
    _PSGV2_PREV_PLAYER = None

try:
    _PSGV2_PREV_BUILD_PANPLAY_DETAIL = globals().get("_psq_build_panplay_detail")
except Exception:
    _PSGV2_PREV_BUILD_PANPLAY_DETAIL = None


_PSGV2_DEFAULT_OK_HOST = "127.0.0.1"
_PSGV2_DEFAULT_OK_PORT = "10078"
_PSGV2_DEFAULT_GO_HOST = "127.0.0.1"
_PSGV2_DEFAULT_GO_PORT = "9978"

_PSGV2_115_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/138.0.0.0 Safari/537.36"
)

_PSGV2_115_REFERER = "https://anxia.com/"

_PSGV2_QUARK_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "quark-cloud-drive/2.5.20 "
    "Chrome/100.0.4896.160 "
    "Electron/18.3.5.4-b478491100 "
    "Safari/537.36 Channel/pckk_other_ch"
)


# ============================================================
# 通用
# ============================================================

def _psgv2_parse_ext(extend):
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str) and extend.strip().startswith("{"):
            return _psgv2_json.loads(extend)
        return {}
    except Exception:
        return {}


def _psgv2_init(self, extend=""):
    ret = None

    if _PSGV2_PREV_INIT:
        try:
            ret = _PSGV2_PREV_INIT(self, extend)
        except Exception as e:
            print("[PanSou 原画V2 init] prev init error:", e)

    try:
        ext = _psgv2_parse_ext(extend)

        # outer OK代理地址
        self.psgo_ok_host = str(
            ext.get(
                "psgo_ok_host",
                ext.get("ok_host", getattr(self, "psgo_ok_host", _PSGV2_DEFAULT_OK_HOST))
            ) or _PSGV2_DEFAULT_OK_HOST
        ).strip()

        self.psgo_ok_port = str(
            ext.get(
                "psgo_ok_port",
                ext.get("ok_port", getattr(self, "psgo_ok_port", _PSGV2_DEFAULT_OK_PORT))
            ) or _PSGV2_DEFAULT_OK_PORT
        ).strip()

        # inner Go代理地址，默认 127.0.0.1:9978
        self.psgo_go_host = str(
            ext.get(
                "psgo_go_host",
                ext.get("go_host", getattr(self, "psgo_go_host", _PSGV2_DEFAULT_GO_HOST))
            ) or _PSGV2_DEFAULT_GO_HOST
        ).strip()

        self.psgo_go_port = str(
            ext.get(
                "psgo_go_port",
                ext.get("go_port", getattr(self, "psgo_go_port", _PSGV2_DEFAULT_GO_PORT))
            ) or _PSGV2_DEFAULT_GO_PORT
        ).strip()

        try:
            self.psgo_max_depth = max(
                1,
                int(ext.get("psgo_max_depth", getattr(self, "psgo_max_depth", 3)))
            )
        except Exception:
            self.psgo_max_depth = 3

        # 115 cookie 兼容读取
        self.psgo_115_cookie = str(
            ext.get(
                "pan_115_cookie",
                ext.get(
                    "psgo_115_cookie",
                    ext.get(
                        "cookie_115",
                        getattr(self, "psgo_115_cookie", getattr(self, "pan_115_cookie", ""))
                    )
                )
            ) or ""
        ).strip()

        # 夸克 CK 仅用于列目录时可选携带，不参与最终播放地址。
        self.psgo_quark_cookie = str(
            ext.get(
                "quark_cookie",
                ext.get(
                    "pan_quark_cookie",
                    ext.get(
                        "cookie_quark",
                        getattr(self, "psgo_quark_cookie", "")
                    )
                )
            ) or ""
        ).strip()

        print("[PanSou 原画V2 init] outer OK = %s:%s" % (
            self.psgo_ok_host,
            self.psgo_ok_port,
        ))
        print("[PanSou 原画V2 init] inner GO = %s:%s" % (
            self.psgo_go_host,
            self.psgo_go_port,
        ))
        print("[PanSou 原画V2 init] depth=%s 115_cookie=%s quark_cookie_for_list=%s" % (
            self.psgo_max_depth,
            "yes" if self.psgo_115_cookie else "no",
            "yes" if self.psgo_quark_cookie else "no",
        ))

    except Exception as e:
        print("[PanSou 原画V2 init] error:", e)

    return ret if ret is not None else {}


def _psgv2_hosts(self):
    ok_host = str(getattr(self, "psgo_ok_host", _PSGV2_DEFAULT_OK_HOST) or _PSGV2_DEFAULT_OK_HOST).strip()
    ok_port = str(getattr(self, "psgo_ok_port", _PSGV2_DEFAULT_OK_PORT) or _PSGV2_DEFAULT_OK_PORT).strip()
    go_host = str(getattr(self, "psgo_go_host", _PSGV2_DEFAULT_GO_HOST) or _PSGV2_DEFAULT_GO_HOST).strip()
    go_port = str(getattr(self, "psgo_go_port", _PSGV2_DEFAULT_GO_PORT) or _PSGV2_DEFAULT_GO_PORT).strip()
    return ok_host, ok_port, go_host, go_port


def _psgv2_ack(self):
    try:
        if "_pf_ack" in globals():
            return _pf_ack(self)
    except Exception:
        pass

    try:
        if "_psq_ack" in globals():
            return _psq_ack(self)
    except Exception:
        pass

    return {
        "parse": 0,
        "playUrl": "",
        "url": getattr(self, "wait_video_url", "") or getattr(self, "ack_mp4", "") or "",
        "header": {
            "User-Agent": getattr(self, "HEADERS", {}).get("User-Agent", "Mozilla/5.0")
        }
    }


def _psgv2_b64e_json(obj):
    try:
        txt = _psgv2_json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        return _psgv2_base64.urlsafe_b64encode(
            txt.encode("utf-8")
        ).decode("utf-8").rstrip("=")
    except Exception:
        return ""


def _psgv2_b64d_json(text):
    try:
        text = str(text or "")
        text += "=" * (-len(text) % 4)
        raw = _psgv2_base64.urlsafe_b64decode(
            text.encode("utf-8")
        ).decode("utf-8")
        return _psgv2_json.loads(raw)
    except Exception:
        return {}


def _psgv2_is_video(name):
    try:
        n = str(name or "").lower()
        return n.endswith((
            ".mp4", ".mkv", ".iso", ".avi", ".mov", ".wmv", ".flv",
            ".ts", ".m2ts", ".webm", ".m3u8", ".rmvb",
            ".mpg", ".mpeg", ".3gp", ".m4v", ".vob", ".f4v"
        ))
    except Exception:
        return False


def _psgv2_file_ext(name):
    try:
        name = str(name or "").strip()
        if "." in name:
            ext = name.rsplit(".", 1)[-1].strip().lower()
            if ext:
                return ext
    except Exception:
        pass
    return "mp4"


def _psgv2_format_size(size):
    try:
        size = int(size or 0)
        if size >= 1024 ** 4:
            return "%.2fTB" % (size / 1024 ** 4)
        if size >= 1024 ** 3:
            return "%.2fGB" % (size / 1024 ** 3)
        if size >= 1024 ** 2:
            return "%.2fMB" % (size / 1024 ** 2)
        if size >= 1024:
            return "%.2fKB" % (size / 1024)
        if size > 0:
            return "%dB" % size
    except Exception:
        pass
    return ""


def _psgv2_clean_name(name, limit=180):
    try:
        name = str(name or "")
        name = name.replace("#", "＃").replace("$", "＄")
        name = name.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        name = _psgv2_re.sub(r"\s+", " ", name).strip()
        if not name:
            name = "视频"
        return name[:limit]
    except Exception:
        return "视频"


def _psgv2_nat_key(text):
    try:
        text = str(text or "").strip().lower()
        parts = _psgv2_re.split(r"(\d+)", text)
        out = []
        for p in parts:
            out.append(int(p) if p.isdigit() else p)
        return out
    except Exception:
        return [str(text or "").lower()]


def _psgv2_episode_key(name):
    try:
        raw = str(name or "")
        low = raw.lower()

        m = _psgv2_re.search(r"\bs(\d{1,3})\s*e(\d{1,4})\b", low, _psgv2_re.I)
        if m:
            return (0, int(m.group(1)), int(m.group(2)), _psgv2_nat_key(raw))

        m = _psgv2_re.search(r"\b(\d{1,3})x(\d{1,4})\b", low, _psgv2_re.I)
        if m:
            return (0, int(m.group(1)), int(m.group(2)), _psgv2_nat_key(raw))

        m = _psgv2_re.search(r"\b(?:ep|episode|e)\s*0*(\d{1,4})\b", low, _psgv2_re.I)
        if m:
            return (1, 1, int(m.group(1)), _psgv2_nat_key(raw))

        m = _psgv2_re.search(r"第\s*0*(\d{1,4})\s*[集话話]", raw)
        if m:
            return (1, 1, int(m.group(1)), _psgv2_nat_key(raw))

        m = _psgv2_re.search(r"^\s*0*(\d{1,4})(?:[\s._\-集话話]|$)", raw)
        if m:
            return (2, 1, int(m.group(1)), _psgv2_nat_key(raw))

        return (9, 999, 999999, _psgv2_nat_key(raw))

    except Exception:
        return (9, 999, 999999, _psgv2_nat_key(name))


def _psgv2_sort_files(files):
    out = []
    seen = set()

    for f in files or []:
        try:
            if not isinstance(f, dict):
                continue
            k = "%s|%s|%s" % (
                str(f.get("fid") or f.get("file_id") or ""),
                str(f.get("name") or f.get("file_name") or ""),
                str(f.get("sha1") or f.get("content_hash") or f.get("share_fid_token") or "")
            )
            if k in seen:
                continue
            seen.add(k)
            out.append(f)
        except Exception:
            pass

    out.sort(key=lambda x: _psgv2_episode_key(x.get("name") or x.get("file_name") or ""))
    return out


# ============================================================
# 类型判断
# ============================================================

def _psgv2_is_115_type(api_type):
    try:
        return str(api_type or "").strip().lower() in ["115", "a115"]
    except Exception:
        return False


def _psgv2_is_quark_type(api_type):
    try:
        return str(api_type or "").strip().lower() in ["quark"]
    except Exception:
        return False


def _psgv2_is_115_url(url):
    try:
        u = str(url or "").lower()
        return "115.com/s/" in u or "115cdn.com/s/" in u or "anxia.com/s/" in u
    except Exception:
        return False


def _psgv2_is_quark_url(url):
    try:
        return "pan.quark.cn/s/" in str(url or "").lower()
    except Exception:
        return False


# ============================================================
# 115
# ============================================================

def _psgv2_get_115_cookie(self):
    try:
        ck = str(getattr(self, "psgo_115_cookie", "") or "").strip()
        if ck:
            return ck
    except Exception:
        pass

    for attr in [
        "pan_115_cookie",
        "cookie_115",
        "pan115_cookie",
        "jb115_cookie",
        "jbo_final_cookie",
        "cookie",
        "_cookie",
    ]:
        try:
            v = str(getattr(self, attr, "") or "").strip()
            if v and ("UID=" in v or "CID=" in v or "SEID=" in v):
                return v
        except Exception:
            pass

    return ""


def _psgv2_uid_from_115_cookie(cookie):
    try:
        m = _psgv2_re.search(r"(?:^|;\s*)UID=([^;]+)", str(cookie or ""))
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return ""


def _psgv2_115_headers(self):
    ck = _psgv2_get_115_cookie(self)
    h = {
        "User-Agent": _PSGV2_115_UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://115.com/",
        "Origin": "https://115.com",
    }
    if ck:
        h["Cookie"] = ck
    return h


def _psgv2_parse_115_url(url, password=""):
    try:
        url = str(url or "").strip().replace("&amp;", "&")
        password = str(password or "").strip()

        if not url:
            return {}

        if not url.startswith(("http://", "https://")):
            url = "https://" + url.lstrip("/")

        p = _psgv2_urlparse(url)
        m = _psgv2_re.search(r"/s/([A-Za-z0-9_\-]+)", p.path or "", _psgv2_re.I)
        if not m:
            return {}

        share_code = m.group(1).strip()
        q = dict(_psgv2_parse_qsl(p.query or "", keep_blank_values=True))

        receive_code = (
            q.get("password")
            or q.get("pwd")
            or q.get("passcode")
            or q.get("code")
            or q.get("receive_code")
            or password
            or ""
        )

        return {
            "url": url,
            "share_code": share_code,
            "receive_code": str(receive_code or "").strip(),
        }

    except Exception as e:
        print("[PanSou 115原画V2] parse url error:", e)
        return {}


def _psgv2_115_snap(self, share_code, receive_code="", cid="0", offset=0, limit=200):
    try:
        s = _psgv2_requests.Session()
        s.verify = False

        params = {
            "share_code": share_code,
            "receive_code": receive_code or "",
            "cid": str(cid or "0"),
            "offset": int(offset or 0),
            "limit": int(limit or 200),
        }

        r = s.get(
            "https://webapi.115.com/share/snap",
            headers=_psgv2_115_headers(self),
            params=params,
            timeout=20,
            verify=False,
        )

        txt = r.text or ""
        if r.status_code != 200:
            print("[PanSou 115原画V2 snap] HTTP=%s text=%s" % (r.status_code, txt[:200]))
            return {}

        data = r.json()
        if data.get("state") is False:
            print("[PanSou 115原画V2 snap] state false:", data)

        return data

    except Exception as e:
        print("[PanSou 115原画V2 snap] error:", e)
        return {}


def _psgv2_115_name(it):
    return str(it.get("n") or it.get("name") or it.get("file_name") or it.get("fname") or "")


def _psgv2_115_size(it):
    try:
        return int(it.get("s") or it.get("size") or it.get("file_size") or 0)
    except Exception:
        return 0


def _psgv2_115_fid(it):
    return str(it.get("fid") or it.get("file_id") or it.get("id") or "")


def _psgv2_115_cid(it):
    return str(it.get("cid") or it.get("category_id") or it.get("file_id") or it.get("fid") or it.get("id") or "")


def _psgv2_115_sha1(it):
    return str(it.get("sha") or it.get("sha1") or it.get("file_sha1") or it.get("content_hash") or "")


def _psgv2_115_is_dir(it):
    try:
        name = _psgv2_115_name(it)
        size = _psgv2_115_size(it)
        sha1 = _psgv2_115_sha1(it)

        if it.get("is_dir") is True or it.get("isDir") is True:
            return True

        if str(it.get("type", "")).lower() in ["1", "dir", "folder"]:
            return True

        if str(it.get("fc", "")) == "0" and not _psgv2_is_video(name):
            return True

        if size <= 0 and not sha1 and not _psgv2_is_video(name):
            return True

        return False

    except Exception:
        return False


def _psgv2_115_list_videos(self, share_code, receive_code="", cid="0", depth=0, max_depth=None):
    out = []

    try:
        if max_depth is None:
            max_depth = int(getattr(self, "psgo_max_depth", 3) or 3)

        if depth > max_depth:
            return []

        data = _psgv2_115_snap(self, share_code, receive_code, cid=cid, offset=0, limit=200)
        if not data:
            return []

        d = data.get("data") or {}

        if isinstance(d, list):
            items = d
        else:
            items = d.get("list") or d.get("data") or d.get("files") or d.get("content") or []

        if not isinstance(items, list):
            items = []

        print("[PanSou 115原画V2 list] share=%s cid=%s depth=%s count=%s" % (
            share_code,
            cid,
            depth,
            len(items),
        ))

        for it in items:
            try:
                if not isinstance(it, dict):
                    continue

                name = _psgv2_115_name(it)
                if not name:
                    continue

                if _psgv2_115_is_dir(it):
                    child = _psgv2_115_cid(it)
                    if child and depth < max_depth:
                        out.extend(
                            _psgv2_115_list_videos(
                                self,
                                share_code,
                                receive_code,
                                cid=child,
                                depth=depth + 1,
                                max_depth=max_depth,
                            )
                        )
                    continue

                if not _psgv2_is_video(name):
                    continue

                fid = _psgv2_115_fid(it)
                if not fid:
                    continue

                out.append({
                    "source": "115share",
                    "name": name,
                    "file_name": name,
                    "fid": fid,
                    "file_id": fid,
                    "size": _psgv2_115_size(it),
                    "sha1": _psgv2_115_sha1(it),
                    "share_code": share_code,
                    "share_id": share_code,
                    "receive_code": receive_code or "",
                    "share_pwd": receive_code or "",
                    "cid": str(cid or "0"),
                })

            except Exception as e:
                print("[PanSou 115原画V2 list item] error:", e)

    except Exception as e:
        print("[PanSou 115原画V2 list] error:", e)

    return _psgv2_sort_files(out)


def _psgv2_build_115_items(self, share_info):
    try:
        share_code = share_info.get("share_code") or ""
        receive_code = share_info.get("receive_code") or ""

        if not share_code:
            return ""

        videos = _psgv2_115_list_videos(
            self,
            share_code,
            receive_code,
            cid="0",
            depth=0,
            max_depth=getattr(self, "psgo_max_depth", 3),
        )

        items = []

        for v in videos:
            try:
                name = v.get("name") or v.get("file_name") or "115视频"
                size = _psgv2_format_size(v.get("size") or 0)
                show = _psgv2_clean_name(("%s %s" % (size, name)).strip(), 180)
                pid = "__PSGV2_115_FILE__|" + _psgv2_b64e_json(v)
                items.append("%s$%s" % (show, pid))
            except Exception:
                pass

        return "#".join(items)

    except Exception as e:
        print("[PanSou 115原画V2] build items error:", e)
        return ""


def _psgv2_build_115_url(self, file_info):
    try:
        if not isinstance(file_info, dict):
            return "", {}

        fid = str(file_info.get("fid") or file_info.get("file_id") or "").strip()
        share_code = str(file_info.get("share_code") or file_info.get("share_id") or "").strip()
        receive_code = str(file_info.get("receive_code") or file_info.get("share_pwd") or "").strip()
        name = str(file_info.get("name") or file_info.get("file_name") or "video.mp4").strip()
        size = str(file_info.get("size") or file_info.get("file_size") or "0").strip()
        sha1 = str(file_info.get("sha1") or file_info.get("content_hash") or "").strip().upper()

        if not fid or not share_code:
            print("[PanSou 115原画V2] missing fid/share_code:", file_info)
            return "", {}

        ext = _psgv2_file_ext(name)
        ok_host, ok_port, go_host, go_port = _psgv2_hosts(self)

        inner_params = [
            ("do", "115"),
            ("type", "dwnz"),
            ("file_id", fid),
            ("share_id", share_code),
            ("share_pwd", receive_code),
            ("file_size", size),
            ("content_hash", sha1),
            ("file_name", ext),
        ]

        inner_url = "http://%s:%s/proxy?%s" % (
            go_host,
            go_port,
            _psgv2_urlencode(inner_params),
        )

        inner_b64 = _psgv2_base64.b64encode(
            inner_url.encode("utf-8")
        ).decode("utf-8").rstrip("=")

        cookie = _psgv2_get_115_cookie(self)
        uid = _psgv2_uid_from_115_cookie(cookie)

        header_obj = {
            "cookie": cookie,
            "User-Agent": _PSGV2_115_UA,
            "Referer": _PSGV2_115_REFERER,
            "p115uid": uid,
            "SPEEDLIMIT": "0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        header_json = _psgv2_json.dumps(
            header_obj,
            ensure_ascii=False,
            separators=(",", ":")
        )

        final_url = (
            "http://%s:%s/p/32/null/%s/%s?header=%s"
            % (
                ok_host,
                ok_port,
                inner_b64,
                ext,
                _psgv2_quote(header_json, safe="()"),
            )
        )

        print("[PanSou 115原画V2] build ok")
        print("[PanSou 115原画V2] inner=%s" % inner_url)
        print("[PanSou 115原画V2] final=%s" % final_url)

        return final_url, header_obj

    except Exception as e:
        print("[PanSou 115原画V2] build url error:", e)
        return "", {}


# ============================================================
# 夸克
# ============================================================

def _psgv2_quark_headers(self, referer=""):
    try:
        h = {
            "User-Agent": _PSGV2_QUARK_UA,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Referer": referer or "https://pan.quark.cn/",
            "Origin": "https://pan.quark.cn",
        }

        ck = str(getattr(self, "psgo_quark_cookie", "") or "").strip()
        if ck:
            h["Cookie"] = ck

        return h

    except Exception:
        return {
            "User-Agent": _PSGV2_QUARK_UA,
            "Accept": "application/json, text/plain, */*",
        }


def _psgv2_parse_quark_url(url, password=""):
    try:
        url = str(url or "").strip().replace("&amp;", "&")
        password = str(password or "").strip()

        if not url:
            return {}

        if not url.startswith(("http://", "https://")):
            url = "https://" + url.lstrip("/")

        p = _psgv2_urlparse(url)
        m = _psgv2_re.search(r"/s/([A-Za-z0-9_\-]+)", p.path or "", _psgv2_re.I)
        if not m:
            return {}

        pwd_id = m.group(1).strip()
        q = dict(_psgv2_parse_qsl(p.query or "", keep_blank_values=True))

        passcode = (
            q.get("pwd")
            or q.get("password")
            or q.get("passcode")
            or q.get("code")
            or password
            or ""
        )

        passcode = str(passcode or "").strip()

        return {
            "url": url,
            "pwd_id": pwd_id,
            "share_id": pwd_id,
            "passcode": passcode,
            "pass_code": passcode,
        }

    except Exception as e:
        print("[PanSou 夸克原画V2] parse url error:", e)
        return {}


def _psgv2_quark_get_stoken(self, pwd_id, passcode=""):
    try:
        url = (
            "https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token"
            "?pr=ucpro&fr=pc&uc_param_str="
        )

        payload = {
            "pwd_id": pwd_id,
            "passcode": passcode or "",
        }

        referer = "https://pan.quark.cn/s/%s" % pwd_id

        s = _psgv2_requests.Session()
        s.verify = False

        r = s.post(
            url,
            headers=_psgv2_quark_headers(self, referer),
            json=payload,
            timeout=20,
            verify=False,
        )

        txt = r.text or ""
        if r.status_code != 200:
            print("[PanSou 夸克原画V2 stoken] HTTP=%s text=%s" % (r.status_code, txt[:200]))
            return ""

        data = r.json()
        stoken = (data.get("data") or {}).get("stoken") or data.get("stoken") or ""

        if not stoken:
            print("[PanSou 夸克原画V2 stoken] empty:", data)

        return str(stoken or "")

    except Exception as e:
        print("[PanSou 夸克原画V2 stoken] error:", e)
        return ""


def _psgv2_quark_list_files(self, pwd_id, stoken, pdir_fid="0", depth=0, max_depth=None):
    out = []

    try:
        if max_depth is None:
            max_depth = int(getattr(self, "psgo_max_depth", 3) or 3)

        if depth > max_depth:
            return []

        url = (
            "https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail"
            "?pr=ucpro&fr=pc&uc_param_str="
        )

        params = {
            "pwd_id": pwd_id,
            "stoken": stoken,
            "pdir_fid": pdir_fid or "0",
            "_page": 1,
            "_size": 200,
            "_sort": "file_type:asc,updated_at:desc",
        }

        referer = "https://pan.quark.cn/s/%s" % pwd_id

        s = _psgv2_requests.Session()
        s.verify = False

        r = s.get(
            url,
            headers=_psgv2_quark_headers(self, referer),
            params=params,
            timeout=20,
            verify=False,
        )

        txt = r.text or ""
        if r.status_code != 200:
            print("[PanSou 夸克原画V2 list] HTTP=%s text=%s" % (r.status_code, txt[:200]))
            return []

        data = r.json()
        d = data.get("data") or {}

        items = d.get("list") or d.get("files") or d.get("content") or []

        if not isinstance(items, list):
            items = []

        print("[PanSou 夸克原画V2 list] pwd_id=%s pdir=%s depth=%s count=%s" % (
            pwd_id,
            pdir_fid,
            depth,
            len(items),
        ))

        for it in items:
            try:
                if not isinstance(it, dict):
                    continue

                name = str(it.get("file_name") or it.get("name") or "").strip()
                fid = str(it.get("fid") or it.get("file_id") or it.get("id") or "").strip()

                if not name or not fid:
                    continue

                share_fid_token = str(
                    it.get("share_fid_token")
                    or it.get("fid_token")
                    or it.get("file_token")
                    or it.get("share_file_token")
                    or ""
                ).strip()

                fid_token = str(
                    it.get("fid_token")
                    or it.get("share_fid_token")
                    or it.get("file_token")
                    or it.get("share_file_token")
                    or ""
                ).strip()

                is_dir = False

                if it.get("dir") is True or it.get("is_dir") is True:
                    is_dir = True

                if str(it.get("file_type", "")).lower() in ["0", "folder", "dir"]:
                    if not _psgv2_is_video(name):
                        is_dir = True

                if str(it.get("obj_category", "")).lower() in ["folder", "dir"]:
                    is_dir = True

                if is_dir:
                    if depth < max_depth:
                        out.extend(
                            _psgv2_quark_list_files(
                                self,
                                pwd_id,
                                stoken,
                                pdir_fid=fid,
                                depth=depth + 1,
                                max_depth=max_depth,
                            )
                        )
                    continue

                if not _psgv2_is_video(name):
                    continue

                try:
                    size = int(it.get("size") or it.get("file_size") or 0)
                except Exception:
                    size = 0

                composite_file_id = fid

                if "_" not in composite_file_id:
                    token = share_fid_token or fid_token
                    if token:
                        composite_file_id = fid + "_" + token

                out.append({
                    "source": "quarkshare",
                    "name": name,
                    "file_name": name,
                    "fid": fid,
                    "file_id": fid,
                    "size": size,
                    "pwd_id": pwd_id,
                    "share_id": pwd_id,
                    "stoken": stoken,
                    "pdir_fid": str(pdir_fid or "0"),
                    "fid_token": fid_token,
                    "share_fid_token": share_fid_token,
                    "composite_file_id": composite_file_id,
                })

                print("[PanSou 夸克原画V2 file] name=%s composite_file_id=%s" % (
                    name,
                    composite_file_id,
                ))

            except Exception as e:
                print("[PanSou 夸克原画V2 list item] error:", e)

    except Exception as e:
        print("[PanSou 夸克原画V2 list] error:", e)

    return _psgv2_sort_files(out)


def _psgv2_build_quark_items(self, share_info):
    try:
        pwd_id = share_info.get("pwd_id") or share_info.get("share_id") or ""
        passcode = share_info.get("pass_code") or share_info.get("passcode") or ""

        if not pwd_id:
            return ""

        stoken = _psgv2_quark_get_stoken(self, pwd_id, passcode)
        if not stoken:
            return ""

        files = _psgv2_quark_list_files(
            self,
            pwd_id,
            stoken,
            pdir_fid="0",
            depth=0,
            max_depth=getattr(self, "psgo_max_depth", 3),
        )

        items = []

        for f in files:
            try:
                if not isinstance(f, dict):
                    continue

                f["pwd_id"] = pwd_id
                f["share_id"] = pwd_id
                f["passcode"] = passcode or ""
                f["pass_code"] = passcode or ""

                name = f.get("name") or f.get("file_name") or "夸克视频"
                size = _psgv2_format_size(f.get("size") or 0)
                show = _psgv2_clean_name(("%s %s" % (size, name)).strip(), 180)

                pid = "__PSGV2_QUARK_FILE__|" + _psgv2_b64e_json(f)
                items.append("%s$%s" % (show, pid))

            except Exception:
                pass

        return "#".join(items)

    except Exception as e:
        print("[PanSou 夸克原画V2] build items error:", e)
        return ""


def _psgv2_quark_composite_file_id(file_info):
    try:
        composite = str(file_info.get("composite_file_id") or "").strip()
        if composite:
            return composite

        fid = str(file_info.get("fid") or file_info.get("file_id") or "").strip()
        if not fid:
            return ""

        if "_" in fid:
            return fid

        token = str(
            file_info.get("share_fid_token")
            or file_info.get("fid_token")
            or file_info.get("file_token")
            or file_info.get("share_file_token")
            or ""
        ).strip()

        if token:
            return fid + "_" + token

        return fid

    except Exception:
        return ""


def _psgv2_build_quark_url(self, file_info):
    try:
        if not isinstance(file_info, dict):
            return "", {}

        file_id = _psgv2_quark_composite_file_id(file_info)

        share_id = str(
            file_info.get("share_id")
            or file_info.get("pwd_id")
            or ""
        ).strip()

        pass_code = str(
            file_info.get("pass_code")
            or file_info.get("passcode")
            or file_info.get("password")
            or file_info.get("pwd")
            or ""
        ).strip()

        file_name = str(
            file_info.get("file_name")
            or file_info.get("name")
            or "video.mp4"
        ).strip()

        if not file_id or not share_id:
            print("[PanSou 夸克原画V2] missing file_id/share_id:", file_info)
            return "", {}

        ok_host, ok_port, go_host, go_port = _psgv2_hosts(self)

        inner_params = [
            ("do", "quark"),
            ("type", "dwnz"),
            ("file_id", file_id),
            ("share_id", share_id),
            ("pass_code", pass_code),
            ("file_name", file_name),
        ]

        inner_url = "http://%s:%s/proxy?%s" % (
            go_host,
            go_port,
            _psgv2_urlencode(inner_params),
        )

        inner_b64 = _psgv2_base64.b64encode(
            inner_url.encode("utf-8")
        ).decode("utf-8").rstrip("=")

        final_url = (
            "http://%s:%s/p/32/null/262144/%s/%s"
            % (
                ok_host,
                ok_port,
                inner_b64,
                _psgv2_quote(file_name, safe=""),
            )
        )

        print("[PanSou 夸克原画V2] build ok")
        print("[PanSou 夸克原画V2] inner=%s" % inner_url)
        print("[PanSou 夸克原画V2] final=%s" % final_url)

        return final_url, {}

    except Exception as e:
        print("[PanSou 夸克原画V2] build url error:", e)
        return "", {}


# ============================================================
# detailContent 接管三级目录 panplay
# ============================================================

def _psgv2_build_panplay_detail(self, data):
    try:
        if not isinstance(data, dict):
            data = {}

        api_type = data.get("api_type") or data.get("group") or ""
        url = data.get("url") or ""
        password = data.get("password") or ""

        title = data.get("name") or "网盘资源"
        pic = data.get("pic") or getattr(self, "last_vod_pic", "") or ""

        if pic:
            self.last_vod_pic = pic

        # 115
        if _psgv2_is_115_type(api_type) or _psgv2_is_115_url(url):
            share_info = _psgv2_parse_115_url(url, password)

            if not share_info:
                return {
                    "list": [{
                        "vod_id": "psgv2_115_bad",
                        "vod_name": title,
                        "vod_pic": pic,
                        "vod_remarks": "115链接解析失败",
                        "vod_content": "无法解析115分享链接。\n资源链接：%s" % url,
                        "vod_play_from": "0",
                        "vod_play_url": "等待视频$__ACK__",
                    }]
                }

            play_items = _psgv2_build_115_items(self, share_info)
            if not play_items:
                play_items = "暂无可播放115分享视频或缺少提取码$__ACK__"

            content = [
                "资源名称：%s" % title,
                "网盘类型：115",
                "资源链接：%s" % url,
                "分享码：%s" % (share_info.get("share_code") or ""),
            ]

            if share_info.get("receive_code"):
                content.append("提取码：%s" % share_info.get("receive_code"))

            return {
                "list": [{
                    "vod_id": "psgv2_115_panplay",
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": "115分享原画",
                    "vod_content": "\n".join(content),
                    "vod_play_from": "115分享原画",
                    "vod_play_url": play_items,
                }]
            }

        # 夸克
        if _psgv2_is_quark_type(api_type) or _psgv2_is_quark_url(url):
            share_info = _psgv2_parse_quark_url(url, password)

            if not share_info:
                return {
                    "list": [{
                        "vod_id": "psgv2_quark_bad",
                        "vod_name": title,
                        "vod_pic": pic,
                        "vod_remarks": "夸克链接解析失败",
                        "vod_content": "无法解析夸克分享链接。\n资源链接：%s" % url,
                        "vod_play_from": "0",
                        "vod_play_url": "等待视频$__ACK__",
                    }]
                }

            play_items = _psgv2_build_quark_items(self, share_info)
            if not play_items:
                play_items = "暂无可播放夸克分享视频或分享解析失败$__ACK__"

            content = [
                "资源名称：%s" % title,
                "网盘类型：夸克",
                "资源链接：%s" % url,
                "分享ID：%s" % (share_info.get("pwd_id") or ""),
            ]

            if share_info.get("passcode"):
                content.append("提取码：%s" % share_info.get("passcode"))

            return {
                "list": [{
                    "vod_id": "psgv2_quark_panplay",
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": "夸克分享原画",
                    "vod_content": "\n".join(content),
                    "vod_play_from": "夸克分享原画",
                    "vod_play_url": play_items,
                }]
            }

        if _PSGV2_PREV_BUILD_PANPLAY_DETAIL:
            return _PSGV2_PREV_BUILD_PANPLAY_DETAIL(self, data)

        return {"list": []}

    except Exception as e:
        print("[PanSou 原画V2] build panplay detail error:", e)
        try:
            if _PSGV2_PREV_BUILD_PANPLAY_DETAIL:
                return _PSGV2_PREV_BUILD_PANPLAY_DETAIL(self, data)
        except Exception:
            pass
        return {"list": []}


# ============================================================
# playerContent
# ============================================================

def _psgv2_playerContent(self, flag, pid, vipFlags):
    try:
        flag_s = str(flag or "").strip()
        pid_s = str(pid or "").strip()

        # 115分享原画
        if flag_s == "115分享原画" or pid_s.startswith("__PSGV2_115_FILE__|"):
            if not pid_s.startswith("__PSGV2_115_FILE__|"):
                print("[PanSou 115原画V2] invalid pid:", pid_s)
                return _psgv2_ack(self)

            b64 = pid_s.split("|", 1)[1].strip()
            file_info = _psgv2_b64d_json(b64)

            final_url, header_obj = _psgv2_build_115_url(self, file_info)
            if not final_url:
                return _psgv2_ack(self)

            pic = getattr(self, "last_vod_pic", "") or ""

            ret = {
                "parse": 0,
                "playUrl": "",
                "url": final_url,
                "header": header_obj,
            }

            if pic:
                ret["pic"] = pic
                ret["poster"] = pic

            return ret

        # 夸克分享原画
        if flag_s == "夸克分享原画" or pid_s.startswith("__PSGV2_QUARK_FILE__|"):
            if not pid_s.startswith("__PSGV2_QUARK_FILE__|"):
                print("[PanSou 夸克原画V2] invalid pid:", pid_s)
                return _psgv2_ack(self)

            b64 = pid_s.split("|", 1)[1].strip()
            file_info = _psgv2_b64d_json(b64)

            final_url, header_obj = _psgv2_build_quark_url(self, file_info)
            if not final_url:
                return _psgv2_ack(self)

            pic = getattr(self, "last_vod_pic", "") or ""

            ret = {
                "parse": 0,
                "playUrl": "",
                "url": final_url,
                "header": header_obj,
            }

            if pic:
                ret["pic"] = pic
                ret["poster"] = pic

            return ret

        if _PSGV2_PREV_PLAYER:
            return _PSGV2_PREV_PLAYER(self, flag, pid, vipFlags)

        return {
            "parse": 1,
            "playUrl": "",
            "url": pid_s,
            "header": getattr(self, "HEADERS", {}),
        }

    except Exception as e:
        print("[PanSou 原画V2] playerContent error:", e)
        try:
            if _PSGV2_PREV_PLAYER:
                return _PSGV2_PREV_PLAYER(self, flag, pid, vipFlags)
        except Exception:
            pass
        return _psgv2_ack(self)


# ============================================================
# 绑定
# ============================================================

try:
    if _PSGV2_TARGET is not None:
        _PSGV2_TARGET.init = _psgv2_init
        _PSGV2_TARGET.playerContent = _psgv2_playerContent

        # 关键：
        # 原代码里的 _psq_detailContent 一般运行时查找全局 _psq_build_panplay_detail。
        globals()["_psq_build_panplay_detail"] = _psgv2_build_panplay_detail

        # 调试方法挂类
        _PSGV2_TARGET._psgv2_build_115_url = _psgv2_build_115_url
        _PSGV2_TARGET._psgv2_build_quark_url = _psgv2_build_quark_url
        _PSGV2_TARGET._psgv2_115_list_videos = _psgv2_115_list_videos
        _PSGV2_TARGET._psgv2_quark_list_files = _psgv2_quark_list_files

        Spider = _PSGV2_TARGET

        print("[PANSOU 115/QUARK SHARE ORIGINAL FULL V2] loaded")
        print("[PANSOU FULL V2] outer OK 与 inner GO 分离")
        print("[PANSOU FULL V2] 115分享原画已启用")
        print("[PANSOU FULL V2] 夸克分享原画已启用：file_id=fid_share_fid_token&pass_code")
        print("[PANSOU FULL V2] 文件列表按文件名自然排序")

except Exception as e:
    print("[PANSOU 115/QUARK SHARE ORIGINAL FULL V2] load error:", e)

# ===== PANSOU_115_QUARK_SHARE_ORIGINAL_FULL_V2_END =====

# ===== PANSOU_TMDB_POSTER_AUTO_SEARCH_PATCH_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou + TMDB 海报入口 V2
#
# 功能：
#   1. 不使用 HDHive；
#   2. 首页 / 分类显示 TMDB 海报；
#   3. TMDB 海报走内置 localProxy 图片代理；
#   4. 点击首页 TMDB 海报或分类 TMDB 海报后，自动用标题调用 PanSou 搜索；
#   5. 搜索后的二级、三级、盘检、播放、115、夸克、磁力等逻辑全部沿用原 PanSou 逻辑；
#   6. 三级资源列表不补海报，保持纯列表形式。
#
# ext 示例：
# {
#   "server": "https://so.252035.xyz",
#   "src": "all",
#
#   "tmdb_api_key": "你的TMDB_API_KEY",
#   "tmdb_language": "zh-CN",
#   "tmdb_region": "CN",
#
#   "tmdb_api_base": "https://api.themoviedb.org/3",
#   "tmdb_image_base": "https://image.tmdb.org/t/p/w500",
#   "tmdb_backdrop_base": "https://image.tmdb.org/t/p/w780",
#
#   "tmdb_proxy": "",
#   "tmdb_image_proxy": true,
#   "tmdb_click_year_keyword": false
# }
# ============================================================

import json as _pstmdb_json
import time as _pstmdb_time
import base64 as _pstmdb_base64
import requests as _pstmdb_requests
from urllib.parse import urlencode as _pstmdb_urlencode
from urllib.parse import quote as _pstmdb_quote
from urllib.parse import unquote as _pstmdb_unquote
from urllib.parse import urlparse as _pstmdb_urlparse
from urllib.parse import parse_qs as _pstmdb_parse_qs

try:
    import urllib3 as _pstmdb_urllib3
    _pstmdb_urllib3.disable_warnings()
except Exception:
    pass

try:
    _PSTMDB_TARGET = PanSouSpider
except Exception:
    _PSTMDB_TARGET = globals().get("Spider")

if _PSTMDB_TARGET is None:
    print("[PANSOU TMDB V2] no target class, skip")
else:
    try:
        _PSTMDB_PREV_INIT = _PSTMDB_TARGET.init
    except Exception:
        _PSTMDB_PREV_INIT = None

    try:
        _PSTMDB_PREV_HOME = _PSTMDB_TARGET.homeContent
    except Exception:
        _PSTMDB_PREV_HOME = None

    try:
        _PSTMDB_PREV_HOME_VIDEO = _PSTMDB_TARGET.homeVideoContent
    except Exception:
        _PSTMDB_PREV_HOME_VIDEO = None

    try:
        _PSTMDB_PREV_CATEGORY = _PSTMDB_TARGET.categoryContent
    except Exception:
        _PSTMDB_PREV_CATEGORY = None

    try:
        _PSTMDB_PREV_DETAIL = _PSTMDB_TARGET.detailContent
    except Exception:
        _PSTMDB_PREV_DETAIL = None

    try:
        _PSTMDB_PREV_LOCAL_PROXY = _PSTMDB_TARGET.localProxy
    except Exception:
        _PSTMDB_PREV_LOCAL_PROXY = None

    try:
        _PSTMDB_PREV_THIRD_BUILDER = globals().get("_psq_build_third_category")
    except Exception:
        _PSTMDB_PREV_THIRD_BUILDER = None

    # ============================================================
    # 基础工具
    # ============================================================

    def _pstmdb_parse_ext(extend):
        try:
            if not extend:
                return {}
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _pstmdb_json.loads(extend)
            return {}
        except Exception:
            return {}

    def _pstmdb_bool(v, default=False):
        try:
            if isinstance(v, bool):
                return v
            if isinstance(v, int):
                return v != 0
            if isinstance(v, str):
                s = v.strip().lower()
                if s in ["1", "true", "yes", "y", "on"]:
                    return True
                if s in ["0", "false", "no", "n", "off", ""]:
                    return False
            return bool(v)
        except Exception:
            return default

    def _pstmdb_b64e(obj):
        try:
            txt = _pstmdb_json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            return _pstmdb_base64.urlsafe_b64encode(
                txt.encode("utf-8")
            ).decode("utf-8").rstrip("=")
        except Exception:
            return ""

    def _pstmdb_b64d(text):
        try:
            text = str(text or "")
            text += "=" * (-len(text) % 4)
            raw = _pstmdb_base64.urlsafe_b64decode(
                text.encode("utf-8")
            ).decode("utf-8")
            return _pstmdb_json.loads(raw)
        except Exception:
            return {}

    def _pstmdb_make_id(vtype, data):
        return "pstmdb|%s|%s" % (str(vtype), _pstmdb_b64e(data or {}))

    def _pstmdb_parse_id(vod_id):
        try:
            vod_id = str(vod_id or "")
            if not vod_id.startswith("pstmdb|"):
                return "", {}
            arr = vod_id.split("|", 2)
            if len(arr) < 3:
                return "", {}
            return arr[1], _pstmdb_b64d(arr[2])
        except Exception:
            return "", {}

    def _pstmdb_clean_text(text, limit=120):
        try:
            text = str(text or "").replace("\r", " ").replace("\n", " ")
            text = " ".join(text.split()).strip()
            if len(text) > limit:
                text = text[:limit] + "..."
            return text
        except Exception:
            return ""

    def _pstmdb_year(date_text):
        try:
            s = str(date_text or "")
            if len(s) >= 4 and s[:4].isdigit():
                return s[:4]
            return ""
        except Exception:
            return ""

    def _pstmdb_get_param(param, key):
        try:
            if not isinstance(param, dict):
                return ""
            v = param.get(key, "")
            if isinstance(v, list):
                return v[0] if v else ""
            return v
        except Exception:
            return ""

    # ============================================================
    # init
    # ============================================================

    def _pstmdb_init(self, extend=""):
        ret = None
        if _PSTMDB_PREV_INIT:
            try:
                ret = _PSTMDB_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU TMDB V2] prev init error:", e)

        ext = _pstmdb_parse_ext(extend)

        self.tmdb_api_key = str(
            ext.get(
                "tmdb_api_key",
                ext.get("tmdb_key", getattr(self, "tmdb_api_key", ""))
            ) or ""
        ).strip()

        self.tmdb_api_base = str(
            ext.get(
                "tmdb_api_base",
                getattr(self, "tmdb_api_base", "https://api.themoviedb.org/3")
            ) or "https://api.themoviedb.org/3"
        ).strip().rstrip("/")

        self.tmdb_image_base = str(
            ext.get(
                "tmdb_image_base",
                getattr(self, "tmdb_image_base", "https://image.tmdb.org/t/p/w500")
            ) or "https://image.tmdb.org/t/p/w500"
        ).strip().rstrip("/")

        self.tmdb_backdrop_base = str(
            ext.get(
                "tmdb_backdrop_base",
                getattr(self, "tmdb_backdrop_base", "https://image.tmdb.org/t/p/w780")
            ) or "https://image.tmdb.org/t/p/w780"
        ).strip().rstrip("/")

        self.tmdb_language = str(
            ext.get(
                "tmdb_language",
                getattr(self, "tmdb_language", "zh-CN")
            ) or "zh-CN"
        ).strip()

        self.tmdb_region = str(
            ext.get(
                "tmdb_region",
                getattr(self, "tmdb_region", "CN")
            ) or "CN"
        ).strip()

        self.tmdb_proxy = str(
            ext.get(
                "tmdb_proxy",
                ext.get("site_proxy", ext.get("proxy_url", getattr(self, "tmdb_proxy", "")))
            ) or ""
        ).strip()

        try:
            self.tmdb_timeout = int(
                ext.get("tmdb_timeout", getattr(self, "tmdb_timeout", 15))
            )
        except Exception:
            self.tmdb_timeout = 15

        self.tmdb_include_adult = _pstmdb_bool(
            ext.get(
                "tmdb_include_adult",
                getattr(self, "tmdb_include_adult", False)
            ),
            False
        )

        self.tmdb_click_year_keyword = _pstmdb_bool(
            ext.get(
                "tmdb_click_year_keyword",
                getattr(self, "tmdb_click_year_keyword", False)
            ),
            False
        )

        # 关键：TMDB 图片是否走内置 localProxy
        self.tmdb_image_proxy = _pstmdb_bool(
            ext.get(
                "tmdb_image_proxy",
                getattr(self, "tmdb_image_proxy", True)
            ),
            True
        )

        if not hasattr(self, "_pstmdb_kw_pic"):
            self._pstmdb_kw_pic = {}

        if not hasattr(self, "_pstmdb_cache"):
            self._pstmdb_cache = {}

        print("[PANSOU TMDB V2] enabled")
        print("[PANSOU TMDB V2] tmdb_api_key =", "已配置" if self.tmdb_api_key else "未配置")
        print("[PANSOU TMDB V2] tmdb_proxy =", self.tmdb_proxy or "未配置")
        print("[PANSOU TMDB V2] tmdb_image_proxy =", self.tmdb_image_proxy)
        print("[PANSOU TMDB V2] click_year_keyword =", self.tmdb_click_year_keyword)

        return ret if ret is not None else {}

    # ============================================================
    # TMDB 请求 / 图片代理
    # ============================================================

    def _pstmdb_headers(self, image=False):
        try:
            ua = getattr(self, "HEADERS", {}).get("User-Agent", "Mozilla/5.0")
        except Exception:
            ua = "Mozilla/5.0"

        if image:
            accept = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        else:
            accept = "application/json,text/plain,*/*"

        return {
            "User-Agent": ua,
            "Accept": accept,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.themoviedb.org/"
        }

    def _pstmdb_proxies(self):
        try:
            p = str(getattr(self, "tmdb_proxy", "") or "").strip()
            if not p:
                return None
            return {
                "http": p,
                "https": p
            }
        except Exception:
            return None

    def _pstmdb_fetch(self, path, params=None):
        try:
            if not getattr(self, "tmdb_api_key", ""):
                return {}

            if params is None:
                params = {}

            params = dict(params)
            params["api_key"] = getattr(self, "tmdb_api_key", "")

            if "language" not in params:
                params["language"] = getattr(self, "tmdb_language", "zh-CN")

            if str(path).startswith(("http://", "https://")):
                url = str(path)
            else:
                if not str(path).startswith("/"):
                    path = "/" + str(path)
                url = getattr(self, "tmdb_api_base", "https://api.themoviedb.org/3").rstrip("/") + str(path)

            cache_key = "GET|" + url + "?" + _pstmdb_urlencode(sorted(params.items()))
            cache = getattr(self, "_pstmdb_cache", {})
            old = cache.get(cache_key)
            now = _pstmdb_time.time()

            if old and now - old[0] < 600:
                return old[1]

            r = _pstmdb_requests.get(
                url,
                params=params,
                headers=_pstmdb_headers(self, image=False),
                timeout=getattr(self, "tmdb_timeout", 15),
                proxies=_pstmdb_proxies(self),
                verify=False
            )

            if r.status_code != 200:
                print("[PANSOU TMDB V2] TMDB HTTP", r.status_code, url, r.text[:160])
                return {}

            data = r.json()
            cache[cache_key] = (now, data)
            self._pstmdb_cache = cache
            return data

        except Exception as e:
            print("[PANSOU TMDB V2] fetch error:", e)
            return {}

    def _pstmdb_raw_img(self, path, backdrop=False):
        try:
            if not path:
                return ""
            path = str(path)
            if path.startswith(("http://", "https://")):
                return path
            base = getattr(
                self,
                "tmdb_backdrop_base" if backdrop else "tmdb_image_base",
                "https://image.tmdb.org/t/p/w500"
            )
            return str(base).rstrip("/") + path
        except Exception:
            return ""

    def _pstmdb_get_proxy_url(self):
        """
        获取壳内置 localProxy 地址。
        OK/PG/FongMi 常见 Spider 有 getProxyUrl()。
        没有时返回空，图片只能直连。
        """
        try:
            if hasattr(self, "getProxyUrl"):
                u = self.getProxyUrl()
                if u:
                    return str(u)
        except Exception:
            pass
        return ""

    def _pstmdb_to_img_proxy(self, raw_url):
        """
        把 TMDB 原始图片 URL 转为内置代理 URL。
        """
        try:
            raw_url = str(raw_url or "").strip()
            if not raw_url:
                return ""

            if not getattr(self, "tmdb_image_proxy", True):
                return raw_url

            proxy = _pstmdb_get_proxy_url(self)
            if not proxy:
                # 没有内置代理地址时，退回直链
                return raw_url

            sep = "&" if "?" in proxy else "?"
            return proxy + sep + "type=tmdb_img&url=" + _pstmdb_quote(raw_url, safe="")
        except Exception:
            return str(raw_url or "")

    def _pstmdb_img(self, path, backdrop=False):
        raw = _pstmdb_raw_img(self, path, backdrop)
        return _pstmdb_to_img_proxy(self, raw)

    def _pstmdb_guess_ctype(url, content=None, rsp=None):
        try:
            if rsp is not None:
                ctype = rsp.headers.get("Content-Type") or ""
                if ctype:
                    return ctype

            if content:
                if content[:3] == b"\xff\xd8\xff":
                    return "image/jpeg"
                if content[:8] == b"\x89PNG\r\n\x1a\n":
                    return "image/png"
                if content[:4] == b"RIFF" and b"WEBP" in content[:20]:
                    return "image/webp"
                if content[:6] in [b"GIF87a", b"GIF89a"]:
                    return "image/gif"

            low = str(url or "").lower()
            if ".png" in low:
                return "image/png"
            if ".webp" in low:
                return "image/webp"
            if ".gif" in low:
                return "image/gif"
            if ".avif" in low:
                return "image/avif"

            return "image/jpeg"
        except Exception:
            return "application/octet-stream"

    def _pstmdb_localProxy(self, param):
        """
        内置图片代理：
        客户端请求 localProxy?type=tmdb_img&url=...
        Python 内部再请求真实 TMDB 图片。
        """
        try:
            ptype = str(_pstmdb_get_param(param, "type") or "").strip()
            if ptype != "tmdb_img":
                if _PSTMDB_PREV_LOCAL_PROXY:
                    return _PSTMDB_PREV_LOCAL_PROXY(self, param)
                return [404, "text/plain", "Not Found"]

            raw_url = str(_pstmdb_get_param(param, "url") or "").strip()
            raw_url = _pstmdb_unquote(raw_url)

            if not raw_url:
                return [404, "text/plain", "No Url"]

            if not raw_url.startswith(("http://", "https://")):
                return [404, "text/plain", "Bad Url"]

            # 只允许代理 TMDB 图片，避免被滥用
            try:
                host = _pstmdb_urlparse(raw_url).netloc.lower()
                if "image.tmdb.org" not in host:
                    return [403, "text/plain", "Forbidden"]
            except Exception:
                return [403, "text/plain", "Forbidden"]

            rsp = _pstmdb_requests.get(
                raw_url,
                headers=_pstmdb_headers(self, image=True),
                timeout=30,
                allow_redirects=True,
                proxies=_pstmdb_proxies(self),
                verify=False
            )

            content = rsp.content or b""

            print("[PANSOU TMDB IMG PROXY] status=%s len=%s url=%s proxy=%s" % (
                rsp.status_code,
                len(content),
                raw_url,
                getattr(self, "tmdb_proxy", "") or "none"
            ))

            if rsp.status_code != 200 or not content:
                return [404, "text/plain", "Proxy Image Failed"]

            return [200, _pstmdb_guess_ctype(raw_url, content, rsp), content]

        except Exception as e:
            print("[PANSOU TMDB IMG PROXY] error:", e)
            return [404, "text/plain", "Proxy Error"]

    # ============================================================
    # TMDB 分类
    # ============================================================

    _PSTMDB_CLASSES = [
        {"type_id": "pstmdb_popular_movie", "type_name": "TMDB热门电影"},
        {"type_id": "pstmdb_popular_tv", "type_name": "TMDB热门剧集"},
        {"type_id": "pstmdb_trending", "type_name": "TMDB今日趋势"},
        {"type_id": "pstmdb_now_playing", "type_name": "TMDB正在上映"},
        {"type_id": "pstmdb_top_movie", "type_name": "TMDB高分电影"},
        {"type_id": "pstmdb_top_tv", "type_name": "TMDB高分剧集"},
        {"type_id": "pstmdb_anime_movie", "type_name": "TMDB动漫电影"},
        {"type_id": "pstmdb_anime_tv", "type_name": "TMDB动漫剧集"},
        {"type_id": "pstmdb_documentary", "type_name": "TMDB纪录片"}
    ]

    def _pstmdb_endpoint(tid):
        tid = str(tid or "")

        if tid == "pstmdb_popular_movie":
            return "/movie/popular", "movie", {}

        if tid == "pstmdb_popular_tv":
            return "/tv/popular", "tv", {}

        if tid == "pstmdb_trending":
            return "/trending/all/day", "multi", {}

        if tid == "pstmdb_now_playing":
            return "/movie/now_playing", "movie", {}

        if tid == "pstmdb_top_movie":
            return "/movie/top_rated", "movie", {}

        if tid == "pstmdb_top_tv":
            return "/tv/top_rated", "tv", {}

        if tid == "pstmdb_anime_movie":
            return "/discover/movie", "movie", {
                "with_genres": "16",
                "sort_by": "popularity.desc"
            }

        if tid == "pstmdb_anime_tv":
            return "/discover/tv", "tv", {
                "with_genres": "16",
                "sort_by": "popularity.desc"
            }

        if tid == "pstmdb_documentary":
            return "/discover/movie", "movie", {
                "with_genres": "99",
                "sort_by": "popularity.desc"
            }

        return "/movie/popular", "movie", {}

    def _pstmdb_format_item(self, item, media_type="movie"):
        try:
            if not isinstance(item, dict):
                return None

            mt = item.get("media_type") or media_type

            if mt == "multi":
                mt = item.get("media_type") or "movie"

            if mt not in ["movie", "tv"]:
                return None

            if mt == "movie":
                title = item.get("title") or item.get("name") or item.get("original_title") or ""
                date = item.get("release_date") or ""
            else:
                title = item.get("name") or item.get("title") or item.get("original_name") or ""
                date = item.get("first_air_date") or ""

            if not title:
                return None

            tmdb_id = str(item.get("id") or "")
            year = _pstmdb_year(date)

            # 海报走内置代理
            poster = _pstmdb_img(self, item.get("poster_path") or "", False)
            backdrop = _pstmdb_img(self, item.get("backdrop_path") or "", True)
            pic = poster or backdrop

            vote = item.get("vote_average", "")
            remarks = []

            if year:
                remarks.append(year)

            try:
                if vote not in ["", None]:
                    remarks.append("TMDB %.1f" % float(vote))
            except Exception:
                pass

            data = {
                "title": title,
                "kw": title,
                "pic": pic,
                "media_type": mt,
                "tmdb_id": tmdb_id,
                "year": year,
                "overview": item.get("overview") or ""
            }

            vod_id = _pstmdb_make_id("search", data)

            return {
                "vod_id": vod_id,
                "vod_name": _pstmdb_clean_text(title, 80),
                "vod_pic": pic,
                "vod_remarks": " · ".join(remarks) if remarks else "TMDB",
                "vod_content": item.get("overview") or ("点击后自动盘搜：" + title),
                "vod_tag": "folder"
            }

        except Exception as e:
            print("[PANSOU TMDB V2] format item error:", e)
            return None

    def _pstmdb_category(self, tid, pg=1):
        try:
            page = int(pg)
        except Exception:
            page = 1

        if page < 1:
            page = 1

        if not getattr(self, "tmdb_api_key", ""):
            return {
                "list": [{
                    "vod_id": "tmdb_no_key",
                    "vod_name": "请配置 tmdb_api_key",
                    "vod_pic": "",
                    "vod_remarks": "TMDB",
                    "vod_content": "ext 中加入 tmdb_api_key 后可显示 TMDB 海报分类。"
                }],
                "page": 1,
                "pagecount": 1,
                "limit": 1,
                "total": 1
            }

        path, media_type, extra = _pstmdb_endpoint(tid)

        params = {
            "page": page,
            "language": getattr(self, "tmdb_language", "zh-CN"),
            "region": getattr(self, "tmdb_region", "CN"),
            "include_adult": "true" if getattr(self, "tmdb_include_adult", False) else "false"
        }

        params.update(extra or {})

        data = _pstmdb_fetch(self, path, params)

        results = data.get("results", []) if isinstance(data, dict) else []
        total_pages = data.get("total_pages", 1) if isinstance(data, dict) else 1
        total_results = data.get("total_results", len(results)) if isinstance(data, dict) else len(results)

        videos = []

        for item in results:
            v = _pstmdb_format_item(self, item, media_type)
            if v:
                videos.append(v)

        return {
            "list": videos,
            "page": page,
            "pagecount": int(total_pages or 1),
            "limit": 20,
            "total": int(total_results or len(videos))
        }

    # ============================================================
    # TMDB 海报点击后：进入 PanSou 搜索二级分类
    # ============================================================

    def _pstmdb_keyword_from_data(self, data):
        title = str(data.get("kw") or data.get("title") or "").strip()
        year = str(data.get("year") or "").strip()

        if getattr(self, "tmdb_click_year_keyword", False) and year:
            if year not in title:
                return ("%s %s" % (title, year)).strip()

        return title

    def _pstmdb_build_pansou_second(self, data, pg=1):
        """
        TMDB 海报 -> PanSou 搜索 -> 原有二级分类。
        """
        try:
            keyword = _pstmdb_keyword_from_data(self, data)
            pic = str(data.get("pic") or "").strip()
            title = str(data.get("title") or keyword).strip()

            if not keyword:
                return {
                    "list": [],
                    "page": 1,
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            if pic:
                if not hasattr(self, "_pstmdb_kw_pic"):
                    self._pstmdb_kw_pic = {}
                self._pstmdb_kw_pic[keyword] = pic
                if title:
                    self._pstmdb_kw_pic[title] = pic
                self.last_vod_pic = pic

            # 关键：直接复用七味式 PanSou 搜索、分组逻辑。
            if "_psq_fetch_search_items" in globals() and "_psq_group_items" in globals() and "_psq_make_id" in globals():
                items = _psq_fetch_search_items(self, keyword)
                groups = _psq_group_items(items)

                videos = []

                group_order = globals().get("_PSQ_GROUP_ORDER", [])
                group_name = globals().get("_PSQ_GROUP_NAME", {})

                for gkey in group_order:
                    arr = groups.get(gkey) or []
                    if not arr:
                        continue

                    # 二级分类可以显示 TMDB 海报作为文件夹封面
                    cover = pic

                    vod_id = _psq_make_id("group", {
                        "kw": keyword,
                        "group": gkey
                    })

                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": group_name.get(gkey, gkey),
                        "vod_pic": cover,
                        "vod_remarks": "%s条资源" % len(arr),
                        "vod_content": "TMDB：%s\n盘搜词：%s\n资源类型：%s\n点击进入具体资源列表。" % (
                            title or keyword,
                            keyword,
                            group_name.get(gkey, gkey)
                        ),
                        "vod_tag": "folder"
                    })

                for gkey, arr in groups.items():
                    if gkey in group_order:
                        continue

                    if not arr:
                        continue

                    vod_id = _psq_make_id("group", {
                        "kw": keyword,
                        "group": gkey
                    })

                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": "📦 %s" % gkey,
                        "vod_pic": pic,
                        "vod_remarks": "%s条资源" % len(arr),
                        "vod_content": "TMDB：%s\n盘搜词：%s\n资源类型：%s" % (
                            title or keyword,
                            keyword,
                            gkey
                        ),
                        "vod_tag": "folder"
                    })

                if not videos:
                    videos.append({
                        "vod_id": "pstmdb_empty",
                        "vod_name": "盘搜无结果：" + keyword,
                        "vod_pic": pic,
                        "vod_remarks": "空",
                        "vod_content": "TMDB 标题已搜索，但 PanSou 暂无结果。"
                    })

                return {
                    "list": videos,
                    "page": 1,
                    "pagecount": 1,
                    "limit": len(videos),
                    "total": len(videos)
                }

            # 兜底：调用原搜索。
            try:
                return self.searchContent(keyword, False, "1")
            except Exception:
                return {
                    "list": [],
                    "page": 1,
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

        except Exception as e:
            print("[PANSOU TMDB V2] build pansou second error:", e)
            return {
                "list": [],
                "page": 1,
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    # ============================================================
    # home / category / detail
    # ============================================================

    def _pstmdb_homeContent(self, filter):
        try:
            old = {}
            if _PSTMDB_PREV_HOME:
                old = _PSTMDB_PREV_HOME(self, filter) or {}

            classes = old.get("class", []) if isinstance(old, dict) else []
            filters = old.get("filters", {}) if isinstance(old, dict) else {}

            old_ids = set([
                str(x.get("type_id"))
                for x in classes
                if isinstance(x, dict)
            ])

            new_classes = []

            for c in _PSTMDB_CLASSES:
                if c["type_id"] not in old_ids:
                    new_classes.append(c)

            return {
                "class": new_classes + classes,
                "filters": filters
            }

        except Exception as e:
            print("[PANSOU TMDB V2] homeContent error:", e)
            if _PSTMDB_PREV_HOME:
                return _PSTMDB_PREV_HOME(self, filter)
            return {
                "class": _PSTMDB_CLASSES,
                "filters": {}
            }

    def _pstmdb_homeVideoContent(self):
        """
        首页推荐：
        显示 TMDB 热门电影。
        首页内容 vod_id 也是 pstmdb|search|xxx，
        所以点击后同样进入 PanSou 搜索二级分类。
        """
        try:
            if getattr(self, "tmdb_api_key", ""):
                ret = _pstmdb_category(self, "pstmdb_popular_movie", 1)
                if ret.get("list"):
                    return {
                        "list": ret.get("list", [])
                    }

            if _PSTMDB_PREV_HOME_VIDEO:
                return _PSTMDB_PREV_HOME_VIDEO(self)

            return {
                "list": []
            }

        except Exception as e:
            print("[PANSOU TMDB V2] homeVideoContent error:", e)
            if _PSTMDB_PREV_HOME_VIDEO:
                return _PSTMDB_PREV_HOME_VIDEO(self)
            return {
                "list": []
            }

    def _pstmdb_categoryContent(self, tid, pg, filter, extend):
        try:
            tid_s = str(tid or "")

            # TMDB 分类
            if tid_s.startswith("pstmdb_") and not tid_s.startswith("pstmdb|"):
                return _pstmdb_category(self, tid_s, pg)

            # TMDB 海报点击后进入 PanSou 二级分类
            if tid_s.startswith("pstmdb|"):
                vtype, data = _pstmdb_parse_id(tid_s)
                if vtype == "search":
                    return _pstmdb_build_pansou_second(self, data, pg)

            if _PSTMDB_PREV_CATEGORY:
                return _PSTMDB_PREV_CATEGORY(self, tid, pg, filter, extend)

        except Exception as e:
            print("[PANSOU TMDB V2] categoryContent error:", e)

        return {
            "list": [],
            "page": 1,
            "pagecount": 1,
            "limit": 0,
            "total": 0
        }

    def _pstmdb_detailContent(self, ids):
        """
        兼容不识别 folder 的壳：
        如果壳把首页/分类 TMDB 海报当详情打开，
        这里也直接返回 PanSou 搜索二级分类列表。
        """
        try:
            vod_id = ids[0] if isinstance(ids, list) and ids else ids
            vod_id_s = str(vod_id or "")

            if vod_id_s.startswith("pstmdb|"):
                vtype, data = _pstmdb_parse_id(vod_id_s)
                if vtype == "search":
                    return _pstmdb_build_pansou_second(self, data, 1)

            if _PSTMDB_PREV_DETAIL:
                return _PSTMDB_PREV_DETAIL(self, ids)

        except Exception as e:
            print("[PANSOU TMDB V2] detailContent error:", e)

        return {
            "list": []
        }

    # ============================================================
    # 三级分类：保持列表形式，不补海报
    # ============================================================

    def _pstmdb_third_category_wrapper(self, data, pg=1):
        """
        包装原 _psq_build_third_category：
        1. 原盘检逻辑照旧执行；
        2. 原排序逻辑照旧执行；
        3. 原 vod_id / 播放 payload 照旧；
        4. 只把三级列表 vod_pic 清空，保持列表形式。
        """
        try:
            if _PSTMDB_PREV_THIRD_BUILDER:
                ret = _PSTMDB_PREV_THIRD_BUILDER(self, data, pg)
            else:
                ret = {
                    "list": []
                }

            if not isinstance(ret, dict):
                return ret

            lst = ret.get("list", [])

            if not isinstance(lst, list):
                return ret

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue
                    # 三级分类不需要海报
                    v["vod_pic"] = ""
                except Exception:
                    pass

            return ret

        except Exception as e:
            print("[PANSOU TMDB V2] third wrapper error:", e)
            if _PSTMDB_PREV_THIRD_BUILDER:
                return _PSTMDB_PREV_THIRD_BUILDER(self, data, pg)
            return {
                "list": []
            }

    # ============================================================
    # 绑定
    # ============================================================

    try:
        _PSTMDB_TARGET.init = _pstmdb_init
        _PSTMDB_TARGET.homeContent = _pstmdb_homeContent
        _PSTMDB_TARGET.homeVideoContent = _pstmdb_homeVideoContent
        _PSTMDB_TARGET.categoryContent = _pstmdb_categoryContent
        _PSTMDB_TARGET.detailContent = _pstmdb_detailContent
        _PSTMDB_TARGET.localProxy = _pstmdb_localProxy

        # 原 _psq_categoryContent 运行时会查找全局 _psq_build_third_category。
        # 这里包一层，保留原盘检和三级逻辑，只清空三级海报。
        globals()["_psq_build_third_category"] = _pstmdb_third_category_wrapper

        Spider = _PSTMDB_TARGET

        print("[PANSOU TMDB POSTER AUTO SEARCH PATCH V2] loaded")
        print("[PANSOU TMDB V2] TMDB海报走localProxy，点击海报走PanSou全部逻辑，三级不显示海报")

    except Exception as e:
        print("[PANSOU TMDB V2] bind error:", e)

# ===== PANSOU_TMDB_POSTER_AUTO_SEARCH_PATCH_END =====

# ===== PANSOU_TMDB_V3_THIRD_PIC_HOME_FIX_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou + TMDB V3 修复
#
# 修复：
#   1. 三级分类不再清空 vod_pic；
#   2. 三级分类无图时补对应网盘小图标；
#   3. 三级保持原盘检、排序、密码、播放逻辑；
#   4. 首页 TMDB 点击做兼容，但如果壳固定首页走详情页，
#      无法在 Spider 层强制切换为 categoryContent 页面。
# ============================================================

try:
    _PSTV3_TARGET = PanSouSpider
except Exception:
    _PSTV3_TARGET = globals().get("Spider")

if _PSTV3_TARGET is None:
    print("[PANSOU TMDB V3] no target class, skip")
else:
    try:
        _PSTV3_PREV_DETAIL = _PSTV3_TARGET.detailContent
    except Exception:
        _PSTV3_PREV_DETAIL = None

    try:
        # 优先拿 V2 保存的原三级构造器。
        # 这个通常是带盘检逻辑的 _psqcc_build_third_category / 后续覆盖版本。
        _PSTV3_BASE_THIRD = globals().get("_PSTMDB_PREV_THIRD_BUILDER")
    except Exception:
        _PSTV3_BASE_THIRD = None

    if _PSTV3_BASE_THIRD is None:
        try:
            _PSTV3_BASE_THIRD = globals().get("_psq_build_third_category")
        except Exception:
            _PSTV3_BASE_THIRD = None

    def _pstv3_group_key(api_type):
        try:
            if "_psq_group_key" in globals():
                return _psq_group_key(api_type)
        except Exception:
            pass

        api_type = str(api_type or "").strip().lower()

        if api_type in ["115", "a115"]:
            return "115"
        if api_type in ["ali", "aliyun", "alipan"]:
            return "aliyun"
        if api_type in ["123", "a123", "123pan"]:
            return "123"
        if api_type in ["tianyi", "189"]:
            return "tianyi"
        if api_type in ["mobile", "139"]:
            return "mobile"

        return api_type or "other"

    def _pstv3_group_to_pan_type(group):
        group = str(group or "").strip().lower()
        mapping = {
            "quark": "quark",
            "115": "a115",
            "a115": "a115",
            "aliyun": "ali",
            "ali": "ali",
            "baidu": "baidu",
            "uc": "uc",
            "tianyi": "tianyi",
            "189": "tianyi",
            "mobile": "mobile",
            "139": "mobile",
            "xunlei": "xunlei",
            "123": "a123",
            "a123": "a123",
            "pikpak": "pikpak",
            "magnet": "magnet",
            "ed2k": "ed2k"
        }
        return mapping.get(group, group)

    def _pstv3_group_icon(self, group):
        """
        给三级列表补小图标。
        注意：
        - 这里不是 TMDB 大海报；
        - 是网盘图标，目的是让壳按搜索结果那种小图列表显示。
        """
        try:
            group = _pstv3_group_key(group)
            pan_type = _pstv3_group_to_pan_type(group)

            icon_name = ""

            try:
                cfg = getattr(self, "PAN_CONFIG", {}).get(pan_type, {}) or {}
                icon_name = cfg.get("icon", "") or ""
            except Exception:
                icon_name = ""

            # 兜底
            if not icon_name:
                fallback = {
                    "quark": "quark.png",
                    "115": "115.png",
                    "aliyun": "ali.png",
                    "baidu": "baidu.png",
                    "uc": "uc.png",
                    "tianyi": "189.png",
                    "mobile": "139.png",
                    "xunlei": "xunlei.png",
                    "123": "123.png",
                    "pikpak": "pikpak.png",
                    "magnet": "cili.png",
                    "ed2k": ""
                }
                icon_name = fallback.get(group, "")

            if not icon_name:
                return ""

            try:
                if hasattr(self, "_get_icon_url"):
                    return self._get_icon_url(icon_name)
            except Exception:
                pass

            return "http://127.0.0.1:9978/file/Download/lib/icon/%s" % icon_name

        except Exception:
            return ""

    def _pstv3_fix_third_vod_pics(self, ret, data):
        """
        修复三级列表图片：
        1. 原有资源图保留；
        2. 没图则补网盘小图标；
        3. 不再清空 vod_pic。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            group = ""
            try:
                group = str((data or {}).get("group") or "").strip()
            except Exception:
                group = ""

            icon = _pstv3_group_icon(self, group)

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue

                    # 空结果不强制补图
                    vid = str(v.get("vod_id") or "")
                    name = str(v.get("vod_name") or "")
                    if vid == "empty" or "暂无" in name:
                        if not v.get("vod_pic"):
                            v["vod_pic"] = icon
                        continue

                    # 保留原图；无图才补小图标
                    if not v.get("vod_pic"):
                        v["vod_pic"] = icon

                    # 保持 file 标记
                    v["vod_tag"] = v.get("vod_tag") or "file"

                except Exception:
                    pass

            return ret

        except Exception as e:
            print("[PANSOU TMDB V3] fix third pic error:", e)
            return ret

    def _pstv3_build_third_category(self, data, pg=1):
        """
        重新覆盖三级构造：
        调用原始带盘检的三级构造器，然后只修图。
        """
        try:
            if _PSTV3_BASE_THIRD:
                ret = _PSTV3_BASE_THIRD(self, data, pg)
            else:
                ret = {"list": []}
            return _pstv3_fix_third_vod_pics(self, ret, data)
        except Exception as e:
            print("[PANSOU TMDB V3] build third error:", e)
            try:
                if _PSTV3_BASE_THIRD:
                    return _PSTV3_BASE_THIRD(self, data, pg)
            except Exception:
                pass
            return {"list": []}

    def _pstv3_parse_pstmdb_id(vod_id):
        try:
            if "_pstmdb_parse_id" in globals():
                return _pstmdb_parse_id(vod_id)
        except Exception:
            pass
        return "", {}

    def _pstv3_build_pansou_second(self, data, pg=1):
        try:
            if "_pstmdb_build_pansou_second" in globals():
                return _pstmdb_build_pansou_second(self, data, pg)
        except Exception as e:
            print("[PANSOU TMDB V3] call _pstmdb_build_pansou_second error:", e)
        return {
            "list": [],
            "page": 1,
            "pagecount": 1,
            "limit": 0,
            "total": 0
        }

    def _pstv3_detailContent(self, ids):
        """
        首页海报点击兼容。

        说明：
        - 有些壳首页 item 点击固定进入 detailContent；
        - detailContent 原生是详情页，不是分类页；
        - 所以这里尽量返回二级分类 list；
        - 如果壳仍只取 list[0] 当详情，这是壳行为限制。
        """
        try:
            vod_id = ids[0] if isinstance(ids, list) and ids else ids
            vod_id_s = str(vod_id or "")

            if vod_id_s.startswith("pstmdb|"):
                vtype, data = _pstv3_parse_pstmdb_id(vod_id_s)
                if vtype == "search":
                    return _pstv3_build_pansou_second(self, data, 1)

            if _PSTV3_PREV_DETAIL:
                return _PSTV3_PREV_DETAIL(self, ids)

        except Exception as e:
            print("[PANSOU TMDB V3] detailContent error:", e)

        return {"list": []}

    try:
        # 关键：覆盖全局三级构造函数。
        # 原 categoryContent 点击二级分类时会运行时查找这个名字。
        globals()["_psq_build_third_category"] = _pstv3_build_third_category

        _PSTV3_TARGET.detailContent = _pstv3_detailContent

        Spider = _PSTV3_TARGET

        print("[PANSOU TMDB V3 THIRD PIC HOME FIX] loaded")
        print("[PANSOU TMDB V3] 三级不再清图，无图补网盘小图标，盘检逻辑不变")

    except Exception as e:
        print("[PANSOU TMDB V3] bind error:", e)

# ===== PANSOU_TMDB_V3_THIRD_PIC_HOME_FIX_END =====

# ===== PANSOU_TMDB_V4_FORCE_THIRD_LIST_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou + TMDB V4
#
# 目的：
#   强制三级分类尽量按“小图列表”显示，而不是海报大图。
#
# 做法：
#   1. 保留原三级构造逻辑；
#   2. 保留原盘检逻辑；
#   3. 保留原排序逻辑；
#   4. 保留原播放逻辑；
#   5. 只在三级返回结果上追加 style={"type":"list"}；
#   6. 三级 item 强制 vod_tag=file；
#   7. 三级 item 无图时补网盘小图标。
#
# 注意：
#   是否真正显示小图列表，最终取决于壳是否支持 style.type=list。
# ============================================================

try:
    _PSTV4_TARGET = PanSouSpider
except Exception:
    _PSTV4_TARGET = globals().get("Spider")

if _PSTV4_TARGET is None:
    print("[PANSOU TMDB V4] no target class, skip")
else:

    def _pstv4_pick_base_third():
        """
        选择真正的三级构造函数。
        尽量避开 V2/V3/V4 自己的 wrapper，避免递归。
        """
        candidates = []

        # 你基准代码里点击检测后的三级构造函数，优先级最高
        for name in [
            "_psqcc_build_third_category",
            "_PSTMDB_PREV_THIRD_BUILDER",
            "_PSTV3_BASE_THIRD"
        ]:
            try:
                fn = globals().get(name)
                if fn:
                    candidates.append(fn)
            except Exception:
                pass

        # 兜底取当前全局，但要避免取到 V3/V4 wrapper 自己
        try:
            fn = globals().get("_psq_build_third_category")
            if fn:
                candidates.append(fn)
        except Exception:
            pass

        for fn in candidates:
            try:
                nm = getattr(fn, "__name__", "")
                if nm.startswith("_pstv4_"):
                    continue
                if nm.startswith("_pstv3_"):
                    continue
                if nm.startswith("_pstmdb_third"):
                    continue
                return fn
            except Exception:
                return fn

        return None

    _PSTV4_BASE_THIRD = _pstv4_pick_base_third()

    def _pstv4_group_key(api_type):
        try:
            if "_psq_group_key" in globals():
                return _psq_group_key(api_type)
        except Exception:
            pass

        api_type = str(api_type or "").strip().lower()

        if api_type in ["115", "a115"]:
            return "115"
        if api_type in ["ali", "aliyun", "alipan"]:
            return "aliyun"
        if api_type in ["123", "a123", "123pan"]:
            return "123"
        if api_type in ["tianyi", "189"]:
            return "tianyi"
        if api_type in ["mobile", "139"]:
            return "mobile"
        if api_type in ["quark"]:
            return "quark"
        if api_type in ["baidu"]:
            return "baidu"
        if api_type in ["uc"]:
            return "uc"
        if api_type in ["xunlei"]:
            return "xunlei"
        if api_type in ["magnet"]:
            return "magnet"
        if api_type in ["ed2k"]:
            return "ed2k"

        return api_type or "other"

    def _pstv4_group_to_pan_type(group):
        group = str(group or "").strip().lower()
        mapping = {
            "quark": "quark",
            "115": "a115",
            "a115": "a115",
            "aliyun": "ali",
            "ali": "ali",
            "baidu": "baidu",
            "uc": "uc",
            "tianyi": "tianyi",
            "189": "tianyi",
            "mobile": "mobile",
            "139": "mobile",
            "xunlei": "xunlei",
            "123": "a123",
            "a123": "a123",
            "pikpak": "pikpak",
            "magnet": "magnet",
            "ed2k": "ed2k"
        }
        return mapping.get(group, group)

    def _pstv4_icon(self, group):
        try:
            group = _pstv4_group_key(group)
            pan_type = _pstv4_group_to_pan_type(group)

            icon_name = ""

            try:
                cfg = getattr(self, "PAN_CONFIG", {}).get(pan_type, {}) or {}
                icon_name = cfg.get("icon", "") or ""
            except Exception:
                icon_name = ""

            if not icon_name:
                fallback = {
                    "quark": "quark.png",
                    "115": "115.png",
                    "aliyun": "ali.png",
                    "baidu": "baidu.png",
                    "uc": "uc.png",
                    "tianyi": "189.png",
                    "mobile": "139.png",
                    "xunlei": "xunlei.png",
                    "123": "123.png",
                    "pikpak": "pikpak.png",
                    "magnet": "cili.png",
                    "ed2k": ""
                }
                icon_name = fallback.get(group, "")

            if not icon_name:
                return ""

            try:
                if hasattr(self, "_get_icon_url"):
                    return self._get_icon_url(icon_name)
            except Exception:
                pass

            return "http://127.0.0.1:9978/file/Download/lib/icon/%s" % icon_name

        except Exception:
            return ""

    def _pstv4_force_list_ret(self, ret, data):
        """
        关键修正：
        分类页返回 style.type=list，item 强制 file。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            # 尽量提示壳：这个页面用列表样式
            ret["style"] = {
                "type": "list"
            }

            # 有些壳识别 list_style / vod_style，也一并给上
            ret["list_style"] = "list"
            ret["vod_style"] = "list"

            group = ""
            try:
                group = str((data or {}).get("group") or "").strip()
            except Exception:
                group = ""

            icon = _pstv4_icon(self, group)

            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue

                    # 三级资源必须是文件，不是文件夹
                    v["vod_tag"] = "file"

                    # 有些壳看 tag/type，这里也尽量声明
                    v["tag"] = "file"

                    # 不要清空图。清空图反而会变成绿色大占位。
                    # 如果原本有资源图，保留；没图才补网盘小图标。
                    if not v.get("vod_pic"):
                        v["vod_pic"] = icon

                    # 避免被壳误判成 folder
                    if str(v.get("vod_id") or "").startswith("psq|group|"):
                        # 正常三级资源不应该是 group，这里只是保险
                        v["vod_tag"] = "file"
                        v["tag"] = "file"

                except Exception:
                    pass

            return ret

        except Exception as e:
            print("[PANSOU TMDB V4] force list ret error:", e)
            return ret

    def _pstv4_build_third_category(self, data, pg=1):
        """
        覆盖三级构造：
        先走原逻辑，再强制列表样式。
        """
        try:
            if _PSTV4_BASE_THIRD:
                ret = _PSTV4_BASE_THIRD(self, data, pg)
            else:
                ret = {"list": []}

            return _pstv4_force_list_ret(self, ret, data)

        except Exception as e:
            print("[PANSOU TMDB V4] build third error:", e)
            try:
                if _PSTV4_BASE_THIRD:
                    return _PSTV4_BASE_THIRD(self, data, pg)
            except Exception:
                pass
            return {
                "list": [],
                "page": 1,
                "pagecount": 1,
                "limit": 0,
                "total": 0,
                "style": {
                    "type": "list"
                }
            }

    try:
        globals()["_psq_build_third_category"] = _pstv4_build_third_category
        Spider = _PSTV4_TARGET

        print("[PANSOU TMDB V4 FORCE THIRD LIST] loaded")
        print("[PANSOU TMDB V4] 三级强制 style=list，vod_tag=file，无图补网盘小图标")
        try:
            print("[PANSOU TMDB V4] base third =", getattr(_PSTV4_BASE_THIRD, "__name__", str(_PSTV4_BASE_THIRD)))
        except Exception:
            pass

    except Exception as e:
        print("[PANSOU TMDB V4] bind error:", e)

# ===== PANSOU_TMDB_V4_FORCE_THIRD_LIST_END =====

# ===== PANSOU_TMDB_V6_SAFE_THIRD_LIST_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou + TMDB V6 保守三级列表补丁
#
# 目的：
#   不删除三级，不改三级点击逻辑。
#   只把三级 categoryContent 返回结果尽量伪装成文件列表。
#
# 特点：
#   1. 保留原来的二级 -> 三级 categoryContent；
#   2. 保留原三级 vod_id；
#   3. 保留原 playerContent / detailContent 逻辑；
#   4. 三级资源默认使用网盘小图标；
#   5. 返回 style/list_style/vod_style；
#   6. item 尽量标记为 file；
#   7. 如果壳固定海报墙，则无法 100% 强制。
#
# ext 可选：
#   "pstv6_third_pic_mode": "icon"   默认，三级资源统一用网盘小图标
#   "pstv6_third_pic_mode": "keep"   保留原图，无图才补图标
#   "pstv6_force_file_tag": true     默认 true，三级 vod_tag 尽量 file
# ============================================================

import json as _pstv6_json

try:
    _PSTV6_TARGET = PanSouSpider
except Exception:
    _PSTV6_TARGET = globals().get("Spider")

if _PSTV6_TARGET is None:
    print("[PANSOU TMDB V6] no target class, skip")
else:
    try:
        _PSTV6_PREV_INIT = _PSTV6_TARGET.init
    except Exception:
        _PSTV6_PREV_INIT = None

    try:
        _PSTV6_PREV_CATEGORY = _PSTV6_TARGET.categoryContent
    except Exception:
        _PSTV6_PREV_CATEGORY = None

    # ------------------------------------------------------------
    # 选择原三级构造函数
    # ------------------------------------------------------------

    def _pstv6_pick_base_third():
        """
        选择原来的三级构造函数，尽量避开 V3/V4/V5/V6 包装。
        优先选 _psqcc_build_third_category，因为它通常是盘检增强后的三级构造。
        """
        names = [
            "_psqcc_build_third_category",
            "_PSTMDB_PREV_THIRD_BUILDER",
            "_PSTV3_BASE_THIRD",
            "_PSTV4_BASE_THIRD",
            "_psq_build_third_category"
        ]

        for name in names:
            try:
                fn = globals().get(name)
                if not fn:
                    continue

                nm = getattr(fn, "__name__", "")

                bad_prefixes = [
                    "_pstv6_",
                    "_pstv5_",
                    "_pstv4_",
                    "_pstv3_",
                    "_pstmdb_third"
                ]

                if any(nm.startswith(x) for x in bad_prefixes):
                    continue

                return fn
            except Exception:
                pass

        return None

    _PSTV6_BASE_THIRD = _pstv6_pick_base_third()

    # ------------------------------------------------------------
    # 工具函数
    # ------------------------------------------------------------

    def _pstv6_parse_ext(extend):
        try:
            if not extend:
                return {}
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _pstv6_json.loads(extend)
            return {}
        except Exception:
            return {}

    def _pstv6_bool(v, default=False):
        try:
            if isinstance(v, bool):
                return v
            if v is None:
                return default
            s = str(v).strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off"]:
                return False
            return default
        except Exception:
            return default

    def _pstv6_group_key(api_type):
        try:
            if "_psq_group_key" in globals():
                return _psq_group_key(api_type)
        except Exception:
            pass

        api_type = str(api_type or "").strip().lower()

        if api_type in ["115", "a115"]:
            return "115"
        if api_type in ["ali", "aliyun", "alipan"]:
            return "aliyun"
        if api_type in ["123", "a123", "123pan"]:
            return "123"
        if api_type in ["tianyi", "189"]:
            return "tianyi"
        if api_type in ["mobile", "139"]:
            return "mobile"
        if api_type in ["quark"]:
            return "quark"
        if api_type in ["baidu"]:
            return "baidu"
        if api_type in ["uc"]:
            return "uc"
        if api_type in ["xunlei"]:
            return "xunlei"
        if api_type in ["magnet"]:
            return "magnet"
        if api_type in ["ed2k"]:
            return "ed2k"

        return api_type or "other"

    def _pstv6_group_to_pan_type(group):
        group = str(group or "").strip().lower()
        mapping = {
            "quark": "quark",
            "115": "a115",
            "a115": "a115",
            "aliyun": "ali",
            "ali": "ali",
            "baidu": "baidu",
            "uc": "uc",
            "tianyi": "tianyi",
            "189": "tianyi",
            "mobile": "mobile",
            "139": "mobile",
            "xunlei": "xunlei",
            "123": "a123",
            "a123": "a123",
            "pikpak": "pikpak",
            "magnet": "magnet",
            "ed2k": "ed2k"
        }
        return mapping.get(group, group)

    def _pstv6_icon(self, group):
        """
        获取网盘小图标。
        优先使用原 Spider 的 _get_icon_url。
        """
        try:
            group = _pstv6_group_key(group)
            pan_type = _pstv6_group_to_pan_type(group)

            icon_name = ""

            try:
                cfg = getattr(self, "PAN_CONFIG", {}).get(pan_type, {}) or {}
                icon_name = cfg.get("icon", "") or ""
            except Exception:
                icon_name = ""

            if not icon_name:
                fallback = {
                    "quark": "quark.png",
                    "115": "115.png",
                    "aliyun": "ali.png",
                    "ali": "ali.png",
                    "baidu": "baidu.png",
                    "uc": "uc.png",
                    "tianyi": "189.png",
                    "189": "189.png",
                    "mobile": "139.png",
                    "139": "139.png",
                    "xunlei": "xunlei.png",
                    "123": "123.png",
                    "pikpak": "pikpak.png",
                    "magnet": "cili.png",
                    "ed2k": "cili.png"
                }
                icon_name = fallback.get(group, "")

            if not icon_name:
                return ""

            try:
                if hasattr(self, "_get_icon_url"):
                    return self._get_icon_url(icon_name)
            except Exception:
                pass

            # 兜底。不同壳端口可能不同，所以只是最后兜底。
            return "http://127.0.0.1:9978/file/Download/lib/icon/%s" % icon_name

        except Exception:
            return ""

    def _pstv6_parse_psq_id(tid):
        """
        尝试解析原 PanSou 的 psq id。
        只用于判断是不是 group 三级入口。
        """
        try:
            if "_psq_parse_id" in globals():
                return _psq_parse_id(tid)
        except Exception:
            pass

        return "", {}

    def _pstv6_is_group_tid(tid):
        """
        判断当前 categoryContent 是否是二级分组点进去的三级页面。
        """
        try:
            tid_s = str(tid or "")

            # 原 PanSou 通常是 psq|group|...
            if "group" in tid_s and ("psq" in tid_s or "pansou" in tid_s):
                return True

            typ, data = _pstv6_parse_psq_id(tid_s)
            if str(typ or "").lower() == "group":
                return True

            if isinstance(data, dict) and data.get("group") and data.get("kw"):
                return True

        except Exception:
            pass

        return False

    def _pstv6_extract_group_from_tid(tid):
        try:
            typ, data = _pstv6_parse_psq_id(tid)
            if isinstance(data, dict):
                return str(data.get("group") or "").strip()
        except Exception:
            pass
        return ""

    def _pstv6_apply_list_style(ret):
        """
        给返回结果加各种列表样式提示。
        不保证所有壳都支持。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            # 常见风格提示
            ret["style"] = {
                "type": "list"
            }

            # 一些壳可能读这些
            ret["list_style"] = "list"
            ret["vod_style"] = "list"
            ret["view_type"] = "list"
            ret["layout"] = "list"

            return ret
        except Exception:
            return ret

    def _pstv6_fix_third_items(self, ret, group=""):
        """
        只修三级 item 的显示字段，不改 vod_id。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            icon = _pstv6_icon(self, group)

            pic_mode = str(getattr(self, "pstv6_third_pic_mode", "icon") or "icon").strip().lower()
            force_file_tag = _pstv6_bool(
                getattr(self, "pstv6_force_file_tag", True),
                True
            )

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue

                    # 不改 vod_id，保证点击后的原逻辑不变
                    # old_id = v.get("vod_id")

                    # 三级资源尽量声明为 file，但不改 vod_id。
                    # 如果你的壳把 file 用于列表显示，会生效；
                    # 如果不识别，也不会删除三级。
                    if force_file_tag:
                        v["vod_tag"] = "file"
                        v["tag"] = "file"
                    else:
                        if not v.get("vod_tag"):
                            v["vod_tag"] = "file"
                        if not v.get("tag"):
                            v["tag"] = "file"

                    # 图片策略：
                    # icon：三级统一用网盘小图标，避免 TMDB 大海报铺满；
                    # keep：保留原图，无图才补图标。
                    if pic_mode == "keep":
                        if not v.get("vod_pic"):
                            v["vod_pic"] = icon
                    else:
                        # 默认 icon
                        if icon:
                            v["vod_pic"] = icon
                        elif not v.get("vod_pic"):
                            v["vod_pic"] = ""

                    # item 级别也加一点提示，部分壳可能读取
                    v["style"] = {
                        "type": "list"
                    }
                    v["view_type"] = "list"

                except Exception:
                    pass

            return ret

        except Exception as e:
            print("[PANSOU TMDB V6] fix third items error:", e)
            return ret

    def _pstv6_process_third_ret(self, ret, group=""):
        """
        处理三级返回。
        """
        try:
            ret = _pstv6_apply_list_style(ret)
            ret = _pstv6_fix_third_items(self, ret, group)
            return ret
        except Exception as e:
            print("[PANSOU TMDB V6] process third ret error:", e)
            return ret

    # ------------------------------------------------------------
    # init
    # ------------------------------------------------------------

    def _pstv6_init(self, extend=""):
        ret = None

        if _PSTV6_PREV_INIT:
            try:
                ret = _PSTV6_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU TMDB V6] prev init error:", e)

        ext = _pstv6_parse_ext(extend)

        self.pstv6_third_pic_mode = str(
            ext.get(
                "pstv6_third_pic_mode",
                getattr(self, "pstv6_third_pic_mode", "icon")
            ) or "icon"
        ).strip().lower()

        if self.pstv6_third_pic_mode not in ["icon", "keep"]:
            self.pstv6_third_pic_mode = "icon"

        self.pstv6_force_file_tag = _pstv6_bool(
            ext.get(
                "pstv6_force_file_tag",
                getattr(self, "pstv6_force_file_tag", True)
            ),
            True
        )

        print("[PANSOU TMDB V6] enabled")
        print("[PANSOU TMDB V6] third_pic_mode =", self.pstv6_third_pic_mode)
        print("[PANSOU TMDB V6] force_file_tag =", self.pstv6_force_file_tag)
        try:
            print("[PANSOU TMDB V6] base third =", getattr(_PSTV6_BASE_THIRD, "__name__", str(_PSTV6_BASE_THIRD)))
        except Exception:
            pass

        return ret if ret is not None else {}

    # ------------------------------------------------------------
    # 覆盖三级构造函数：保留原逻辑，只修显示
    # ------------------------------------------------------------

    def _pstv6_build_third_category(self, data, pg=1):
        """
        原来的二级 -> 三级路径一般会调用 _psq_build_third_category。
        这里覆盖它：
            原三级 ret = 原函数(self, data, pg)
            然后追加 style 和小图标。
        """
        try:
            if _PSTV6_BASE_THIRD:
                ret = _PSTV6_BASE_THIRD(self, data, pg)
            else:
                ret = {
                    "list": [],
                    "page": int(pg or 1),
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            group = ""
            try:
                group = str((data or {}).get("group") or "").strip()
            except Exception:
                group = ""

            return _pstv6_process_third_ret(self, ret, group)

        except Exception as e:
            print("[PANSOU TMDB V6] build third error:", e)
            try:
                if _PSTV6_BASE_THIRD:
                    return _PSTV6_BASE_THIRD(self, data, pg)
            except Exception:
                pass
            return {
                "list": [],
                "page": int(pg or 1),
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    # ------------------------------------------------------------
    # categoryContent 兜底包装
    # ------------------------------------------------------------

    def _pstv6_categoryContent(self, tid, pg, filter, extend):
        """
        兜底处理：
        即使原代码没有走 _psq_build_third_category，
        只要判断是 group 三级入口，也对返回结果修显示。
        """
        try:
            ret = None

            if _PSTV6_PREV_CATEGORY:
                ret = _PSTV6_PREV_CATEGORY(self, tid, pg, filter, extend)
            else:
                ret = {
                    "list": [],
                    "page": int(pg or 1),
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            if _pstv6_is_group_tid(tid):
                group = _pstv6_extract_group_from_tid(tid)
                return _pstv6_process_third_ret(self, ret, group)

            return ret

        except Exception as e:
            print("[PANSOU TMDB V6] categoryContent error:", e)

            if _PSTV6_PREV_CATEGORY:
                try:
                    return _PSTV6_PREV_CATEGORY(self, tid, pg, filter, extend)
                except Exception:
                    pass

            return {
                "list": [],
                "page": int(pg or 1),
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    # ------------------------------------------------------------
    # 绑定
    # ------------------------------------------------------------

    try:
        _PSTV6_TARGET.init = _pstv6_init

        # 不改二级、不改详情、不改播放。
        # 只包装 categoryContent 和三级构造函数。
        _PSTV6_TARGET.categoryContent = _pstv6_categoryContent

        # 关键：保留原 二级 -> 三级 category 路线，只修三级显示。
        globals()["_psq_build_third_category"] = _pstv6_build_third_category

        Spider = _PSTV6_TARGET

        print("[PANSOU TMDB V6 SAFE THIRD LIST] loaded")
        print("[PANSOU TMDB V6] 不删除三级，不改 vod_id，只伪装三级为文件列表样式")

    except Exception as e:
        print("[PANSOU TMDB V6] bind error:", e)

# ===== PANSOU_TMDB_V6_SAFE_THIRD_LIST_END =====

# ===== PANSOU_TMDB_V65_INHERIT_CLICKED_PIC_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou + TMDB V6.5
#
# 目的：
#   三级列表小图沿用“当前点击进入三级的那个二级/网盘分类 item”的 vod_pic。
#
# 路径区分：
#   1. TMDB 海报路径：
#      TMDB海报 -> 二级网盘分类 -> 三级
#      三级小图 = TMDB 二级分类 item 的 vod_pic
#
#   2. 搜索结果路径：
#      搜索结果 item / 网盘分类 -> 三级
#      三级小图 = 搜索结果 item 自己的 vod_pic
#
# 明确不使用：
#   self.last_vod_pic
#   三级时重新 TMDB 搜索
#
# 不改：
#   vod_id
#   点击逻辑
#   播放逻辑
#   盘检逻辑
# ============================================================

import json as _pstv65_json
import re as _pstv65_re

try:
    _PSTV65_TARGET = PanSouSpider
except Exception:
    _PSTV65_TARGET = globals().get("Spider")

if _PSTV65_TARGET is None:
    print("[PANSOU TMDB V6.5] no target class, skip")
else:
    try:
        _PSTV65_PREV_INIT = _PSTV65_TARGET.init
    except Exception:
        _PSTV65_PREV_INIT = None

    try:
        _PSTV65_PREV_SEARCH = _PSTV65_TARGET.searchContent
    except Exception:
        _PSTV65_PREV_SEARCH = None

    try:
        _PSTV65_PREV_CATEGORY = _PSTV65_TARGET.categoryContent
    except Exception:
        _PSTV65_PREV_CATEGORY = None

    try:
        _PSTV65_PREV_SECOND = globals().get("_pstmdb_build_pansou_second")
    except Exception:
        _PSTV65_PREV_SECOND = None

    try:
        _PSTV65_PREV_THIRD = globals().get("_psq_build_third_category")
    except Exception:
        _PSTV65_PREV_THIRD = None

    # ------------------------------------------------------------
    # ext
    # ------------------------------------------------------------

    def _pstv65_parse_ext(extend):
        try:
            if not extend:
                return {}
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _pstv65_json.loads(extend)
            return {}
        except Exception:
            return {}

    def _pstv65_bool(v, default=True):
        try:
            if isinstance(v, bool):
                return v
            if v is None:
                return default
            s = str(v).strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off"]:
                return False
            return default
        except Exception:
            return default

    def _pstv65_init(self, extend=""):
        ret = None

        if _PSTV65_PREV_INIT:
            try:
                ret = _PSTV65_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU TMDB V6.5] prev init error:", e)

        ext = _pstv65_parse_ext(extend)

        self.pstv65_inherit_clicked_pic = _pstv65_bool(
            ext.get(
                "pstv65_inherit_clicked_pic",
                getattr(self, "pstv65_inherit_clicked_pic", True)
            ),
            True
        )

        if not hasattr(self, "_pstv65_pic_by_tid"):
            self._pstv65_pic_by_tid = {}

        if not hasattr(self, "_pstv65_pic_by_key"):
            self._pstv65_pic_by_key = {}

        print("[PANSOU TMDB V6.5] enabled")
        print("[PANSOU TMDB V6.5] inherit_clicked_pic =", self.pstv65_inherit_clicked_pic)

        return ret if ret is not None else {}

    # ------------------------------------------------------------
    # id / data 工具
    # ------------------------------------------------------------

    def _pstv65_clean(s):
        try:
            return _pstv65_re.sub(r"\s+", " ", str(s or "")).strip()
        except Exception:
            return str(s or "").strip()

    def _pstv65_parse_psq_id(tid):
        try:
            if "_psq_parse_id" in globals():
                return _psq_parse_id(tid)
        except Exception:
            pass
        return "", {}

    def _pstv65_is_group_tid(tid):
        try:
            tid_s = str(tid or "")

            typ, data = _pstv65_parse_psq_id(tid_s)

            if str(typ or "").lower() == "group":
                return True

            if isinstance(data, dict) and data.get("kw") and data.get("group"):
                return True

            # 兜底兼容
            if "group" in tid_s and ("psq" in tid_s or "pansou" in tid_s):
                return True

        except Exception:
            pass

        return False

    def _pstv65_extract_data_from_tid(tid):
        try:
            typ, data = _pstv65_parse_psq_id(tid)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    def _pstv65_data_kw(data):
        try:
            if not isinstance(data, dict):
                return ""
            return _pstv65_clean(
                data.get("kw")
                or data.get("keyword")
                or data.get("title")
                or data.get("name")
                or ""
            )
        except Exception:
            return ""

    def _pstv65_data_group(data):
        try:
            if not isinstance(data, dict):
                return ""
            return _pstv65_clean(
                data.get("group")
                or data.get("type")
                or data.get("api_type")
                or ""
            )
        except Exception:
            return ""

    def _pstv65_key(kw, group):
        return "%s@@%s" % (_pstv65_clean(kw), _pstv65_clean(group))

    def _pstv65_item_pic(item):
        try:
            if not isinstance(item, dict):
                return ""
            return str(
                item.get("vod_pic")
                or item.get("pic")
                or item.get("poster")
                or item.get("cover")
                or ""
            ).strip()
        except Exception:
            return ""

    # ------------------------------------------------------------
    # 记录当前可点击分类 item 的图片
    # ------------------------------------------------------------

    def _pstv65_store_pic(self, tid, pic, data=None, source=""):
        """
        tid 是之后进入三级时 categoryContent 收到的 tid。
        pic 是当前被点击的二级/网盘分类 item 的 vod_pic。
        """
        try:
            if not getattr(self, "pstv65_inherit_clicked_pic", True):
                return

            tid_s = str(tid or "").strip()
            pic = str(pic or "").strip()

            if not tid_s or not pic:
                return

            if not hasattr(self, "_pstv65_pic_by_tid"):
                self._pstv65_pic_by_tid = {}

            if not hasattr(self, "_pstv65_pic_by_key"):
                self._pstv65_pic_by_key = {}

            # 最重要：精确 tid -> pic
            self._pstv65_pic_by_tid[tid_s] = pic

            # 辅助：kw + group -> pic
            if data is None:
                data = {}

            kw = _pstv65_data_kw(data)
            group = _pstv65_data_group(data)

            if kw and group:
                self._pstv65_pic_by_key[_pstv65_key(kw, group)] = pic

            # 打印少量日志，方便确认来源
            try:
                print("[PANSOU TMDB V6.5] store pic source=%s tid=%s pic=%s" % (
                    source,
                    tid_s[:80],
                    pic[:80]
                ))
            except Exception:
                pass

        except Exception as e:
            print("[PANSOU TMDB V6.5] store pic error:", e)

    def _pstv65_scan_list_and_store(self, ret, source=""):
        """
        扫描 searchContent / 二级 categoryContent 返回的 list。
        只要 item 有 vod_id 和 vod_pic，就记录。
        这样搜索结果路径和 TMDB 二级路径都能覆盖。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            for item in lst:
                try:
                    if not isinstance(item, dict):
                        continue

                    tid = str(item.get("vod_id") or "").strip()
                    pic = _pstv65_item_pic(item)

                    if not tid or not pic:
                        continue

                    typ, data = _pstv65_parse_psq_id(tid)
                    if not isinstance(data, dict):
                        data = {}

                    # 记录所有有图 item。
                    # 这样不依赖它一定被识别为 group。
                    # 真正应用时，只在 group 三级页面应用。
                    _pstv65_store_pic(self, tid, pic, data, source)

                except Exception:
                    pass

            return ret

        except Exception as e:
            print("[PANSOU TMDB V6.5] scan list error:", e)
            return ret

    # ------------------------------------------------------------
    # 包装 searchContent：解决搜索结果直接进入三级无图
    # ------------------------------------------------------------

    def _pstv65_searchContent(self, key, quick, pg="1"):
        try:
            if _PSTV65_PREV_SEARCH:
                ret = _PSTV65_PREV_SEARCH(self, key, quick, pg)
            else:
                ret = {"list": []}

            # 关键：
            # 搜索结果里的 item 有自己的 vod_pic。
            # 之后点击它进入三级时，三级就沿用这个图。
            return _pstv65_scan_list_and_store(self, ret, "search")

        except Exception as e:
            print("[PANSOU TMDB V6.5] searchContent error:", e)

            if _PSTV65_PREV_SEARCH:
                try:
                    return _PSTV65_PREV_SEARCH(self, key, quick, pg)
                except Exception:
                    pass

            return {"list": []}

    # ------------------------------------------------------------
    # 包装 TMDB 二级分类构造：解决 TMDB 海报路径
    # ------------------------------------------------------------

    def _pstv65_build_pansou_second(self, data, pg=1):
        try:
            if _PSTV65_PREV_SECOND:
                ret = _PSTV65_PREV_SECOND(self, data, pg)
            else:
                ret = {
                    "list": [],
                    "page": 1,
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            # TMDB 二级分类 item 的 vod_pic 是 TMDB 海报。
            # 记录它，进入三级时沿用。
            return _pstv65_scan_list_and_store(self, ret, "tmdb_second")

        except Exception as e:
            print("[PANSOU TMDB V6.5] build pansou second error:", e)

            if _PSTV65_PREV_SECOND:
                try:
                    return _PSTV65_PREV_SECOND(self, data, pg)
                except Exception:
                    pass

            return {
                "list": [],
                "page": 1,
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    # ------------------------------------------------------------
    # 进入三级时找当前点击项图片
    # ------------------------------------------------------------

    def _pstv65_get_pic_for_third(self, tid="", data=None):
        """
        图片来源优先级：
        1. 当前 tid 精确匹配的点击项 vod_pic；
        2. 当前 data 自带 pic；
        3. 当前 kw+group 缓存图。

        明确不使用 last_vod_pic。
        明确不重新查 TMDB。
        """
        try:
            if not getattr(self, "pstv65_inherit_clicked_pic", True):
                return ""

            tid_s = str(tid or "").strip()

            # 1. tid 精确匹配：搜索结果路径最关键
            try:
                mp = getattr(self, "_pstv65_pic_by_tid", {}) or {}
                if tid_s and isinstance(mp, dict) and mp.get(tid_s):
                    return str(mp.get(tid_s) or "").strip()
            except Exception:
                pass

            if data is None:
                data = {}

            # 2. 当前 data 自带 pic
            try:
                if isinstance(data, dict):
                    pic = str(
                        data.get("pic")
                        or data.get("vod_pic")
                        or data.get("poster")
                        or data.get("cover")
                        or ""
                    ).strip()
                    if pic:
                        return pic
            except Exception:
                pass

            # 3. kw + group
            try:
                kw = _pstv65_data_kw(data)
                group = _pstv65_data_group(data)

                mp2 = getattr(self, "_pstv65_pic_by_key", {}) or {}
                if kw and group and isinstance(mp2, dict):
                    pic = mp2.get(_pstv65_key(kw, group))
                    if pic:
                        return str(pic or "").strip()
            except Exception:
                pass

        except Exception as e:
            print("[PANSOU TMDB V6.5] get pic for third error:", e)

        return ""

    def _pstv65_apply_pic_to_third(self, ret, pic):
        try:
            if not isinstance(ret, dict):
                return ret

            # 保留三级列表样式
            ret["style"] = {"type": "list"}
            ret["list_style"] = "list"
            ret["vod_style"] = "list"
            ret["view_type"] = "list"
            ret["layout"] = "list"

            pic = str(pic or "").strip()
            if not pic:
                return ret

            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue

                    # 核心：三级小图 = 当前点击项自己的 vod_pic
                    v["vod_pic"] = pic

                    # 保留文件列表伪装，不改 vod_id
                    v["vod_tag"] = "file"
                    v["tag"] = "file"
                    v["style"] = {"type": "list"}
                    v["view_type"] = "list"

                except Exception:
                    pass

            return ret

        except Exception as e:
            print("[PANSOU TMDB V6.5] apply pic error:", e)
            return ret

    # ------------------------------------------------------------
    # 包装三级构造函数
    # ------------------------------------------------------------

    def _pstv65_build_third_category(self, data, pg=1):
        try:
            if _PSTV65_PREV_THIRD:
                ret = _PSTV65_PREV_THIRD(self, data, pg)
            else:
                ret = {
                    "list": [],
                    "page": int(pg or 1),
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            # 函数路径没有 tid，只能用 data 自带 pic 或 kw+group 缓存。
            pic = _pstv65_get_pic_for_third(self, "", data)
            return _pstv65_apply_pic_to_third(self, ret, pic)

        except Exception as e:
            print("[PANSOU TMDB V6.5] build third error:", e)

            if _PSTV65_PREV_THIRD:
                try:
                    return _PSTV65_PREV_THIRD(self, data, pg)
                except Exception:
                    pass

            return {
                "list": [],
                "page": int(pg or 1),
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    # ------------------------------------------------------------
    # 包装 categoryContent
    # ------------------------------------------------------------

    def _pstv65_categoryContent(self, tid, pg, filter, extend):
        try:
            if _PSTV65_PREV_CATEGORY:
                ret = _PSTV65_PREV_CATEGORY(self, tid, pg, filter, extend)
            else:
                ret = {
                    "list": [],
                    "page": int(pg or 1),
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            tid_s = str(tid or "").strip()

            # 先扫描当前返回。
            # 如果当前返回的是二级/分类列表，也记录它们的图。
            ret = _pstv65_scan_list_and_store(self, ret, "category")

            # 如果当前 tid 是 group，即三级页面，则应用当前点击项图。
            if _pstv65_is_group_tid(tid_s):
                data = _pstv65_extract_data_from_tid(tid_s)
                pic = _pstv65_get_pic_for_third(self, tid_s, data)
                return _pstv65_apply_pic_to_third(self, ret, pic)

            return ret

        except Exception as e:
            print("[PANSOU TMDB V6.5] categoryContent error:", e)

            if _PSTV65_PREV_CATEGORY:
                try:
                    return _PSTV65_PREV_CATEGORY(self, tid, pg, filter, extend)
                except Exception:
                    pass

            return {
                "list": [],
                "page": int(pg or 1),
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    # ------------------------------------------------------------
    # 绑定
    # ------------------------------------------------------------

    try:
        _PSTV65_TARGET.init = _pstv65_init

        # 搜索结果路径：必须包装 searchContent
        _PSTV65_TARGET.searchContent = _pstv65_searchContent

        # 分类路径：扫描二级，处理三级
        _PSTV65_TARGET.categoryContent = _pstv65_categoryContent

        # TMDB 海报路径：二级构造时记录二级 vod_pic
        globals()["_pstmdb_build_pansou_second"] = _pstv65_build_pansou_second

        # 三级构造路径：不改原逻辑，只补图
        globals()["_psq_build_third_category"] = _pstv65_build_third_category

        Spider = _PSTV65_TARGET

        print("[PANSOU TMDB V6.5 INHERIT CLICKED PIC] loaded")
        print("[PANSOU TMDB V6.5] 搜索路径用搜索结果图，TMDB路径用TMDB二级图，不混用 last_vod_pic")

    except Exception as e:
        print("[PANSOU TMDB V6.5] bind error:", e)

# ===== PANSOU_TMDB_V65_INHERIT_CLICKED_PIC_END =====

# ===== PANSOU_TMDB_V7_FILTER_NO_IMAGE_PROXY_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou + TMDB V7
#
# 功能：
#   1. TMDB 海报图强制直链，不走壳代理；
#   2. TMDB 分类增加筛选项；
#   3. 筛选使用 TMDB discover 接口；
#   4. 点击海报后继续进入原盘搜二级分类；
#   5. 不改播放逻辑；
#   6. 不改 vod_id；
#   7. 不使用 last_vod_pic。
#
# 推荐 ext：
#   "tmdb_proxy": "",
#   "tmdb_image_proxy": false,
#   "pstv7_tmdb_filter": true,
#   "pstv7_tmdb_image_direct": true
# ============================================================

import json as _pstv7_json
import base64 as _pstv7_base64
import urllib.parse as _pstv7_parse
import urllib.request as _pstv7_request
import re as _pstv7_re
import time as _pstv7_time

try:
    _PSTV7_TARGET = PanSouSpider
except Exception:
    _PSTV7_TARGET = globals().get("Spider")

if _PSTV7_TARGET is None:
    print("[PANSOU TMDB V7] no target class, skip")
else:
    try:
        _PSTV7_PREV_INIT = _PSTV7_TARGET.init
    except Exception:
        _PSTV7_PREV_INIT = None

    try:
        _PSTV7_PREV_HOME = _PSTV7_TARGET.homeContent
    except Exception:
        _PSTV7_PREV_HOME = None

    try:
        _PSTV7_PREV_CATEGORY = _PSTV7_TARGET.categoryContent
    except Exception:
        _PSTV7_PREV_CATEGORY = None

    try:
        _PSTV7_PREV_HOME_VIDEO = _PSTV7_TARGET.homeVideoContent
    except Exception:
        _PSTV7_PREV_HOME_VIDEO = None

    # ------------------------------------------------------------
    # 基础工具
    # ------------------------------------------------------------

    def _pstv7_parse_ext(extend):
        try:
            if not extend:
                return {}
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _pstv7_json.loads(extend)
            return {}
        except Exception:
            return {}

    def _pstv7_bool(v, default=True):
        try:
            if isinstance(v, bool):
                return v
            if v is None:
                return default
            s = str(v).strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off"]:
                return False
            return default
        except Exception:
            return default

    def _pstv7_clean(s):
        try:
            return _pstv7_re.sub(r"\s+", " ", str(s or "")).strip()
        except Exception:
            return str(s or "").strip()

    def _pstv7_b64e(obj):
        try:
            txt = _pstv7_json.dumps(obj or {}, ensure_ascii=False, separators=(",", ":"))
            return _pstv7_base64.urlsafe_b64encode(txt.encode("utf-8")).decode("utf-8").rstrip("=")
        except Exception:
            return ""

    def _pstv7_b64d(text):
        try:
            text = str(text or "")
            text += "=" * (-len(text) % 4)
            raw = _pstv7_base64.urlsafe_b64decode(text.encode("utf-8")).decode("utf-8")
            return _pstv7_json.loads(raw)
        except Exception:
            return {}

    def _pstv7_make_pstmdb_id(vtype, data):
        try:
            if "_pstmdb_make_id" in globals():
                return _pstmdb_make_id(vtype, data)
        except Exception:
            pass
        return "pstmdb|%s|%s" % (str(vtype), _pstv7_b64e(data or {}))

    def _pstv7_parse_pstmdb_id(vod_id):
        try:
            if "_pstmdb_parse_id" in globals():
                return _pstmdb_parse_id(vod_id)
        except Exception:
            pass

        try:
            s = str(vod_id or "")
            if not s.startswith("pstmdb|"):
                return "", {}
            arr = s.split("|", 2)
            if len(arr) < 3:
                return "", {}
            return arr[1], _pstv7_b64d(arr[2])
        except Exception:
            return "", {}

    # ------------------------------------------------------------
    # init：强制 TMDB 图片不走壳代理
    # ------------------------------------------------------------

    def _pstv7_init(self, extend=""):
        ret = None

        if _PSTV7_PREV_INIT:
            try:
                ret = _PSTV7_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU TMDB V7] prev init error:", e)

        ext = _pstv7_parse_ext(extend)

        self.pstv7_tmdb_filter = _pstv7_bool(
            ext.get("pstv7_tmdb_filter", getattr(self, "pstv7_tmdb_filter", True)),
            True
        )

        self.pstv7_tmdb_image_direct = _pstv7_bool(
            ext.get("pstv7_tmdb_image_direct", getattr(self, "pstv7_tmdb_image_direct", True)),
            True
        )

        self.pstv7_tmdb_image_size = str(
            ext.get("pstv7_tmdb_image_size", getattr(self, "pstv7_tmdb_image_size", "w500")) or "w500"
        ).strip()

        if self.pstv7_tmdb_image_size not in ["w92", "w154", "w185", "w342", "w500", "w780", "original"]:
            self.pstv7_tmdb_image_size = "w500"

        # 关键：强制关闭旧 TMDB 图片代理。
        # 即使 ext 里写了 tmdb_image_proxy:true，这里也覆盖为 False。
        if self.pstv7_tmdb_image_direct:
            try:
                self.tmdb_image_proxy = False
            except Exception:
                pass

        print("[PANSOU TMDB V7] enabled")
        print("[PANSOU TMDB V7] tmdb_filter =", self.pstv7_tmdb_filter)
        print("[PANSOU TMDB V7] tmdb_image_direct =", self.pstv7_tmdb_image_direct)
        print("[PANSOU TMDB V7] tmdb_image_size =", self.pstv7_tmdb_image_size)
        print("[PANSOU TMDB V7] force tmdb_image_proxy = False")

        return ret if ret is not None else {}

    # ------------------------------------------------------------
    # TMDB 配置
    # ------------------------------------------------------------

    def _pstv7_tmdb_key(self):
        for name in ["tmdb_api_key", "TMDB_API_KEY", "api_key"]:
            try:
                v = str(getattr(self, name, "") or "").strip()
                if v:
                    return v
            except Exception:
                pass

        try:
            ext = getattr(self, "extend", {}) or {}
            if isinstance(ext, dict):
                v = str(ext.get("tmdb_api_key") or "").strip()
                if v:
                    return v
        except Exception:
            pass

        return ""

    def _pstv7_tmdb_lang(self):
        try:
            return str(getattr(self, "tmdb_language", "") or "zh-CN").strip() or "zh-CN"
        except Exception:
            return "zh-CN"

    def _pstv7_tmdb_region(self):
        try:
            return str(getattr(self, "tmdb_region", "") or "CN").strip() or "CN"
        except Exception:
            return "CN"

    def _pstv7_tmdb_proxy(self):
        for name in ["tmdb_proxy", "proxy", "http_proxy"]:
            try:
                v = str(getattr(self, name, "") or "").strip()
                if v:
                    return v
            except Exception:
                pass
        return ""

    def _pstv7_http_json(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }

            req = _pstv7_request.Request(url, headers=headers)
            proxy = _pstv7_tmdb_proxy(self)

            if proxy:
                opener = _pstv7_request.build_opener(
                    _pstv7_request.ProxyHandler({
                        "http": proxy,
                        "https": proxy
                    })
                )
                resp = opener.open(req, timeout=15)
            else:
                resp = _pstv7_request.urlopen(req, timeout=15)

            raw = resp.read().decode("utf-8", errors="ignore")
            return _pstv7_json.loads(raw)

        except Exception as e:
            print("[PANSOU TMDB V7] http json error:", e)
            return {}

    # ------------------------------------------------------------
    # TMDB 图片直链
    # ------------------------------------------------------------

    def _pstv7_tmdb_img(self, poster_path):
        """
        强制生成 TMDB 原始图片直链，不走壳代理。
        """
        try:
            poster_path = str(poster_path or "").strip()
            if not poster_path:
                return ""

            if poster_path.startswith("http://") or poster_path.startswith("https://"):
                # 如果本身就是 image.tmdb.org，直接返回。
                return poster_path

            size = str(getattr(self, "pstv7_tmdb_image_size", "w500") or "w500").strip()
            return "https://image.tmdb.org/t/p/%s%s" % (size, poster_path)
        except Exception:
            return ""

    def _pstv7_deproxy_tmdb_pic(pic):
        """
        如果旧补丁已经把 image.tmdb.org 包进壳代理，这里尽量还原成直链。
        """
        try:
            pic = str(pic or "").strip()
            if not pic:
                return ""

            if "image.tmdb.org" not in pic:
                return pic

            # 已经是直链
            if pic.startswith("https://image.tmdb.org/") or pic.startswith("http://image.tmdb.org/"):
                return pic.replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            # 从代理 URL 里提取被编码的 image.tmdb.org 地址
            unq = _pstv7_parse.unquote(pic)
            m = _pstv7_re.search(r"https?://image\.tmdb\.org/[^\s&\"']+", unq)
            if m:
                return m.group(0).replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            return pic
        except Exception:
            return pic

    def _pstv7_fix_tmdb_pics_in_ret(ret):
        """
        扫描返回 list，把 TMDB 代理图还原成直链。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue
                    pic = str(v.get("vod_pic") or "").strip()
                    if pic and "image.tmdb.org" in pic:
                        v["vod_pic"] = _pstv7_deproxy_tmdb_pic(pic)
                except Exception:
                    pass

            return ret
        except Exception:
            return ret

    # ------------------------------------------------------------
    # 筛选项
    # ------------------------------------------------------------

    _PSTV7_MOVIE_GENRES = [
        ("全部", ""),
        ("动作", "28"),
        ("冒险", "12"),
        ("动画", "16"),
        ("喜剧", "35"),
        ("犯罪", "80"),
        ("纪录", "99"),
        ("剧情", "18"),
        ("家庭", "10751"),
        ("奇幻", "14"),
        ("历史", "36"),
        ("恐怖", "27"),
        ("音乐", "10402"),
        ("悬疑", "9648"),
        ("爱情", "10749"),
        ("科幻", "878"),
        ("电视电影", "10770"),
        ("惊悚", "53"),
        ("战争", "10752"),
        ("西部", "37")
    ]

    _PSTV7_TV_GENRES = [
        ("全部", ""),
        ("动作冒险", "10759"),
        ("动画", "16"),
        ("喜剧", "35"),
        ("犯罪", "80"),
        ("纪录", "99"),
        ("剧情", "18"),
        ("家庭", "10751"),
        ("儿童", "10762"),
        ("悬疑", "9648"),
        ("新闻", "10763"),
        ("真人秀", "10764"),
        ("科幻奇幻", "10765"),
        ("肥皂剧", "10766"),
        ("脱口秀", "10767"),
        ("战争政治", "10768"),
        ("西部", "37")
    ]

    _PSTV7_COUNTRIES = [
        ("全部", ""),
        ("中国大陆", "CN"),
        ("中国香港", "HK"),
        ("中国台湾", "TW"),
        ("美国", "US"),
        ("日本", "JP"),
        ("韩国", "KR"),
        ("英国", "GB"),
        ("法国", "FR"),
        ("德国", "DE"),
        ("印度", "IN"),
        ("泰国", "TH"),
        ("加拿大", "CA"),
        ("澳大利亚", "AU"),
        ("意大利", "IT"),
        ("西班牙", "ES")
    ]

    _PSTV7_SORTS = [
        ("热门度", "popularity.desc"),
        ("评分最高", "vote_average.desc"),
        ("投票最多", "vote_count.desc"),
        ("最新上映/首播", "date.desc"),
        ("最早上映/首播", "date.asc")
    ]

    def _pstv7_years():
        try:
            now = _pstv7_time.localtime().tm_year
        except Exception:
            now = 2026

        arr = [("全部", "")]
        for y in range(now + 1, 1979, -1):
            arr.append((str(y), str(y)))
        return arr

    def _pstv7_filter_obj(media):
        genres = _PSTV7_TV_GENRES if media == "tv" else _PSTV7_MOVIE_GENRES

        return [
            {
                "key": "genre",
                "name": "类型",
                "value": [{"n": n, "v": v} for n, v in genres]
            },
            {
                "key": "year",
                "name": "年份",
                "value": [{"n": n, "v": v} for n, v in _pstv7_years()]
            },
            {
                "key": "country",
                "name": "地区",
                "value": [{"n": n, "v": v} for n, v in _PSTV7_COUNTRIES]
            },
            {
                "key": "sort",
                "name": "排序",
                "value": [{"n": n, "v": v} for n, v in _PSTV7_SORTS]
            }
        ]

    def _pstv7_guess_media_from_class(cls):
        try:
            tid = str((cls or {}).get("type_id") or "").lower()
            name = str((cls or {}).get("type_name") or "").lower()

            text = tid + " " + name

            if "tv" in text or "剧" in text or "series" in text or "show" in text:
                return "tv"

            return "movie"
        except Exception:
            return "movie"

    def _pstv7_is_tmdb_class(cls):
        try:
            tid = str((cls or {}).get("type_id") or "").lower()
            name = str((cls or {}).get("type_name") or "").lower()
            text = tid + " " + name
            return ("tmdb" in text) or ("pstmdb" in text)
        except Exception:
            return False

    # ------------------------------------------------------------
    # homeContent：给 TMDB 分类挂筛选项
    # ------------------------------------------------------------

    def _pstv7_homeContent(self, filter):
        try:
            if _PSTV7_PREV_HOME:
                ret = _PSTV7_PREV_HOME(self, filter)
            else:
                ret = {"class": []}

            if not isinstance(ret, dict):
                return ret

            if not getattr(self, "pstv7_tmdb_filter", True):
                return ret

            classes = ret.get("class", [])
            if not isinstance(classes, list):
                return ret

            filters = ret.get("filters", {})
            if not isinstance(filters, dict):
                filters = {}

            for cls in classes:
                try:
                    if not isinstance(cls, dict):
                        continue

                    if not _pstv7_is_tmdb_class(cls):
                        continue

                    tid = str(cls.get("type_id") or "").strip()
                    if not tid:
                        continue

                    media = _pstv7_guess_media_from_class(cls)
                    filters[tid] = _pstv7_filter_obj(media)

                except Exception:
                    pass

            ret["filters"] = filters

            # 部分壳读 filter 字段
            try:
                ret["filter"] = filters
            except Exception:
                pass

            return ret

        except Exception as e:
            print("[PANSOU TMDB V7] homeContent error:", e)
            if _PSTV7_PREV_HOME:
                try:
                    return _PSTV7_PREV_HOME(self, filter)
                except Exception:
                    pass
            return {"class": []}

    # ------------------------------------------------------------
    # 判断 TMDB 分类 tid
    # ------------------------------------------------------------

    def _pstv7_parse_tmdb_tid(tid):
        """
        返回：
            should_handle, media, data
        注意：
            pstmdb|search|xxx 是海报点击后进入盘搜二级，不应该被 V7 分类拦截。
        """
        try:
            s = str(tid or "").strip()
            low = s.lower()

            vtype, data = _pstv7_parse_pstmdb_id(s)

            if vtype:
                vt = str(vtype or "").lower()

                # search 是点击海报后的盘搜入口，不拦截
                if vt in ["search", "pansou", "group", "second"]:
                    return False, "", {}

                # 这些才作为 TMDB 列表分类处理
                if vt in [
                    "movie", "tv",
                    "movie_popular", "tv_popular",
                    "popular_movie", "popular_tv",
                    "movie_top", "tv_top",
                    "top_movie", "top_tv",
                    "discover_movie", "discover_tv",
                    "tmdb_movie", "tmdb_tv",
                    "list"
                ]:
                    media = str((data or {}).get("media") or (data or {}).get("media_type") or "").lower()
                    if media not in ["movie", "tv"]:
                        if "tv" in vt:
                            media = "tv"
                        else:
                            media = "movie"
                    return True, media, data if isinstance(data, dict) else {}

            # 普通字符串 tid
            if "tmdb" in low or "pstmdb" in low:
                if "search" in low:
                    return False, "", {}
                media = "tv" if ("tv" in low or "剧" in low or "series" in low) else "movie"
                return True, media, {}

        except Exception:
            pass

        return False, "", {}

    # ------------------------------------------------------------
    # TMDB discover 分类
    # ------------------------------------------------------------

    def _pstv7_extend_dict(extend):
        try:
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _pstv7_json.loads(extend)
        except Exception:
            pass
        return {}

    def _pstv7_sort_value(media, sort):
        sort = str(sort or "").strip()

        if sort == "date.desc":
            return "first_air_date.desc" if media == "tv" else "primary_release_date.desc"
        if sort == "date.asc":
            return "first_air_date.asc" if media == "tv" else "primary_release_date.asc"

        if sort in [
            "popularity.desc",
            "popularity.asc",
            "vote_average.desc",
            "vote_average.asc",
            "vote_count.desc",
            "vote_count.asc"
        ]:
            return sort

        return "popularity.desc"

    def _pstv7_build_tmdb_discover(self, tid, pg, extend):
        try:
            api_key = _pstv7_tmdb_key(self)
            if not api_key:
                return {
                    "list": [],
                    "page": int(pg or 1),
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            should, media, data = _pstv7_parse_tmdb_tid(tid)
            if not should:
                return None

            ext = _pstv7_extend_dict(extend)

            page = int(pg or 1)
            if page < 1:
                page = 1

            genre = str(ext.get("genre") or "").strip()
            year = str(ext.get("year") or "").strip()
            country = str(ext.get("country") or "").strip()
            sort = str(ext.get("sort") or "").strip()

            lang = _pstv7_tmdb_lang(self)
            region = _pstv7_tmdb_region(self)

            endpoint = "tv" if media == "tv" else "movie"

            params = {
                "api_key": api_key,
                "language": lang,
                "page": str(page),
                "include_adult": "false",
                "sort_by": _pstv7_sort_value(media, sort)
            }

            if media == "movie":
                params["include_video"] = "false"
                if region:
                    params["region"] = region
            else:
                params["include_null_first_air_dates"] = "false"

            if genre:
                params["with_genres"] = genre

            if year:
                if media == "tv":
                    params["first_air_date_year"] = year
                else:
                    params["primary_release_year"] = year

            if country:
                params["with_origin_country"] = country

            url = "https://api.themoviedb.org/3/discover/%s?%s" % (
                endpoint,
                _pstv7_parse.urlencode(params)
            )

            js = _pstv7_http_json(self, url)

            results = js.get("results", []) if isinstance(js, dict) else []

            videos = []

            for r in results:
                try:
                    if not isinstance(r, dict):
                        continue

                    title = str(r.get("title") or r.get("name") or "").strip()
                    if not title:
                        continue

                    original_title = str(r.get("original_title") or r.get("original_name") or "").strip()
                    overview = str(r.get("overview") or "").strip()

                    date = str(r.get("release_date") or r.get("first_air_date") or "").strip()
                    year2 = date[:4] if len(date) >= 4 else ""

                    poster_path = str(r.get("poster_path") or "").strip()
                    pic = _pstv7_tmdb_img(self, poster_path)

                    vote = r.get("vote_average", "")
                    try:
                        vote_s = "%.1f" % float(vote)
                    except Exception:
                        vote_s = ""

                    remarks_parts = []
                    if year2:
                        remarks_parts.append(year2)
                    if vote_s:
                        remarks_parts.append("⭐" + vote_s)

                    remarks = " ".join(remarks_parts)

                    kw = title
                    try:
                        if getattr(self, "tmdb_click_year_keyword", False) and year2 and year2 not in kw:
                            kw = ("%s %s" % (title, year2)).strip()
                    except Exception:
                        pass

                    vod_id = _pstv7_make_pstmdb_id("search", {
                        "kw": kw,
                        "title": title,
                        "original_title": original_title,
                        "year": year2,
                        "pic": pic,
                        "overview": overview,
                        "media_type": media,
                        "tmdb_id": r.get("id")
                    })

                    item = {
                        "vod_id": vod_id,
                        "vod_name": title,
                        "vod_pic": pic,
                        "vod_remarks": remarks,
                        "vod_content": overview,
                        "vod_year": year2,
                        "vod_tag": "folder"
                    }

                    videos.append(item)

                    # 写入原 TMDB 图缓存，给后续二级/三级继承用。
                    try:
                        if not hasattr(self, "_pstmdb_kw_pic"):
                            self._pstmdb_kw_pic = {}
                        if kw and pic:
                            self._pstmdb_kw_pic[kw] = pic
                        if title and pic:
                            self._pstmdb_kw_pic[title] = pic
                    except Exception:
                        pass

                except Exception:
                    pass

            total_pages = 1
            total_results = len(videos)

            try:
                total_pages = int(js.get("total_pages") or 1)
            except Exception:
                total_pages = 1

            try:
                total_results = int(js.get("total_results") or len(videos))
            except Exception:
                total_results = len(videos)

            if total_pages < 1:
                total_pages = 1

            return {
                "list": videos,
                "page": page,
                "pagecount": total_pages,
                "limit": len(videos),
                "total": total_results
            }

        except Exception as e:
            print("[PANSOU TMDB V7] build tmdb discover error:", e)
            return {
                "list": [],
                "page": int(pg or 1),
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    # ------------------------------------------------------------
    # categoryContent：TMDB 分类走 discover；其他走原逻辑
    # ------------------------------------------------------------

    def _pstv7_categoryContent(self, tid, pg, filter, extend):
        try:
            # 如果是 TMDB 分类，则用 V7 discover，支持筛选。
            if getattr(self, "pstv7_tmdb_filter", True):
                should, media, data = _pstv7_parse_tmdb_tid(tid)
                if should:
                    ret = _pstv7_build_tmdb_discover(self, tid, pg, extend)
                    if isinstance(ret, dict):
                        return _pstv7_fix_tmdb_pics_in_ret(ret)

            # 非 TMDB 分类走原逻辑，包括：
            # - 点击 TMDB 海报后的 pstmdb|search
            # - 盘搜二级分类
            # - 盘搜三级列表
            if _PSTV7_PREV_CATEGORY:
                ret = _PSTV7_PREV_CATEGORY(self, tid, pg, filter, extend)
                return _pstv7_fix_tmdb_pics_in_ret(ret)

        except Exception as e:
            print("[PANSOU TMDB V7] categoryContent error:", e)

            if _PSTV7_PREV_CATEGORY:
                try:
                    ret = _PSTV7_PREV_CATEGORY(self, tid, pg, filter, extend)
                    return _pstv7_fix_tmdb_pics_in_ret(ret)
                except Exception:
                    pass

        return {
            "list": [],
            "page": int(pg or 1),
            "pagecount": 1,
            "limit": 0,
            "total": 0
        }

    # ------------------------------------------------------------
    # homeVideoContent：首页 TMDB 图也尽量还原直链
    # ------------------------------------------------------------

    def _pstv7_homeVideoContent(self):
        try:
            if _PSTV7_PREV_HOME_VIDEO:
                ret = _PSTV7_PREV_HOME_VIDEO(self)
                return _pstv7_fix_tmdb_pics_in_ret(ret)
        except Exception as e:
            print("[PANSOU TMDB V7] homeVideoContent error:", e)

            if _PSTV7_PREV_HOME_VIDEO:
                try:
                    return _PSTV7_PREV_HOME_VIDEO(self)
                except Exception:
                    pass

        return {"list": []}

    # ------------------------------------------------------------
    # 兼容：替换常见 TMDB 图片构造函数
    # ------------------------------------------------------------

    def _pstv7_patch_common_image_helpers():
        """
        如果旧 TMDB 补丁里有图片构造函数，尽量替换为直链版本。
        名字不一定存在，存在就覆盖。
        """
        try:
            helper_names = [
                "_pstmdb_img",
                "_pstmdb_img_url",
                "_pstmdb_image_url",
                "_pstmdb_build_img",
                "_pstmdb_poster_url"
            ]

            for name in helper_names:
                try:
                    if name in globals():
                        globals()[name] = lambda self_or_path, maybe_path=None: (
                            _pstv7_tmdb_img(
                                self_or_path if maybe_path is None else maybe_path
                            )
                        )
                except Exception:
                    pass
        except Exception:
            pass

    # ------------------------------------------------------------
    # 绑定
    # ------------------------------------------------------------

    try:
        _PSTV7_TARGET.init = _pstv7_init
        _PSTV7_TARGET.homeContent = _pstv7_homeContent
        _PSTV7_TARGET.categoryContent = _pstv7_categoryContent

        if _PSTV7_PREV_HOME_VIDEO:
            _PSTV7_TARGET.homeVideoContent = _pstv7_homeVideoContent

        _pstv7_patch_common_image_helpers()

        Spider = _PSTV7_TARGET

        print("[PANSOU TMDB V7 FILTER NO IMAGE PROXY] loaded")
        print("[PANSOU TMDB V7] TMDB 图片直链 + 分类筛选已启用")

    except Exception as e:
        print("[PANSOU TMDB V7] bind error:", e)

# ===== PANSOU_TMDB_V7_FILTER_NO_IMAGE_PROXY_END =====

# ===== PANSOU_TMDB_V71_FORCE_NO_PROXY_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou + TMDB V7.1
#
# 目的：
#   测试 TMDB 全直连：
#     1. API 不走 ；
#     2. 图片不走壳代理；
#     3. 图片使用 image.tmdb.org 直链。
#
# 不改：
#   vod_id
#   点击逻辑
#   播放逻辑
#   三级继承逻辑
# ============================================================

import json as _pstv71_json
import urllib.parse as _pstv71_parse
import re as _pstv71_re

try:
    _PSTV71_TARGET = PanSouSpider
except Exception:
    _PSTV71_TARGET = globals().get("Spider")

if _PSTV71_TARGET is None:
    print("[PANSOU TMDB V7.1] no target class, skip")
else:
    try:
        _PSTV71_PREV_INIT = _PSTV71_TARGET.init
    except Exception:
        _PSTV71_PREV_INIT = None

    try:
        _PSTV71_PREV_HOME = _PSTV71_TARGET.homeContent
    except Exception:
        _PSTV71_PREV_HOME = None

    try:
        _PSTV71_PREV_CATEGORY = _PSTV71_TARGET.categoryContent
    except Exception:
        _PSTV71_PREV_CATEGORY = None

    try:
        _PSTV71_PREV_SEARCH = _PSTV71_TARGET.searchContent
    except Exception:
        _PSTV71_PREV_SEARCH = None

    try:
        _PSTV71_PREV_HOME_VIDEO = _PSTV71_TARGET.homeVideoContent
    except Exception:
        _PSTV71_PREV_HOME_VIDEO = None

    def _pstv71_parse_ext(extend):
        try:
            if not extend:
                return {}
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _pstv71_json.loads(extend)
            return {}
        except Exception:
            return {}

    def _pstv71_bool(v, default=True):
        try:
            if isinstance(v, bool):
                return v
            if v is None:
                return default
            s = str(v).strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off"]:
                return False
            return default
        except Exception:
            return default

    def _pstv71_init(self, extend=""):
        ret = None

        if _PSTV71_PREV_INIT:
            try:
                ret = _PSTV71_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU TMDB V7.1] prev init error:", e)

        ext = _pstv71_parse_ext(extend)

        self.pstv71_tmdb_no_proxy = _pstv71_bool(
            ext.get(
                "pstv71_tmdb_no_proxy",
                getattr(self, "pstv71_tmdb_no_proxy", True)
            ),
            True
        )

        self.pstv71_tmdb_image_direct = _pstv71_bool(
            ext.get(
                "pstv71_tmdb_image_direct",
                getattr(self, "pstv71_tmdb_image_direct", True)
            ),
            True
        )

        self.pstv71_tmdb_image_size = str(
            ext.get(
                "pstv71_tmdb_image_size",
                getattr(self, "pstv71_tmdb_image_size", getattr(self, "pstv7_tmdb_image_size", "w500"))
            ) or "w500"
        ).strip()

        if self.pstv71_tmdb_image_size not in ["w92", "w154", "w185", "w342", "w500", "w780", "original"]:
            self.pstv71_tmdb_image_size = "w500"

        if self.pstv71_tmdb_no_proxy:
            # 关键：只清 TMDB 代理，不动盘搜 server。
            # 不要清 self.server。
            try:
                self.tmdb_proxy = ""
            except Exception:
                pass
            try:
                self.tmdb_api_proxy = ""
            except Exception:
                pass
            try:
                self.TMDB_PROXY = ""
            except Exception:
                pass

        if self.pstv71_tmdb_image_direct:
            try:
                self.tmdb_image_proxy = False
            except Exception:
                pass
            try:
                self.pstv7_tmdb_image_direct = True
            except Exception:
                pass

        print("[PANSOU TMDB V7.1] enabled")
        print("[PANSOU TMDB V7.1] TMDB API no proxy =", self.pstv71_tmdb_no_proxy)
        print("[PANSOU TMDB V7.1] TMDB image direct =", self.pstv71_tmdb_image_direct)
        print("[PANSOU TMDB V7.1] image size =", self.pstv71_tmdb_image_size)

        return ret if ret is not None else {}

    # ------------------------------------------------------------
    # 强制 V7 的 TMDB API 代理函数返回空
    # ------------------------------------------------------------

    def _pstv71_tmdb_proxy_empty(self=None):
        return ""

    try:
        # V7 里 _pstv7_http_json 会运行时查找 _pstv7_tmdb_proxy。
        # 这里覆盖它，让 TMDB API 请求不走 。
        globals()["_pstv7_tmdb_proxy"] = _pstv71_tmdb_proxy_empty
    except Exception:
        pass

    try:
        # 如果旧 TMDB 补丁有这些代理函数，也一并覆盖。
        for _name in [
            "_pstmdb_proxy",
            "_pstmdb_tmdb_proxy",
            "_pstmdb_get_proxy",
            "_pstmdb_get_tmdb_proxy"
        ]:
            if _name in globals():
                globals()[_name] = _pstv71_tmdb_proxy_empty
    except Exception:
        pass

    # ------------------------------------------------------------
    # 图片直链处理
    # ------------------------------------------------------------

    def _pstv71_image_size(self):
        try:
            return str(getattr(self, "pstv71_tmdb_image_size", "") or getattr(self, "pstv7_tmdb_image_size", "") or "w500").strip()
        except Exception:
            return "w500"

    def _pstv71_tmdb_img(self, poster_path):
        try:
            poster_path = str(poster_path or "").strip()
            if not poster_path:
                return ""

            if poster_path.startswith("https://image.tmdb.org/"):
                return poster_path

            if poster_path.startswith("http://image.tmdb.org/"):
                return poster_path.replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            if poster_path.startswith("http://") or poster_path.startswith("https://"):
                # 不是 TMDB 图，不动它。搜索结果的盘搜图不能误改。
                return poster_path

            size = _pstv71_image_size(self)
            return "https://image.tmdb.org/t/p/%s%s" % (size, poster_path)
        except Exception:
            return ""

    def _pstv71_deproxy_tmdb_pic(pic):
        """
        如果旧补丁把 TMDB 图包成了壳代理 URL，这里尽量还原：
        http://127.0.0.1:9978/xxx?url=https%3A%2F%2Fimage.tmdb.org...
        ->
        https://image.tmdb.org/...
        """
        try:
            pic = str(pic or "").strip()
            if not pic:
                return ""

            if "image.tmdb.org" not in pic:
                return pic

            if pic.startswith("https://image.tmdb.org/"):
                return pic

            if pic.startswith("http://image.tmdb.org/"):
                return pic.replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            unq = _pstv71_parse.unquote(pic)

            m = _pstv71_re.search(r"https?://image\.tmdb\.org/[^\s&\"']+", unq)
            if m:
                return m.group(0).replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            return pic

        except Exception:
            return pic

    def _pstv71_fix_ret_pics(ret):
        try:
            if not isinstance(ret, dict):
                return ret

            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue

                    pic = str(v.get("vod_pic") or "").strip()
                    if not pic:
                        continue

                    # 只处理 TMDB 图片，不动盘搜搜索结果图。
                    if "image.tmdb.org" in pic:
                        v["vod_pic"] = _pstv71_deproxy_tmdb_pic(pic)

                except Exception:
                    pass

            return ret

        except Exception:
            return ret

    # 覆盖 V7 图片函数
    try:
        globals()["_pstv7_tmdb_img"] = _pstv71_tmdb_img
    except Exception:
        pass

    try:
        for _name in [
            "_pstmdb_img",
            "_pstmdb_img_url",
            "_pstmdb_image_url",
            "_pstmdb_build_img",
            "_pstmdb_poster_url"
        ]:
            if _name in globals():
                globals()[_name] = _pstv71_tmdb_img
    except Exception:
        pass

    # ------------------------------------------------------------
    # 包装输出，修正已生成的 TMDB 图片 URL
    # ------------------------------------------------------------

    def _pstv71_homeContent(self, filter):
        try:
            if _PSTV71_PREV_HOME:
                ret = _PSTV71_PREV_HOME(self, filter)
            else:
                ret = {"class": []}
            return ret
        except Exception as e:
            print("[PANSOU TMDB V7.1] homeContent error:", e)
            if _PSTV71_PREV_HOME:
                try:
                    return _PSTV71_PREV_HOME(self, filter)
                except Exception:
                    pass
            return {"class": []}

    def _pstv71_categoryContent(self, tid, pg, filter, extend):
        try:
            if _PSTV71_PREV_CATEGORY:
                ret = _PSTV71_PREV_CATEGORY(self, tid, pg, filter, extend)
            else:
                ret = {
                    "list": [],
                    "page": int(pg or 1),
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }

            return _pstv71_fix_ret_pics(ret)

        except Exception as e:
            print("[PANSOU TMDB V7.1] categoryContent error:", e)
            if _PSTV71_PREV_CATEGORY:
                try:
                    return _pstv71_fix_ret_pics(_PSTV71_PREV_CATEGORY(self, tid, pg, filter, extend))
                except Exception:
                    pass
            return {
                "list": [],
                "page": int(pg or 1),
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    def _pstv71_searchContent(self, key, quick, pg="1"):
        try:
            if _PSTV71_PREV_SEARCH:
                ret = _PSTV71_PREV_SEARCH(self, key, quick, pg)
            else:
                ret = {"list": []}

            # 搜索结果的盘搜图不动，只还原里面可能存在的 TMDB 图。
            return _pstv71_fix_ret_pics(ret)

        except Exception as e:
            print("[PANSOU TMDB V7.1] searchContent error:", e)
            if _PSTV71_PREV_SEARCH:
                try:
                    return _pstv71_fix_ret_pics(_PSTV71_PREV_SEARCH(self, key, quick, pg))
                except Exception:
                    pass
            return {"list": []}

    def _pstv71_homeVideoContent(self):
        try:
            if _PSTV71_PREV_HOME_VIDEO:
                return _pstv71_fix_ret_pics(_PSTV71_PREV_HOME_VIDEO(self))
        except Exception as e:
            print("[PANSOU TMDB V7.1] homeVideoContent error:", e)
            if _PSTV71_PREV_HOME_VIDEO:
                try:
                    return _pstv71_fix_ret_pics(_PSTV71_PREV_HOME_VIDEO(self))
                except Exception:
                    pass
        return {"list": []}

    try:
        _PSTV71_TARGET.init = _pstv71_init
        _PSTV71_TARGET.homeContent = _pstv71_homeContent
        _PSTV71_TARGET.categoryContent = _pstv71_categoryContent

        if _PSTV71_PREV_SEARCH:
            _PSTV71_TARGET.searchContent = _pstv71_searchContent

        if _PSTV71_PREV_HOME_VIDEO:
            _PSTV71_TARGET.homeVideoContent = _pstv71_homeVideoContent

        Spider = _PSTV71_TARGET

        print("[PANSOU TMDB V7.1 FORCE NO PROXY] loaded")
        print("[PANSOU TMDB V7.1] TMDB API 和 TMDB 图片均强制直连")

    except Exception as e:
        print("[PANSOU TMDB V7.1] bind error:", e)

# ===== PANSOU_TMDB_V71_FORCE_NO_PROXY_END =====

# ===== PANSOU_TMDB_NO_PROXY_FINAL_PATCH_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou TMDB 最终去代理补丁
#
# 只处理：
#   1. TMDB API 不走 10172 / 科学上网代理；
#   2. TMDB 图片不走 localProxy；
#   3. TMDB 图片使用 image.tmdb.org 直链；
#
# 明确不处理：
#   1. 不改三级分类；
#   2. 不改二级分类图片传三级图片；
#   3. 不改播放；
#   4. 不改盘检；
#   5. 不改搜索分组。
# ============================================================

try:
    _PSTMDBNP_TARGET = PanSouSpider
except Exception:
    _PSTMDBNP_TARGET = globals().get("Spider")

if _PSTMDBNP_TARGET is None:
    print("[PANSOU TMDB NO PROXY FINAL] no target class, skip")
else:
    try:
        _PSTMDBNP_PREV_INIT = _PSTMDBNP_TARGET.init
    except Exception:
        _PSTMDBNP_PREV_INIT = None

    def _pstmdbnp_clear_proxy_attrs(self):
        """
        只清 TMDB 相关代理，不动 PanSou 搜索 server，不动网盘播放。
        """
        try:
            self.tmdb_proxy = ""
        except Exception:
            pass
        try:
            self.tmdb_api_proxy = ""
        except Exception:
            pass
        try:
            self.TMDB_PROXY = ""
        except Exception:
            pass
        try:
            self.site_proxy = ""
        except Exception:
            pass
        try:
            self.proxy_url = ""
        except Exception:
            pass

        # TMDB 图片强制直链，不走 localProxy
        try:
            self.tmdb_image_proxy = False
        except Exception:
            pass
        try:
            self.pstv7_tmdb_image_direct = True
        except Exception:
            pass
        try:
            self.pstv71_tmdb_image_direct = True
        except Exception:
            pass
        try:
            self.pstv71_tmdb_no_proxy = True
        except Exception:
            pass

    def _pstmdbnp_init(self, extend=""):
        ret = None
        if _PSTMDBNP_PREV_INIT:
            try:
                ret = _PSTMDBNP_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU TMDB NO PROXY FINAL] prev init error:", e)

        # 关键：上一层 init 可能又读 ext 写回 tmdb_proxy，所以这里最后清一次
        _pstmdbnp_clear_proxy_attrs(self)

        print("[PANSOU TMDB NO PROXY FINAL] enabled")
        print("[PANSOU TMDB NO PROXY FINAL] TMDB API proxy = disabled")
        print("[PANSOU TMDB NO PROXY FINAL] TMDB image proxy = disabled")
        print("[PANSOU TMDB NO PROXY FINAL] third category untouched")
        return ret if ret is not None else {}

    # ------------------------------------------------------------
    # 强制 TMDB API 不走代理
    # ------------------------------------------------------------
    def _pstmdb_proxies(self=None):
        """
        覆盖旧 V2 的 _pstmdb_proxies。
        返回空代理配置，避免 requests 走 http_proxy / https_proxy 环境变量。
        """
        return {
            "http": "",
            "https": "",
            "all": ""
        }

    def _pstv7_tmdb_proxy(self=None):
        """
        覆盖 V7 的 urllib 代理函数。
        """
        return ""

    def _pstv71_tmdb_proxy_empty(self=None):
        return ""

    # 兼容可能存在的其他 TMDB 代理函数名
    try:
        globals()["_pstmdb_proxies"] = _pstmdb_proxies
    except Exception:
        pass

    try:
        globals()["_pstv7_tmdb_proxy"] = _pstv7_tmdb_proxy
    except Exception:
        pass

    try:
        globals()["_pstv71_tmdb_proxy_empty"] = _pstv71_tmdb_proxy_empty
    except Exception:
        pass

    for _pstmdbnp_name in [
        "_pstmdb_proxy",
        "_pstmdb_tmdb_proxy",
        "_pstmdb_get_proxy",
        "_pstmdb_get_tmdb_proxy",
    ]:
        try:
            if _pstmdbnp_name in globals():
                globals()[_pstmdbnp_name] = _pstv71_tmdb_proxy_empty
        except Exception:
            pass

    # ------------------------------------------------------------
    # 强制 TMDB 图片直链，不走 localProxy
    # ------------------------------------------------------------
    def _pstmdbnp_img(self_or_path=None, path=None, backdrop=False):
        """
        兼容多种调用方式：

        旧 V2:
            _pstmdb_img(self, path, False)

        V7:
            _pstv7_tmdb_img(self, poster_path)

        其他可能:
            _pstmdb_img(path)

        返回：
            https://image.tmdb.org/t/p/w500/xxx.jpg
        """
        try:
            self = None

            # 情况 1：_pstmdb_img(path)
            if path is None:
                maybe_path = self_or_path
                if isinstance(maybe_path, str):
                    path = maybe_path
                else:
                    path = ""
                    self = maybe_path
            else:
                # 情况 2：_pstmdb_img(self, path)
                self = self_or_path

            path = str(path or "").strip()
            if not path:
                return ""

            if path.startswith("https://image.tmdb.org/"):
                return path

            if path.startswith("http://image.tmdb.org/"):
                return path.replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            # 如果是其他 http 图片，不强行改
            if path.startswith("http://") or path.startswith("https://"):
                return path

            # 取图片尺寸
            size = "w500"
            try:
                if self is not None:
                    size = (
                        getattr(self, "pstv71_tmdb_image_size", "")
                        or getattr(self, "pstv7_tmdb_image_size", "")
                        or "w500"
                    )
            except Exception:
                size = "w500"

            size = str(size or "w500").strip()
            if size not in ["w92", "w154", "w185", "w342", "w500", "w780", "original"]:
                size = "w500"

            return "https://image.tmdb.org/t/p/%s%s" % (size, path)
        except Exception as e:
            print("[PANSOU TMDB NO PROXY FINAL] image build error:", e)
            return ""

    def _pstmdbnp_to_img_proxy(self, raw_url):
        """
        覆盖 V2 的 _pstmdb_to_img_proxy。
        不再生成 localProxy 图片地址，直接返回原图。
        """
        try:
            return _pstmdbnp_img(self, raw_url)
        except Exception:
            return str(raw_url or "")

    def _pstmdbnp_deproxy_pic(pic):
        """
        如果旧逻辑已经把 TMDB 图包成 localProxy，这里尽量还原。
        """
        try:
            import urllib.parse as _pstmdbnp_parse
            import re as _pstmdbnp_re

            pic = str(pic or "").strip()
            if not pic:
                return ""

            if "image.tmdb.org" not in pic:
                return pic

            if pic.startswith("https://image.tmdb.org/"):
                return pic

            if pic.startswith("http://image.tmdb.org/"):
                return pic.replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            unq = _pstmdbnp_parse.unquote(pic)
            m = _pstmdbnp_re.search(r"https?://image\.tmdb\.org/[^\s&\"']+", unq)
            if m:
                return m.group(0).replace("http://image.tmdb.org/", "https://image.tmdb.org/")

            return pic
        except Exception:
            return pic

    def _pstmdbnp_fix_tmdb_pics_in_ret(ret):
        """
        只修返回结果里的 TMDB 图片链接。
        不改 vod_id，不改 vod_tag，不改三级分类。
        """
        try:
            if not isinstance(ret, dict):
                return ret
            lst = ret.get("list", [])
            if not isinstance(lst, list):
                return ret

            for v in lst:
                try:
                    if not isinstance(v, dict):
                        continue
                    pic = str(v.get("vod_pic") or "").strip()
                    if pic and "image.tmdb.org" in pic:
                        v["vod_pic"] = _pstmdbnp_deproxy_pic(pic)
                except Exception:
                    pass
            return ret
        except Exception:
            return ret

    # 覆盖常见图片函数名
    for _pstmdbnp_img_name in [
        "_pstmdb_img",
        "_pstmdb_raw_img",
        "_pstv7_tmdb_img",
        "_pstv71_tmdb_img",
        "_pstmdb_img_url",
        "_pstmdb_image_url",
        "_pstmdb_build_img",
        "_pstmdb_poster_url",
    ]:
        try:
            globals()[_pstmdbnp_img_name] = _pstmdbnp_img
        except Exception:
            pass

    try:
        globals()["_pstmdb_to_img_proxy"] = _pstmdbnp_to_img_proxy
    except Exception:
        pass

    # ------------------------------------------------------------
    # 只包装输出，修正已经生成的 TMDB 代理图。
    # 不改三级分类逻辑。
    # ------------------------------------------------------------
    try:
        _PSTMDBNP_PREV_HOME_VIDEO = _PSTMDBNP_TARGET.homeVideoContent
    except Exception:
        _PSTMDBNP_PREV_HOME_VIDEO = None

    try:
        _PSTMDBNP_PREV_CATEGORY = _PSTMDBNP_TARGET.categoryContent
    except Exception:
        _PSTMDBNP_PREV_CATEGORY = None

    def _pstmdbnp_homeVideoContent(self):
        try:
            if _PSTMDBNP_PREV_HOME_VIDEO:
                ret = _PSTMDBNP_PREV_HOME_VIDEO(self)
                return _pstmdbnp_fix_tmdb_pics_in_ret(ret)
        except Exception as e:
            print("[PANSOU TMDB NO PROXY FINAL] homeVideoContent error:", e)
            try:
                if _PSTMDBNP_PREV_HOME_VIDEO:
                    return _PSTMDBNP_PREV_HOME_VIDEO(self)
            except Exception:
                pass
        return {"list": []}

    def _pstmdbnp_categoryContent(self, tid, pg, filter, extend):
        """
        只做一件事：
        调用原 categoryContent 后，把其中可能存在的 TMDB 代理图还原直链。

        不改：
        - 三级分类生成；
        - 二级图传三级图；
        - vod_id；
        - vod_tag；
        - style；
        - 播放。
        """
        try:
            if _PSTMDBNP_PREV_CATEGORY:
                ret = _PSTMDBNP_PREV_CATEGORY(self, tid, pg, filter, extend)
            else:
                ret = {
                    "list": [],
                    "page": int(pg or 1),
                    "pagecount": 1,
                    "limit": 0,
                    "total": 0
                }
            return _pstmdbnp_fix_tmdb_pics_in_ret(ret)
        except Exception as e:
            print("[PANSOU TMDB NO PROXY FINAL] categoryContent error:", e)
            try:
                if _PSTMDBNP_PREV_CATEGORY:
                    return _PSTMDBNP_PREV_CATEGORY(self, tid, pg, filter, extend)
            except Exception:
                pass
            return {
                "list": [],
                "page": int(pg or 1),
                "pagecount": 1,
                "limit": 0,
                "total": 0
            }

    try:
        _PSTMDBNP_TARGET.init = _pstmdbnp_init
        if _PSTMDBNP_PREV_HOME_VIDEO:
            _PSTMDBNP_TARGET.homeVideoContent = _pstmdbnp_homeVideoContent
        if _PSTMDBNP_PREV_CATEGORY:
            _PSTMDBNP_TARGET.categoryContent = _pstmdbnp_categoryContent

        Spider = _PSTMDBNP_TARGET

        print("[PANSOU TMDB NO PROXY FINAL PATCH] loaded")
        print("[PANSOU TMDB NO PROXY FINAL PATCH] TMDB API no proxy")
        print("[PANSOU TMDB NO PROXY FINAL PATCH] TMDB image direct")
        print("[PANSOU TMDB NO PROXY FINAL PATCH] third inherited pic untouched")
    except Exception as e:
        print("[PANSOU TMDB NO PROXY FINAL PATCH] bind error:", e)

# ===== PANSOU_TMDB_NO_PROXY_FINAL_PATCH_END =====
# ===== PANSOU_SEARCH_AND_TMDB_IMAGE_LOGIC_SPLIT_FINAL_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou 搜索图片 / TMDB点击图片 逻辑分离最终补丁
#
# 目标：
#   1. 普通搜索结果的二级/三级图片，完全按参考代码：
#      - 二级：资源 images[0] 优先，没有则网盘图标；
#      - 三级：当前 item images[0] 优先，没有则同分类第一张图兜底；
#
#   2. 点击 TMDB 海报后的二级/三级图片，继续使用 TMDB 海报；
#
#   3. 不使用 last_vod_pic 来决定搜索路径三级图片；
#   4. 不改播放逻辑；
#   5. 不改盘检逻辑；
#   6. 不改 115/夸克/磁力原画逻辑。
# ============================================================

import json as _psimg_json

try:
    _PSIMG_TARGET = PanSouSpider
except Exception:
    _PSIMG_TARGET = globals().get("Spider")

if _PSIMG_TARGET is None:
    print("[PANSOU IMAGE SPLIT FINAL] no target class, skip")
else:
    try:
        _PSIMG_PREV_CATEGORY = _PSIMG_TARGET.categoryContent
    except Exception:
        _PSIMG_PREV_CATEGORY = None

    try:
        _PSIMG_PREV_DETAIL = _PSIMG_TARGET.detailContent
    except Exception:
        _PSIMG_PREV_DETAIL = None

    # ------------------------------------------------------------
    # 基础工具
    # ------------------------------------------------------------
    def _psimg_empty(page=1):
        try:
            page = int(page)
        except Exception:
            page = 1
        return {
            "list": [],
            "page": page,
            "pagecount": 1,
            "limit": 0,
            "total": 0
        }

    def _psimg_page(pg):
        try:
            p = int(pg)
        except Exception:
            p = 1
        if p < 1:
            p = 1
        return p

    def _psimg_to_bool(v, default=False):
        try:
            if isinstance(v, bool):
                return v
            if v is None:
                return default
            s = str(v).strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off", ""]:
                return False
            return bool(v)
        except Exception:
            return default

    def _psimg_parse_psq_id(vod_id):
        try:
            if "_psq_parse_id" in globals():
                return _psq_parse_id(vod_id)
        except Exception:
            pass
        return "", {}

    def _psimg_make_psq_id(vtype, data):
        try:
            if "_psq_make_id" in globals():
                return _psq_make_id(vtype, data)
        except Exception:
            pass
        return ""

    def _psimg_parse_pstmdb_id(vod_id):
        try:
            if "_pstmdb_parse_id" in globals():
                return _pstmdb_parse_id(vod_id)
        except Exception:
            pass
        return "", {}

    def _psimg_group_key(api_type):
        try:
            if "_psq_group_key" in globals():
                return _psq_group_key(api_type)
        except Exception:
            pass

        api_type = str(api_type or "").strip().lower()
        if api_type in ["115", "a115"]:
            return "115"
        if api_type in ["ali", "aliyun", "alipan"]:
            return "aliyun"
        if api_type in ["123", "a123", "123pan"]:
            return "123"
        if api_type in ["tianyi", "189"]:
            return "tianyi"
        if api_type in ["mobile", "139"]:
            return "mobile"
        if api_type in [
            "quark", "magnet", "baidu", "uc", "xunlei",
            "pikpak", "ed2k", "other"
        ]:
            return api_type
        return "other"

    def _psimg_group_name(gkey):
        try:
            return globals().get("_PSQ_GROUP_NAME", {}).get(gkey, gkey)
        except Exception:
            return gkey

    def _psimg_group_order():
        try:
            arr = globals().get("_PSQ_GROUP_ORDER", [])
            if arr:
                return arr
        except Exception:
            pass
        return [
            "quark", "115", "magnet", "baidu", "uc", "aliyun",
            "xunlei", "123", "mobile", "tianyi", "pikpak", "ed2k", "other"
        ]

    def _psimg_icon_for_group(self, group):
        """
        普通搜索路径二级无图时，按参考代码补网盘图标。
        """
        try:
            group = _psimg_group_key(group)
            mapping = {
                "quark": "quark",
                "115": "a115",
                "aliyun": "ali",
                "baidu": "baidu",
                "uc": "uc",
                "tianyi": "tianyi",
                "mobile": "mobile",
                "xunlei": "xunlei",
                "123": "a123",
                "pikpak": "pikpak",
                "magnet": "magnet",
                "ed2k": "ed2k",
            }
            pan_type = mapping.get(group, group)
            icon = ""
            try:
                icon = getattr(self, "PAN_CONFIG", {}).get(pan_type, {}).get("icon", "") or ""
            except Exception:
                icon = ""

            if not icon:
                fallback = {
                    "quark": "quark.png",
                    "115": "115.png",
                    "aliyun": "ali.png",
                    "baidu": "baidu.png",
                    "uc": "uc.png",
                    "tianyi": "189.png",
                    "mobile": "139.png",
                    "xunlei": "xunlei.png",
                    "123": "123.png",
                    "pikpak": "pikpak.png",
                    "magnet": "cili.png",
                    "ed2k": ""
                }
                icon = fallback.get(group, "")

            if not icon:
                return ""

            try:
                return self._get_icon_url(icon)
            except Exception:
                return "http://127.0.0.1:9978/file/Download/lib/icon/%s" % icon
        except Exception:
            return ""

    def _psimg_get_group_cover_from_items(self, arr, group=""):
        """
        普通搜索路径二级分类封面：
        参考代码逻辑：
            1. 当前分类内第一张 images[0]
            2. 网盘图标
        """
        try:
            for x in arr or []:
                imgs = x.get("images") or []
                if imgs:
                    return imgs[0]
        except Exception:
            pass
        return _psimg_icon_for_group(self, group)

    def _psimg_apply_list_style(ret):
        """
        只给三级列表加列表样式提示，不改 vod_id。
        """
        try:
            if not isinstance(ret, dict):
                return ret
            ret["style"] = {"type": "list"}
            ret["list_style"] = "list"
            ret["vod_style"] = "list"
            ret["view_type"] = "list"
            ret["layout"] = "list"
            lst = ret.get("list", [])
            if isinstance(lst, list):
                for v in lst:
                    try:
                        if not isinstance(v, dict):
                            continue
                        v["vod_tag"] = "file"
                        v["tag"] = "file"
                        v["style"] = {"type": "list"}
                        v["view_type"] = "list"
                    except Exception:
                        pass
            return ret
        except Exception:
            return ret

    # ------------------------------------------------------------
    # 普通搜索：二级分类图片按参考代码
    # ------------------------------------------------------------
    def _psimg_build_search_second(self, keyword, pg=1):
        page = _psimg_page(pg)
        if page > 1:
            return _psimg_empty(page)

        keyword = str(keyword or "").strip()
        if not keyword:
            return _psimg_empty(page)

        try:
            items = _psq_fetch_search_items(self, keyword)
            groups = _psq_group_items(items)
        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] fetch/group search error:", e)
            return _psimg_empty(page)

        videos = []
        order = _psimg_group_order()

        for gkey in order:
            arr = groups.get(gkey) or []
            if not arr:
                continue

            # 关键：普通搜索路径按参考代码取图
            cover = _psimg_get_group_cover_from_items(self, arr, gkey)

            vod_id = _psimg_make_psq_id("group", {
                "kw": keyword,
                "group": gkey,
                "source": "search"
            })

            videos.append({
                "vod_id": vod_id,
                "vod_name": _psimg_group_name(gkey),
                "vod_pic": cover,
                "vod_remarks": "%s条资源" % len(arr),
                "vod_content": "搜索词：%s\n资源类型：%s\n点击进入具体资源列表。" % (
                    keyword,
                    _psimg_group_name(gkey)
                ),
                "vod_tag": "folder",
                "tag": "folder"
            })

        for gkey, arr in groups.items():
            if gkey in order:
                continue
            if not arr:
                continue

            cover = _psimg_get_group_cover_from_items(self, arr, gkey)

            vod_id = _psimg_make_psq_id("group", {
                "kw": keyword,
                "group": gkey,
                "source": "search"
            })

            videos.append({
                "vod_id": vod_id,
                "vod_name": "📦 %s" % gkey,
                "vod_pic": cover,
                "vod_remarks": "%s条资源" % len(arr),
                "vod_content": "搜索词：%s\n资源类型：%s" % (keyword, gkey),
                "vod_tag": "folder",
                "tag": "folder"
            })

        return {
            "list": videos,
            "page": 1,
            "pagecount": 1,
            "limit": len(videos),
            "total": len(videos)
        }

    def _psimg_searchContent(self, key, quick=False, pg="1"):
        try:
            page = _psimg_page(pg)

            # 保留原来 quickSearch 返回空的习惯，避免重复。
            if _psimg_to_bool(quick, False) and getattr(self, "psq_quick_empty", True):
                return _psimg_empty(page)

            return _psimg_build_search_second(self, key, page)
        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] searchContent error:", e)
            return _psimg_empty(pg)

    def _psimg_searchContentPage(self, key, quick, page):
        return _psimg_searchContent(self, key, quick, page)

    # ------------------------------------------------------------
    # TMDB海报点击：二级分类继续使用 TMDB 图
    # ------------------------------------------------------------
    def _psimg_keyword_from_tmdb_data(self, data):
        try:
            if "_pstmdb_keyword_from_data" in globals():
                return _pstmdb_keyword_from_data(self, data)
        except Exception:
            pass

        title = str((data or {}).get("kw") or (data or {}).get("title") or "").strip()
        year = str((data or {}).get("year") or "").strip()
        try:
            if getattr(self, "tmdb_click_year_keyword", False) and year and year not in title:
                return ("%s %s" % (title, year)).strip()
        except Exception:
            pass
        return title

    def _psimg_build_tmdb_second(self, data, pg=1):
        """
        TMDB海报 -> PanSou二级分类。
        二级分类封面强制 TMDB pic。
        """
        page = _psimg_page(pg)
        if page > 1:
            return _psimg_empty(page)

        data = data or {}
        keyword = _psimg_keyword_from_tmdb_data(self, data)
        title = str(data.get("title") or keyword).strip()
        tmdb_pic = str(
            data.get("pic")
            or data.get("vod_pic")
            or data.get("poster")
            or data.get("cover")
            or ""
        ).strip()

        if not keyword:
            return _psimg_empty(page)

        try:
            if tmdb_pic:
                if not hasattr(self, "_pstmdb_kw_pic"):
                    self._pstmdb_kw_pic = {}
                self._pstmdb_kw_pic[keyword] = tmdb_pic
                if title:
                    self._pstmdb_kw_pic[title] = tmdb_pic
        except Exception:
            pass

        try:
            items = _psq_fetch_search_items(self, keyword)
            groups = _psq_group_items(items)
        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] tmdb second fetch error:", e)
            return _psimg_empty(page)

        videos = []
        order = _psimg_group_order()

        for gkey in order:
            arr = groups.get(gkey) or []
            if not arr:
                continue

            vod_id = _psimg_make_psq_id("group", {
                "kw": keyword,
                "group": gkey,
                "source": "tmdb",
                "pic": tmdb_pic,
                "tmdb_title": title
            })

            videos.append({
                "vod_id": vod_id,
                "vod_name": _psimg_group_name(gkey),
                "vod_pic": tmdb_pic,
                "vod_remarks": "%s条资源" % len(arr),
                "vod_content": "TMDB：%s\n盘搜词：%s\n资源类型：%s\n点击进入具体资源列表。" % (
                    title or keyword,
                    keyword,
                    _psimg_group_name(gkey)
                ),
                "vod_tag": "folder",
                "tag": "folder"
            })

        for gkey, arr in groups.items():
            if gkey in order:
                continue
            if not arr:
                continue

            vod_id = _psimg_make_psq_id("group", {
                "kw": keyword,
                "group": gkey,
                "source": "tmdb",
                "pic": tmdb_pic,
                "tmdb_title": title
            })

            videos.append({
                "vod_id": vod_id,
                "vod_name": "📦 %s" % gkey,
                "vod_pic": tmdb_pic,
                "vod_remarks": "%s条资源" % len(arr),
                "vod_content": "TMDB：%s\n盘搜词：%s\n资源类型：%s" % (
                    title or keyword,
                    keyword,
                    gkey
                ),
                "vod_tag": "folder",
                "tag": "folder"
            })

        if not videos:
            videos.append({
                "vod_id": "pstmdb_empty",
                "vod_name": "盘搜无结果：" + keyword,
                "vod_pic": tmdb_pic,
                "vod_remarks": "空",
                "vod_content": "TMDB 标题已搜索，但 PanSou 暂无结果。"
            })

        return {
            "list": videos,
            "page": 1,
            "pagecount": 1,
            "limit": len(videos),
            "total": len(videos)
        }

    # 覆盖 TMDB 二级构造函数，让后续 detail/category 都走这里。
    try:
        globals()["_pstmdb_build_pansou_second"] = _psimg_build_tmdb_second
    except Exception:
        pass

    # ------------------------------------------------------------
    # 选择真正的三级基础构造函数
    # ------------------------------------------------------------
    def _psimg_pick_base_third():
        """
        优先选择带盘检、排序、密码逻辑的三级构造。
        避开后面 TMDB V6/V6.5 的图片继承 wrapper。
        """
        names = [
            "_psqcc_build_third_category",        # 点击夸克/115检测版
            "_PSTMDB_PREV_THIRD_BUILDER",        # TMDB V2保存的旧三级
            "_PSTV3_BASE_THIRD",
            "_PSTV4_BASE_THIRD",
            "_PSTV6_BASE_THIRD",
        ]

        for name in names:
            try:
                fn = globals().get(name)
                if not fn:
                    continue
                nm = getattr(fn, "__name__", "")
                if nm.startswith("_pstv"):
                    continue
                if nm.startswith("_pstmdb"):
                    continue
                if nm.startswith("_psimg"):
                    continue
                return fn
            except Exception:
                pass

        # 兜底：当前全局 _psq_build_third_category
        try:
            fn = globals().get("_psq_build_third_category")
            if fn:
                nm = getattr(fn, "__name__", "")
                if not nm.startswith("_psimg"):
                    return fn
        except Exception:
            pass

        return None

    _PSIMG_BASE_THIRD = _psimg_pick_base_third()

    def _psimg_fix_third_pics_by_reference(self, ret, data):
        """
        普通搜索路径三级图片：
        按参考代码重新计算：
            cover_fallback = 当前分类第一张 images[0]
            item_pic = item.images[0] or cover_fallback
        这里通过 vod_id 解出的资源 payload 里已经保存 pic，
        如果基础三级构造就是参考代码，则无需大改。
        但为了防止前面 TMDB wrapper 污染，这里重新按搜索结果 item 修正一次。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            keyword = str((data or {}).get("kw") or "").strip()
            group = str((data or {}).get("group") or "").strip()
            if group in ["a115"]:
                group = "115"

            if not keyword or not group:
                return _psimg_apply_list_style(ret)

            items = _psq_fetch_search_items(self, keyword)
            groups = _psq_group_items(items)
            current = groups.get(group) or []

            try:
                current = _psq_sort_items(current)
            except Exception:
                pass

            # 如果当前是 quark/115 并开启检测，基础构造可能隐藏/排序了 bad。
            # 这里不重新生成列表，只根据 URL 建立图片映射，避免影响盘检结果。
            cover_fallback = ""
            for x in current:
                imgs = x.get("images") or []
                if imgs:
                    cover_fallback = imgs[0]
                    break

            pic_by_url = {}
            for item in current:
                try:
                    url = str(item.get("normalized_url") or item.get("url") or "").strip()
                    raw_url = str(item.get("url") or "").strip()
                    imgs = item.get("images") or []
                    pic = imgs[0] if imgs else cover_fallback
                    if raw_url:
                        pic_by_url[raw_url] = pic
                    if url:
                        pic_by_url[url] = pic
                except Exception:
                    pass

            lst = ret.get("list", [])
            if isinstance(lst, list):
                for v in lst:
                    try:
                        if not isinstance(v, dict):
                            continue

                        vid = str(v.get("vod_id") or "")
                        if vid == "empty":
                            v["vod_pic"] = cover_fallback
                            continue

                        # 从 psq|panplay/magnetplay/ed2kplay payload 里拿 url
                        typ, payload = _psimg_parse_psq_id(vid)
                        url = ""
                        if isinstance(payload, dict):
                            url = str(payload.get("url") or "").strip()

                        if url and url in pic_by_url:
                            v["vod_pic"] = pic_by_url.get(url) or ""
                        else:
                            # 如果基础构造已经给了正常资源图，保留；
                            # 如果没有图，用当前分类 fallback。
                            if not v.get("vod_pic"):
                                v["vod_pic"] = cover_fallback
                    except Exception:
                        pass

            return _psimg_apply_list_style(ret)
        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] fix third reference pics error:", e)
            return _psimg_apply_list_style(ret)

    def _psimg_fix_third_pics_by_tmdb(self, ret, tmdb_pic):
        """
        TMDB点击路径三级图片：
        统一使用 TMDB 海报。
        """
        try:
            if not isinstance(ret, dict):
                return ret

            tmdb_pic = str(tmdb_pic or "").strip()
            ret = _psimg_apply_list_style(ret)

            if not tmdb_pic:
                return ret

            lst = ret.get("list", [])
            if isinstance(lst, list):
                for v in lst:
                    try:
                        if not isinstance(v, dict):
                            continue
                        v["vod_pic"] = tmdb_pic
                    except Exception:
                        pass

            return ret
        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] fix third tmdb pics error:", e)
            return ret

    def _psimg_build_third_category(self, data, pg=1):
        """
        三级入口统一在这里拆分图片逻辑：
            source == tmdb   -> 三级用 TMDB 海报
            其他 / search    -> 三级按参考代码资源 images 逻辑
        """
        try:
            data = data or {}
            source = str(data.get("source") or "").strip().lower()
            tmdb_pic = str(data.get("pic") or "").strip()

            if _PSIMG_BASE_THIRD:
                ret = _PSIMG_BASE_THIRD(self, data, pg)
            else:
                ret = _psimg_empty(pg)

            if source == "tmdb":
                return _psimg_fix_third_pics_by_tmdb(self, ret, tmdb_pic)

            return _psimg_fix_third_pics_by_reference(self, ret, data)

        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] build third error:", e)
            try:
                if _PSIMG_BASE_THIRD:
                    return _PSIMG_BASE_THIRD(self, data, pg)
            except Exception:
                pass
            return _psimg_empty(pg)

    # 覆盖全局三级构造，防止旧 TMDB V6/V6.5 wrapper 继续污染图片。
    try:
        globals()["_psq_build_third_category"] = _psimg_build_third_category
    except Exception:
        pass

    # ------------------------------------------------------------
    # categoryContent 最终接管：
    #   1. psq|group|xxx 直接进我们的三级；
    #   2. pstmdb|search|xxx 直接进我们的 TMDB 二级；
    #   3. 其他 TMDB 分类 / 筛选交回旧逻辑。
    # ------------------------------------------------------------
    def _psimg_categoryContent(self, tid, pg, filter, extend):
        try:
            tid_s = str(tid or "")

            # PanSou 二级分类 -> 三级资源
            if tid_s.startswith("psq|"):
                vtype, data = _psimg_parse_psq_id(tid_s)
                if vtype == "group":
                    return _psimg_build_third_category(self, data, pg)

            # TMDB 海报点击 -> PanSou 二级分类
            if tid_s.startswith("pstmdb|"):
                vtype, data = _psimg_parse_pstmdb_id(tid_s)
                if vtype == "search":
                    return _psimg_build_tmdb_second(self, data, pg)

            # 其他分类，比如 TMDB 热门/筛选，交回旧逻辑。
            if _PSIMG_PREV_CATEGORY:
                return _PSIMG_PREV_CATEGORY(self, tid, pg, filter, extend)

        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] categoryContent error:", e)
            try:
                if _PSIMG_PREV_CATEGORY:
                    return _PSIMG_PREV_CATEGORY(self, tid, pg, filter, extend)
            except Exception:
                pass

        return _psimg_empty(pg)

    # ------------------------------------------------------------
    # detailContent 兼容：
    # 有些壳点击 TMDB 海报会走 detailContent。
    # ------------------------------------------------------------
    def _psimg_detailContent(self, ids):
        try:
            vod_id = ids[0] if isinstance(ids, list) and ids else ids
            vod_id_s = str(vod_id or "")

            if vod_id_s.startswith("pstmdb|"):
                vtype, data = _psimg_parse_pstmdb_id(vod_id_s)
                if vtype == "search":
                    return _psimg_build_tmdb_second(self, data, 1)

            if _PSIMG_PREV_DETAIL:
                return _PSIMG_PREV_DETAIL(self, ids)

        except Exception as e:
            print("[PANSOU IMAGE SPLIT FINAL] detailContent error:", e)
            try:
                if _PSIMG_PREV_DETAIL:
                    return _PSIMG_PREV_DETAIL(self, ids)
            except Exception:
                pass

        return {"list": []}

    # ------------------------------------------------------------
    # 绑定
    # ------------------------------------------------------------
    try:
        _PSIMG_TARGET.searchContent = _psimg_searchContent
        _PSIMG_TARGET.searchContentPage = _psimg_searchContentPage
        _PSIMG_TARGET.categoryContent = _psimg_categoryContent
        _PSIMG_TARGET.detailContent = _psimg_detailContent

        Spider = _PSIMG_TARGET

        print("[PANSOU SEARCH AND TMDB IMAGE LOGIC SPLIT FINAL] loaded")
        try:
            print("[PANSOU IMAGE SPLIT FINAL] base third =", getattr(_PSIMG_BASE_THIRD, "__name__", str(_PSIMG_BASE_THIRD)))
        except Exception:
            pass
        print("[PANSOU IMAGE SPLIT FINAL] 普通搜索二级/三级按资源 images 逻辑")
        print("[PANSOU IMAGE SPLIT FINAL] TMDB海报点击二级/三级按 TMDB 图逻辑")
    except Exception as e:
        print("[PANSOU IMAGE SPLIT FINAL] bind error:", e)

# ===== PANSOU_SEARCH_AND_TMDB_IMAGE_LOGIC_SPLIT_FINAL_END =====
# ===== PANSOU_TMDB_BUILTIN_PROXY_10172_FINAL_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou TMDB 内置代理最终补丁
#
# 作用：
#   1. 仅 TMDB API 走 http://127.0.0.1:10172
#   2. 仅 TMDB 图片走 http://127.0.0.1:10172
#   3. 不影响 PanSou 搜索、盘检、115、夸克、磁力、OpenList、播放等
#
# 注意：
#   请追加在所有 TMDB 补丁之后，尤其要放在：
#   PANSOU_TMDB_NO_PROXY_FINAL_PATCH
#   PANSOU_SEARCH_AND_TMDB_IMAGE_LOGIC_SPLIT_FINAL
#   之后。
#
# ext 可选：
# {
#   "tmdb_api_key": "你的TMDB_KEY",
#   "tmdb_builtin_proxy": "http://127.0.0.1:10172",
#   "tmdb_image_proxy": true
# }
#
# 不要用全局 "proxy"，否则 PanSou 搜索也会走代理。
# ============================================================

import json as _tmdbbp_json
import base64 as _tmdbbp_base64
import requests as _tmdbbp_requests
from urllib.parse import quote as _tmdbbp_quote
from urllib.parse import unquote as _tmdbbp_unquote

try:
    _TMDBBP_TARGET = PanSouSpider
except Exception:
    _TMDBBP_TARGET = globals().get("Spider")

if _TMDBBP_TARGET is None:
    print("[PANSOU TMDB BUILTIN PROXY 10172] no target class, skip")
else:
    try:
        _TMDBBP_PREV_INIT = _TMDBBP_TARGET.init
    except Exception:
        _TMDBBP_PREV_INIT = None

    try:
        _TMDBBP_PREV_LOCAL_PROXY = _TMDBBP_TARGET.localProxy
    except Exception:
        _TMDBBP_PREV_LOCAL_PROXY = None

    # ------------------------------------------------------------
    # ext / bool
    # ------------------------------------------------------------
    def _tmdbbp_parse_ext(extend):
        try:
            if not extend:
                return {}
            if isinstance(extend, dict):
                return extend
            if isinstance(extend, str) and extend.strip().startswith("{"):
                return _tmdbbp_json.loads(extend)
            return {}
        except Exception:
            return {}

    def _tmdbbp_bool(v, default=True):
        try:
            if isinstance(v, bool):
                return v
            if v is None:
                return default
            s = str(v).strip().lower()
            if s in ["1", "true", "yes", "y", "on"]:
                return True
            if s in ["0", "false", "no", "n", "off", ""]:
                return False
            return default
        except Exception:
            return default

    # ------------------------------------------------------------
    # init：最后重新写回 TMDB 专用代理
    # ------------------------------------------------------------
    def _tmdbbp_init(self, extend=""):
        ret = None
        if _TMDBBP_PREV_INIT:
            try:
                ret = _TMDBBP_PREV_INIT(self, extend)
            except Exception as e:
                print("[PANSOU TMDB BUILTIN PROXY 10172] prev init error:", e)

        ext = _tmdbbp_parse_ext(extend)

        # 只给 TMDB 用的内置代理端口
        self.tmdb_builtin_proxy = str(
            ext.get(
                "tmdb_builtin_proxy",
                ext.get(
                    "tmdb_10172_proxy",
                    getattr(self, "tmdb_builtin_proxy", "http://127.0.0.1:10172")
                )
            ) or "http://127.0.0.1:10172"
        ).strip()

        # 兼容旧 TMDB 补丁使用的 tmdb_proxy 变量
        # 注意：只改 tmdb_proxy，不改 self.proxy / self.session.proxies
        self.tmdb_proxy = self.tmdb_builtin_proxy

        # TMDB 图片必须走 localProxy，然后 localProxy 内部再走 10172
        self.tmdb_image_proxy = _tmdbbp_bool(
            ext.get(
                "tmdb_image_proxy",
                getattr(self, "tmdb_image_proxy", True)
            ),
            True
        )

        # 覆盖前面 no proxy 补丁留下的开关
        try:
            self.pstv7_tmdb_image_direct = False
        except Exception:
            pass
        try:
            self.pstv71_tmdb_image_direct = False
        except Exception:
            pass
        try:
            self.pstv71_tmdb_no_proxy = False
        except Exception:
            pass

        print("[PANSOU TMDB BUILTIN PROXY 10172] enabled")
        print("[PANSOU TMDB BUILTIN PROXY 10172] TMDB API proxy =", self.tmdb_builtin_proxy)
        print("[PANSOU TMDB BUILTIN PROXY 10172] TMDB image localProxy =", self.tmdb_image_proxy)
        print("[PANSOU TMDB BUILTIN PROXY 10172] only TMDB uses proxy, PanSou/search/play untouched")

        return ret if ret is not None else {}

    # ------------------------------------------------------------
    # TMDB 专用 proxies
    # ------------------------------------------------------------
    def _tmdbbp_proxy_url(self=None):
        try:
            p = str(getattr(self, "tmdb_builtin_proxy", "") or "").strip()
            if p:
                return p
        except Exception:
            pass
        return "http://127.0.0.1:10172"

    def _tmdbbp_requests_proxies(self=None):
        """
        给 requests 用。
        只会被 TMDB 请求函数调用。
        """
        p = _tmdbbp_proxy_url(self)
        if not p:
            return None
        return {
            "http": p,
            "https": p
        }

    # 覆盖 V2 TMDB requests 代理函数
    def _pstmdb_proxies(self=None):
        return _tmdbbp_requests_proxies(self)

    # 覆盖 V7 urllib 代理函数
    def _pstv7_tmdb_proxy(self=None):
        return _tmdbbp_proxy_url(self)

    # 覆盖 V7.1 代理函数
    def _pstv71_tmdb_proxy_empty(self=None):
        return _tmdbbp_proxy_url(self)

    # 其他可能存在的代理函数名也覆盖
    try:
        globals()["_pstmdb_proxies"] = _pstmdb_proxies
        globals()["_pstv7_tmdb_proxy"] = _pstv7_tmdb_proxy
        globals()["_pstv71_tmdb_proxy_empty"] = _pstv71_tmdb_proxy_empty
    except Exception:
        pass

    for _tmdbbp_proxy_name in [
        "_pstmdb_proxy",
        "_pstmdb_tmdb_proxy",
        "_pstmdb_get_proxy",
        "_pstmdb_get_tmdb_proxy",
    ]:
        try:
            globals()[_tmdbbp_proxy_name] = _pstv7_tmdb_proxy
        except Exception:
            pass

    # ------------------------------------------------------------
    # 图片 URL 构造
    # ------------------------------------------------------------
    def _tmdbbp_raw_img(self, path, backdrop=False):
        """
        生成 TMDB 原始图片地址。
        """
        try:
            path = str(path or "").strip()
            if not path:
                return ""
            if path.startswith("https://image.tmdb.org/"):
                return path
            if path.startswith("http://image.tmdb.org/"):
                return path.replace("http://image.tmdb.org/", "https://image.tmdb.org/")
            if path.startswith(("http://", "https://")):
                return path

            # 优先读取原配置
            if backdrop:
                base = str(
                    getattr(self, "tmdb_backdrop_base", "https://image.tmdb.org/t/p/w780")
                    or "https://image.tmdb.org/t/p/w780"
                ).rstrip("/")
            else:
                size = (
                    getattr(self, "pstv71_tmdb_image_size", "")
                    or getattr(self, "pstv7_tmdb_image_size", "")
                    or ""
                )
                size = str(size or "").strip()
                if size in ["w92", "w154", "w185", "w342", "w500", "w780", "original"]:
                    base = "https://image.tmdb.org/t/p/%s" % size
                else:
                    base = str(
                        getattr(self, "tmdb_image_base", "https://image.tmdb.org/t/p/w500")
                        or "https://image.tmdb.org/t/p/w500"
                    ).rstrip("/")

            return base + path
        except Exception:
            return ""

    def _tmdbbp_b64e_text(text):
        try:
            return _tmdbbp_base64.urlsafe_b64encode(
                str(text or "").encode("utf-8")
            ).decode("utf-8").rstrip("=")
        except Exception:
            return ""

    def _tmdbbp_b64d_text(text):
        try:
            text = str(text or "")
            text += "=" * (-len(text) % 4)
            return _tmdbbp_base64.urlsafe_b64decode(
                text.encode("utf-8")
            ).decode("utf-8")
        except Exception:
            return ""

    def _tmdbbp_get_proxy_url(self):
        """
        获取 Spider localProxy 地址。
        OK/PG/FongMi 通常都有 getProxyUrl()。
        """
        try:
            if hasattr(self, "getProxyUrl"):
                u = self.getProxyUrl()
                if u:
                    return str(u)
        except Exception:
            pass
        return ""

    def _tmdbbp_to_local_proxy(self, raw_url):
        """
        把 TMDB 图片变成 Spider localProxy 地址。
        这里用 b64 参数，不用 url=，避免前面的 no-proxy 补丁从 URL 中识别
        image.tmdb.org 后又还原成直链。
        """
        try:
            raw_url = str(raw_url or "").strip()
            if not raw_url:
                return ""

            # 如果关闭图片代理，则返回原图。
            if not getattr(self, "tmdb_image_proxy", True):
                return raw_url

            proxy_url = _tmdbbp_get_proxy_url(self)
            if not proxy_url:
                print("[PANSOU TMDB BUILTIN PROXY 10172] getProxyUrl empty, image fallback direct")
                return raw_url

            sep = "&" if "?" in proxy_url else "?"
            return proxy_url + sep + "type=tmdb_img&b64=" + _tmdbbp_b64e_text(raw_url)
        except Exception:
            return str(raw_url or "")

    def _tmdbbp_img(self_or_path=None, path=None, backdrop=False):
        """
        兼容多种调用方式：

        _pstmdb_img(self, path, False)
        _pstv7_tmdb_img(self, poster_path)
        _pstmdb_img(path)
        """
        try:
            self = None

            # _pstmdb_img(path)
            if path is None:
                if isinstance(self_or_path, str):
                    raw_path = self_or_path
                else:
                    self = self_or_path
                    raw_path = ""
            else:
                self = self_or_path
                raw_path = path

            if self is None:
                # 没 self 时只能返回 TMDB 直链，无法拼 localProxy
                raw_path = str(raw_path or "").strip()
                if not raw_path:
                    return ""
                if raw_path.startswith(("http://", "https://")):
                    return raw_path
                return "https://image.tmdb.org/t/p/w500" + raw_path

            raw = _tmdbbp_raw_img(self, raw_path, backdrop)
            return _tmdbbp_to_local_proxy(self, raw)
        except Exception as e:
            print("[PANSOU TMDB BUILTIN PROXY 10172] image helper error:", e)
            return ""

    def _tmdbbp_to_img_proxy(self, raw_url):
        """
        覆盖 V2 的 _pstmdb_to_img_proxy。
        """
        try:
            raw_url = str(raw_url or "").strip()
            if not raw_url:
                return ""
            return _tmdbbp_to_local_proxy(self, raw_url)
        except Exception:
            return str(raw_url or "")

    # 覆盖所有常见 TMDB 图片函数
    for _tmdbbp_img_name in [
        "_pstmdb_img",
        "_pstmdb_raw_img",
        "_pstv7_tmdb_img",
        "_pstv71_tmdb_img",
        "_pstmdb_img_url",
        "_pstmdb_image_url",
        "_pstmdb_build_img",
        "_pstmdb_poster_url",
    ]:
        try:
            globals()[_tmdbbp_img_name] = _tmdbbp_img
        except Exception:
            pass

    try:
        globals()["_pstmdb_to_img_proxy"] = _tmdbbp_to_img_proxy
    except Exception:
        pass

    # ------------------------------------------------------------
    # localProxy：真正下载 TMDB 图片时走 10172
    # ------------------------------------------------------------
    def _tmdbbp_guess_ctype(url, content=None, rsp=None):
        try:
            if rsp is not None:
                ctype = rsp.headers.get("Content-Type") or ""
                if ctype:
                    return ctype
            if content:
                if content[:3] == b"\xff\xd8\xff":
                    return "image/jpeg"
                if content[:8] == b"\x89PNG\r\n\x1a\n":
                    return "image/png"
                if content[:4] == b"RIFF" and b"WEBP" in content[:20]:
                    return "image/webp"
                if content[:6] in [b"GIF87a", b"GIF89a"]:
                    return "image/gif"
            low = str(url or "").lower()
            if ".png" in low:
                return "image/png"
            if ".webp" in low:
                return "image/webp"
            if ".gif" in low:
                return "image/gif"
            if ".avif" in low:
                return "image/avif"
            return "image/jpeg"
        except Exception:
            return "application/octet-stream"

    def _tmdbbp_get_param(param, key):
        try:
            if not isinstance(param, dict):
                return ""
            v = param.get(key, "")
            if isinstance(v, list):
                return v[0] if v else ""
            return v
        except Exception:
            return ""

    def _tmdbbp_localProxy(self, param):
        """
        只接管 type=tmdb_img。
        其他 localProxy 请求全部交给上一层。
        """
        try:
            ptype = str(_tmdbbp_get_param(param, "type") or "").strip()
            if ptype != "tmdb_img":
                if _TMDBBP_PREV_LOCAL_PROXY:
                    return _TMDBBP_PREV_LOCAL_PROXY(self, param)
                return None

            raw_url = ""

            # 优先 b64
            b64 = str(_tmdbbp_get_param(param, "b64") or "").strip()
            if b64:
                raw_url = _tmdbbp_b64d_text(b64)

            # 兼容旧 url=
            if not raw_url:
                raw_url = str(_tmdbbp_get_param(param, "url") or "").strip()
                raw_url = _tmdbbp_unquote(raw_url)

            raw_url = str(raw_url or "").strip()
            if not raw_url:
                return [404, "text/plain", "No Url"]

            if not raw_url.startswith(("http://", "https://")):
                return [404, "text/plain", "Bad Url"]

            # 安全限制：只代理 TMDB 图片
            if "image.tmdb.org" not in raw_url:
                return [403, "text/plain", "Forbidden"]

            headers = {
                "User-Agent": getattr(self, "HEADERS", {}).get("User-Agent", "Mozilla/5.0"),
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://www.themoviedb.org/"
            }

            rsp = _tmdbbp_requests.get(
                raw_url,
                headers=headers,
                timeout=30,
                allow_redirects=True,
                proxies=_tmdbbp_requests_proxies(self),
                verify=False
            )

            content = rsp.content or b""

            print("[PANSOU TMDB BUILTIN PROXY 10172 IMG] status=%s len=%s proxy=%s url=%s" % (
                rsp.status_code,
                len(content),
                _tmdbbp_proxy_url(self),
                raw_url
            ))

            if rsp.status_code != 200 or not content:
                return [404, "text/plain", "Proxy Image Failed"]

            return [200, _tmdbbp_guess_ctype(raw_url, content, rsp), content]

        except Exception as e:
            print("[PANSOU TMDB BUILTIN PROXY 10172 IMG] error:", e)
            return [404, "text/plain", "Proxy Error"]

    # ------------------------------------------------------------
    # 防止前面的 no-proxy 输出修正把 localProxy 图又还原成直链
    # ------------------------------------------------------------
    def _tmdbbp_fix_ret_keep_proxy(ret):
        """
        这里只做保护，不把 localProxy 还原成直链。
        """
        return ret

    try:
        globals()["_pstmdbnp_fix_tmdb_pics_in_ret"] = _tmdbbp_fix_ret_keep_proxy
    except Exception:
        pass
    try:
        globals()["_pstv71_fix_ret_pics"] = _tmdbbp_fix_ret_keep_proxy
    except Exception:
        pass
    try:
        globals()["_pstv7_fix_tmdb_pics_in_ret"] = _tmdbbp_fix_ret_keep_proxy
    except Exception:
        pass

    # ------------------------------------------------------------
    # 绑定
    # ------------------------------------------------------------
    try:
        _TMDBBP_TARGET.init = _tmdbbp_init
        _TMDBBP_TARGET.localProxy = _tmdbbp_localProxy

        Spider = _TMDBBP_TARGET

        print("[PANSOU TMDB BUILTIN PROXY 10172 FINAL] loaded")
        print("[PANSOU TMDB BUILTIN PROXY 10172 FINAL] TMDB API -> http://127.0.0.1:10172")
        print("[PANSOU TMDB BUILTIN PROXY 10172 FINAL] TMDB IMG -> localProxy -> http://127.0.0.1:10172")
        print("[PANSOU TMDB BUILTIN PROXY 10172 FINAL] other requests untouched")
    except Exception as e:
        print("[PANSOU TMDB BUILTIN PROXY 10172 FINAL] bind error:", e)

# ===== PANSOU_TMDB_BUILTIN_PROXY_10172_FINAL_END =====

# ===== PANSOU_EXCLUDE_SOURCE_PATCH_BEGIN =====
import json as _psex_json

try:
    _PSEX_PREV_INIT = PanSouSpider.init
    _PSEX_PREV_PARSE = PanSouSpider._parse_search_results
except Exception:
    _PSEX_PREV_INIT = None
    _PSEX_PREV_PARSE = None


def _psex_parse_ext(extend):
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str) and extend.strip().startswith("{"):
            return _psex_json.loads(extend)
        return {}
    except Exception:
        return {}


def _psex_to_list(v):
    try:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, tuple):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            return [x.strip() for x in v.split(",") if x.strip()]
        return []
    except Exception:
        return []


def _psex_init(self, extend=""):
    ret = None
    if _PSEX_PREV_INIT:
        ret = _PSEX_PREV_INIT(self, extend)

    try:
        ext = _psex_parse_ext(extend)

        self.exclude_plugins = _psex_to_list(
            ext.get("exclude_plugins", getattr(self, "exclude_plugins", []))
        )

        self.exclude_channels = _psex_to_list(
            ext.get("exclude_channels", getattr(self, "exclude_channels", []))
        )

        self.exclude_sources = _psex_to_list(
            ext.get("exclude_sources", getattr(self, "exclude_sources", []))
        )

        print("[PanSou Exclude] exclude_plugins =", self.exclude_plugins)
        print("[PanSou Exclude] exclude_channels =", self.exclude_channels)
        print("[PanSou Exclude] exclude_sources =", self.exclude_sources)

    except Exception as e:
        print("[PanSou Exclude] init error:", e)

    return ret if ret is not None else {}


def _psex_match(text, rules):
    try:
        text = str(text or "").lower()
        for r in rules or []:
            r = str(r or "").strip().lower()
            if r and r in text:
                return True
        return False
    except Exception:
        return False


def _psex_should_drop(self, item):
    try:
        source = str(item.get("source") or "").lower()

        exclude_plugins = getattr(self, "exclude_plugins", []) or []
        exclude_channels = getattr(self, "exclude_channels", []) or []
        exclude_sources = getattr(self, "exclude_sources", []) or []

        # 通用来源排除
        if exclude_sources and _psex_match(source, exclude_sources):
            return True

        # 插件排除，常见 source: plugin:xxx
        if exclude_plugins:
            if source.startswith("plugin:"):
                plugin_name = source.split(":", 1)[1]
                if _psex_match(plugin_name, exclude_plugins):
                    return True

            # 兜底包含匹配
            if _psex_match(source, exclude_plugins):
                return True

        # 频道排除，常见 source: tg:xxx / channel:xxx
        if exclude_channels:
            if source.startswith("tg:") or source.startswith("channel:"):
                channel_name = source.split(":", 1)[1]
                if _psex_match(channel_name, exclude_channels):
                    return True

            # 兜底包含匹配
            if _psex_match(source, exclude_channels):
                return True

        return False
    except Exception:
        return False


def _psex_parse_search_results(self, data, keywords):
    if _PSEX_PREV_PARSE:
        items = _PSEX_PREV_PARSE(self, data, keywords)
    else:
        items = []

    try:
        if not items:
            return items

        out = []
        drop_count = 0

        for item in items:
            if _psex_should_drop(self, item):
                drop_count += 1
                continue
            out.append(item)

        if drop_count:
            print("[PanSou Exclude] dropped =", drop_count)

        return out

    except Exception as e:
        print("[PanSou Exclude] filter error:", e)
        return items


try:
    PanSouSpider.init = _psex_init
    PanSouSpider._parse_search_results = _psex_parse_search_results
    Spider = PanSouSpider
    print("[PANSOU EXCLUDE SOURCE PATCH] loaded")
except Exception as e:
    print("[PANSOU EXCLUDE SOURCE PATCH] load error:", e)

# ===== PANSOU_EXCLUDE_SOURCE_PATCH_END =====

# ===== PANSOU_115_ALL_ISO_9999_ORIGINAL_FIX_BEGIN =====
# -*- coding: utf-8 -*-
# ============================================================
# PanSou 115 ISO 原画播放 /p/9999 修复
#
# 作用：
# 1. 磁力云下载后的 115原画播放：
#      share_id=self
#      share_pwd=pickcode
#
# 2. 115分享原画播放：
#      share_id=分享码
#      share_pwd=提取码
#
# 3. 只要文件是 .iso，统一使用：
#      http://OK_HOST:10078/p/9999/null/{base64(inner)}/{完整文件名.iso}
#
# 4. inner 中 file_name 使用完整文件名：
#      file_name=完整文件名.iso
#
# 5. 非 ISO 文件不改，继续走原来的 /p/32/null/{base64}/{ext}?header=...
#
# 6. 不影响：
#      - 夸克分享原画
#      - 普通推送
#      - 磁力云下载
#      - 播放列表
#      - OpenList
# ============================================================

import base64 as _psiso_base64
from urllib.parse import urlencode as _psiso_urlencode
from urllib.parse import quote as _psiso_quote

try:
    _PSISO_PREV_SELF_115_ORIGINAL_URL = globals().get("_ps115op_build_original_url")
except Exception:
    _PSISO_PREV_SELF_115_ORIGINAL_URL = None

try:
    _PSISO_PREV_SHARE_115_ORIGINAL_URL = globals().get("_psgv2_build_115_url")
except Exception:
    _PSISO_PREV_SHARE_115_ORIGINAL_URL = None


def _psiso_clean_filename(name, default_name="video.iso"):
    """
    清理文件名，避免带路径。
    """
    try:
        name = str(name or "").strip()
        name = name.replace("\\", "/").rsplit("/", 1)[-1].strip()
        if not name:
            name = default_name
        return name
    except Exception:
        return default_name


def _psiso_ext(name):
    try:
        name = str(name or "").strip()
        if "." in name:
            ext = name.rsplit(".", 1)[-1].strip().lower()
            if ext:
                return ext
    except Exception:
        pass
    return ""


def _psiso_is_iso(name):
    try:
        return _psiso_ext(name) == "iso"
    except Exception:
        return False


def _psiso_outer_name(name):
    """
    /p/9999/null/ 最后一段文件名。

    中文文件名样本通常是双重 URL 编码：
      [死神来了].iso
      -> %5B%E6%AD%BB...
      -> %255B%25E6%25AD%25BB...

    ASCII 文件名双重编码后基本不变。
    """
    try:
        name = _psiso_clean_filename(name)
        return _psiso_quote(
            _psiso_quote(name, safe=""),
            safe=""
        )
    except Exception:
        return "video.iso"


def _psiso_build_9999_url(ok_host, ok_port, go_host, go_port, inner_params, full_name):
    """
    构造 ISO 专用原画链接：

    outer:
      http://OK_HOST:10078/p/9999/null/{base64(inner)}/{完整文件名.iso}

    inner:
      http://GO_HOST:9978/proxy?do=115&type=dwnz&...
    """
    try:
        inner_url = "http://%s:%s/proxy?%s" % (
            go_host,
            go_port,
            _psiso_urlencode(inner_params),
        )

        inner_b64 = _psiso_base64.b64encode(
            inner_url.encode("utf-8")
        ).decode("utf-8").rstrip("=")

        final_url = (
            "http://%s:%s/p/9999/null/%s/%s"
            % (
                ok_host,
                ok_port,
                inner_b64,
                _psiso_outer_name(full_name),
            )
        )

        return final_url, inner_url

    except Exception as e:
        print("[PanSou 115 ISO 9999] build url error:", e)
        return "", ""


def _psiso_self_hosts(self):
    """
    读取磁力云下载后 115原画播放 那套 host/port。
    对应原 _ps115op_build_original_url。
    """
    try:
        host = str(
            getattr(self, "ps115op_host", "127.0.0.1")
            or "127.0.0.1"
        ).strip()

        ok_port = str(
            getattr(self, "ps115op_ok_port", "10078")
            or "10078"
        ).strip()

        go_port = str(
            getattr(self, "ps115op_go_port", "9978")
            or "9978"
        ).strip()

        return host, ok_port, host, go_port
    except Exception:
        return "127.0.0.1", "10078", "127.0.0.1", "9978"


def _psiso_share_hosts(self):
    """
    读取 115分享原画 V2 那套 outer OK / inner GO 地址。
    优先调用 _psgv2_hosts。
    """
    try:
        fn = globals().get("_psgv2_hosts")
        if fn:
            return fn(self)
    except Exception:
        pass

    try:
        ok_host = str(
            getattr(self, "psgo_ok_host", "127.0.0.1")
            or "127.0.0.1"
        ).strip()

        ok_port = str(
            getattr(self, "psgo_ok_port", "10078")
            or "10078"
        ).strip()

        go_host = str(
            getattr(self, "psgo_go_host", "127.0.0.1")
            or "127.0.0.1"
        ).strip()

        go_port = str(
            getattr(self, "psgo_go_port", "9978")
            or "9978"
        ).strip()

        return ok_host, ok_port, go_host, go_port
    except Exception:
        return "127.0.0.1", "10078", "127.0.0.1", "9978"


# ============================================================
# A. 磁力云下载后的 115原画播放：share_id=self
# ============================================================
def _psiso_self_115_original_url(self, file_info):
    """
    覆盖 _ps115op_build_original_url。

    只处理 ISO：
      share_id=self
      share_pwd=pickcode
      file_name=完整文件名.iso
      /p/9999/null/{base64(inner)}/{完整文件名.iso}

    非 ISO 回退原函数。
    """
    try:
        if not isinstance(file_info, dict):
            if _PSISO_PREV_SELF_115_ORIGINAL_URL:
                return _PSISO_PREV_SELF_115_ORIGINAL_URL(self, file_info)
            return "", {}

        name = _psiso_clean_filename(
            file_info.get("name")
            or file_info.get("file_name")
            or file_info.get("fname")
            or "video.iso"
        )

        if not _psiso_is_iso(name):
            if _PSISO_PREV_SELF_115_ORIGINAL_URL:
                return _PSISO_PREV_SELF_115_ORIGINAL_URL(self, file_info)
            return "", {}

        fid = str(
            file_info.get("fid")
            or file_info.get("file_id")
            or file_info.get("id")
            or ""
        ).strip()

        pickcode = str(
            file_info.get("pickcode")
            or file_info.get("pick_code")
            or file_info.get("pickCode")
            or file_info.get("pc")
            or ""
        ).strip()

        size = str(
            file_info.get("size")
            or file_info.get("file_size")
            or file_info.get("s")
            or "0"
        ).strip()

        sha1 = str(
            file_info.get("sha1")
            or file_info.get("sha")
            or file_info.get("file_sha1")
            or file_info.get("content_hash")
            or ""
        ).strip().upper()

        if not fid or not pickcode:
            print("[PanSou 115 ISO self] missing fid/pickcode:", file_info)
            if _PSISO_PREV_SELF_115_ORIGINAL_URL:
                return _PSISO_PREV_SELF_115_ORIGINAL_URL(self, file_info)
            return "", {}

        ok_host, ok_port, go_host, go_port = _psiso_self_hosts(self)

        inner_params = [
            ("do", "115"),
            ("type", "dwnz"),
            ("file_id", fid),
            ("share_id", "self"),
            ("share_pwd", pickcode),
            ("file_size", size),
            ("content_hash", sha1),
            # ISO 关键：完整文件名，不是 iso
            ("file_name", name),
        ]

        final_url, inner_url = _psiso_build_9999_url(
            ok_host,
            ok_port,
            go_host,
            go_port,
            inner_params,
            name,
        )

        if not final_url:
            if _PSISO_PREV_SELF_115_ORIGINAL_URL:
                return _PSISO_PREV_SELF_115_ORIGINAL_URL(self, file_info)
            return "", {}

        try:
            self._psiso_last_inner = inner_url
            self._psiso_last_url = final_url
        except Exception:
            pass

        print("[PanSou 115 ISO self] build /p/9999 ok")
        print("[PanSou 115 ISO self] name=%s" % name)
        print("[PanSou 115 ISO self] fid=%s" % fid)
        print("[PanSou 115 ISO self] pickcode=%s" % pickcode)
        print("[PanSou 115 ISO self] size=%s" % size)
        print("[PanSou 115 ISO self] sha1=%s" % sha1)
        print("[PanSou 115 ISO self] inner=%s" % inner_url)
        print("[PanSou 115 ISO self] final=%s" % final_url)

        # 你的 /p/9999 样本没有 ?header=json。
        # 返回空 header，避免额外干扰。
        return final_url, {}

    except Exception as e:
        print("[PanSou 115 ISO self] error:", e)
        try:
            if _PSISO_PREV_SELF_115_ORIGINAL_URL:
                return _PSISO_PREV_SELF_115_ORIGINAL_URL(self, file_info)
        except Exception:
            pass
        return "", {}


# ============================================================
# B. 115分享原画：share_id=分享码
# ============================================================
def _psiso_share_115_original_url(self, file_info):
    """
    覆盖 _psgv2_build_115_url。

    只处理 ISO：
      share_id=分享码
      share_pwd=提取码
      file_name=完整文件名.iso
      /p/9999/null/{base64(inner)}/{完整文件名.iso}

    非 ISO 回退原函数。
    """
    try:
        if not isinstance(file_info, dict):
            if _PSISO_PREV_SHARE_115_ORIGINAL_URL:
                return _PSISO_PREV_SHARE_115_ORIGINAL_URL(self, file_info)
            return "", {}

        name = _psiso_clean_filename(
            file_info.get("name")
            or file_info.get("file_name")
            or file_info.get("fname")
            or "video.iso"
        )

        if not _psiso_is_iso(name):
            if _PSISO_PREV_SHARE_115_ORIGINAL_URL:
                return _PSISO_PREV_SHARE_115_ORIGINAL_URL(self, file_info)
            return "", {}

        fid = str(
            file_info.get("fid")
            or file_info.get("file_id")
            or file_info.get("id")
            or ""
        ).strip()

        share_code = str(
            file_info.get("share_code")
            or file_info.get("share_id")
            or ""
        ).strip()

        receive_code = str(
            file_info.get("receive_code")
            or file_info.get("share_pwd")
            or file_info.get("password")
            or file_info.get("pwd")
            or ""
        ).strip()

        size = str(
            file_info.get("size")
            or file_info.get("file_size")
            or file_info.get("s")
            or "0"
        ).strip()

        sha1 = str(
            file_info.get("sha1")
            or file_info.get("sha")
            or file_info.get("file_sha1")
            or file_info.get("content_hash")
            or ""
        ).strip().upper()

        if not fid or not share_code:
            print("[PanSou 115 ISO share] missing fid/share_code:", file_info)
            if _PSISO_PREV_SHARE_115_ORIGINAL_URL:
                return _PSISO_PREV_SHARE_115_ORIGINAL_URL(self, file_info)
            return "", {}

        ok_host, ok_port, go_host, go_port = _psiso_share_hosts(self)

        inner_params = [
            ("do", "115"),
            ("type", "dwnz"),
            ("file_id", fid),
            ("share_id", share_code),
            ("share_pwd", receive_code),
            ("file_size", size),
            ("content_hash", sha1),
            # ISO 关键：完整文件名，不是 iso
            ("file_name", name),
        ]

        final_url, inner_url = _psiso_build_9999_url(
            ok_host,
            ok_port,
            go_host,
            go_port,
            inner_params,
            name,
        )

        if not final_url:
            if _PSISO_PREV_SHARE_115_ORIGINAL_URL:
                return _PSISO_PREV_SHARE_115_ORIGINAL_URL(self, file_info)
            return "", {}

        try:
            self._psiso_last_share_inner = inner_url
            self._psiso_last_share_url = final_url
        except Exception:
            pass

        print("[PanSou 115 ISO share] build /p/9999 ok")
        print("[PanSou 115 ISO share] name=%s" % name)
        print("[PanSou 115 ISO share] fid=%s" % fid)
        print("[PanSou 115 ISO share] share_id=%s" % share_code)
        print("[PanSou 115 ISO share] share_pwd=%s" % receive_code)
        print("[PanSou 115 ISO share] size=%s" % size)
        print("[PanSou 115 ISO share] sha1=%s" % sha1)
        print("[PanSou 115 ISO share] inner=%s" % inner_url)
        print("[PanSou 115 ISO share] final=%s" % final_url)

        # /p/9999 样本没有 ?header=json。
        return final_url, {}

    except Exception as e:
        print("[PanSou 115 ISO share] error:", e)
        try:
            if _PSISO_PREV_SHARE_115_ORIGINAL_URL:
                return _PSISO_PREV_SHARE_115_ORIGINAL_URL(self, file_info)
        except Exception:
            pass
        return "", {}


try:
    # 覆盖磁力云下载后的 115原画播放构造函数
    if _PSISO_PREV_SELF_115_ORIGINAL_URL:
        globals()["_ps115op_build_original_url"] = _psiso_self_115_original_url
        try:
            PanSouSpider._ps115op_build_original_url = _psiso_self_115_original_url
        except Exception:
            pass
        print("[PanSou 115 ISO] override _ps115op_build_original_url ok")
    else:
        print("[PanSou 115 ISO] _ps115op_build_original_url not found, skip self/cache ISO")

    # 覆盖 115分享原画 V2 构造函数
    if _PSISO_PREV_SHARE_115_ORIGINAL_URL:
        globals()["_psgv2_build_115_url"] = _psiso_share_115_original_url
        try:
            PanSouSpider._psgv2_build_115_url = _psiso_share_115_original_url
        except Exception:
            pass
        print("[PanSou 115 ISO] override _psgv2_build_115_url ok")
    else:
        print("[PanSou 115 ISO] _psgv2_build_115_url not found, skip share ISO")

    Spider = PanSouSpider

    print("[PANSOU 115 ALL ISO 9999 ORIGINAL FIX] loaded")
    print("[PanSou 115 ISO] self/cache ISO => /p/9999 full filename")
    print("[PanSou 115 ISO] share ISO => /p/9999 full filename")
    print("[PanSou 115 ISO] non-ISO keeps old /p/32 logic")

except Exception as e:
    print("[PANSOU 115 ALL ISO 9999 ORIGINAL FIX] install failed:", e)

# ===== PANSOU_115_ALL_ISO_9999_ORIGINAL_FIX_END =====