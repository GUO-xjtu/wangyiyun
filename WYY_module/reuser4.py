from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from lxml import etree
from SQL_save import MySQLCommand
import re
import time

class wangyiyun():
    def __init__(self):
        options=Options()
        options.headless=True
        self.driver = webdriver.Firefox(options=options)
        # 连接数据库
        self.mysqlCommand = MySQLCommand()
        self.mysqlCommand.connectdb()
        # 每次查询数据库中最后一条数据的ID，新加的数据每成功插入一条ID+1
        self.message = {}
        self.user = {}

    def run(self):
        self.mysqlCommand.cursor.execute("select url,song_name from message")
        name_url = self.mysqlCommand.cursor.fetchall()
        for odd, url in enumerate(name_url):
            if url.get('url') != None and odd % 4 == 3:
                # print(url)
                self.driver.get(url.get('url'))
                # self.request_preson_page(url.get('url'), url.get('song_name'))
                time.sleep(4)
                preson_url = url.get('url')
                song_name = url.get('song_name')
                self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
                source = self.driver.page_source
                #time.sleep(2)
                self.parse_preson_page(source, song_name, preson_url)

    # 解析评论人信息页
    def parse_preson_page(self, source, song_name, preson_url):
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
            print(ids, preson_url)
            exit()
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