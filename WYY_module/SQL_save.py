import pymysql
class MySQLCommand(object):
    # 初始化类
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306  # 端口号
        self.user = 'root'  # 用户名
        self.password = '0321'
        self.db = "Messages"  # 库
        self.table1 = "message"  # 表
        self.table2 = "table_music"
        self.table3 = "table_user"
        self.unum = 0
        self.mnum = 0
        self.pnum = 0
        self.snum = 0
    # 连接数据库
    def connectdb(self):
        print('连接到mysql服务器...')
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                port=self.port,
                db=self.db,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            print('连接上了!')
        except:
            print('连接失败！')
    # 插入歌单信息
    def insert_list(self, list_url, list_name, creator, creator_url,play_num):
        sqlExit = "SELECT list_url FROM song_list WHERE list_url = ' %s '" % list_url
        res = self.cursor.execute(sqlExit)
        # res为查询到得数据条数如果大于0就代表数据已经存在
        if res:
            self.unum += 1
            return 0
        # 插入数据
        try:
            sql = "INSERT INTO song_list (list_name, creator, play_num, list_url, creator_url) VALUES (%s, %s, %s, %s, %s)"
            print(list_url, list_name, creator, creator_url, play_num)
            try:
                result = self.cursor.execute(sql, (list_name, creator, play_num, list_url, creator_url))
                # self.conn.insert_id()  # 插入成功返回ID
                self.conn.commit()
                #     # 判断是否执行成功
                if result:
                    self.unum += 1
                    print('插入第%d个歌单数据成功' % self.unum)
                else:
                    print("第%d位个歌单插入失败" % self.mnum)
                    self.unum += 1
            except pymysql.Error as e:
                # 发生错误回滚
                self.conn.rollback()

                # 主键唯一无法插入
                if "key 'PRIMARY'" in e.args[1]:
                    print("第%d位歌单已存在，无法插入" % self.unum)
                else:

                    print("歌单数据插入失败，原因 %d:%s" % (e.args[0], e.args[1]))
        except pymysql.Error as e:
            print("歌单数据库错误，原因%d:%s" % (e.args[0], e.args[1]))

    # 插入用户数据， 插入之前先查询是否存在，若存在，就不再插入
    def insert_userData(self, user):
        table = "table_user"  # 要操作的表格

        sqlExit = "SELECT url FROM table_user WHERE url = ' %s '" % user['url']
        res = self.cursor.execute(sqlExit)
        # res为查询到得数据条数如果大于0就代表数据已经存在
        if res:
            self.unum += 1
            return 0
        # 插入数据
        try:
            cols = ', '.join(user.keys())
            values = '"," '.join(user.values())
            # print(values)
            sql = ("INSERT INTO table_user (%s) VALUES (%s)" % (cols, '"'+values+'"'))
            print(sql)
            try:
                result = self.cursor.execute(sql)
                # self.conn.insert_id()  # 插入成功返回ID
                self.conn.commit()
                # 判断是否执行成功
                if result:
                    self.unum += 1
                    print('插入第%d位用户数据成功' % self.unum)
                else:
                    print("第%d位用户插入失败" % self.mnum)
                    self.unum += 1
            except pymysql.Error as e:
                # 发生错误回滚
                self.conn.rollback()

                # 主键唯一无法插入
                if "key 'PRIMARY'" in e.args[1]:
                    print("第%d位用户已存在，无法插入" % self.unum)
                else:
                    print("用户数据插入失败，原因 %d:%s" % (e.args[0], e.args[1]))
        except pymysql.Error as e:
            print("用户数据库错误，原因%d:%s" % (e.args[0], e.args[1]))

    # 插入评论数据
    def insert_messageData(self, message):
        table = "message"  # 要操作的表格
        sqlmessage = "SELECT name FROM message where name = '%s'" % message['name']

        res = self.cursor.execute(sqlmessage)
        # res为查询到得数据条数如果大于0就代表数据已经存在

        # 若同一人评论两次以上，则将新评论增加到该评论人的comments中

        sqlExit = "SELECT url FROM message WHERE url = ' %s '" % message['url']
        ret=self.cursor.execute(sqlExit)
        if res and ret:
            self.pnum += 1
            return 0
        else:
            # 插入数据
            try:
                cols = ', '.join(message.keys())
                values = '","'.join(message.values())
                # print('values'+values)
                # print('=='*30)
                sql = ("INSERT INTO message(%s) VALUES (%s)" % (cols, '"' + values + '"'))
                # print(sql)message['url'][i]
                # try:
                result = self.cursor.execute(sql)
                # insert_id = self.conn.insert_id()  # 插入成功返回ID
                self.conn.commit()

                # 判断是否执行成功
                if result:
                    self.pnum += 1
                    print("第%d条评论插入成功" % self.pnum)
                else:
                    print("第%d条评论插入失败" % self.pnum)
                    self.pnum += 1
            except pymysql.Error as e:
                # 发生错误回滚
                self.conn.rollback()
                # 主键唯一无法插入
                if "key 'PRIMARY'" in e.args[1]:
                    print("第%d条评论数据已存在，无法插入" % self.pnum)
                else:
                    print("评论插入失败，原因 %d:%s" % (e.args[0], e.args[1]))
                #   except pymysql.Error as e:
                #   print("数据库错误，原因%d:%s" % (e.args[0], e.args[1]))
                #   update_message = "update message set comments = CONCAT(comments,message.comments) where name = message.name"
                #   self.cursor.execute(update_message)

    # 插入音乐数据
    def insert_musicData(self, song_n, song_u, album, singer):
        table = "table_music"  # 要操作的表格
        sqlExit = "SELECT song_name FROM table_music WHERE song_name = ' %s '" % song_n
        res = self.cursor.execute(sqlExit)
        # res为查询到得数据条数如果大于0就代表数据已经存在
        if res:
            self.mnum += 1
            return 0
        # 插入数据
        try:
            sql = "INSERT INTO table_music (song_name, url, album, singer) VALUES (%s, %s, %s, %s)"

            try:
                result = self.cursor.execute(sql, (song_n, song_u, album, singer))
                # insert_id = self.conn.insert_id()  # 插入成功返回ID
                # print(song_n, song_u, album, singer)
                # print(result)
                self.conn.commit()
            #     # 判断是否执行成功
                if result:
                    self.mnum += 1
                    print("第%d首音乐插入成功" % self.mnum)
                else:
                    print("第%d首音乐插入失败" % self.mnum)
                    self.mnum += 1
            except pymysql.Error as e:
                # 发生错误回滚
                self.conn.rollback()
                # 主键唯一无法插入
                if "key 'PRIMARY'" in e.args[1]:
                    print("第%d首音乐数据已存在，无法插入" % self.mnum)
                else:
                    print("插入失败，原因 %d:%s" % (e.args[0], e.args[1]))
        except pymysql.Error as e:
            print("音乐数据库错误，原因%d:%s" % (e.args[0], e.args[1]))

    def insert_musicnum(self,song_name, comment_num):
            sql = "update table_music set comment_sum='%s' where song_name='%s' " % (comment_num,song_name)
            self.cursor.execute(sql)
    def insert_singer(self, singer_name, url):
        self.snum += 1
        sql = "INSERT INTO table_singer(singer_name, url) VALUES (%s, %s)"
        result = self.cursor.execute(sql, (singer_name, url))
        self.conn.commit()
        if result:
            print('第%d位歌手信息插入成功' % self.snum)
    def closeMysql(self):
        self.cursor.close()
        self.conn.close()  # 创建数据库操作类的实例


