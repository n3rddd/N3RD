// ==UserScript==
// @name         hitv
// @namespace    gmspider
// @version      2024.11.12
// @description  Hi视频 GMSpider
// @author       Luomo
// @match        https://www.upfuhn.com/*
// @require      https://cdn.jsdelivr.net/gh/CatVodSpider-GM/Spiders-Lib@main/lib/browser-extension-url-match-1.2.0.min.js
// @require      https://scriptcat.org/lib/637/1.4.3/ajaxHooker.js
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        unsafeWindow
// @run-at       document-start
// ==/UserScript==
console.log(JSON.stringify(GM_info));
(function () {
    const GMSpiderArgs = {};
    if (typeof GmSpiderInject !== 'undefined') {
        let args = JSON.parse(GmSpiderInject.GetSpiderArgs());
        GMSpiderArgs.fName = args.shift();
        GMSpiderArgs.fArgs = args;
    } else {
        GMSpiderArgs.fName = "searchContent";
        GMSpiderArgs.fArgs = [true];
        // GMSpiderArgs.fName = "categoryContent";
        // GMSpiderArgs.fArgs = ["82", 2, true, {tag: "动作", y: "2024", o: "1", a: "大陆"}];
    }
    Object.freeze(GMSpiderArgs);
    let hookConfigs = {
        "homeContent": [{
            matcher: matchPattern("https://*/v1/report_channel_data").assertValid(),
            onResponseHook: function (response) {
                Array.from(document.querySelectorAll(".left-wrap .tab-box:nth-child(2) .swiper-slide span"))
                    .find(el => el.textContent === "全部").dispatchEvent(new Event("click"));
            }
        }, {
            dataKey: "ys_video_sites", matcher: matchPattern("https://*/v1/ys_video_sites?*").assertValid()
        }], "categoryContent": [{
            matcher: matchPattern("https://*/v1/report_channel_data").assertValid(),
            onResponseHook: function (response) {
                const extend = GMSpiderArgs.fArgs[3];
                let tag = extend?.tag ?? "全部"
                Array.from(document.querySelectorAll(".left-wrap .tab-box:nth-child(2) .swiper-slide span"))
                    .find(el => el.textContent === tag).dispatchEvent(new Event("click"));
            }
        }, {
            dataKey: "ys_video_sites",
            matcher: matchPattern("https://*/v1/ys_video_sites?*").assertValid(),
            onRequestHook: function (response) {
                const page = GMSpiderArgs.fArgs[1];
                const filter = GMSpiderArgs.fArgs[2];
                const extend = GMSpiderArgs.fArgs[3];
                const url = new URL(response.url);
                const params = new URLSearchParams(url.search);
                params.set("pn", page)
                if (filter) {
                    params.set("a", extend?.a ?? "");
                    params.set("y", extend?.y ?? "");
                    params.set("o", extend?.o ?? 0);
                }
                url.search = params.toString();
                response.url = url.toString();
            }
        }],
        "detailContent": [{
            dataKey: "meta", matcher: matchPattern("https://*/v1/report_channel_data").assertValid()
        }],
        "searchContent": [{
            dataKey: "meta", matcher: matchPattern("https://*/v1/report_channel_data").assertValid()
        }],
    };
    const GmSpider = (function () {
        const categoryFilterCachePrefix = "category_";
        const filterTag = {
            key: "tag", name: "分类", value: []
        };
        const filterArea = {
            key: "o", name: "地区", value: []
        };
        const filterYear = {
            key: "y", name: "年份", value: []
        };
        const filterSort = {
            key: "o",
            name: "排序",
            value: [{n: "综合", v: "0"}, {n: "最新", v: "2"}, {n: "最热", v: "1"}, {n: "评分", v: "5"},]
        };
        return {
            homeContent: function (filter) {
                let result = {
                    class: [{type_id: "85", type_name: "短剧"}, {type_id: "81", type_name: "电影"}, {
                        type_id: "82",
                        type_name: "电视剧"
                    }, {type_id: "83", type_name: "综艺"}, {type_id: "84", type_name: "动漫"},], filters: {}, list: []
                };
                document.querySelectorAll(".left-wrap .tab-box:nth-child(3) .swiper-slide span").forEach((filter) => {
                    filterArea.value.push({
                        n: filter.textContent, v: filter.textContent,
                    })
                });
                document.querySelectorAll(".left-wrap .tab-box:nth-child(4) .swiper-slide span").forEach((filter) => {
                    filterYear.value.push({
                        n: filter.textContent, v: filter.textContent,
                    })
                });
                result.class.forEach((category) => {
                    const categoryFilter = [];
                    const cacheFilter = localStorage.getItem(categoryFilterCachePrefix + category.type_id);
                    if (typeof cacheFilter !== "undefined" && cacheFilter !== null) {
                        categoryFilter.push(JSON.parse(cacheFilter));
                    }
                    categoryFilter.push(filterArea, filterYear, filterSort);
                    result.filters[category.type_id] = categoryFilter;
                })
                hookResult.ys_video_sites.data.data.forEach((media) => {
                    result.list.push({
                        vod_id: media.video_site_id,
                        vod_name: media.video_name,
                        vod_pic: media.video_vertical_url,
                        vod_remarks: "评分：" + media.score,
                        vod_year: media.years
                    })
                });
                return result;
            }, categoryContent: function (tid, pg, filter, extend) {
                let result = {
                    list: [], pagecount: Math.ceil(hookResult.ys_video_sites.data.total / 21)
                };
                document.querySelectorAll(".left-wrap .tab-box:nth-child(2) .swiper-slide span").forEach((filter) => {
                    filterTag.value.push({
                        n: filter.textContent, v: filter.textContent,
                    })
                });
                localStorage.setItem(categoryFilterCachePrefix + tid, JSON.stringify(filterTag));
                hookResult.ys_video_sites.data.data.forEach((media) => {
                    result.list.push({
                        vod_id: media.video_site_id,
                        vod_name: media.video_name,
                        vod_pic: media.video_vertical_url,
                        vod_remarks: "评分：" + media.score,
                        vod_year: media.years
                    })
                })
                return result;
            }, detailContent: function (ids) {
                let playUrl = [];
                let vod = {};
                const formatData = JSON.parse(document.getElementById("__NUXT_DATA__").innerHTML);
                formatData.forEach((data) => {
                    if (typeof (vod?.vod_id) == "undefined" && typeof (data?.video_desc) === "number") {
                        vod = {
                            vod_id: formatData[data.video_site_id],
                            vod_name: formatData[data.video_name],
                            vod_content: formatData[data.video_desc],
                            vod_year: formatData[data.years],
                            vod_area: formatData[data.area],
                            vod_actor: formatData[data.main_actor],
                            type_name: formatData[data.tag],
                            vod_play_data: [{
                                from: "Hi视频", url: playUrl
                            }]
                        };
                    }
                    if (typeof (data?.series_num) === "number") {
                        playUrl.push({
                            name: formatData[data.series_num],
                            value: {
                                type: "finalUrl", data: {
                                    header: {
                                        "User-Agent": window.navigator.userAgent, "Referer": window.location.href
                                    }, url: formatData[data.video_url]
                                }
                            }
                        })
                    }
                })
                return vod;
            }, searchContent: function (key, quick, pg) {
                const result = {
                    list: [],
                    page: pg,
                    pagecount: 1
                };
                const formatData = JSON.parse(document.getElementById("__NUXT_DATA__").innerHTML);
                console.log(formatData);
                formatData.forEach((data) => {
                    if (typeof (data?.first_video_series) === "number") {
                        let firstVideo = formatData[data.first_video_series];
                        result.list.push({
                            vod_id: formatData[firstVideo.video_site_id],
                            vod_name: formatData[firstVideo.video_name],
                            vod_pic: formatData[firstVideo.video_vertical_url],
                            vod_remarks: formatData[firstVideo.tag],
                            vod_year: formatData[firstVideo.years]
                        })
                        formatData[data.video_sites].forEach((videoIndex) => {
                            let video = formatData[videoIndex];
                            result.list.push({
                                vod_id: formatData[video.video_site_id],
                                vod_name: formatData[video.video_name],
                                vod_pic: formatData[video.video_vertical_url],
                                vod_remarks: formatData[video.tag],
                                vod_year: formatData[video.years]
                            })
                        })
                    }
                })
                return result;
            }
        };
    })();
    let spiderExecuted = false;
    let dataReadyCount = 0;
    let hookResult = {};
    ajaxHooker.hook(request => {
        hookConfigs[GMSpiderArgs.fName].forEach((hookConfig) => {
            if (typeof hookConfig.onRequestHook === "function" && hookConfig.matcher.match(request.url)) {
                hookConfig.onRequestHook(request);
            }
        });
        if (!spiderExecuted) {
            let dataTodoCount = 0;
            hookConfigs[GMSpiderArgs.fName].forEach((hookConfig) => {
                if (typeof hookConfig.dataKey !== "undefined") {
                    if (hookConfig?.require !== false) {
                        dataTodoCount++;
                    }
                }
                if (hookConfig.matcher.match(request.url)) {
                    request.response = res => {
                        if (typeof hookConfig.onResponseHook === "function") {
                            hookConfig.onResponseHook(res);
                        }
                        if (typeof hookConfig.dataKey !== "undefined") {
                            if (hookConfig?.require !== false) {
                                dataReadyCount++;
                            }
                            let data = JSON.parse(res.text);
                            if (typeof data === 'object' && data) {
                                hookResult[hookConfig.dataKey] = data;
                            } else {
                                hookResult[hookConfig.dataKey] = res.text;
                            }
                            if (dataTodoCount === dataReadyCount) {
                                spiderExecuted = true;
                                const result = GmSpider[GMSpiderArgs.fName](...GMSpiderArgs.fArgs);
                                console.log(result);
                                if (typeof GmSpiderInject !== 'undefined' && spiderExecuted) {
                                    GmSpiderInject.SetSpiderResult(JSON.stringify(result));
                                }
                            }
                        }
                    };
                }

            });
        }
    });
})();