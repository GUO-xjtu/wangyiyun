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
        self.url = ['https://music.163.com/#/discover/toplist?id=19723756',
                    'https://music.163.com/#/discover/toplist?id=3779629',
                    'https://music.163.com/#/discover/toplist?id=2884035',
                    'https://music.163.com/#/discover/toplist?id=3778678',
                    'https://music.163.com/#/discover/toplist?id=991319590',
                    'https://music.163.com/#/discover/toplist?id=71384707',
                    'https://music.163.com/#/discover/toplist?id=1978921795',
                    'https://music.163.com/#/discover/toplist?id=2250011882',
                    'https://music.163.com/#/discover/toplist?id=2617766278',
                    'https://music.163.com/#/discover/toplist?id=71385702',
                    'https://music.163.com/#/discover/toplist?id=745956260',
                    'https://music.163.com/#/discover/toplist?id=10520166',
                    'https://music.163.com/#/discover/toplist?id=2023401535',
                    'https://music.163.com/#/discover/toplist?id=2006508653',
                    'https://music.163.com/#/discover/toplist?id=180106',
                    'https://music.163.com/#/discover/toplist?id=60198',
                    'https://music.163.com/#/discover/toplist?id=3812895',
                    'https://music.163.com/#/discover/toplist?id=27135204',
                    'https://music.163.com/#/discover/toplist?id=21845217',
                    'https://music.163.com/#/discover/toplist?id=11641012',
                    'https://music.163.com/#/discover/toplist?id=60131',
                    'https://music.163.com/#/discover/toplist?id=120001',
                    'https://music.163.com/#/discover/toplist?id=112463',
                    'https://music.163.com/#/discover/toplist?id=10169002',
                    'https://music.163.com/#/discover/toplist?id=2809513713',
                    'https://music.163.com/#/discover/toplist?id=2809577409'
                    ]
        # 连接数据库
        self.mysqlCommand = MySQLCommand()
        self.mysqlCommand.connectdb()
        # 每次查询数据库中最后一条数据的ID，新加的数据每成功插入一条ID+1

    def run(self):

        for s_url in self.url:
            self.driver.get(s_url)
            time.sleep(4)
            self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
            source = self.driver.page_source
            html = etree.HTML(source)
            list_name = html.xpath("//div[@class='hd f-cb']/h2/text()")
            play_num = html.xpath("//div[@class='more s-fc3']/strong[@class='s-fc6']/text()")
            creator = '网易云'
            creator_url = '无'
            try:
                self.mysqlCommand.insert_list(s_url, list_name, creator, creator_url, play_num)
            except:
                print('列表错误' + list_name, play_num, creator_url, creator)

            url = re.findall(r'<span class="txt"><a href="(.*?)"><b', source, re.DOTALL)
            song_name = re.findall(r'><b title="(.*?)">', source, re.DOTALL)
            singer = re.findall(r'div class="text" title="(.*?)"><span', source, re.DOTALL)
            for i in range(len(url)):
                urli = 'https://music.163.com' + url[i]
                song_namei = re.sub(r'&nbsp;', ' ' , song_name[i])
                singeri = singer[i]
                album = '网易云排行榜'
                try:
                    self.mysqlCommand.insert_musicData(song_namei, urli, album, singeri)
                except :
                    song_nameii=''
                    for i in song_namei:
                        if i != '\'' and i != ')':
                            song_nameii = song_nameii + i
                    try:
                        self.mysqlCommand.insert_musicData(song_nameii, urli, album, singeri)
                    except Exception as e:
                        print('歌曲错误 ' + song_nameii, '歌手 ' + singeri, '原名 ' + song_namei)
                        print(e)
        self.mysqlCommand.closeMysql()


if __name__ == '__main__':
    spider = wangyiyun()

    spider.run()
