from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from lxml import etree
from SQL_save import MySQLCommand
import re
import time

class wangyiyun():
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        # 连接数据库
        self.mysqlCommand = MySQLCommand()
        self.mysqlCommand.connectdb()
        # 每次查询数据库中最后一条数据的ID，新加的数据每成功插入一条ID+1
        self.message = {}
        self.user = {}


    def run(self):
        self.mysqlCommand.cursor.execute("select url from table_music")
        music_url = self.mysqlCommand.cursor.fetchall()
        for odd, url in enumerate(music_url):
            if url.get('url') != None and odd % 4 == 2:
                self.driver.get(url.get('url'))
                time.sleep(4)
                self.driver.switch_to.frame(self.driver.find_element_by_name('contentFrame'))
                # 滚动条到页面最底部
                js = "var q=document.documentElement.scrollTop=10000"
                self.driver.execute_script(js)
                time.sleep(1)
                source = self.driver.page_source
                #time.sleep(1)
                j_flag = "".join(re.findall(r'<div class="auto-(.*?) u-page">', source, re.DOTALL))
                i = 1
                while True:
                    source = self.driver.page_source
                    self.parse_detail_page(source)
                    try:
                        # self.parse_detail_page(source)
                        # self.driver.switch_to.window(self.driver.window_handles[1])
                        # self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
                        # source = self.driver.page_source
                        time.sleep(5)
                        # print('刷新本页html：',source)
                        js = "var q=document.documentElement.scrollTop=10000"
                        self.driver.execute_script(js)
                        # self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
                        WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='auto-" + j_flag + " u-page']/a[last()]")))
                        next_btn = self.driver.find_element_by_xpath("//div[@class='auto-"+j_flag+" u-page']/a[last()]")
                        print('爬取第%d页成功！' % i)
                        if "js-disabled" in next_btn.get_attribute("class"):
                            print('本首歌爬取完成！')
                            # self.mysqlCommand.closeMysql()
                            break
                        else:
                            next_btn.click()
                            i += 1
                            time.sleep(2)
                    except:
                        if self.driver.page_source.find("//div[@class='auto-"+j_flag+" u-page']/a[last()]"):
                            print('有btn')
                        print('爬取第%d页失败！' % i)
                        # self.mysqlCommand.closeMysql()
                        print("=="*20)
                        # print(source)
                        print(j_flag)

                # 关闭详情页
                #self.driver.close()
                # 切换回排行榜列表
                #self.driver.switch_to.window(self.driver.window_handles[0])

    # 爬取歌曲评论信息
    def parse_detail_page(self, source):

        html = etree.HTML(source)
        preson_id = html.xpath("//div[@class='cnt f-brk']/a[@class='s-fc7']/@href")
        song_name = "".join(html.xpath("//div[@class='tit']/em[@class='f-ff2']/text()"))
        # 获取点击量
        points_tags = re.findall(r'<i class="zan u-icn2 u-icn2-12">(.*?)</a>', source, re.DOTALL)
        point = []
        for i in points_tags:

            point_rag = re.sub('</i> ', '', i)
            point_rag = re.sub('</i>', '0', point_rag)
            point.append(point_rag)

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

        comment_sum = ''.join(re.findall(r'<span class="j-flag">(.*?)</span>', source, re.DOTALL))
        try:
            self.mysqlCommand.insert_musicnum(song_name, comment_sum)
        except:
            print(song_name, comment_sum, '评论数插入失败！')
            pass


if __name__ == '__main__':
    spider = wangyiyun()

    spider.run()
