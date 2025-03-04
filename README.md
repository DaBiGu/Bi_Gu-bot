<div align="center">

![](https://socialify.git.ci/DaBiGu/Bi_Gu-bot/image?description=1&font=Jost&logo=https%3A%2F%2Fs21.ax1x.com%2F2024%2F12%2F29%2FpAxNAKS.jpg&name=1&owner=1&pattern=Diagonal+Stripes&theme=Dark)

</div>

# 指令列表
### 按字母顺序排列

## `crypto`

* `/crypto` 返回过去2小时交易量涨幅300%及以上的币种
* `/crypto index` 返回当日市场恐慌&贪婪指数
* `/crypto [name]` 返回`[name]`币种过去24小时的15分钟k线图
* `/crypto [name] [interval]` 返回`[name]`币种的`15m/1h/4h/1D/1W`k线图
* 数据来自于[okx合约api](https://www.okx.com/docs-v5/en/#overview)

## `dice`
* `/rd xdy` 掷`x`个`y`面骰子
* `/rd xdy+z` 掷`x`个`y`面骰子，加`z`点修正值

## `github`
* `/github [username]` 查看`[username]`的github contributions chart
    * 搭载3d可视化插件[GitHub Isometric Contributions](https://chromewebstore.google.com/detail/github-isometric-contribu/mjoedlfflcchnleknnceiplgaeoegien)
    * 可选参数 `-2d` 返回原始2d图

## `gamelist`
* `/gamelist|gl` 查看本群游戏列表
* `/gamelist add|remove [game]` 本群游戏列表添加/删除`[game]` (需要管理员权限)
* `/gamelist join|quit [game]` 加入/退出`[game]`

## `group_msg`
* 自动复读群内消息，每2条重复消息复读一次 [40%概率触发]
* 群内消息防撤回
    * 使用`/antirecall on/off` 来开启/关闭此功能
* `/chatcount|cc today|yesterday|week|month|year` 返回今日/昨日/本周/本月/年度群内发言量top10
    * 可选参数 `-o` 以默认风格绘制
    * 数据统计开始于2024-09-06

## `help`
* `/about` 返回芙芙运行状态
* `/help` 返回当前支持的指令列表

## `image`
* `/喜报 [content]` 绘制内容为`content`的喜报
* `/悲报 [content]` 绘制内容为`content`的悲报
* 对图片回复`/对称 左|右|上|下 [percent]` 将图片(以`[percent]`%为轴)进行对称翻转
* `/ba [left] [right]` 生成自定义ba风格标题

## `mahjong`
* `/qh [username]` 查询`[username]`的近30局雀魂战绩
* 数据来自于[雀魂牌谱屋](https://amae-koromo.sapk.ch/)

## `ncm`
* `/ncm search [keyword] [num]` 网易云搜歌, 返回前`num`首搜索`keyword`的歌曲信息
* `/ncm id [song id]` 返回`id`歌曲的分享卡片
* `/ncm lyrics [song id]` 返回`id`歌曲的歌词

## `phigros`
* `/phigros search [songname]` 返回名为`songname`的phigros歌曲信息(支持模糊搜索)

## `setu`

* `/setu` 返回随机色图
* `/setu search` 对消息记录中的图片回复该指令进行以图搜图
* `/setu [tags]` 返回指定`tags`的色图；可以传入多个tag
* 数据来自于[色图api](https://github.com/yuban10703/SetuAPI)

## `sleep`

* `/sleep` 开始睡觉
* `/sleep [hh:mm]` 手动指定睡觉时间
* `/sleep [hh:mm] [utc±t]` 手动指定于指定时区的睡觉时间
* `/awake` 结束睡觉，返回本次睡眠总时长和本周睡眠情况统计
* `/awake [hh:mm]` 手动指定起床时间
* `/awake [hh:mm] [utc±t]` 手动指定于指定时区的起床时间
* `/sleep status` 查询本周睡眠情况统计

## `steam`
* `/steam [steamid]` 返回用户`[steamid]`的steam游戏状态
* `/steam info [steamid]` 返回用户`[steamid]`的总游戏时长/游玩时长top 10
* `/steam random` 从群友推荐列表中随机推荐一款游戏
    * 可选参数 `-a|all` 推荐的游戏可以来自其他群
* `/steam random add [appid]` 将游戏`[appid]`添加到本群推荐列表
* `/steam recommend [steamid]` 随机从用户`[steamid]`的库存推荐游戏
* `/steam recommend [steamid] [appid]` 从用户`[steamid]`的库存推荐id为`[appid]`的游戏
* `/steam search [name]` 返回名为`[name]`的steam游戏列表
* `/视奸群友` 一键视奸群友游戏状态
    * 使用`/视奸群友 add/remove [steamid]` 管理视奸群友列表
* 数据来自于[steam api](https://developer.valvesoftware.com/wiki/Steam_Web_API), [isThereAnyDeal](https://docs.isthereanydeal.com/)

## `wife`
* `/wife` 返回今日随机群老婆
    * 可选参数 `-s` 不@对方
    * 可选参数 `-f [@target]` 强娶`[target]`为群老婆
        * 只有25%概率成功并且每天只能使用一次
* `/wife bind|-b [qq1] [qq2]` 绑定群cp (需要`SUPERUSER`权限)
* `/rbq` 查看成为群老婆次数
    * 数据统计开始于2024-09-21

## `work`
* `/work start [name]` 开始名为`name`的工作
* `/work stop` 结束当前工作，返回本次工作总时长
* `/work today` 返回当前用户本日工作统计

## `miscellaneous`
* `/yuyu` 我有玉玉症
* `/fufu` 芙芙可爱捏
* `/help` 查看目前支持的指令列表
* `/ys|今日运势` 查看今日运势
* `/早安` 对芙芙说早安吧
* `/like` 让芙芙给你的qq资料卡点赞吧
* `/like auto` 每天自动点赞 (通常为服务器时间4am)
* `/plugin count|pc` 查看各插件使用量
* `/update log` 查看本项目更新日志
* `/update` 更新芙芙 (需要`SUPERUSER`权限)
* `/update chromedriver` 更新本机chromedriver (需要`SUPERUSER`权限)
* `/reboot` 重启芙芙 (需要`SUPERUSER`权限)
* `/recall` 让芙芙撤回自己的消息 (需要`SUPERUSER`权限)

### 更多最新最热功能随缘开发中