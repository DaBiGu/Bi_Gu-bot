import textwrap
class Helper_Messages:
    def __init__(self):
        self.helper_messages = ["""
                                芙芙目前支持的指令列表(按首字母顺序排列):
                                ———————— crypto ————————
                                /crypto 查看过去2小时交易量涨幅300%及以上的币种
                                /crypto index 查看当日市场恐慌&贪婪指数
                                /crypto [name] 查看[name]币种过去24小时的15分钟k线图
                                /crypto [name] [interval] 返回[name]币种的 15m/1h/4h/1D/1W k线图
                                
                                ———————— dice ————————
                                /rd xdy 掷x个y面骰子
                                /rd xdy+z 掷x个y面骰子,加z点修正值
                                
                                ———————— github ————————
                                /github [username] 查看[username]的github contributions chart
                                    可选参数 -2d 返回原始2d图
                                ———————— group_msg ————————
                                /chatcount|cc today|yesterday|week|month|year
                                    查看今日/昨日/本周/本月/年度群内b话量top10
                                    可选参数 -o 以默认风格绘制
                                    数据统计开始于2024-09-06
                                
                                ———————— image ————————
                                /喜报 [content] 绘制内容为[content]的喜报
                                /悲报 [content] 绘制内容为[content]的悲报
                                对图片回复 /对称 左|右|上|下 [percent] 将图片(以[percent]%为轴)进行对称翻转
                                /ba [left] [right] 生成自定义ba风格标题
                                
                                ———————— mahjong ————————
                                /qh [username] 查看[username]的近30局雀魂战绩
                                
                                ———————— ncm ————————
                                /ncm search [keyword] [num] 网易云搜索前num首关键词为keyword的歌曲
                                /ncm id [song_id] 获取[song_id]对应的歌曲卡片
                                /ncm lyrics [song_id] 获取id为[song_id]歌曲的歌词卡片
                                
                                ———————— phigros ————————
                                /phigros search [songname] 搜索歌名为[songname]的phigros歌曲信息(支持模糊匹配)
                                ———————— setu ————————
                                /setu 返回随机色图
                                /setu search 对消息记录中的图片回复该指令进行以图搜图
                                /setu [tags] 返回指定tags的色图; 可以传入多个tag, 以空格分隔
                                
                                ———————— sleep ————————
                                /sleep 开始睡觉并记录睡觉时间
                                /sleep [hh:mm] 手动指定睡觉时间
                                /sleep [hh:mm] [utc±t] 手动指定于指定时区的睡觉时间
                                /awake 结束睡觉, 查看本次睡觉时长和本周睡眠状况统计
                                /awake [hh:mm] 手动指定起床时间
                                /awake [hh:mm] [utc±t] 手动指定于指定时区的起床时间
                                /sleep status 查看本周睡眠状况统计
                                """,
                                """
                                ———————— steam ————————
                                /steam [steamid] 查看用户[steamid]的steam游戏状态
                                /steam info [steamid] 查看用户[steamid]的总游戏时长和游玩时长top 10
                                /steam random 从群友推荐列表中随机推荐一款游戏
                                    可选参数 -a|all 使推荐的游戏可以来自其他群 
                                /steam random add [appid] 将游戏[appid]添加到本群推荐列表
                                /steam recommend [steamid] 随机从用户[steamid]的库存推荐游戏
                                /steam recommend [steamid] [appid] 从用户[steamid]的库存推荐id为[appid]的游戏
                                /steam search [name] 搜索名为[name]的steam游戏
                                /视奸群友 一键视奸群友游戏状态 
                                使用/视奸群友 add|remove [steamid] 管理视奸群友列表
                                
                                ———————— wife ————————
                                /wife 今日随机群老婆 
                                    可选参数 -s 不@对方
                                    可选参数 -f [@target] 强娶[target]为群老婆
                                        *只有25%概率成功并且每天只能使用一次
                                /rbq 查看成为群老婆次数
                                    数据统计开始于2024-09-21
                                
                                ———————— work ————————
                                /work start [name] 开始一项名为[name]的工作
                                /work stop 结束当前工作, 查看本次工作时长
                                /work today 查看本日工作统计
                                
                                ———————— miscellaneous ————————
                                /yuyu 我有玉玉症
                                /fufu 芙芙可爱捏
                                /help 查看指令列表
                                /about 查看芙芙运行状态 
                                /ys|今日运势 查看今日运势
                                /早安 对芙芙说早安吧 (此条命令需要@芙芙)
                                /update log 查看芙芙更新日志
                                ———————— SUPERUSER ————————
                                (以下指令需要开发者权限)
                                /antirecall on|off 开启/关闭群内消息防撤回
                                /update 更新芙芙(与github同步)
                                /update chromedriver 更新chromedriver
                                /reboot 重启芙芙
                                /recall 让芙芙撤回自己的消息
                                /wife bind|-b [qq1] [qq2] 绑定群cp
                                """]

        self.update_logs = ["""
                            ———————— Full update log of Bi_Gu-bot ————————
                            Feb 25 2024: 初代版本上线, 搭载插件crypto|ncm|roll|setu|sleep|steam|work
                            Feb 27 2024: 统计每周平均睡眠时间
                            Feb 28 2024: /help查看支持的指令列表
                            
                            Mar 1 2024: 调用saucenao API实现以图搜图功能
                            Mar 3 2024: 绘制每周睡眠情况柱状统计图
                            Mar 7 2024: 绘制喜报和悲报
                            Mar 11 2024: 手动指定睡觉和起床时间
                            Mar 15 2024: 记录睡眠时间时手动指定所在时区
                            Mar 16 2024: 支持更多时间间隔的k线图绘制
                            Mar 18 2024: 将所有的用户qq号改为返回qq昵称
                            
                            Apr 1 2024: 获取玩家雀魂近期战绩
                            Apr 5 2024: 更好的雀魂战绩图绘制方式
                            
                            Jun 29 2024: 复读插件忽略图片和表情
                            
                            Jul 12 2024: 增添群内消息防撤回功能
                            Jul 19 2024: 给复读插件增加冷却时间
                            
                            Aug 4 2024: 绘制crypto市场恐惧&贪婪指数
                            Aug 5 2024: 视奸群友steam游戏状态
                            Aug 6 2024: 修复网易云音乐分享卡片; 找不到指定tag的色图时通知用户
                            Aug 7 2024: 增添图片对称功能; 美化指令列表返回方式
                            Aug 8 2024: 支持指定比例对称图片; Ciallo~(∠・ω< )⌒☆
                            Aug 9 2024: 用户退群时进行提醒
                            Aug 13 2024: 支持通过名称搜索steam游戏
                            Aug 15 2024: 支持从群友库存随机推荐steam游戏
                            Aug 16 2024: 手动指定appid推荐steam游戏; 支持通过指令自动与github同步
                            Aug 19 2024: 随机群老婆
                            Aug 22 2024: 新用户进群时进行欢迎
                            
                            Sep 4 2024: 随机群老婆只在活跃群友中选取
                            Sep 6 2024: 支持统计群友b话量
                            Sep 7 2024: 支持生成ba风格标题图片; 支持获取随机今日运势 
                            Sep 8 2024: 支持对芙芙说早安; 支持记录群友的游戏推荐列表并从中随机推荐游戏 
                            Sep 9 2024: 推荐列表记录群名和推荐人
                            Sep 12 2024: 更好的网易云歌曲歌词卡片绘制方式
                            Sep 13 2024: 全面整理数据储存方式
                            Sep 15 2024: 群友最后发言时间改为本地记录
                            Sep 17 2024: 增加手绘风格绘制群友b话量统计; 芙芙自己也会加入统计
                            Sep 19 2024: 自动更新chromedriver
                            Sep 21 2024: 支持统计群老婆次数
                            Sep 30 2024: 支持指定对象强娶群老婆功能
                            """,
                            """
                            Nov 3 2024: 支持绑定群cp 
                            Nov 8 2024: 更好的网易云音乐歌曲搜索卡片
                            Nov 17 2024 支持模糊搜索phigros歌曲
                            Nov 20 2024 支持查询用户github contributions chart
                            Nov 23 2024 支持查看昨日群发言排行
                            Nov 26 2024 增加用户黑名单
                            
                            Dec 18 2024 给插件增加全局开关模块
                            Dec 21 2024 重构插件创建方式
                            Dec 22 2024 给每个插件添加单独的帮助信息; 支持qq资料卡点赞
                            Dec 25 2024 支持查看用户steam总游戏时长/游玩时长top 10
                            Dec 27 2024 支持查看bot运行状态
                            """]
    
    def get_helper_messages(self):
        return [textwrap.dedent(message).strip() for message in self.helper_messages]
    
    def get_update_logs(self):
        return [textwrap.dedent(log).strip() for log in self.update_logs]