from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import etree
import re
import time


class wangyiyun():

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.url = 'https://music.163.com/discover/toplist?id=3778678'



    def run(self):
        self.driver.get(self.url)
        self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
        # html = requests.get(self.url, headers=self.headers)
        # print(html.text)
        source = self.driver.page_source
        self.parse_list_page(source)



    # 获取歌曲的url
    def parse_list_page(self, source):

        html = etree.HTML(source)


        links = html.xpath("//span[@class='txt']/a/@href")
        for i in links:
            song_url = "https://music.163.com" + i
            self.request_detail_page(song_url)
            time.sleep(1)

    # 请求歌曲详情页
    def request_detail_page(self, url):
        # self.driver.get(url)
        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
        source = self.driver.page_source
        # 滚动条到页面最底部
        js = "var q=document.documentElement.scrollTop=10000"
        self.driver.execute_script(js)
        j_flag = "".join(re.findall(r'<div class="auto-(.*?) u-page">', source, re.DOTALL))
        time.sleep(5)
        while True:
            source = self.driver.page_source
            # print(source)
            # print("++"*30)
            WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.XPATH,  "//div[@class='auto-"+j_flag+" u-page']/a[last()]")))
            self.parse_detail_page(source)
            # j_flag = "".join(re.findall(r'<div class="auto-(.*?) u-page">', source, re.DOTALL))
            # print(j_flag)
            # print('==='*30)



            try:

                next_btn = self.driver.find_element_by_xpath("//div[@class='auto-"+j_flag+" u-page']/a[last()]")
                # print("++"*30)
                # print(next_btn.get_attribute("class"))
                # print("++"*30)
                if "js-disabled" in next_btn.get_attribute("class"):
                    break
                else:
                    next_btn.click()
                    time.sleep(5)


            except:
                print(source)
                print("=="*40)
                # print(j_flag)
        # 关闭详情页
        self.driver.close()
        # 切换回排行榜列表
        self.driver.switch_to.window(self.driver.window_handles[0])

    # 爬取歌曲评论信息
    def parse_detail_page(self, source):
        html = etree.HTML(source)
        preson_id = html.xpath("//div[@class='cnt f-brk']/a[@class='s-fc7']/@href")
        song_name = "".join(html.xpath("//div[@class='tit']/em[@class='f-ff2']/text()"))
        with open(song_name + '歌曲中评论人的个人信息.csv', 'a') as fp:
            fp.write(
                '{}, {}, {}, {}, {}, {}, {}, {}\n'.format('昵称', '个人介绍', '地区', '年龄', '个人动态', '关注的人', '拥有粉丝', '个人主页'))
        fp.close()
        # 获取点击量
        points_tags = re.findall(r'<i class="zan u-icn2 u-icn2-12">(.*?)</a>', source, re.DOTALL)
        point = []
        for i in points_tags:
            # print(i)
            point_rag = re.sub('</i> ', '', i)
            point_rag = re.sub('</i>', '0', point_rag)
            # print(point_rag)
            # print('=='*30)
            point.append(point_rag)
        # print(point)
        # print(len(point))

        j = 0
        for i in preson_id:

            while point[j] != '0':
                preson_url = "https://music.163.com" + i

                self.request_preson_page(preson_url, song_name)
                break
            j = j+1
        name = html.xpath("//div[@class='cnt f-brk']/a[1]/text()")
        # print(name)
        # print(len(name))
        # print("==" * 30)
        # print(len(name))
        comment_tags = re.findall(r'<div class="cnt f-brk">.*?</a>(.*?)</div', source, re.DOTALL)
        comments = []
        for i in comment_tags:

            comment_tag = re.sub('<br />', ' ', i)
            # print(comment_tag)
            comment_tag = re.sub('<(.*?)>', '', comment_tag)
            # print(comment_tag)
            # print('=='*30)
            comments.append(comment_tag)

        # print(len(comments))
        # print(comments)
        # exit()
        time = html.xpath("//div[@class='time s-fc4']/text()")

        # print(time)
        # print(len(time))
        # print("==" * 30)

        # point = []
        # for i in points_tags:
        #     point_rag = re.sub('</i> ', '0', i)
        #     point.append(point_rag)
        # # print(len(point))
        with open(song_name + '歌曲评论.csv', 'a+') as fp:
            fp.write('{}, {}, {}, {}, {}\n'.format('昵称', '评论内容', '点赞量', '评论时间', '个人主页'))
        fp.close()
        # 保存每首歌曲的评论信息
        with open(song_name + '歌曲评论.csv', 'a+') as fp:
            # fp.write('{}, {}, {}, {}, {}\n'.format('昵称', '评论内容', '点赞量', '评论时间', '个人主页'))
            for i in range(len(name)):

                pr_name = name[i]

                pr_comment = comments[i]

                pr_point = "".join(point[i])

                pr_time = time[i]
                pr_page = "https://music.163.com" + preson_id[i]
                fp.write('{}, {}, {}, {}, {}\n'.format(pr_name, pr_comment, pr_point, pr_time, pr_page))
        fp.close()


    # 请求评论人详情页
    def request_preson_page(self, preson_url, song_name):
        self.driver.execute_script("window.open('%s')" %preson_url)
        self.driver.switch_to.window(self.driver.window_handles[2])
        # WebDriverWait(self.driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "")))
        self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
        source = self.driver.page_source
        self.parse_preson_page(source, song_name, preson_url)
        time.sleep(1)
        # 关闭当前页
        self.driver.close()
        # 切换评论详情页
        self.driver.switch_to.window(self.driver.window_handles[1])


    # 解析评论人信息页
    def parse_preson_page(self, source, song_name, preson_url):
        html = etree.HTML(source)
        person_name = "".join(html.xpath("//span[@class='tit f-ff2 s-fc0 f-thide']/text()"))
        #print(person_name)

        IDs = html.xpath("//ul[@class='data s-fc3 f-cb']/li/a/@href")
        count = re.findall(r'<strong.*?</strong>', source, re.DOTALL)
        counts = []
        for i in count:
            count = re.findall(r'">(.*?)</strong>', i)
            counts.append(count)
        ids = []
        for i in IDs:
            ids.append("https://music.163.com" + i)
        # print(counts)
        # print(ids)
        introduce = html.xpath("//div[@class='inf s-fc3 f-brk']/text()")
        if len(introduce) == 0:
            introduce = ['无信息']
        introduce = "".join(introduce)
        # print(introduce)
        # print("++"*30)
        introduce = "".join(re.sub(r'个人介绍：', '',  introduce))
        introduce = re.sub(r'\n', ' ', introduce)

        district = re.findall(r'<div class="inf s-fc3".*?所在地区：(.*?)</span>', source, re.DOTALL)
        if len(district) == 0:
            district = ['无信息']
        # print(district)
        # print(len(district))
        # print(introduce)
        # print("=="*30)
        age = html.xpath("//span[@class='sep']/span/text()")
        if len(age) == 0:
            age = ['无信息']
        # print(len(age))
        # print(age)


        with open(song_name + '歌曲中评论人的个人信息.csv', 'a') as f:
            pr_name = person_name
            pr_introduce = introduce
            pr_district = district
            pr_age = age
            pr_dynamic = ids[0]
            pr_focus = ids[1]
            pr_fans = ids[2]

            f.write('{}, {}, {}, {}, {}, {}, {}, {}\n'.format(pr_name, pr_introduce, pr_district, pr_age, pr_dynamic, pr_focus, pr_fans, preson_url))
        f.close()



if __name__ == '__main__':
    spider = wangyiyun()
    spider.run()