from douyin import Douyin


if __name__ == "__main__":
    # ['post', 'like', 'music','hashtag', 'search', 'collection', 'favorite', 'video', 'note', 'user', 'live', 'follow', 'fans']
    # 主页作品/喜欢/音乐/搜索（用户/视频/直播）/关注/粉丝/合集/收藏/视频/图文

    # ✅post 主页作品
    # a = Douyin('https://v.douyin.com/i6G7cBea/', limit=22)  # 视频
    # a = Douyin(
    #     'https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4',
    #     limit=35
    # )  # 视频
    # a = Douyin('https://v.douyin.com/BK2VMkG/', limit=35)  # 图文
    # a = Douyin()  # 当前登录账号的作品

    # ✅post 主页 喜欢
    # a = Douyin(
    #     target='https://www.douyin.com/user/MS4wLjABAAAAtgtOJlIpkHE1db5HZ8rlFebkhL6p7L64k-lt1aXKHWd_K6XWNQKkegxn1TcLqJ7n',
    #     type='like',
    #     limit=33
    # )
    # a = Douyin(type='like')  # 当前登录账号的喜欢

    # ✅自动读取cookie
    # a = Douyin(type='like', cookie='chrome')  # ✅ Chromed cookie很短但有效
    # a = Douyin(type='like', cookie='edge')  # ❌ Edge的cookie较长但无效

    # ✅video 作品
    # a = Douyin(target='https://v.douyin.com/UhYnoMS/')
    # a = Douyin(target='https://www.douyin.com/video/7395182828473847091')
    # a = Douyin(target='https://www.douyin.com/video/7393803716924640553')

    # ✅note 作品
    # a = Douyin(target='7233251303269453089', type='note')

    # ✅music 音乐作品
    # a = Douyin(target='https://v.douyin.com/BGPBena/', limit=33)
    # a = Douyin(target='https://www.douyin.com/music/6958014354780359461', limit=33)
    # a = Douyin(target='6958014354780359461', limit=33, type='music')

    # ✅collection 合集作品
    # a = Douyin(target='https://www.douyin.com/collection/7018087406876231711', limit=23)
    # a = Douyin(target='7018087406876231711', type='collection', limit=23, cookie='chrome')

    # ✅favorite 收藏作品
    # a = Douyin(type='favorite')  # 当前登录账号的收藏

    # ✅hashtag 话题作品
    a = Douyin(target='https://www.douyin.com/hashtag/1588002245131278', limit=23)
    # a = Douyin(target='1588002245131278', type='hashtag', limit=23)

    # ✅search 搜索 作品
    # a = Douyin(
    #     target='https://www.douyin.com/search/%E4%B8%8D%E8%89%AF%E4%BA%BA', limit=23)
    # a = Douyin(target='不良人', type='search', limit=23)

    # ⭕user 搜索 用户 可能会出现返回结果不稳定，原因不明
    # a = Douyin(target='xinhuashe', type='user', limit=22)
    # a = Douyin(target='新华社', type='user', limit=22)

    # ❌live 搜索 直播 ws接口 暂未实现
    # a = Douyin(target='xinhuashe', type='live')

    # ✅fans 粉丝
    # a = Douyin(
    #     target='https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4',
    #     type='fans',
    #     limit=60)

    # ✅follow 关注
    # a = Douyin(
    #     target='https://www.douyin.com/user/MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4',
    #     type='follow')

    #  python main.py -t https://v.douyin.com/BGf3Wp6/
    # a.get_user()
    # a.get_detail()
    # a.get_user_aweme()
    # a.get_user_info()
    a.run()
    a.download_all()
