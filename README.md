# Steam-Review-Crawling
Suitable for friends who have a basic understanding of network technology to crawl game reviews on Steam.

使用方法：
1、打开steam++（watt toolkit）或其他加速器对steam加速。
2、在网页版steam中，选择要爬取评论的游戏，拉到底，点击“浏览所有评测”
3、在新界面点击F12，在右侧找到网络，选择Fetch/XHR。随后在左侧向下滑动界面，右侧的Fetch/XHR中刷新出第一个文件时停止。
4、点击改文件，在标头处找到请求URL，复制
5、在python环境中打开get_info.py，按照提示操作
