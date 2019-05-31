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
        # 连接数据库
        self.mysqlCommand = MySQLCommand()
        self.mysqlCommand.connectdb()
        # 每次查询数据库中最后一条数据的ID，新加的数据每成功插入一条ID+1
        self.music = {}

    def run(self):
        self.mysqlCommand.cursor.execute("select url ,singer_name from table_singer")
        urls = self.mysqlCommand.cursor.fetchall()

        for odd, url in enumerate(urls):

            if url.get('url') != None and odd % 2 == 1:
                self.driver.get(url.get('url'))
                time.sleep(4)
                self.driver.switch_to.frame(self.driver.find_element_by_name('contentFrame'))
                time.sleep(1)
                source = self.driver.page_source
                # print(url.get('list_url'))
                # print(source)
                html = etree.HTML(source)
                time.sleep(1)

                song_name = html.xpath("//div[@class='j-flag']//div[@class='ttc']/span[@class='txt']/a/b/@title")

                song_url = html.xpath("//div[@class='j-flag']//div[@class='ttc']/span[@class='txt']/a/@href")

                album = html.xpath("//div[@class='text']/a/@title")

                singer = url.get('singer_name')

                for i in range(len(song_name)):
                    song_n=re.sub(r'\\xa0', ' ', song_name[i])
                    song_u = 'https://music.163.com' + song_url[i]
                    albums = re.sub(r'\\xa0', ' ', album[i])
                    print(song_n, '+', song_u, '+', albums, '+', singer)
                    try:
                        self.mysqlCommand.insert_musicData(song_n, song_u, albums, singer)
                        print('=='*20)
                    except:
                        pass
                    print('=='*20)
if __name__ == '__main__':
    spider = wangyiyun()

    spider.run()
