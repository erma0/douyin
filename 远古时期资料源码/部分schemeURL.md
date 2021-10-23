# 抖音
#### 代码
```
home: "snssdk1128://feed?refer=web&gd_label={{gd_label}}",
detail: "snssdk1128://aweme/detail/{{id}}?refer=web&gd_label={{gd_label}}&appParam={{appParam}}&needlaunchlog=1",
user: "snssdk1128://user/profile/{{uid}}?refer=web&gd_label={{gd_label}}&type={{type}}&needlaunchlog=1",
challenge: "snssdk1128://challenge/detail/{{id}}?refer=web",
music: "snssdk1128://music/detail/{{id}}?refer=web",
live: "snssdk1128://live?room_id={{room_id}}&user_id={{user_id}}&from=webview&refer=web",
webview: "snssdk1128://webview?url={{url}}&from=webview&refer=web",
webview_fullscreen: "snssdk1128://webview?url={{url}}&from=webview&hide_nav_bar=1&refer=web",
poidetail: "snssdk1128://poi/detail?id={{id}}&from=webview&refer=web",
forward: "snssdk1128://forward/detail/{{id}}",
billboard_word: "snssdk1128://search/trending",
billboard_video: "snssdk1128://search/trending?type=1",
billboard_music: "snssdk1128://search/trending?type=2",
billboard_positive: "snssdk1128://search/trending?type=3",
billboard_star: "snssdk1128://search/trending?type=4"
```

#### 例子(部分参数可省略)

跳转主页并关注:
`snssdk1128://user/profile/72673737181?refer=web&gd_label=click_wap_profile_bottom&type=need_follow&needlaunchlog=1`
`snssdk1128://user/profile/72673737181?refer=web&gd_label=click_wap_download_follow&type=need_follow&needlaunchlog=1`

打开视频：
`snssdk1128://aweme/detail/6808453751930719502?refer=web&gd_label=click_wap_profile_feature&appParam=&needlaunchlog=1`

原声（同一个音乐的作品）：
`snssdk1128://music/detail/6680045787365247747?refer=web`

热搜榜：
`snssdk1128://search/trending`

最热视频: 
`snssdk1128://search/trending?type=1`

音乐榜: 
`snssdk1128://search/trending?type=2`

热搜（正能量）: 
`snssdk1128://search/trending?type=3`

明星爱豆榜:
 `snssdk1128://search/trending?type=4`

抖音内打开网址: 
`snssdk1128://webview?url=http%3A%2F%2Fbaidu.com&from=webview&refer=web`

抖音内打开网址（全屏）: 
`snssdk1128://webview?url=http%3A%2F%2Fbaidu.com&from=webview&hide_nav_bar=1&refer=web`

# 快手

#### 例子
```
用户主页
kwai://profile/1822393695
指定用户指定作品
kwai://work/5200813169502871215?userId=1822393695
指定作品
kwai://work/5200813169502871215
主页
kwai://home	

```


# 火山(测试发现不能到指定页面)
#### 代码
```

home: "snssdk1112://",
item: "snssdk1112://item?detail_label=return_page",
item_follow: "snssdk1112://item?auto_follow=1&detail_label=return_page",
profile: "snssdk1112://profile",
profile_follow: "snssdk1112://profile?auto_follow=1",
room: "snssdk1112://room",
webview: "snssdk1112://webview",
hash: "snssdk1112://hashtag_collection",
circle: "snssdk1112://moment_detail?media_type=5&show_moment_title=1&is_show_circle=1",
circle_hashtag: "snssdk1112://moment_feed"

```

#### 例子

```
打开主页
snssdk1112://profile?encryptedID=MS4wLjABAAAA1bv7T9AXNkAXGxBNJIY1VCOnfPx522hAtZRxs-Vaf_2PRpQYeXFqufqCZ2-3cnis
snssdk1112://profile?auto_follow=1&encryptedID=MS4wLjABAAAAKoog8IsMa69Zwo_38aUIPZqWfE6sw0-MPHi4yPBsLw5HUowT1WlhRRqmPcEj8Wpq&iid=109731506227
打开主页+关注
snssdk1112://profile?auto_follow=1&encryptedID=MS4wLjABAAAA1bv7T9AXNkAXGxBNJIY1VCOnfPx522hAtZRxs-Vaf_2PRpQYeXFqufqCZ2-3cnis

```

### 火山跳转方法（测试通过）

```
协议用最新的snssdk1112://
路径参数用旧的（老版本火山）
id=4164541389480203是从主页链接重定向里获取到的，在最后一段

打开主页
snssdk1112://profile?id=4164541389480203
打开主页+关注  未登录，测试无效
snssdk1112://profile?id=4164541389480203&auto_follow=1
打开作品
snssdk1112://item?id=6810288059397967111

```



## AutoJs调用方法：
```
"auto";
const _start_app = function() {
    app.startActivity({        
      action: "VIEW",
      data: "kwai://work/5200813169502871215", 
    });
  }
  _start_app();
```
## 按键精灵调用方法：
```
Import "ShanHai.lua"

//RunApp "com.ss.android.ugc.aweme"
ShanHai.execute("am start -a android.intent.action.VIEW  -d snssdk1128://aweme/detail/6682674534149000456")
//TracePrint ShanHai.GetTopActivity()
```
