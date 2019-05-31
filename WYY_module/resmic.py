from selenium import webdriver
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
        self.url = ['https://music.163.com/#/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8',
                    ]
        # 连接数据库
        self.mysqlCommand = MySQLCommand()
        self.mysqlCommand.connectdb()
        # 每次查询数据库中最后一条数据的ID，新加的数据每成功插入一条ID+1

    def run(self):

        for s_url in self.url:
            self.driver.get(s_url)
            time.sleep(5)
            self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
            self.parse_list_page()

    # 获取歌曲的url
    def parse_list_page(self):
        k = 1
        h=0
        while True:
            try:
                source = self.driver.page_source
                time.sleep(2)
                html = etree.HTML(source)
                list_url = html.xpath("//li/div[@class='u-cover u-cover-1']/a/@href")
                creator_url = html.xpath("//li//p[last()]/a/@href")

                play_num = re.findall(r'<span class="nb">(.*?)</span>', source, re.DOTALL)

                creator = html.xpath("//li/p[last()]/a/text()")

                list_name = html.xpath("//li/p[@class='dec']/a/text()")

                js = "var q=document.documentElement.scrollTop=10000"
                self.driver.execute_script(js)
                try:
                    # 插入数据
                    for i in range(len(creator_url)):
                        list = "https://music.163.com" + list_url[i]
                        print(creator_url[i])
                        creator_s = "https://music.163.com" + creator_url[i]
                        print(list, list_name[i], creator[i], creator_s, play_num[i])
                        self.mysqlCommand.insert_list(list, list_name[i], creator[i], creator_s, play_num[i])
                except Exception as e:
                    print("插入歌单数据失败", str(e))  # 输出插入失败的报错语句
                next_btn = self.driver.find_element_by_xpath("//div[@class='u-page']/a[last()]")
                print('爬取第%d页成功！' % k)
                if "zbtn znxt js-disabled" in next_btn.get_attribute("class"):
                    h+=1
                    for i in range(len(creator_url)):
                        list = "https://music.163.com" + list_url[i]
                        print(creator_url[i])
                        creator_s = "https://music.163.com" + creator_url[i]
                        self.mysqlCommand.insert_list(list, list_name[i], creator[i], creator_s, play_num[i])
                    print('本首歌爬取完成！')
                    if h==2:
                        self.mysqlCommand.closeMysql()
                        break
                    next_list = self.driver.find_element_by_xpath("//div[@class='u-btn f-fr u-btn-hot d-flag']/a[last()]")
                    next_list.click()
                else:
                    next_btn.click()
                    time.sleep(2)
                k += 1
                time.sleep(2)
            except:
                print('爬取第%d页失败！' % k)
                self.mysqlCommand.closeMysql()
                print("=="*20)


if __name__ == '__main__':
    spider = wangyiyun()

    spider.run()
