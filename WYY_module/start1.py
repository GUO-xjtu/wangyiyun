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
        self.mysqlCommand.cursor.execute("select list_url from song_list")
        list_song = self.mysqlCommand.cursor.fetchall()

        for odd, url in enumerate(list_song):

            if url.get('list_url') != None and odd % 3 == 0:
                self.driver.get(url.get('list_url'))
                time.sleep(4)
                self.driver.switch_to.frame(self.driver.find_element_by_name('contentFrame'))
                time.sleep(1)
                source = self.driver.page_source
                # print(url.get('list_url'))
                # print(source)
                html = etree.HTML(source)
                time.sleep(1)

                song_name = re.findall(r'"><b title="(.*?)">', source, re.DOTALL)

                song_url = re.findall(r'<div class="ttc"><span class="txt"><a href="(.*?)"><b', source, re.DOTALL)

                album = html.xpath("//div[@class='text']/a/@title")

                singer = html.xpath("//div[@class='text']/@title")

                singer_url = html.xpath("//div[@class='text']/span/a/@href")
                for i in range(len(song_name)):
                    song_n = re.sub(r'&nbsp;', ' ', song_name[i])
                    song_u = 'https://music.163.com' + song_url[i]
                    singerurl = 'https://music.163.com' + singer_url[i]
                    print(singer[i], singerurl)
                    try:
                        self.mysqlCommand.insert_musicData(song_n, song_u, album[i], singer[i])
                        self.mysqlCommand.insert_singer(singer[i], singerurl)
                        print('==' * 20)
                    except Exception as e:
                        print(e)
                        pass
if __name__ == '__main__':
    spider = wangyiyun()

    spider.run()