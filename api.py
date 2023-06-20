# -*- encoding: utf-8 -*-
'''
@File    :   api.py
@Time    :   2023年06月19日 20:20:58 星期一
@Author  :   erma0
@Version :   0.1
@Link    :   https://erma0.cn
@Desc    :   抖音爬虫封装API
'''

import os
import shutil
import stat
import threading
import time
from copy import deepcopy
from enum import Enum
from typing import List, Union

import ujson as json
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, UJSONResponse
from pydantic import BaseModel
from uvicorn.config import LOGGING_CONFIG

from browser import Browser
from spider import Douyin

date_fmt = "%Y-%m-%d %H:%M:%S"
LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = date_fmt
LOGGING_CONFIG["formatters"]["access"]["datefmt"] = date_fmt

title: str = '抖音爬虫API'
version: str = "0.1.0"
update = "20230619"
author = "erma0"
web = "https://douyin.erma0.cn/"
github = "https://github.com/erma0/douyin"
doc = "https://douyin.erma0.cn/docs"

description: str = """
### ❤️开源不易，欢迎star⭐

- 支持采集账号主页作品、喜欢作品、音乐原声作品、搜索作品、关注列表、粉丝列表、合集作品、单个作品

### 📢声明

> 本仓库为学习`playwright`爬虫、命令行调用`Aria2`及`FastAPI/AMIS/Eel`实现`WEBUI`的案例，仅用于测试和学习研究，禁止用于商业用途或任何非法用途。

> 任何用户直接或间接使用、传播本仓库内容时责任自负，本仓库的贡献者不对该等行为产生的任何后果负责。

> 如果相关方认为该项目的代码可能涉嫌侵犯其权利，请及时通知删除相关代码。
"""
contact = {"author": author, "url": github}
tags_metadata = [
    {
        "name": "同步",
        "description": "耗时短的接口，直接返回结果",
    },
    {
        "name": "异步",
        "description": "耗时长的接口，无法直接返回结果，返回一个轮询接口",
    },
]

edge = None
running_ls = []
download_path = './下载_API'

app = FastAPI(
    title=title,
    description=description,
    version=version,
    openapi_tags=tags_metadata,
    contact=contact,
)
# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DouyinAPI(Douyin):

    def _append_awemes(self, aweme_list: List[dict]):
        super()._append_awemes(aweme_list)
        with open(f"{download_path}/{self.type}_{self.id}.json", 'w', encoding='utf-8') as f:
            json.dump({'code': 1, 'num': len(self.results)}, f, ensure_ascii=False)

    def _append_users(self, user_list: List[dict]):
        super()._append_users(user_list)
        with open(f"{download_path}/{self.type}_{self.id}.json", 'w', encoding='utf-8') as f:
            json.dump({'code': 1, 'num': len(self.results)}, f, ensure_ascii=False)


def running(a: DouyinAPI, target: str):
    # a.aria2_conf = f"{download_path}/{a.type}_{a.id}.txt"
    a.run()
    with open(f"{download_path}/{a.type}_{a.id}.json", 'w', encoding='utf-8') as f:
        json.dump({
            'code': 0,
            'num': len(a.results),
            'data': a.results,
        }, f, ensure_ascii=False)
    running_ls.remove(target)


class API(BaseModel):
    Version: str = version
    Update: str = update
    Web: str = web
    GitHub: str = github
    Doc: str = doc
    Time: str = time.ctime()


class DataVideo(BaseModel):
    id: str
    desc: str
    download_addr: Union[str, List[str]]
    time: int = None
    digg_count: int = None
    share_count: int = None
    collect_count: int = None
    comment_count: int = None
    diggCount: int = None
    shareCount: int = None
    collectCount: int = None
    commentCount: int = None
    liveWatchCount: int = None
    music_title: str = None
    music_url: str = None
    cover: str = None
    tags: List[dict] = None


class DataUser(BaseModel):
    nickname: str
    sec_uid: str
    uid: str = None
    signature: str = None
    avatar: str = None
    short_id: str = None
    unique_id: str = None
    unique_id_modify_time: int = None
    aweme_count: int = None
    favoriting_count: int = None
    follower_count: int = None
    following_count: int = None
    constellation: int = None
    create_time: int = None
    enterprise_verify_reason: str = None
    is_gov_media_vip: bool = None
    total_favorited: int = None
    share_qrcode_uri: str = None


class DataSync(BaseModel):
    code: int = 0  # 0 已完成；1 正在运行
    num: int = 0
    data: List[Union[DataVideo, DataUser]] = None


class DataAsync(BaseModel):
    code: int = 0  # 0 成功投递；1 正在运行；
    url: str


class TypeAsync(str, Enum):
    post = 'post'
    like = 'like'
    favorite = 'favorite'
    music = 'music'
    search = 'search'
    collection = 'collection'
    follow = 'follow'
    fans = 'fans'


@app.get(
    "/",
    response_class=UJSONResponse,
    response_model=API,
)
def api(req: Request):
    return {'Web': req.base_url._url, 'Doc': f'{req.base_url._url}docs'}


@app.get(
    "/api/video",
    response_class=UJSONResponse,
    response_model=DataVideo,
    tags=['同步'],
    response_model_exclude_unset=True,
    response_model_exclude_defaults=True,
)
def get_video(url: str):
    start_browser()
    a = DouyinAPI(context=edge.context, url=url, type='video', down_path=download_path)
    a.run()
    return deepcopy(a.results[0])


@app.get("/api/info", response_class=UJSONResponse, tags=['同步'])
def get_info(url: str):
    start_browser()
    a = DouyinAPI(context=edge.context, url=url, down_path=download_path)
    a.has_more = False
    a.run()
    return deepcopy(a.info)


@app.get(
    "/api/{type_async}",
    response_class=UJSONResponse,
    response_model=DataAsync,
    tags=['异步'],
    status_code=201,
)
def start_async(type_async: TypeAsync, url: str, background_tasks: BackgroundTasks, req: Request):
    start_browser()
    target = f"{type_async.value}_{url.strip()}"
    a = DouyinAPI(context=edge.context, url=url, type=type_async.value, down_path=download_path)
    if target in running_ls:
        code = 1
        # return RedirectResponse(url=f"{req.base_url._url}/api/{type_async.value}/{a.id}", status_code=303)
    else:
        code = 0
        running_ls.append(target)
        background_tasks.add_task(running, a, target)
    return {'code': code, 'url': f"{req.base_url._url}api/{type_async.value}/{a.id}"}


@app.get(
    "/api/{type_async}/{id}",
    response_class=UJSONResponse,
    response_model=DataSync,
    tags=['同步'],
    response_model_exclude_unset=True,
    response_model_exclude_defaults=True,
)
def async_result(type_async: TypeAsync, id: str, down: bool = False):
    suffix = 'txt' if down else 'json'
    file = f"{download_path}/{type_async.value}_{id}.{suffix}"
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail="目标不存在")
    return FileResponse(file)


@app.get("/t", response_class=UJSONResponse)
def tt():
    print('start')
    time.sleep(3)
    print('end')
    return {"url": "type"}


@app.get("/init")
def start_browser():
    global edge
    if not isinstance(edge, Browser):
        edge = Browser(headless=False)


# 删除只读文件夹
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


# 每10分钟清理一次下载文件夹，删除1小时以前的记录
def clean_download_path():
    root = download_path
    if not os.path.exists(root): os.makedirs(root)
    while True:
        now = time.time()
        for file in os.listdir(root):
            file_path = os.path.join(root, file)
            if now - os.path.getmtime(file_path) > 60 * 60 * 1:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    shutil.rmtree(file_path, onerror=remove_readonly)
        time.sleep(60 * 10)


# 启动后执行
@app.on_event("startup")
def startup():
    threading.Thread(target=clean_download_path, daemon=True).start()


if __name__ == '__main__':
    # uvicorn api:app --host '0.0.0.0' --port 567 --reload
    # uvicorn.run("api:app", host='0.0.0.0', port=567, reload=True, limit_concurrency=5, use_colors=True)
    uvicorn.run("api:app", host='0.0.0.0', port=567, limit_concurrency=5, use_colors=True)
