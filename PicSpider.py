import os
import requests
from lxml import etree
from queue import Queue
import re
import time
import tkinter
from tkinter import filedialog
from threading import Thread


class BelleSpider():
    def __init__(self):
        self.q = Queue()    #用于存放每一个人物图片的url队列
        self.pre_url = 'https://www.mzitu.com/xinggan/page/'
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
                        'referer':'https://www.mzitu.com/xinggan/'}

    def get_theme(self,start_page=1):
        i = start_page
        while True:
            page = str(i)
            print('{0:*^50}'.format('正在写入第{}页url地址'.format(i)))
            response = requests.get(self.pre_url + page, headers=self.headers)
            print(response.url)
            html_content = response.content.decode()
            tree = etree.HTML(html_content)
            a = tree.xpath("//ul[@id='pins']/li/span[1]/a")
            for each in a:
                theme_url = each.xpath('./@href')[0]
                theme_text = each.xpath('./text()')[0]
                '''put，block参数默认为True,如果队列满了，则会阻塞等待。'''
                self.q.put({theme_text:theme_url})
            time.sleep(2)
            '''有下一页，就继续抓取图片主题url'''
            if html_content.find('下一页') > 0 :
                i += 1
            else:
                print('最后一页theme主题url已经抓取完了~')
                break

    def download(self,start_page=1):
        global  download_directory
        while True:
            print('准备获取队列大小：{}'.format(self.q.qsize()))
            if not self.q.empty():
                '''默认block=True，队列为空，就会阻塞，知道有数据可以取出。'''
                get = self.q.get()
                self.q.task_done()
                for the_theme,the_url in get.items():
                    '''文件命名规则原因，文件名剔除一些特殊的符号'''
                    regexp_bat = re.compile('[\?？\.。！!]*')
                    theme = regexp_bat.sub('',the_theme)
                    url = the_url
                mkdir = os.path.join(download_directory , theme)
                print('theme文件名称为：{}',format(mkdir))
                if not os.path.exists(mkdir):
                    '''如果没有这个目录，则创建该目录'''
                    os.mkdir(mkdir)
                    '''定义该目录下载初始页：1'''
                    picture_page = start_page
                    # if picture_page == 1:
                    #     page = ''
                    # else:
                    page = str(picture_page)
                    while True:
                        the_picture_page_content = requests.get(url=url+'/'+page,
                                                headers=self.headers).content.decode()
                        tree = etree.HTML(the_picture_page_content)
                        '''xpath提取图片下载地址'''
                        the_download_url = tree.xpath("//div[@class='main-image']/p/a/img/@src")[0]
                        response = requests.get(url=the_download_url,headers=self.headers)
                        pic_name = '{}/{}-{}.jpg'.format(mkdir,theme,picture_page)
                        '''保存图片到目录'''
                        with open(pic_name, 'wb') as f:
                            f.write(response.content)
                            print('已经保存好图片{}-{}......'.format(theme,picture_page))
                        time.sleep(2)
                        '''下一页'''
                        picture_page += 1
                        '''如果有下一组，表示这组图片已经爬完了，这个循环结束。'''
                        if the_picture_page_content.find('下一组') > 0:
                            print('当前页已经抓取完毕，请稍等10s钟......')
                            time.sleep(10)
                            break
                else:
                    print('该文件已经下载{}'.format(mkdir))
            else:
                print('队列空了~~')
                break

    def main(self,start_time_wait=20):
        t1 = Thread(target=self.get_theme)
        t1.start()
        '''先等待10秒，防止队列为空，t2线程q.empty直接跳出循环结束线程。'''
        time.sleep(start_time_wait)
        t2 = Thread(target=self.download)
        t2.start()
        '''线程阻塞，直接队列所在线程运行完毕，主线程才往下走。'''
        self.q.join()
        print('所有文件已经下载完毕！')


if __name__ == '__main__':
    win = tkinter.Tk()
    '''调用窗口，选择下载目录'''
    download_directory = filedialog.askdirectory()
    m = BelleSpider()
    m.main()
    print('Done!')
    m.main()
    '''结束Tk循环'''
    win.mainloop()
