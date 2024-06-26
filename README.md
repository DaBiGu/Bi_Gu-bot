# 指令列表
### 按字母顺序排列

## `crypto`

* `/crypto` 返回过去2小时交易量涨幅300%及以上的币种
* `/crypto [name]` 返回`[name]`币种过去24小时的15分钟k线图
* `/crypto [name] [interval]` 返回`[name]`币种的`15m/1h/4h/1D/1W`k线图
* 数据来自于[okx合约api](https://www.okx.com/docs-v5/en/#overview)

## `help`
* `/help` 返回当前支持的指令列表

## `mahjong`
* `/qh [username]` 查询`[username]`的近30局雀魂战绩

## `ncm`
* `/ncm search [keyword] [num]` 网易云搜歌, 返回前`num`首搜索`keyword`的歌曲信息
* `/ncm id [song id]` 返回`id`歌曲的分享卡片

## `repeater`
* 自动复读群内消息，每2条重复消息复读一次

## `roll`
* `/rd xdy` 掷`x`个`y`面骰子
* `/rd xdy+z` 掷`x`个`y`面骰子，加`z`点修正值

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
* 数据来自于[steam api](https://developer.valvesoftware.com/wiki/Steam_Web_API)

## `work`
* `/work start [name]` 开始名为`name`的工作
* `/work stop` 结束当前工作，返回本次工作总时长
* `/work today` 返回当前用户本日工作统计

## `miscellaneous`
* `/yuyu` 我有玉玉症
* `/fufu` 芙芙可爱捏

