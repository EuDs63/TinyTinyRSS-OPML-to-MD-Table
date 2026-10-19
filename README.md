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
7. 尝试实现自动推送到其他仓库的Github Action，最后发现我实际的需求其实没必要这样做。但从中收获了几点：
   - `actions/checkout@v3`的使用：
     ```
      - name: clone EuDs63/EuDs63.github.io
        uses: actions/checkout@v3
        with:
        repository: 'EuDs63/EuDs63.github.io'
     ```
   - `actions/checkout@v3`后，路径实例
     `/home/runner/work/TinyTinyRSS-OPML-to-MD-Table/TinyTinyRSS-OPML-to-MD-Table`
   
   
## 参考
- [API Reference](https://tt-rss.org/wiki/ApiReference)
- [curl命令实现上网认证登录](https://www.cnblogs.com/jiangleads/p/10636696.html)
- [Github Action中python获取仓库的secrets](https://nekokiku.cn/2020/12/22/2020-12-22-Github-Action%E4%B8%ADpython%E8%8E%B7%E5%8F%96%E4%BB%93%E5%BA%93%E7%9A%84secrets/)
- [YAML Validator](https://codebeautify.org/yaml-validator)

## 我的订阅
**更新时间：2026-10-19**
| Title | Feed URL | Html URL|
| --- | --- | --- |
| [Unknown] | https://blog.sina.com.cn/rss/1283569510.xml | https://blog.sina.com.cn/rss/1283569510.xml|
| [Unknown] | https://s3.laisky.com/public/rss.xml | None|
| A Cup of Air | https://acupofair.github.io/index.xml | https://acupofair.github.io/|
| Ash Furrow's Blog | https://ashfurrow.com//feed.xml | https://ashfurrow.com|
| Bigbyto | https://wiyi.org/feed.xml | https://wiyi.org/|
| blog.thea.codes | https://blog.thea.codes/feed.xml | https://blog.thea.codes|
| brianmay.com | https://brianmay.com/feed/ | https://brianmay.com/|
| brr | https://brr.fyi/feed.xml | https://brr.fyi/|
| ByteByteGo Newsletter | https://blog.bytebytego.com/feed | https://blog.bytebytego.com|
| Chew’s Everyday Blog | https://excitedspider.github.io/feed.xml | https://excitedspider.github.io/|
| Chrissy LeMaire's blog on netnerds.net | https://blog.netnerds.net/index.xml | https://blog.netnerds.net/|
| Cmj's Blog | https://blog.caomingjun.com/atom.xml | https://blog.caomingjun.com/|
| Design Scenes | https://fenx.work/rss/ | https://fenx.work/|
| Developer Way: improve your technical skills with in-depth explanations, practical advices and useful tips and tricks. | https://www.developerway.com/rss.xml | https://www.developerway.com|
| Drew DeVault's blog | https://drewdevault.com/blog/index.xml | https://drewdevault.com|
| EuDs's Blog | https://ds63.eu.org/index.xml | https://ds63.eu.org/|
| fatedier blog | https://blog.fatedier.com/index.xml | https://blog.fatedier.com/|
| Free Mind | https://freemind.pluskid.org/rss.xml | http://freemind.pluskid.org|
| Frost's Blog | https://frostming.com/feed.xml | https://frostming.com/|
| Grifel | https://grifel.dev/rss.xml | https://grifel.dev/|
| Hanshi Sun's Blog | https://blog.preminstrel.com/index.xml | https://blog.preminstrel.com/|
| Homepage on Rehoni \| 罗皓 | https://rehoni.github.io/index.xml | https://rehoni.github.io/|
| Huli's blog | https://life.huli.tw/atom.xml | https://life.huli.tw/|
| Huli's blog | https://blog.huli.tw/atom-ch.xml | https://blog.huli.tw/|
| jacobian.org | https://jacobian.org/index.xml | https://jacobian.org/|
| Jesse Li | https://blog.jse.li/index.xml | https://blog.jse.li/|
| Joel on Software | https://www.joelonsoftware.com/feed/ | https://www.joelonsoftware.com|
| Josh Comeau's blog | https://www.joshwcomeau.com/rss.xml | https://www.joshwcomeau.com/|
| Julia Evans | https://jvns.ca/atom.xml | http://jvns.ca|
| Just My Simple Life | https://chils27.wordpress.com/feed/ | https://chils27.wordpress.com|
| kekxv 技术博客 | https://kekxv.github.io/feed.xml | http://kekxv.github.io/|
| Kivinsae's Nest | https://www.kivinsae.com/atom.xml | https://www.kivinsae.com/|
| Kiyan's Blog | https://blog.dotvast.cc/index.xml | https://blog.dotvast.cc/|
| kxxt's blog | https://www.kxxt.dev/rss.xml | https://www.kxxt.dev|
| laike9m's blog | https://laike9m.com/blog/rss/ | https://laike9m.com/blog/rss|
| Largesse's blog | https://largesse.netlify.app/atom.xml | https://largesse.12306.recipes/|
| LearnData-开源笔记 | https://newzone.top/rss.xml | https://newzone.top/|
| Li. | https://bye-lemon.github.io/atom.xml | http://bye-lemon.github.io/|
| Log4D | https://blog.alswl.com/atom.xml | https://blog.alswl.com/|
| Manjusaka | https://www.manjusaka.blog/atom.xml | https://manjusaka.blog/|
| Max's Zone | https://blog.maxxsoft.net/index.php/feed/ | https://blog.maxxsoft.net/|
| MeteorCollector | https://meteorcollector.github.io//feed.xml | https://meteorcollector.github.io//|
| Michael的博客 | https://michaeljier.cn/feed.xml | https://www.michaeljier.cn/blog|
| MINIRPLUS | https://blog.minirplus.com/feed/ | https://blog.minirplus.com|
| mrchi 的博客 | https://mrchi.cc/index.xml | https://mrchi.cc/|
| Normal Mode | https://normalmo.de/index.xml | https://normalmo.de/|
| OhYee 博客 | https://www.ohyee.cc/rss.xml | https://www.ohyee.cc|
| Owen的博客 | https://www.owenyoung.com/atom.xml | https://www.owenyoung.com|
| Pig Fang | https://blog.gplane.win/atom.xml | https://blog.gplane.win/|
| piglei | https://www.piglei.com/feeds/latest/ | http://www.zlovezl.cn/|
| Pine Wu's Blog | https://blog.matsu.io/feed.xml | http://blog.matsu.io|
| Plum's Blog | https://plumz.me/feed/ | https://plumz.me/|
| Plum's Blog | https://plumz.me/feed/rss/ | https://plumz.me/|
| Pockies | https://pockies.github.io/feed.xml | http://pockies.github.io/|
| Posts on Nova Kwok's Awesome Blog | https://nova.moe/posts/index.xml | https://nova.moe/posts/|
| Posts on 生活不在别处 | https://www.kuact.com/post/index.xml | https://www.kuact.com/post/|
| PragDave's Blog | https://pragdave.me/thoughts/index.xml | https://pragdave.me/thoughts/index.html|
| QIWIHUI | https://qiwihui.com/atom.xml | https://qiwihui.com/|
| Randy's Blog | https://lutaonan.com/rss.xml | https://lutaonan.com/|
| Reorx’s Forge | https://reorx.com/feed.xml | https://reorx.com/|
| Richard Stallman's Political Notes | https://stallman.org/rss/rss.xml | https://stallman.org/archives/polnotes.html|
| rxliuli blog | https://blog.rxliuli.com/atom.xml | https://blog.rxliuli.com/|
| Shaleen Jain | https://shaleenjain.com/atom.xml | https://shaleenjain.com|
| Skywind Inside | https://www.skywind.me/blog/feed | https://www.skywind.me/blog|
| SuikaXhq's Homepage | https://suikaxhq.top/index.xml | https://suikaxhq.top/|
| Sukka's Blog | https://blog.skk.moe/atom.xml | https://blog.skk.moe/|
| TARESKY | https://taresky.com/feed.xml | https://taresky.com/|
| TheCollector | https://www.thecollector.com/rss | https://www.thecollector.com|
| This Cute World | https://thiscute.world/index.xml | https://thiscute.world/|
| To the Lighthouse | https://owlswims.com/feed/ | https://owlswims.com/|
| tonsky.me | https://tonsky.me/atom.xml | https://tonsky.me/|
| Tw93 的博客 | https://tw93.fun/feed.xml | https://tw93.fun|
| Verne in GitHub | https://einverne.github.io/atom.xml | https://blog.einverne.info|
| Vincent's Notes | https://missuo.me/index.xml | https://missuo.me/|
| walterlv | https://blog.walterlv.com/feed.xml | https://blog.walterlv.com/|
| Web技术试炼地 | https://www.52cik.com/atom.xml | http://www.52cik.com/|
| Wilson's blog | https://wilsonxia.cn/atom.xml | https://wilsonxia.cn/|
| www.micahlerner.com | https://www.micahlerner.com/feed.xml | http://www.micahlerner.com/|
| yihong0618's gitblog | https://raw.githubusercontent.com/yihong0618/gitblog/master/feed.xml | https://github.com/yihong0618/gitblog|
| Yuko's Blog | https://yuukoamamiya.github.io/index.xml | https://blog.amamiyayuuko.com/|
| Yulin Lewis' Blog | https://lewky.cn/index.xml | https://lewky.cn/|
| Zar_SY \| 小屋 | https://daftneko.com/atom.xml | https://daftneko.com|
| Zgao's blog | https://zgao.top/feed/ | https://zgao.top|
| zmt | https://zmt.pub/feed/ | https://zmt.pub|
| zu1k | https://zu1k.com/rss.xml | https://zu1k.com/|
| Zxch3n's Blog | https://www.zxch3n.com/rss.xml | https://www.zxch3n.com|
| 一个球的博客 | https://jw1.dev/atom.xml | https://jw1.dev/|
| 一派胡言 | https://zhangyet.github.io/feed.xml | https://zhangyet.github.io/|
| 万事屋 | https://tcya.xyz/feed.xml | https://tcya.xyz/|
| 中文日志 on Rehoni \| 罗皓 | https://rehoni.github.io/cn/index.xml | https://rehoni.github.io/cn/|
| 云游君的小站 | https://www.yunyoujun.cn/atom.xml | https://www.yunyoujun.cn/|
| 云风的 BLOG | https://blog.codingnow.com/atom.xml | https://blog.codingnow.com/|
| 余光的部落格 | https://idawnlight.com/atom.xml | https://idawnlight.com/|
| 兮陌 | https://www.simaek.com/feed/ | https://www.simaek.com/|
| 初之音 | https://www.himiku.com/feed/ | https://www.himiku.com/|
| 前端小武的博客 | https://xuexb.com/rss.html | https://xuexb.com|
| 博客园 - 大码王 | https://feed.cnblogs.com/blog/u/601700/rss/ | https://feed.cnblogs.com/blog/u/601700/rss/|
| 卡瓦邦噶！ | https://www.kawabangga.com/feed | https://www.kawabangga.com|
| 土豆不好吃 | https://dmesg.app/feed | https://dmesg.app|
| 奇客Solidot–传递最新科技情报 | https://www.solidot.org/index.rss | https://www.solidot.org|
| 好好学习的郝 | https://www.voidking.com/atom.xml | https://www.voidking.com/|
| 小霖的梦花园 | https://www.xiaolin.in/rss2.xml | https://www.xiaolin.in/|
| 少数派 | https://sspai.com/feed | https://sspai.com|
| 尚弟的小笔记 | https://blog.shrp.me/rss.xml | https://blog.shrp.me/|
| 岁寒 | https://lvwenhan.com/rss.php | https://lvwenhan.com/|
| 峡州仙士 | https://cjh0613.com/categories/%E6%8A%80%E6%9C%AF/rss2.xml | https://cjh0613.com/|
| 川叶 :: 不舍昼夜 | https://blog.lishun.me/feed.xml | https://blog.lishun.me/|
| 惶心博客 | https://huangxin.dev/atom.xml | https://huangxin.dev/|
| 我的小米粥分你一半 | https://corvo.myseu.cn/atom.xml | https://corvo.myseu.cn/|
| 文章 - 硬盘在歌唱 on 硬盘在歌唱 | https://disksing.com/post/index.xml | http://disksing.com/post/|
| 新世界的大门 | https://blog.xinshijiededa.men/atom.xml | https://blog.xinshijiededa.men/|
| 木木木木木 | https://immmmm.com/atom.xml | https://immmmm.com/|
| 机械境 | https://gythialy.github.io/atom.xml | https://gythialy.github.io/|
| 浣心 | https://blog.loikein.one/index.xml | https://blog.loikein.one/|
| 游戏程序员的自我修养 | https://neil3d.github.io/rss-feed.xml | https://neil3d.github.io|
| 潮流周刊 | https://weekly.tw93.fun/rss.xml | https://weekly.tw93.fun/|
| 澄沨的漫游茶记 | https://champhoon.xyz/atom.xml | https://champhoon.xyz/|
| 猫·仁波切 | https://andelf.github.io/feed.xml | https://andelf.github.io/|
| 王子亭的博客 | https://jysperm.me/atom.xml | https://jysperm.me/|
| 生活不在别处 | https://www.kuact.com/index.xml | https://www.kuact.com/|
| 离别歌 | https://www.leavesongs.com/feed/ | https://www.leavesongs.com|
| 竹林里有冰的博客 | https://zhul.in/rss.xml | https://zhul.in/|
| 罗磊的独立博客 | https://luolei.org/feed/ | https://luolei.org/|
| 胡涂说 | https://hutusi.com/feed.xml | https://hutusi.com/|
| 菠菜眾長 | https://lruihao.cn/index.xml | https://lruihao.cn/|
| 贤民的博客 | https://www.xianmin.org/index.xml | https://www.xianmin.org/|
| 辛未羊的网络日志 | https://panqiincs.me/atom.xml | https://panqiincs.me/|
| 酷 壳 – CoolShell | https://coolshell.cn/feed | https://coolshell.cn|
| 银河美术馆 Gallery of Galaxy | https://blog.beautyyu.one/feed | https://blog.beautyyu.one//|
| 静かな森 | https://innei.ren/feed | https://innei.in|
