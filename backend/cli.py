# -*- encoding: utf-8 -*-
"""
@File    :   cli.py
@Time    :   2024年07月16日 12:05:55 星期二
@Author  :   erma0
@Version :   1.0
@Link    :   https://github.com/erma0
@Desc    :   命令行接口
"""

import os

import click
import ujson as json
from loguru import logger

# 统一使用绝对导入
from backend.constants import SETTINGS_FILE
from backend.lib.cookies import CookieManager
from backend.lib.douyin import Douyin
from backend.settings import settings

version = "V5.1.260118"
banner = rf"""
  ____                    _          ____                    _           
 |  _ \  ___  _   _ _   _(_)_ __    / ___|_ __ __ ___      _| | ___ _ __ 
 | | | |/ _ \| | | | | | | | '_ \  | |   | '__/ _` \ \ /\ / / |/ _ \ '__|
 | |_| | (_) | |_| | |_| | | | | | | |___| | | (_| |\ V  V /| |  __/ |   
 |____/ \___/ \__,_|\__, |_|_| |_|  \____|_|  \__,_| \_/\_/ |_|\___|_|   
                    |___/                                                
                              {version}
                Github: https://github.com/erma0/douyin
"""
print(banner)


@click.command()
@click.option(
    "-u",
    "--urls",
    type=click.STRING,
    multiple=True,
    help="作品/账号/话题/音乐等类型的URL链接/ID或搜索关键词，也可输入文件路径（文件内一行一个），可多次输入。",
)
@click.option(
    "-l",
    "--limit",
    type=click.INT,
    default=0,
    help="限制最大采集数量，默认不限制（0表示不限制）",
)
@click.option(
    "--no-download",
    is_flag=True,
    help="不下载文件，仅采集数据",
)
@click.option(
    "-t",
    "--type",
    type=click.Choice(
        [
            "post",
            "favorite",
            "music",
            "hashtag",
            "search",
            "following",
            "follower",
            "collection",
            "mix",
            "aweme",
        ],
        case_sensitive=False,
    ),
    default="post",
    help="采集类型，默认为post（主页作品）。支持：post/favorite/music/hashtag/search/following/follower/collection/mix/aweme",
)
@click.option(
    "-p",
    "--path",
    type=click.STRING,
    default="下载",
    help="下载文件夹路径，默认为[下载]",
)
@click.option(
    "-c",
    "--cookie",
    type=click.STRING,
    help=f"已登录账号的cookie，可填写在 {SETTINGS_FILE} 中",
)
@click.option(
    "--sort-type",
    type=click.Choice(["0", "1", "2"], case_sensitive=False),
    help="搜索排序（仅search类型）：0=综合，1=最多点赞，2=最新",
)
@click.option(
    "--publish-time",
    type=click.Choice(["0", "1", "7", "180"], case_sensitive=False),
    help="发布时间（仅search类型）：0=不限，1=一天内，7=一周内，180=半年内",
)
@click.option(
    "--filter-duration",
    type=click.Choice(["", "0-1", "1-5", "5-10000"], case_sensitive=False),
    help="视频时长（仅search类型）：空=不限，0-1=1分钟以下，1-5=1-5分钟，5-10000=5分钟以上",
)
def main(
    urls,
    limit,
    no_download,
    type,
    path,
    cookie,
    sort_type,
    publish_time,
    filter_duration,
):
    """
    抖音数据采集命令行工具

    示例：
    \b
    # 采集用户主页作品
    python -m backend.cli -u https://www.douyin.com/user/xxx -l 10

    \b
    # 搜索视频
    python -m backend.cli -u "美食" -t search --sort-type 2 --publish-time 7

    \b
    # 批量采集（从文件读取）
    python -m backend.cli -u urls.txt
    """

    # 构建筛选条件
    filters = {}
    if sort_type:
        filters["sort_type"] = sort_type
    if publish_time:
        filters["publish_time"] = publish_time
    if filter_duration is not None:
        filters["filter_duration"] = filter_duration


    # 加载 Cookie
    cookie_str = ""
    if cookie:
        # 命令行指定了 cookie
        logger.info("正在加载命令行指定的Cookie...")
        cookie_str = cookie.strip()
        if not cookie_str:
            logger.error("无法加载指定的Cookie")
            return
    else:
        # 从配置加载
        cookie_str = settings.get("cookie", "").strip()
        if cookie_str:
            logger.info("✓ 已从配置文件加载Cookie")

    # 如果没有 Cookie，提示用户输入（所有类型都需要Cookie）
    if not cookie_str:
        logger.warning("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.warning("⚠ 未找到Cookie配置")
        logger.info("配置方法：")
        logger.info(f"  方法1：在 {SETTINGS_FILE} 中设置 cookie 字段")
        logger.info("  方法2：使用 -c 参数：python -m backend.cli -c 'your_cookie'")
        logger.warning("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 询问用户是否现在输入Cookie
        try:
            cookie_input = input("请粘贴Cookie字符串: ").strip()
            if cookie_input:
                cookie_str = cookie_input
                logger.success("✓ Cookie已输入")
            else:
                logger.error("未输入Cookie，程序退出")
                return
        except (KeyboardInterrupt, EOFError):
            logger.warning("\n用户取消输入")
            return

    # 验证 Cookie
    if not CookieManager.validate_cookie(cookie_str):
        logger.error("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.error("✗ Cookie验证失败")
        logger.info("可能原因：")
        logger.info("  1. Cookie已过期，请重新获取")
        logger.info("  2. Cookie格式不正确")
        logger.info("  3. 账号已退出登录")
        logger.error("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return

    logger.success("✓ Cookie验证通过")

    if not urls:  # 未输入目标
        if type in ["favorite", "collection", "following", "follower"]:
            # 直接采集本账号
            logger.info(f"采集本账号的 {type} 数据")
            start("", limit, no_download, type, path, cookie_str, filters)
            return
        else:
            # 提示输入目标
            url_input = input(
                f"采集类型：{type}，请输入目标关键词/URL链接/ID或文件路径："
            ).strip()
            if not url_input:
                logger.error("未输入目标，退出程序")
                return
            urls = (url_input,)

    # 处理多个URL
    success_count = 0
    fail_count = 0

    for url in urls:
        url = url.strip()
        if not url:
            continue

        if os.path.exists(url):  # 文件路径
            logger.info(f"从文件读取目标：{url}")
            try:
                with open(url, "r", encoding="utf-8") as f:
                    lines = [line.strip()
                             for line in f.readlines() if line.strip()]

                if not lines:
                    logger.error(f"文件 [{url}] 中没有发现目标URL")
                    fail_count += 1
                    continue

                logger.info(f"文件中共有 {len(lines)} 个目标")
                for idx, line in enumerate(lines, 1):
                    logger.info(f"处理第 {idx}/{len(lines)} 个目标")
                    if start(line, limit, no_download, type, path, cookie_str, filters):
                        success_count += 1
                    else:
                        fail_count += 1
            except Exception as e:
                logger.error(f"读取文件失败: {e}")
                fail_count += 1
        else:
            # 单个URL
            if start(url, limit, no_download, type, path, cookie_str, filters):
                success_count += 1
            else:
                fail_count += 1

    # 输出统计信息
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.success(f"✓ 任务完成：成功 {success_count} 个，失败 {fail_count} 个")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def start(url, limit, no_download, type, path, cookie, filters):
    """
    启动单个采集任务

    Returns:
        bool: 是否成功
    """
    try:
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"开始采集任务")
        logger.info(f"  目标: {url or '本账号'}")
        logger.info(f"  类型: {type}")
        logger.info(f"  数量限制: {'不限' if limit == 0 else f'{limit}条'}")
        if filters:
            logger.info(f"  筛选条件: {filters}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 创建爬虫实例
        douyin = Douyin(
            target=url,
            limit=limit,
            type=type,
            down_path=path,
            cookie=cookie,
            user_agent=settings.get("userAgent", ""),
            filters=filters,
        )

        # 执行采集
        douyin.run()

        # 判断是否需要下载
        if no_download:
            logger.info("已跳过下载（--no-download）")
        elif douyin.type in ["following", "follower"]:
            logger.info("此类型不需要下载文件")
        else:
            # 调用下载模块
            from backend.lib.download import download

            logger.info("开始下载文件...")
            download(douyin.down_path, douyin.aria2_conf)

        return True

    except KeyboardInterrupt:
        logger.warning("用户中断任务")
        return False
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        import traceback

        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    main()
