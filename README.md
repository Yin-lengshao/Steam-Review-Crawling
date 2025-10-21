# Steam-Review-Crawling
Suitable for friends who have a basic understanding of network technology to crawl game reviews on Steam.
该项目适合对网络技术有初步了解的朋友们爬取steam中游戏的评论

使用方法：
1、打开steam++（watt toolkit）或其他加速器对steam加速。
2、在网页版steam中，选择要爬取评论的游戏，拉到底，点击“浏览所有评测”
3、在新界面点击F12，在右侧找到网络，选择Fetch/XHR。随后在左侧向下滑动界面，右侧的Fetch/XHR中刷新出第一个文件时停止。
4、点击该文件，在标头处找到请求URL，复制
5、在python环境中运行get_info.py，按照提示操作。会抓取html内容
6、运行extract_data.py，按照提示操作，会将html的内容提取出来


是我写的，如果看起来眼熟，那说明好的设计总是相似的，而坏的bug则各有各的坏法。本项目允许任何形式的使用，但因此导致的任何时间或精神上的损失本人概不负责。感谢！

欢迎所有人与我进行技术交流，邮箱：335515598@qq.com
