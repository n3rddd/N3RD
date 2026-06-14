const axios = require("axios");
const crypto = require("crypto");
const http = require("http");
const https = require("https");

const HOST = "https://apinew.uozvr.com";
const TOKEN =
  "bc2f1d031b3eb444d84528b4dcce5e07.3e091c3550c1cb09899ac4013a76a7731f946f4461c9dd7c7c2ca1f9090dc4841c7e0168fed38d3312a8a38650edeef2e2d47f24c884bb3bd7005e1280f3b6eb2d36829134992c0ece8748ae5b85fa57a94d3d6e38faa44168d7f24e4a588424a6bee7779c18ade979353688e3c56fbdcf1d5590385f5f7ef6e01d1850974aa220eb5178c89e61c24411af9b9a19435e.ca9d8de0fa2798b5695845f64adbabeee3d38f39506170d5deda14add46d37f0";
const AES_KEY = "tOEryzJxZ8T385vS";
const AES_IV = "uqPY6IFCoiLOjA5M";
const SIGN_KEYS =
  "QS9HiIvlxGT3HDFcXpj2M2+DC+yJxR3m/5sIQGLNISEQNSs6z+PzHCtC3IGpey72DBQ8cxLklnOMgqZUgPycruySDW0e7qWyyNlYPMw0Uc6PnSITLVvG8mRA+06QwhRr4qdY7pQfYVfSFd/bfn7d7UmM+SxnSwT+8uqF74r1lK4=";
const RSA_PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGAe6hKrWLi1zQmjTT1
ozbE4QdFeJGNxubxld6GrFGximxfMsMB6BpJhpcTouAqywAFppiKetUBBbXwYsYU
1wNr648XVmPmCMCy4rY8vdliFnbMUj086DU6Z+/oXBdWU3/b1G0DN3E9wULRSwcK
ZT3wj/cCI1vsCm3gj2R5SqkA9Y0CAwEAAQKBgAJH+4CxV0/zBVcLiBCHvSANm0l7
HetybTh/j2p0Y1sTXro4ALwAaCTUeqdBjWiLSo9lNwDHFyq8zX90+gNxa7c5EqcW
V9FmlVXr8VhfBzcZo1nXeNdXFT7tQ2yah/odtdcx+vRMSGJd1t/5k5bDd9wAvYdI
DblMAg+wiKKZ5KcdAkEA1cCakEN4NexkF5tHPRrR6XOY/XHfkqXxEhMqmNbB9U34
saTJnLWIHC8IXys6Qmzz30TtzCjuOqKRRy+FMM4TdwJBAJQZFPjsGC+RqcG5UvVM
iMPhnwe/bXEehShK86yJK/g/UiKrO87h3aEu5gcJqBygTq3BBBoH2md3pr/W+hUM
WBsCQQChfhTIrdDinKi6lRxrdBnn0Ohjg2cwuqK5zzU9p/N+S9x7Ck8wUI53DKm8
jUJE8WAG7WLj/oCOWEh+ic6NIwTdAkEAj0X8nhx6AXsgCYRql1klbqtVmL8+95KZ
K7PnLWG/IfjQUy3pPGoSaZ7fdquG8bq8oyf5+dzjE/oTXcByS+6XRQJAP/5ciy1b
L3NhUhsaOVy55MHXnPjdcTX0FaLi+ybXZIfIQ2P4rb19mVq1feMbCXhz+L1rG8oa
t5lYKfpe8k83ZA==
-----END PRIVATE KEY-----`;

const LIMIT = 30;
const PLAY_UA = "Lavf/57.83.100";

const meta = {
  key: "guazi",
  name: "\u74dc\u5b50",
  type: 4,
  api: "/video/guazi",
  searchable: 1,
  quickSearch: 1,
  filterable: 1,
  changeable: 0,
};

const CLASSES = [
  { type_id: "1", type_name: "\u7535\u5f71" },
  { type_id: "2", type_name: "\u7535\u89c6\u5267" },
  { type_id: "4", type_name: "\u52a8\u6f2b" },
  { type_id: "3", type_name: "\u7efc\u827a" },
  { type_id: "64", type_name: "\u77ed\u5267" },
];

const AREA_FILTER = {
  key: "area",
  name: "\u5730\u533a",
  value: [
    { n: "\u5168\u90e8", v: "0" },
    { n: "\u5927\u9646", v: "\u5927\u9646" },
    { n: "\u9999\u6e2f", v: "\u9999\u6e2f" },
    { n: "\u53f0\u6e7e", v: "\u53f0\u6e7e" },
    { n: "\u7f8e\u56fd", v: "\u7f8e\u56fd" },
    { n: "\u97e9\u56fd", v: "\u97e9\u56fd" },
    { n: "\u65e5\u672c", v: "\u65e5\u672c" },
    { n: "\u82f1\u56fd", v: "\u82f1\u56fd" },
    { n: "\u6cd5\u56fd", v: "\u6cd5\u56fd" },
    { n: "\u6cf0\u56fd", v: "\u6cf0\u56fd" },
    { n: "\u5370\u5ea6", v: "\u5370\u5ea6" },
    { n: "\u5176\u4ed6", v: "\u5176\u4ed6" },
  ],
};
const YEAR_FILTER = {
  key: "year",
  name: "\u5e74\u4efd",
  value: [
    { n: "\u5168\u90e8", v: "0" },
    ...Array.from({ length: 21 }, (_, index) => {
      const year = String(2025 - index);
      return { n: year, v: year };
    }),
    { n: "\u66f4\u65e9", v: "2004" },
  ],
};
const SORT_FILTER = {
  key: "sort",
  name: "\u6392\u5e8f",
  value: [
    { n: "\u6700\u65b0", v: "d_id" },
    { n: "\u6700\u70ed", v: "d_hits" },
    { n: "\u63a8\u8350", v: "d_score" },
  ],
};
const FILTERS = Object.fromEntries(CLASSES.map((item) => [item.type_id, [AREA_FILTER, YEAR_FILTER, SORT_FILTER]]));

const client = axios.create({
  timeout: 22000,
  maxRedirects: 3,
  httpAgent: new http.Agent({ keepAlive: true }),
  httpsAgent: new https.Agent({ keepAlive: true, rejectUnauthorized: false }),
  validateStatus: () => true,
  headers: {
    "Cache-Control": "no-cache",
    Version: "2406025",
    PackageName: "com.uf076bf0c246.qe439f0d5e.m8aaf56b725a.ifeb647346f",
    Ver: "1.9.2",
    Referer: HOST,
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "okhttp/3.12.0",
  },
});

const cache = {
  api: new Map(),
  detail: new Map(),
  ttl: {
    api: 5 * 60 * 1000,
    detail: 30 * 60 * 1000,
  },
};

function cacheGet(map, key, ttl) {
  const hit = map.get(key);
  if (!hit) return null;
  if (Date.now() - hit.ts > ttl) {
    map.delete(key);
    return null;
  }
  return hit.value;
}

function cacheSet(map, key, value) {
  map.set(key, { ts: Date.now(), value });
  if (map.size > 500) map.clear();
  return value;
}

function cleanText(value = "") {
  return String(value || "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function sanitizeValue(value = "") {
  return cleanText(value).replace(/[$#]/g, " ").slice(0, 240);
}

function pageOf(value) {
  return Math.max(1, parseInt(value || "1", 10) || 1);
}

function decodeExt(raw) {
  if (!raw) return {};
  if (typeof raw === "object") return raw;

  const attempts = [String(raw)];
  try {
    attempts.push(Buffer.from(String(raw), "base64").toString("utf8"));
  } catch {}
  try {
    attempts.push(Buffer.from(String(raw), "base64url").toString("utf8"));
  } catch {}

  for (const item of attempts) {
    try {
      const parsed = JSON.parse(item);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch {}
  }
  return {};
}

function encodePlay(data) {
  return Buffer.from(JSON.stringify(data), "utf8").toString("base64url");
}

function decodePlay(id) {
  const raw = String(id || "");
  try {
    const parsed = JSON.parse(Buffer.from(raw, "base64url").toString("utf8"));
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch {}

  const parts = raw.split("||");
  if (parts.length >= 2) {
    return {
      param: parts[0],
      resolutions: parts[1].split("@").filter(Boolean),
    };
  }
  return raw ? { param: raw, resolutions: [] } : null;
}

function stableStringify(value) {
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  if (!value || typeof value !== "object") return JSON.stringify(value);
  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(",")}}`;
}

function apiJsonStringify(value) {
  return JSON.stringify(value).replace(/[^\x00-\x7F]/g, (char) => {
    return `\\u${char.charCodeAt(0).toString(16).padStart(4, "0")}`;
  });
}

function md5(value) {
  return crypto.createHash("md5").update(String(value)).digest("hex");
}

function aesEncryptHex(text, key = AES_KEY, iv = AES_IV) {
  const cipher = crypto.createCipheriv("aes-128-cbc", Buffer.from(key, "utf8"), Buffer.from(iv, "utf8"));
  cipher.setAutoPadding(true);
  return Buffer.concat([cipher.update(String(text), "utf8"), cipher.final()]).toString("hex").toUpperCase();
}

function aesDecryptHex(hexText, key, iv) {
  const decipher = crypto.createDecipheriv("aes-128-cbc", Buffer.from(key, "utf8"), Buffer.from(iv, "utf8"));
  decipher.setAutoPadding(true);
  return Buffer.concat([
    decipher.update(Buffer.from(String(hexText || ""), "hex")),
    decipher.final(),
  ]).toString("utf8");
}

function rsaDecrypt(encryptedText) {
  const encrypted = Buffer.from(String(encryptedText || ""), "base64");
  try {
    return crypto
      .privateDecrypt({ key: RSA_PRIVATE_KEY, padding: crypto.constants.RSA_PKCS1_PADDING }, encrypted)
      .toString("utf8");
  } catch (error) {
    if (!crypto.constants.RSA_NO_PADDING) throw error;
  }

  const raw = crypto.privateDecrypt({ key: RSA_PRIVATE_KEY, padding: crypto.constants.RSA_NO_PADDING }, encrypted);
  if (raw[0] !== 0x00 || raw[1] !== 0x02) {
    throw new Error("\u54cd\u5e94\u5bc6\u94a5 RSA padding \u4e0d\u5339\u914d");
  }
  const split = raw.indexOf(0x00, 2);
  if (split < 10) throw new Error("\u54cd\u5e94\u5bc6\u94a5 RSA padding \u65e0\u6548");
  return raw.slice(split + 1).toString("utf8");
}

function buildSignature(requestKey, timestamp) {
  const text =
    `token_id=,token=${TOKEN},phone_type=1,` +
    `request_key=${requestKey},app_id=1,time=${timestamp},` +
    `keys=${SIGN_KEYS}*&zvdvdvddbfikkkumtmdwqppp?|4Y!s!2br`;
  return md5(text);
}

async function apiRequest(data, path, options = {}) {
  const useCache = options.useCache !== false;
  const cacheKey = `${path}:${md5(stableStringify(data))}`;
  if (useCache) {
    const cached = cacheGet(cache.api, cacheKey, cache.ttl.api);
    if (cached) return cached;
  }

  const requestKey = aesEncryptHex(apiJsonStringify(data));
  const timestamp = String(Math.floor(Date.now() / 1000));
  const body = {
    token: TOKEN,
    token_id: "",
    phone_type: "1",
    time: timestamp,
    phone_model: "xiaomi-22021211rc",
    keys: SIGN_KEYS,
    request_key: requestKey,
    signature: buildSignature(requestKey, timestamp),
    app_id: "1",
    ad_version: "1",
  };

  const res = await client.post(`${HOST}${path}`, new URLSearchParams(body).toString());
  if (res.status < 200 || res.status >= 400) {
    throw new Error(`HTTP ${res.status} ${path}`);
  }

  const response = typeof res.data === "string" ? JSON.parse(res.data) : res.data;
  const encryptedData = response?.data;
  if (!encryptedData?.keys || !encryptedData?.response_key) {
    throw new Error(`API \u8fd4\u56de\u7f3a\u5c11\u52a0\u5bc6\u6570\u636e: ${path}`);
  }

  const keyInfo = JSON.parse(rsaDecrypt(encryptedData.keys));
  const decrypted = aesDecryptHex(encryptedData.response_key, keyInfo.key, keyInfo.iv);
  const result = JSON.parse(decrypted);

  if (useCache) cacheSet(cache.api, cacheKey, result);
  return result;
}

function vodRemarks(vodContinu) {
  const continu = String(vodContinu ?? "0");
  return continu === "0" || continu === "" ? "\u7535\u5f71" : `\u66f4\u65b0\u81f3${continu}\u96c6`;
}

function listItem(item = {}) {
  const vodId = String(item.vod_id ?? item.id ?? "");
  const vodContinu = item.vod_continu ?? "0";
  if (!vodId) return null;
  return {
    vod_id: `${vodId}|${vodContinu}`,
    vod_name: sanitizeValue(item.vod_name || item.name || ""),
    vod_pic: String(item.vod_pic || item.pic || ""),
    vod_remarks: vodRemarks(vodContinu),
  };
}

function listResult(list, page) {
  return {
    list: (Array.isArray(list) ? list : []).map(listItem).filter((item) => item && item.vod_name),
    page: pageOf(page),
    pagecount: 9999,
    limit: LIMIT,
    total: 999999,
  };
}

function parseVodId(ids) {
  const raw = Array.isArray(ids) ? ids[0] : String(ids || "").split(",")[0];
  const [vodId, vodContinu = ""] = String(raw || "").split("|");
  return { vodId, vodContinu };
}

function resolutionScore(value) {
  const text = String(value || "").toLowerCase();
  if (/4k|2160|uhd|\u84dd\u5149|\u85cd\u5149/.test(text)) return 2160;
  if (/1080/.test(text)) return 1080;
  if (/720|\u8d85\u6e05/.test(text)) return 720;
  if (/480|\u9ad8\u6e05/.test(text)) return 480;
  if (/360|\u6807\u6e05|\u6a19\u6e05/.test(text)) return 360;

  const numbers = text.match(/\d{3,4}/g);
  if (!numbers) return 0;
  return Math.max(...numbers.map((num) => parseInt(num, 10) || 0));
}

function normalizePlayEntries(play = {}) {
  return Object.entries(play)
    .map(([quality, value]) => ({
      quality: sanitizeValue(quality),
      param: String(value?.param || ""),
      score: resolutionScore(quality),
    }))
    .filter((item) => item.param)
    .sort((left, right) => right.score - left.score);
}

function episodeName(item, index, total, vodName) {
  const name =
    item?.name ||
    item?.vurl_name ||
    item?.title ||
    item?.play_name ||
    item?.vod_name ||
    item?.vod_remarks ||
    "";
  if (name) return sanitizeValue(name);
  return total > 1 ? String(index + 1) : sanitizeValue(vodName);
}

function parseParamString(value) {
  const text = String(value || "").replace(/&amp;/g, "&").replace(/^\?/, "");
  const params = {};
  for (const [key, val] of new URLSearchParams(text)) {
    params[key] = val;
  }
  return params;
}

async function homeContent() {
  return {
    class: CLASSES,
    filters: FILTERS,
    list: [],
  };
}

async function categoryContent({ id, page, ext }) {
  const pg = pageOf(page);
  const decodedExt = decodeExt(ext);
  const data = await apiRequest(
    {
      area: decodedExt.area || "0",
      year: decodedExt.year || "0",
      pageSize: String(LIMIT),
      sort: decodedExt.sort || "d_id",
      page: String(pg),
      tid: String(id || "1"),
    },
    "/App/IndexList/indexList"
  );
  return listResult(data?.list || [], pg);
}

async function searchContent({ wd, page }) {
  const keyword = cleanText(wd);
  const pg = pageOf(page);
  if (!keyword) return listResult([], pg);

  const data = await apiRequest(
    {
      keywords: keyword,
      order_val: "1",
      page: String(pg),
    },
    "/App/Index/findMoreVod",
    { useCache: false }
  );

  const list = Array.isArray(data?.list) ? data.list : [];
  const lowered = keyword.toLowerCase();
  const hasTitleHit = list.some((item) => String(item?.vod_name || "").toLowerCase().includes(lowered));
  return listResult(hasTitleHit ? list : [], pg);
}

async function detailContent({ ids }) {
  const { vodId, vodContinu } = parseVodId(ids);
  if (!vodId) return { list: [] };

  const cacheKey = `detail:${vodId}`;
  const cached = cacheGet(cache.detail, cacheKey, cache.ttl.detail);
  if (cached) return cached;

  const [infoData, playData] = await Promise.all([
    apiRequest(
      {
        token_id: "1649412",
        vod_id: vodId,
        mobile_time: String(Math.floor(Date.now() / 1000)),
        token: TOKEN,
      },
      "/App/IndexPlay/playInfo"
    ),
    apiRequest(
      {
        vurl_cloud_id: "2",
        vod_d_id: vodId,
      },
      "/App/Resource/Vurl/show"
    ),
  ]);

  const vod = infoData?.vodInfo || {};
  const vodName = sanitizeValue(vod.vod_name || "");
  const playItems = [];
  const episodes = Array.isArray(playData?.list) ? playData.list : [];
  episodes.forEach((item, index) => {
    const entries = normalizePlayEntries(item?.play || {});
    if (!entries.length) return;

    const best = entries[0];
    const playId = encodePlay({
      param: best.param,
      resolutions: entries.map((entry) => entry.quality).filter(Boolean),
    });
    playItems.push(`${episodeName(item, index, episodes.length, vodName)}$${playId}`);
  });

  const result = {
    list: [
      {
        vod_id: `${vodId}|${vodContinu}`,
        vod_name: vodName,
        vod_pic: String(vod.vod_pic || ""),
        vod_remarks: vodRemarks(vodContinu || vod.vod_continu || "0"),
        vod_year: String(vod.vod_year || ""),
        vod_area: sanitizeValue(vod.vod_area || ""),
        vod_actor: sanitizeValue(vod.vod_actor || ""),
        vod_director: sanitizeValue(vod.vod_director || ""),
        vod_content: cleanText(vod.vod_use_content || vod.vod_content || ""),
        vod_play_from: "\u74dc\u5b50\u4e13\u7ebf",
        vod_play_url: playItems.join("#"),
      },
    ],
  };

  return cacheSet(cache.detail, cacheKey, result);
}

async function playContent({ id }) {
  const decoded = decodePlay(id);
  if (!decoded?.param) return { parse: 0, jx: 0, playUrl: "", url: "" };

  const params = parseParamString(decoded.param);
  const resolutions = Array.isArray(decoded.resolutions) ? decoded.resolutions.slice() : [];
  if (resolutions.length) {
    resolutions.sort((left, right) => resolutionScore(right) - resolutionScore(left));
    params.resolution = String(resolutions[0]);
  }

  const data = await apiRequest(params, "/App/Resource/VurlDetail/showOne", { useCache: false });
  const url = String(data?.url || "");
  return {
    parse: 0,
    jx: 0,
    playUrl: "",
    url,
    header: {
      "User-Agent": PLAY_UA,
    },
  };
}

module.exports = async function guazi(app, opt) {
  app.get(meta.api, async (req) => {
    try {
      const q = req.query || {};
      if (q.play) return await playContent({ id: q.play });
      if (q.wd) return await searchContent({ wd: q.wd, page: q.pg || q.page });
      if (q.ids || q.id) return await detailContent({ ids: q.ids || q.id });
      if (q.t) return await categoryContent({ id: q.t, page: q.pg || q.page, ext: q.ext || q.extend });
      return await homeContent();
    } catch (error) {
      return {
        list: [],
        msg: error?.message || String(error),
      };
    }
  });

  if (opt && Array.isArray(opt.sites)) {
    opt.sites.push(meta);
  }
};

module.exports.meta = meta;
