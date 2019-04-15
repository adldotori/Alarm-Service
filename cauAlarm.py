# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pymysql
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BlockingScheduler
import logging
from selenium.webdriver.chrome.options import Options
import sys

reload(sys)

sys.setdefaultencoding('utf-8')


def main_func():
    print("Checking...")
    # Init Mail Service
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login('adldotori@gmail.com', '###')  # input your password

    # mysql
    conn = pymysql.connect(host='localhost', user='root', password='###', db='cau',
                           charset='utf8')  # MYSQL connect  input your password
    curs = conn.cursor()  # MYSQL 커서(탐색 도구)

    # curs.execute('create table subjects(id int primary key,name varchar(20));')
    # curs.execute('create table lectures(contents varchar(40),foreign key(sub_id) references subjects(id));')
    print("ready")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome('/usr/bin/chromedriver',
                              chrome_options=chrome_options)  # 드라이버 설정(Windows는 chromedriver.exe)
    driver.implicitly_wait(3)  # 3초간 기다려달라(실행 후 준비를 위한 규약적인 시간)
    driver.get('https://eclass3.cau.ac.kr/')  # 원하는 URL로 이동하기

    driver.find_element_by_xpath('//*[@id="gnb"]/ul/li[3]/a').click()
    driver.find_element_by_id('login_user_id').send_keys('###')  # input your ID
    driver.find_element_by_id('login_user_password').send_keys('###')  # input your password
    driver.find_element_by_xpath('//*[@id="login_wapper"]/div[1]/div[4]/a').click()  # 로그인 버튼 클릭
    print("Login")
    htmls = driver.find_elements_by_class_name('ic-DashboardCard')
    course_list = []
    for html in htmls:
        soup = bs(html.get_attribute('outerHTML'), 'html.parser')
        course_id_raw = soup.find('a', href=True)
        course_name = str(soup).split('aria-label="')[1].split("\" class")[0]
        course_id = int(str(course_id_raw).split('/courses/')[1].split('"><')[0])
        course_list.append([course_name, course_id])
        sql = 'select * from subjects where id=' + str(course_id) + ';'
        curs.execute(sql)
        rows = curs.fetchall()
        # print(rows)
        if len(rows) == 0:
            sql = 'insert into subjects values(' + str(course_id) + ',\'' + course_name + '\');'
            curs.execute(sql)
            conn.commit()
            print(sql)

    for course in course_list:
        driver.get('https://eclass3.cau.ac.kr/courses/' + str(course[1]) + '/external_tools/3')
        lectures = []
        iframes = driver.find_elements_by_tag_name('iframe')

        if len(iframes) >= 1:
            driver.switch_to.frame(iframes[1])
        else:
            break

        for i in driver.find_elements_by_class_name('xnri-resource-title'):
            lectures.append(i.text)
            sql = 'select * from lectures where sub_id=' + str(course[1]) + ' and contents=\'' + i.text + '\';'
            curs.execute(sql)
            rows = curs.fetchall()
            # print(rows)
            if len(rows) == 0:
                sql = 'insert into lectures values(' + str(course[1]) + ',\'' + i.text + '\');'
                curs.execute(sql)
                conn.commit()
                contents = "someone에게\n\n과목(" + course[0] + ")에 \"" + i.text + "\"(이)라는 강의자료가 올라왔으니 꼭 확인하고 열공해요!!!"
                print(str(unicode(contents)))
                msg = MIMEText(str(unicode(contents)))
                msg['Subject'] = course[0] + ' 강의자료가 올라왔어요!!'.decode('utf-8').encode('utf-8')
                msg['To'] = 'someone\'s mail'
                smtp.sendmail('adldotori@gmail.com', msg['To'], msg.as_string())
    driver.quit()


logging.basicConfig()
print('Scheduler start...')
sched = BlockingScheduler()
sched.add_job(main_func, 'interval', hours=1)
sched.start()
