# TinyTinyRSS-OPML-to-MD-Table

## 功能
*适用于[Tiny Tiny RSS](https://tt-rss.org/)*
1. 获取opml文件
2. 解析opml文件
3. 按表格格式写入MarkDown中
4. 每次运行时，将自动修改README.md
   
## 使用
1. fork本仓库
2. 添加一个Repository secret。
3. 点击“New repository secret”按钮，添加变量：Name为`MY_CONFIG_JSON`,value请参考`config.json.example`。

## TodoList
- [x] 使用GithubAction实现定时更新
- [ ] 当添加新的订阅时自动更新
- [x] 每次运行时，将自动修改README.md
- [ ] 将订阅列表同步到博客中。

## 历程
1. 大部分时间是花在了如何获取opml文件上。Tiny Tiny RSS所给的文档较为精简，而网上相关的资料大都仅局限于如何部署。所以这一段只能是自己摸索。
   - TinyTinyRSS的网页版有给一个按钮能导出OPML，而这个按钮所指向的网址是`http://example.com/tt-rss/backend.php?op=opml&method=export'`。但它是有个鉴权操作的。需要登录。
   - 它的示例中有提供了一个登录的api调用，所以我开始的想法也是顺着这个来。想着直接添加data参数。但尝试了多种添加方式无果。
   - 后来注意到登录成功是会返回session值的，于是先用curl试验了下。
     ```bash
     # 登录并获取Session ID
     SESSION=$(curl -s -d '{"op":"login","user":"user","password":"password"}' http://example.com/tt-rss/api/ | python -c "import sys, json; print(json.load(sys.stdin)['content']['session_id'])")

     #获得opml文件
     curl -o my_tiny_tiny_rss.opml 'http://example.com/tt-rss/backend.php?op=opml&method=export' --cookie "ttrss_sid=${SESSION}"
     ```
   - 转写成python是用的request。其实现在回头想想，这应该是蛮基础的操作，而且session之前也有接触过。如果早点想起来的话是可以少花些时间的。
2. opml的解析有现成的库，用就是了。
3. 然后就是把一些个人信息抽出来写在配置文件中。这里踩了一个坑。`data = {'op': 'login', 'user': user, 'password': password}`,我开始的时候是这样写的`data = f"{{'op': 'login', 'user': {user}, 'password': {password}}}"`。后者虽然在形式上看着一样，但前者是json对象，后者是字符串。这里也给我提了个醒：Python虽然有动态类型这个特性，但还是要注意类型错误。
4. 最后是使用Github Action。之前也有使用过，但是是直接用的别人写好的workflow。所以也花了些时间学习了下。遇到的几个问题是
   - Yml文件的格式问题。这个可以用[YAML Validator](https://codebeautify.org/yaml-validator)来检查。Vscode应该也有相应的插件吧。
   - 运行时需要用到的变量，是用的secret。我之前以为secret的value只能是字符串。但[Github Action中python获取仓库的secrets](https://nekokiku.cn/2020/12/22/2020-12-22-Github-Action%E4%B8%ADpython%E8%8E%B7%E5%8F%96%E4%BB%93%E5%BA%93%E7%9A%84secrets/)中提到，可以把一整个yml文件放在value里面。所以我就想那json文件应该也可以。试了下确实能行。这样我的代码需要修改的地方就很少了。
   - workflow的触发方式,要添加手动触发，需加上`workflow_dispatch:`
5. 尝试实现功能4：每次运行时，将自动修改README.md;
   - 先是用正则表达式实现：读取文件内容到一个字符串中，再去匹配`r'## 我的订阅(.*)\n'`并替换。这里踩了一个坑：刚开始我写的是`r'## 我的订阅(.*?)\n'`，非贪婪匹配，只匹配了一个换行。
   - 感觉这个方法不是很好，就想着查找所要替换的内容的开头在文件中的位置，然后直接在那里开始写。这个折腾了比较久。尝试了如下写法：
  
     1.  这个的问题是还是将一整个文件的内容都赋给了一个字符串
      ```python
       readme = f.read() 
       start = readme.find('## 我的订阅\n')  
       f.seek(start)
      ```
     2. 写之前我看不出来代码有什么问题，但运行结果是在文件的末尾追加replace。觉得是write的问题，但不知道为什么
     ```python
        if '## 我的订阅\n' in line:
            start_line_num = line_num  # 记录所在行号
            f.seek(0)  # 重新定位到文件开头
            for i in range(start_line_num):  
                f.readline()  # 读取到标题所在行
            # print(f.tell()) 此时文件指针位于所需位置
            f.write(replace)  # 文件指针自动变到了末尾
            break
     ```
     3. 使用了seek
     ```python
        if '## 我的订阅\n' in line:
            title_pos = f.tell()  # 使用f.tell()记录标题行位置
            #print(title_pos)
            f.seek(title_pos)   # 定位到标题行位置  
            replace2 = md_text + md_table+'\n'
            f.write(replace2)  
            break      
     ```
6. 添加了运行时参数，这样开发的时候就不用特地去注释代码了。
   
## 参考
- [API Reference](https://tt-rss.org/wiki/ApiReference)
- [curl命令实现上网认证登录](https://www.cnblogs.com/jiangleads/p/10636696.html)
- [Github Action中python获取仓库的secrets](https://nekokiku.cn/2020/12/22/2020-12-22-Github-Action%E4%B8%ADpython%E8%8E%B7%E5%8F%96%E4%BB%93%E5%BA%93%E7%9A%84secrets/)
- [YAML Validator](https://codebeautify.org/yaml-validator)

## 我的订阅
**更新时间：2023-07-09**
| Title | Feed URL | Html URL|
| --- | --- | --- |
| EuDs's blog | https://euds63.github.io/atom.xml | http://euds63.github.io/|
| JerryQu 的小站 | https://imququ.com/rss.html | https://imququ.com|
| drdr.xp Blog | http://drmingdrmer.github.io/feed.xml | https://drmingdrmer.github.io/|
| 博客园 - 大码王 | https://feed.cnblogs.com/blog/u/601700/rss/ | https://feed.cnblogs.com/blog/u/601700/rss/|
| 胡涂说 | https://hutusi.com/feed.xml | https://hutusi.com/|
| Chenyang's blog | http://blog.ch3nyang.top/feed.xml | https://wcy-dt.github.io|
| Plum's Blog | https://plumz.me/feed/ | https://plumz.me/|
| Randy's Blog | https://lutaonan.com/rss.xml | https://lutaonan.com/|
| 王子亭的博客 | https://jysperm.me/atom.xml | https://jysperm.me/|
| Pockies | https://pockies.github.io/feed.xml | http://pockies.github.io/|
| Yuko's Blog | https://yuukoamamiya.github.io/index.xml | https://blog.amamiyayuuko.com/|
| yihong0618's gitblog | https://raw.githubusercontent.com/yihong0618/gitblog/master/feed.xml | https://github.com/yihong0618/gitblog|
| Kaede Akatsuki | http://kaedea.com/atom.xml | https://kaedea.com/|
| 无二博客 | https://1kb.day/atom.xml | None|
| 峡州仙士 | https://cjh0613.com/categories/%E6%8A%80%E6%9C%AF/rss2.xml | https://cjh0613.com/|
| 川叶 :: 不舍昼夜 | https://blog.lishun.me/feed.xml | https://blog.lishun.me/|
| / Blog - MAKE / MUSIC | http://www.makemusic.sg/blog?format=rss | http://www.makemusic.sg/blog/|
| AabyssZG's Blog | https://blog.zgsec.cn/index.php/feed/ | https://blog.zgsec.cn/|
| Free Mind | https://freemind.pluskid.org/rss.xml | http://freemind.pluskid.org|
| Grifel | https://grifel.dev/rss.xml | https://grifel.dev/|
| Josh Comeau's blog | https://www.joshwcomeau.com/rss.xml | https://www.joshwcomeau.com/|
| JungleyNet | https://www.jungley.net/rss/ | https://www.jungley.net/|
| Kivinsae's Nest | https://www.kivinsae.com/atom.xml | https://www.kivinsae.com/|
| Konata Tech Blog | https://tech.konata.co/atom.xml | https://tech.konata.co/|
| Largesse's blog | https://largesse.netlify.app/atom.xml | https://largesse.12306.recipes/|
| LearnData-开源笔记 | https://newzone.top/rss.xml | https://newzone.top/|
| MINIRPLUS | https://blog.minirplus.com/feed/ | https://blog.minirplus.com|
| Manjusaka | https://www.manjusaka.blog/atom.xml | https://manjusaka.blog/|
| OhYee 博客 | https://www.ohyee.cc/rss.xml | https://www.ohyee.cc|
| Plum's Blog | https://plumz.me/feed/rss/ | https://plumz.me/|
| Posts on 生活不在别处 | https://www.kuact.com/post/index.xml | https://www.kuact.com/post/|
| QIWIHUI | https://qiwihui.com/atom.xml | https://qiwihui.com/|
| Skywind Inside | https://www.skywind.me/blog/feed | https://www.skywind.me/blog|
| SuikaXhq's Homepage | https://suikaxhq.top/index.xml | https://suikaxhq.top/|
| To the Lighthouse | https://owlswims.com/feed/ | https://owlswims.com/|
| Verne in GitHub | https://einverne.github.io/atom.xml | https://blog.einverne.info|
| Vincent's Notes | https://missuo.me/index.xml | https://missuo.me/|
| Yulin Lewis' Blog | https://lewky.cn/index.xml | https://lewky.cn/|
| Zxch3n's Blog | https://www.zxch3n.com/rss.xml | https://www.zxch3n.com|
| [Unknown] | https://blog.sina.com.cn/rss/1283569510.xml | https://blog.sina.com.cn/rss/1283569510.xml|
| jacobian.org | https://jacobian.org/index.xml | https://jacobian.org/|
| kekxv 技术博客 | https://kekxv.github.io/feed.xml | http://kekxv.github.io/|
| piglei | https://www.piglei.com/feeds/latest/ | http://www.zlovezl.cn/|
| plantegg | https://plantegg.github.io/atom.xml | https://plantegg.github.io/|
| walterlv | https://blog.walterlv.com/feed.xml | https://blog.walterlv.com/|
| ximu | https://xlog.timero.xyz/feed/xml | https://ximu.xlog.app|
| 一派胡言 | https://zhangyet.github.io/feed.xml | https://zhangyet.github.io/|
| 中文日志 on Rehoni | 罗皓 | https://rehoni.github.io/cn/index.xml | https://rehoni.github.io/cn/|
| 博客园 - marsggbo | https://www.cnblogs.com/marsggbo/rss | https://www.cnblogs.com/marsggbo/rss|
| 博客园 - nmydt | https://www.cnblogs.com/nmydt/rss | https://www.cnblogs.com/nmydt/rss|
| 土豆不好吃 | https://dmesg.app/feed | https://dmesg.app|
| 奇客Solidot–传递最新科技情报 | https://www.solidot.org/index.rss | https://www.solidot.org|
| 好好学习的郝 | https://www.voidking.com/atom.xml | https://www.voidking.com/|
| 尚弟的小笔记 | https://blog.shrp.me/rss.xml | https://blog.shrp.me/|
| 岁寒 | https://lvwenhan.com/rss.php | https://lvwenhan.com/|
| 戴兜的小屋 | https://daidr.me/rsslatest.xml | https://daidr.me|
| 扯氮集 | http://weiwuhui.com/feed | http://weiwuhui.com|
| 木木木木木 | https://immmmm.com/atom.xml | https://immmmm.com/|
| 机械境 | https://gythialy.github.io/atom.xml | https://gythialy.github.io/|
| 此方方有限公司 | https://blog.konata.co/?feed=rss2 | https://blog.konata.co|
| 生活不在别处 | https://www.kuact.com/index.xml | https://www.kuact.com/|
| 罗磊的独立博客 | https://luolei.org/feed/ | https://luolei.org/|
| 自拙集 | https://densecollections.top/atom.xml | http://densecollections.top/|
| 致远博客 - 开往-Travelling 的评论 | https://blog.uniartisan.com/feed/atom/archives/Travelling.html | https://blog.uniartisan.com/archives/Travelling.html|
| 菠菜眾長 | https://lruihao.cn/index.xml | https://lruihao.cn/|
| 辛未羊的网络日志 | https://panqiincs.me/atom.xml | https://panqiincs.me/|
| 青山绿水 | https://eirms.com/feed | https://eirms.com|
| Li. | https://bye-lemon.github.io/atom.xml | http://bye-lemon.github.io/|
| Pine Wu's Blog | https://blog.matsu.io/feed.xml | http://blog.matsu.io|
| 万事屋 | https://tcya.xyz/feed.xml | https://tcya.xyz/|
| 云风的 BLOG | http://blog.codingnow.com/atom.xml | https://blog.codingnow.com/|
| 少数派 | https://sspai.com/feed | https://sspai.com|
| 开源实验室 | http://www.kymjs.com/feed.xml | https://www.kymjs.com/|
| 海德沙龙·翻译组 | https://translations.headsalon.org/index.xml | https://translations.headsalon.org/|
| 路人酱 | https://passerby5566.xlog.app/feed/xml | https://passerby5566.xlog.app|
| 酷 壳 – CoolShell | https://coolshell.cn/feed | https://coolshell.cn|

