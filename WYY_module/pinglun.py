from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from lxml import etree
from wangyiyun.SQL_save import MySQLCommand
import re
import time

class wangyiyun():
    def __init__(self):
        options=Options()
        options.headless=True
        self.driver = webdriver.Firefox()
        self.url = 'https://music.163.com/#/discover/toplist?id=19723756'
        # 连接数据库
        self.mysqlCommand = MySQLCommand()
        self.mysqlCommand.connectdb()
        # 每次查询数据库中最后一条数据的ID，新加的数据每成功插入一条ID+1
        self.message = {}
        self.user = {}
        self.music = {}

    def run(self):
        self.driver.get(self.url)
        self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
        source = self.driver.page_source
        self.parse_list_page(source)

    # 获取歌曲的url
    def parse_list_page(self, source):

        html = etree.HTML(source)
        links = html.xpath("//span[@class='txt']/a/@href")
        # self.mysqlCommand.insert_musicData(self.music)
        for i in links:
            song_url = "https://music.163.com" + i
            try:
                self.request_detail_page(song_url)
            except:

                self.mysqlCommand = MySQLCommand()
                self.mysqlCommand.connectdb()
                self.driver.close()
                # 切换回排行榜列表
                self.driver.switch_to.window(self.driver.window_handles[0])
            # 插入音乐数据到music表中
            # self.mysqlCommand.insert_musicData(self.music)
            # time.sleep(1)

    # 请求歌曲详情页
    def request_detail_page(self, url):
        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(5)
        self.driver.switch_to.frame(self.driver.find_element_by_name('contentFrame'))
        # 滚动条到页面最底部
        js = "var q=document.documentElement.scrollTop=10000"
        self.driver.execute_script(js)
        time.sleep(1)
        source = self.driver.page_source
        time.sleep(1)
        j_flag = "".join(re.findall(r'<div class="auto-(.*?) u-page">', source, re.DOTALL))
        i = 1
        while True:
            # self.parse_detail_page(source)
            try:
                # self.parse_detail_page(source)
                self.driver.switch_to.window(self.driver.window_handles[1])
                # self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
                source = self.driver.page_source
                time.sleep(2)
                # print('刷新本页html：',source)
                js = "var q=document.documentElement.scrollTop=10000"
                self.driver.execute_script(js)
                time.sleep(2)
                # self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
                # WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='auto-" + j_flag + " u-page']/a[last()]")))
                next_btn = self.driver.find_element_by_xpath("//div[@class='auto-"+j_flag+" u-page']/a[last()]")
                print(next_btn)
                print(type(next_btn))
                exit()
                print('爬取第%d页成功！' % i)
                if "js-disabled" in next_btn.get_attribute("class"):
                    self.mysqlCommand.insert_musicData(self.music)
                    print('本首歌爬取完成！')
                    self.mysqlCommand.closeMysql()
                    break
                else:
                    next_btn.click()
                    i += 1
                    time.sleep(2)
            except:
                if self.driver.page_source.find("//div[@class='auto-"+j_flag+" u-page']/a[last()]"):
                    print('有btn')
                print('爬取第%d页失败！' % i)
                self.mysqlCommand.closeMysql()
                print("=="*20)
                # print(source)
                print(j_flag)

        # 关闭详情页
        self.driver.close()
        # 切换回排行榜列表
        self.driver.switch_to.window(self.driver.window_handles[0])

    # 爬取歌曲评论信息
    def parse_detail_page(self, source):

        html = etree.HTML(source)
        preson_id = html.xpath("//div[@class='cnt f-brk']/a[@class='s-fc7']/@href")
        song_name = "".join(html.xpath("//div[@class='tit']/em[@class='f-ff2']/text()"))
        singer = ''.join(html.xpath("//div[@class='cnt']/p[1]/span/a[@class='s-fc7']/text()"))
        album = ''.join(html.xpath("//div[@class='cnt']/p[2]/a[@class='s-fc7']/text()"))
        comment_sum = ''.join(re.findall(r'<span class="j-flag">(.*?)</span>', source, re.DOTALL))
        self.music['album'] = album
        # print(self.message)
        # print('++'*30)
        self.music['song_name'] = song_name
        self.music['singer'] = singer
        self.music['album'] = album
        self.music['comment_sum'] = comment_sum
        try:
            # 插入数据
            self.mysqlCommand.insert_musicData(self.music)
        except Exception as e:
            print("插入音乐数据失败", str(e))  # 输出插入失败的报错语句
        # 获取点击量
        points_tags = re.findall(r'<i class="zan u-icn2 u-icn2-12">(.*?)</a>', source, re.DOTALL)
        point = []
        for i in points_tags:

            point_rag = re.sub('</i> ', '', i)
            point_rag = re.sub('</i>', '0', point_rag)
            point.append(point_rag)
        # 请求评论人详情页
        for i in preson_id:
            preson_url = "https://music.163.com" + i
            try:
                self.request_preson_page(preson_url, song_name)
            except:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
        name = html.xpath("//div[@class='cnt f-brk']/a[1]/text()")
        comment_tags = re.findall(r'<div class="cnt f-brk">.*?</a>(.*?)</div>.*?</a>(.*?)</div>', source, re.DOTALL)
        comments = []
        for item in comment_tags:
            comment=str()
            for i in item:
                comment_tag = re.sub('<br />', ' ', i)

                comment_tag = re.sub('<(.*?)>', '', comment_tag)
                if item.index(i) == 1 and comment_tag != '|回复':
                    comment_tag = '\n 评论回复'+comment_tag
                comment += comment_tag
            comment=comment.rstrip('|回复')
            comment=''.join(comment)
            comment='""'+comment+'""'
            comments.append(comment)

        time = []
        times = html.xpath("//div[@class='time s-fc4']/text()")
        for i in times:
            time.append(i.replace(' ', ''))
        # print('++' * 30)
        for i in range(len(name)):
            self.message['song_name'] = song_name
            self.message['name'] = name[i]
            self.message['comments'] = comments[i]
            self.message['time'] = time[i]
            self.message['point'] = point[i]
            self.message['url'] = "https://music.163.com"+preson_id[i]
            self.mysqlCommand.insert_messageData(self.message)

    # 请求评论人详情页
    def request_preson_page(self, preson_url, song_name):
        self.driver.execute_script("window.open('%s')" %preson_url)
        self.driver.switch_to.window(self.driver.window_handles[2])
        time.sleep(5)
        # WebDriverWait(self.driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, '//iframe[@allowfullscreen="true"]')))
        self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
        source = self.driver.page_source
        time.sleep(2)
        self.parse_preson_page(source, song_name, preson_url)
        # time.sleep(1)
        # 关闭当前页
        self.driver.close()
        # 切换评论详情页
        self.driver.switch_to.window(self.driver.window_handles[1])
        # time.sleep(1)

    # 解析评论人信息页
    def parse_preson_page(self, source,song_name, preson_url):
        html = etree.HTML(source)
        person_name = "".join(html.xpath("//span[@class='tit f-ff2 s-fc0 f-thide']/text()"))
        IDs = html.xpath("//ul[@class='data s-fc3 f-cb']/li/a/@href")
        count = re.findall(r'<strong.*?</strong>', source, re.DOTALL)
        counts = []
        for i in count:
            count = re.findall(r'">(.*?)</strong>', i)
            counts.append(count)
        ids = []
        for i in IDs:
            ids.append("https://music.163.com" + i)
        if len(ids) == 0:
            print(source)
        introduce = html.xpath("//div[@class='inf s-fc3 f-brk']/text()")
        if len(introduce) == 0:
            introduce = ['无信息']
        introduce = "".join(introduce)

        introduce = "".join(re.sub(r'个人介绍：', '',  introduce))
        introduce = re.sub(r'\n', ' ', introduce)

        district = "".join(re.findall(r'<div class="inf s-fc3".*?所在地区：(.*?)</span>', source, re.DOTALL))
        if len(district) == 0:
            district = '无信息'

        age = "".join(html.xpath("//span[@class='sep']/span/text()"))
        if len(age) == 0:
            age = '无信息'

        self.user['name'] = person_name
        self.user['introduction'] = introduce
        self.user['region'] = district
        self.user['age'] = age
        self.user['dynamic'] = ids[0]
        self.user['focus'] = ids[1]
        self.user['fans'] = ids[2]
        self.user['url'] = preson_url
        # print(self.user)

        try:
            # 插入数据
            self.mysqlCommand.insert_userData(self.user)
        except Exception as e:
            print("插入用户数据失败", str(e))  # 输出插入失败的报错语句


if __name__ == '__main__':
    spider = wangyiyun()

    spider.run()





