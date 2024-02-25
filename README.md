# 指令列表
### 按字母顺序排列

## `crypto`

* `/crypto` 返回过去2小时交易量涨幅300%及以上的币种
* `/crypto [name]` 返回`[name]`币种过去24小时的15分钟k线图
* 数据来自于[okx合约api](https://www.okx.com/docs-v5/en/#overview)

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
* `/setu [tags]` 返回指定`tags`的色图；可以传入多个tag
* 数据来自于[色图api](https://github.com/yuban10703/SetuAPI)

## `sleep`

* `/sleep` 开始睡觉
* `/awake` 结束睡觉，返回本次睡眠总时长

## `steam`
* `/steam [steamid]` 返回用户`[steamid]`的steam游戏状态

## `work`

* `/work start [name]` 开始名为`name`的工作
* `/work stop` 结束当前工作，返回本次工作总时长
* `/work today` 返回当前用户本日工作统计

### `TODO`
* `mahjong` 自娱自乐立直麻将
