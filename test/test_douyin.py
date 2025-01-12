from lib.douyin import Douyin

# ['post', 'like', 'music','hashtag', 'search', 'collection', 'favorite', 'video', 'note', 'user', 'live', 'follow', 'fans']
# 主页作品/喜欢/音乐/搜索（用户/视频/直播）/关注/粉丝/合集/收藏/视频/图文


def test_post():
    # ✅post 主页作品
    a = Douyin('https://v.douyin.com/iSNbMea7/')  # 视频
    # a = Douyin('https://v.douyin.com/i6G7cBea/', limit=22)  # 视频
    # a = Douyin(
    #     'https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4',
    #     limit=35
    # )  # 视频
    # a = Douyin('https://v.douyin.com/BK2VMkG/', limit=35)  # 图文
    # a = Douyin()  # 当前登录账号的作品
    a.run()
    assert len(a.results) > 0


def test_like():
    # ✅like 主页 喜欢
    a = Douyin(
        target='https://www.douyin.com/user/MS4wLjABAAAAtgtOJlIpkHE1db5HZ8rlFebkhL6p7L64k-lt1aXKHWd_K6XWNQKkegxn1TcLqJ7n',
        type='like',
        limit=33
    )
    # a = Douyin(type='like')  # 当前登录账号的喜欢
    a.run()
    assert len(a.results) > 0


def test_video():
    # ✅video 作品
    a = Douyin(target='https://v.douyin.com/UhYnoMS/')
    # a = Douyin(target='https://www.douyin.com/video/7395182828473847091')
    # a = Douyin(target='https://www.douyin.com/video/7393803716924640553')
    a.run()
    assert len(a.results) > 0


def test_note():
    # ✅note 作品
    a = Douyin(target='7233251303269453089', type='note')
    a.run()
    assert len(a.results) > 0


def test_music():
    # ✅music 音乐作品
    a = Douyin(target='https://v.douyin.com/BGPBena/', limit=33)
    # a = Douyin(target='https://www.douyin.com/music/6958014354780359461', limit=33)
    # a = Douyin(target='6958014354780359461', limit=33, type='music')
    a.run()
    assert len(a.results) > 0


def test_collection():
    # ✅collection 合集作品
    a = Douyin(
        target='https://www.douyin.com/collection/7018087406876231711', limit=23)
    # a = Douyin(target='7018087406876231711', type='collection', limit=23, cookie='chrome')
    a.run()
    assert len(a.results) > 0


def test_favorite():
    # ✅favorite 收藏作品
    a = Douyin(type='favorite')  # 当前登录账号的收藏
    a.run()
    assert len(a.results) > 0


def test_hashtag():
    # ✅hashtag 话题作品
    a = Douyin(target='https://www.douyin.com/hashtag/1588002245131278', limit=23)
    # a = Douyin(target='1588002245131278', type='hashtag', limit=23)
    a.run()
    assert len(a.results) > 0


def test_search():
    # ✅search 搜索 作品
    # a = Douyin(
    #     target='https://www.douyin.com/search/%E4%B8%8D%E8%89%AF%E4%BA%BA', limit=23)
    a = Douyin(target='不良人', type='search', limit=23)
    a.run()
    assert len(a.results) > 0


def test_user():
    # ⭕user 搜索 用户 可能会出现返回结果不稳定，原因不明
    # a = Douyin(target='xinhuashe', type='user', limit=22)
    a = Douyin(target='新华社', type='user', limit=22)
    a.run()
    assert len(a.results) > 0


def test_live():
    # ❌live 搜索 直播 ws接口 暂未实现
    a = Douyin(target='xinhuashe', type='live')
    a.run()
    assert len(a.results) > 0


def test_fans():
    # ✅fans 粉丝
    a = Douyin(
        target='https://www.douyin.com/user/MS4wLjABAAAAoOAjq-KborUpL2ezhf4SdMXL5Uge2Yu_sk2Fji-VvkQ?from_tab_name=main',
        type='fans', limit=60)
    a.run()
    assert len(a.results) > 0


def test_follow():
    # ✅follow 关注
    a = Douyin(
        target='https://www.douyin.com/user/MS4wLjABAAAAoOAjq-KborUpL2ezhf4SdMXL5Uge2Yu_sk2Fji-VvkQ',
        type='follow', limit=60)
    a.run()
    assert len(a.results) > 0

    # ✅自动读取cookie
    # a = Douyin(type='like', cookie='chrome')  # ✅ Chromed cookie很短但有效
    # a = Douyin(type='like', cookie='edge')  # ❌ Edge的cookie较长但无效

    #  python main.py -t https://v.douyin.com/BGf3Wp6/
    # a.get_user()
    # a.get_detail()
    # a.get_user_aweme()
    # a.get_user_info()
    # a.run()
    # a.download_all()
