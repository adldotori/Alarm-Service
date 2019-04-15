from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import pymysql
import smtplib
from email.mime.text import MIMEText

# Init Mail Service
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.ehlo()
smtp.starttls()
smtp.login('adldotori@gmail.com', '###')

#mysql
conn = pymysql.connect(host='localhost', user='root', password='###', db='blackboard', charset='utf8') # MYSQL connect
curs = conn.cursor() # MYSQL 커서(탐색 도구)

driver = webdriver.Chrome('/Users/taeho/Downloads/chromedriver') # 드라이버 설정(Windows는 chromedriver.exe)
driver.implicitly_wait(3) # 3초간 기다려달라(실행 후 준비를 위한 규약적인 시간)
driver.get('https://kulms.korea.ac.kr') # 원하는 URL로 이동하기

driver.find_element_by_name('id').send_keys('adldotori')
driver.find_element_by_name('pw').send_keys('###')
driver.find_element_by_xpath('//*[@id="entry-login"]').click() # 로그인 버튼 클릭
driver.find_element_by_xpath('//*[@id="Courses.label"]/a').click()
try: # 내가 원하는 element가 load 될때까지 기다리기
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "_22_1termCourses__62_1")))
finally:
    pass


html = driver.find_element_by_xpath('//*[@id="_22_1termCourses__62_1"]/ul').get_attribute('innerHTML')
soup = bs(html, 'html.parser') # bs 객체 생성
course_list_raw = soup.find_all('a', href=True) # a 태그 중 href(즉 url) 존재하는 값들 모두 가져오기
course_list = [] # 과목 id 저장될 리스트
course_detail_base = 'https://kulms.korea.ac.kr/webapps/blackboard/execute/announcement?method=search&context=course_entry&course_id='
course_detail_list = []

for i in course_list_raw:
    course_each_id = str(i).split('id=')[1].split('&amp')[0] # 원하는 모양으로 파싱
    course_list.append(course_each_id)
    course_each_url = course_detail_base + course_each_id
    course_detail_list.append([course_each_url]) # 나중에 과제 주소 추가를 위해 리스트 형태로 넣음

print(course_detail_list)

for i in course_detail_list: # 각 코스별로의 url
    driver.get(i[0])
    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "courseMenuPalette_contents")))
        announce_raw = driver.page_source
        soup = bs(announce_raw, 'html.parser')
        announce_list_raw = soup.find('ul',{'id':'announcementList'})
        announce_list = announce_list_raw.find_all('li')
        announce_list.reverse()
        for ann in announce_list:
            #print(ann.attrs['id'])
            #print(ann.text)
            print('---------------')
            #sql = 'insert into announce values(\''+ann.attrs['id']+'\');'
            #curs.execute(sql)
            #conn.commit()
            msg = MIMEText(ann.text)
            msg['Subject'] = 'Announcement for ' + i[0].split('&course_id=')[1]
            msg['To'] = '777bogo@naver.com'
            #smtp.sendmail('adldotori@gmail.com','777bogo@naver.com', msg.as_string())

        homework_html = driver.find_element_by_xpath('//*[@id="courseMenuPalette_contents"]').get_attribute('innerHTML')
        soup = bs(homework_html, 'html.parser')
        nav_bars = soup.find_all('a')
        for bar in nav_bars:
            if str(bar.find('span').text) == '과제' or str(bar.find('span').text) == 'Assignments':
                homework_url = 'https://kulms.korea.ac.kr' + str(bar['href'])
                i.append(homework_url)
                driver.get(homework_url)
                homework_raw = driver.page_source
                soup = bs(homework_raw, 'html.parser')
                homeworks = soup.find('ul',{'id':'content_listContainer'}).find_all('li')
                for home in homeworks:
                    print(home.attrs['id'])
                    #print(home.text)
                    print('---------------')
                    sql = 'insert into homework values(\'' + home.attrs['id'] + '\');'
                    curs.execute(sql)
                    conn.commit()

    except Exception as e:
        homework_html = None
        print(e)
        pass


