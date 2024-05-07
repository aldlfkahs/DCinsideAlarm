# -*- coding: utf-8 -*-
'''
제작자 이메일 : aldlfkahs95@naver.com
제작자 블로그 : https://togomi.tistory.com/
참고 : https://github.com/jithurjacob/Windows-10-Toast-Notifications
      https://medium.com/@mjhans83/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%9C%BC%EB%A1%9C-%ED%81%AC%EB%A1%A4%EB%A7%81-%ED%95%98%EA%B8%B0-908e78ee09e0
      http://blog.naver.com/PostView.nhn?blogId=dbstjdans123&logNo=221163430022&categoryNo=23&parentCategoryNo=-1&viewDate=&currentPage=&postListTopCurrentPage=&isAfterWrite=true
      https://stackoverflow.com/questions/56695061/is-there-any-way-to-disable-the-notification-sound-on-win10toast-python-library
      https://wikidocs.net/4238
      https://www.element14.com/community/thread/57051/l/how-to-break-out-of-a-while-true-loop-with-a-button?displayFullThread=true
      https://stackoverflow.com/questions/37815371/pyinstaller-failed-to-execute-script-pyi-rth-pkgres-and-missing-packages
      https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
      https://wikidocs.net/21938
      https://wikidocs.net/35496
      https://wikidocs.net/36766
      https://weejw.tistory.com/264
      https://github.com/Charnelx/Windows-10-Toast-Notifications
      https://stackoverflow.com/questions/63867448/interactive-notification-windows-10-using-python
      https://cjsal95.tistory.com/35
      https://m.blog.naver.com/scyan2011/221723880069
      https://m.blog.naver.com/scyan2011/221723880069
      https://wikidocs.net/26
      https://stackoverflow.com/questions/22726860/beautifulsoup-webscraping-find-all-finding-exact-match
      https://pypi.org/project/win10toast-click/
      https://malja.github.io/zroya/index.html
      https://pypi.org/project/cloudscraper/
      https://websockets.readthedocs.io/en/stable/index.html
      https://github.com/APSODE/revived-witch-notice-bot/blob/main/ArcaLive.py
      https://m.blog.naver.com/draco6/221664143794
'''
'''
사용 전 필수 설정사항

시작 -> 설정 -> 시스템 -> 알림 및 작업 
-> 앱 및 다른 보낸사람의 알림 받기 -> 켬
'''
import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import asyncio
import websockets
import requests
import cloudscraper
import time
import logging
import threading
import webbrowser
from bs4 import BeautifulSoup
import platform
try:
    import zroya
except ImportError:
    zroya = None
import re
import yaml
import smtplib
import cerberus
from email.message import EmailMessage
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

version = '1.9.0'

class get_default_logger(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            logger = logging.getLogger('Notification')
            logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler(stream=sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(funcName)s - %(levelname)s - %(message)s'))
            logger.addHandler(console_handler)
            file_handler = logging.FileHandler('Notification.log', mode='a', encoding='utf-8', delay=True)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(f'{os.getpid():0>4X} - %(asctime)s - %(funcName)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)
            cls.instance = logger
        return cls.instance

class get_validator(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            schema = {
                'config_name': {'type': 'string'},
                'channel_url': {'type': 'string'},
                'use_filtering': {'type': 'boolean'},
                'filtering_type': {'type': 'dict', 'schema': {'Title': {'type': 'boolean'}, 'Author': {'type': 'boolean'}}},
                'keyword_list': {'type': 'list', 'schema': {'type': 'string'}},
                'notify_type': {'type': 'dict', 'schema': {'Desktop': {'type': 'boolean'}, 'Mobile': {'type': 'boolean'}}},
                'email': {'type': 'string'},
                'passwd': {'type': 'string'},
                'arcaid': {'type': 'string'},
                'arcapasswd': {'type': 'string'}
            }
            cls.instance = cerberus.Validator(schema, require_all=True)
        return cls.instance

class get_default_config(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            default_config = dict()
            default_config['config_name'] = 'default'
            default_config['channel_url'] = 'https://arca.live/b/breaking'
            default_config['use_filtering'] = False
            default_config['filtering_type'] = {'Title': True, 'Author': False}
            default_config['keyword_list'] = []
            default_config['notify_type'] = {'Desktop': True, 'Mobile': False}
            default_config['email'] = ''
            default_config['passwd'] = ''
            default_config['arcaid'] = ''
            default_config['arcapasswd'] = ''
            cls.instance = default_config
        return cls.instance

class get_session(object):
    @classmethod
    def create_new(cls):
        browsers = ['chrome', 'firefox']
        platforms = ['linux', 'windows', 'darwin']
        current_platform = platform.system().lower()
        if current_platform in platforms:
            platforms.insert(0, platforms.pop(platforms.index(current_platform)))
        for p in platforms:
            for b in browsers:
                scraper = cloudscraper.create_scraper(browser={'browser': b, 'platform': p, 'mobile': False})
                try:
                    status_code = scraper.get('https://arca.live/', timeout=5).status_code
                except cloudscraper.exceptions.CloudflareChallengeError:
                    pass
                else:
                    cls.instance = scraper
                    return cls()
        cls.instance = cloudscraper.create_scraper(browser={'custom': 'Mozilla/5.0'})
        return cls()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.create_new()
        return cls.instance

# url로 요청을 보내는 함수
def get_html(url, session, bot_account: dict = None):
    try:
        resp = session.get(url, timeout=5)
    except requests.exceptions.RequestException as e:
        return e
    except cloudscraper.exceptions.CloudflareException as e1:
        try:
            session.create_new()
            Login(session, bot_account)
            get_default_logger().warning('HTTP 세션을 초기화됨')
        except (requests.exceptions.RequestException,
                cloudscraper.exceptions.CloudflareException) as e2:
            get_default_logger().warning('HTTP 세션을 초기화하지 못했습니다.', exc_info=e2)
        return e1
    else:
        if resp.status_code == 200:
            return resp.text
        else:
            return requests.exceptions.HTTPError(f'Status Code: {resp.status_code}')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def toast_setup():
    try:
        if zroya:
            status = zroya.init(
                app_name="ArcaAlarm",
                company_name="python",
                product_name="python",
                sub_product="python",
                version=f"v{version}"
            )
    except Exception as e:
        get_default_logger().warning('WinToast 초기화에 실패했습니다.', exc_info=e)

def show_toast(title, body, link):
    try:
        if zroya:
            template = zroya.Template(zroya.TemplateType.ImageAndText3)
            if os.path.exists(resource_path("image.ico")):
                template.setImage(resource_path("image.ico"))
            template.setFirstLine(title)
            template.setSecondLine(body)
            def onClickHandler(notification_id):
                webbrowser.open_new(link)
            zroya.show(template, on_click=onClickHandler)
    except SystemError as e:
        return e
    else:
        return None

def send_email(subject, content, email, passwd):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = email
    try:
        email_domain = email.split('@').pop()
        smtp_server = f'smtp.{email_domain}'
        with smtplib.SMTP(smtp_server, 587) as smtp:
            smtp.starttls()
            smtp.login(email, passwd)
            smtp.send_message(msg)
    except (smtplib.SMTPException, OSError) as e:
        return e
    else:
        return None

def load_config():
    if os.path.exists('config.yaml'):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as yaml_file:
                yaml_data = list(yaml.safe_load_all(yaml_file))
        except yaml.YAMLError as e:
            get_default_logger().warning('yaml 파일을 불러오지 못했습니다.', exc_info=e)
            return [get_default_config()]
        else:
            config_data = list()
            for i in range(len(yaml_data)):
                if get_validator().validate(yaml_data[i]):
                    if yaml_data[i]['config_name'] == 'default':
                        config_data.insert(0, yaml_data[i])
                    else:
                        config_data.append(yaml_data[i])
                else:
                    get_default_logger().warning('검증에 실패한 config를 제외했습니다.', exc_info=ValueError(f'Invalid Config: {yaml_data[i]}'))
            if len(config_data) == 0 or config_data[0]['config_name'] != 'default':
                config_data.insert(0, get_default_config())
            return config_data
    else:
        return [get_default_config()]

def save_config(config_data):
    with open('config.yaml', 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump_all(config_data, yaml_file, indent=2, sort_keys=False, default_flow_style=False, allow_unicode=True)

class WebSocketEventListener(QThread):

    send_event = pyqtSignal()

    def __init__(self, location, parent=None):
        super().__init__(parent)
        self.location = location
        self.logger = get_default_logger()
        self.flag = True

    def run(self):
        while self.flag:
            try:
                asyncio.run(self.websocket_event_listener())
            except Exception as e:
                self.logger.error('웹소켓 통신 중 알 수 없는 오류 발생', exc_info=e)
                self.send_event.emit()
                time.sleep(3)

    async def websocket_event_listener(self):
        while self.flag:
            try:
                async with websockets.connect('wss://arca.live/arcalive',
                                                subprotocols=['arcalive'],
                                                origin='https://arca.live',
                                                extra_headers=get_session().headers) as websocket:
                    try:
                        self.logger.info('웹소켓 연결 성공')
                        await websocket.send('hello')
                        await websocket.send(f'c|{self.location}')
                        while self.flag:
                            try:
                                message = await asyncio.wait_for(websocket.recv(), timeout=1)
                                if message == 'na':
                                    self.send_event.emit()
                                    self.logger.info('새글 이벤트 감지')
                            except asyncio.TimeoutError:
                                pass
                    except (websockets.ConnectionClosed, RuntimeError) as e:
                        self.logger.warning('웹소켓 연결이 종료되었습니다.', exc_info=e)
            except (websockets.WebSocketException, asyncio.TimeoutError, OSError) as e:
                self.logger.warning('웹소켓 연결에 실패했습니다.', exc_info=e)
            finally:
                if self.flag:
                    self.send_event.emit()
                    await asyncio.sleep(3)
                    self.logger.info('웹소켓 연결 재시도')

    def stop(self):
        self.flag = False


#캡챠로 인해 사용하기 어려워진 구 로그인함수
#기기인증 화면을 따올려고 해도, beatifulsoup를 이용하면 제대로 이동이 안되는 문제가 있음.
'''
# 로그인 전송 데이터 생성
def CreateLoginPayloadData(session, url, bot_account: dict = None) -> dict:
    html = BeautifulSoup(get_html(url, session, bot_account), "html.parser")
    csrf = html.find("input", {"name": "_csrf"}).attrs.get("value")
    goto = html.find("input", {"name": "goto"}).attrs.get("value")
    login_payload = {
        "username": bot_account.get("ID"),
        "password": bot_account.get("PW"),
        "_csrf": csrf,
        "goto": goto
    }
    return login_payload

#로그인 하는 함수
def Login(session, bot_account):
    LOGIN_URL = "https://arca.live/u/login"
    LOGIN_RQ_RESPONSE = session.post(LOGIN_URL, data = CreateLoginPayloadData(session, LOGIN_URL, bot_account))
    if LOGIN_RQ_RESPONSE.status_code == 200:
        get_default_logger().info("로그인에 성공하였습니다.")
        return True
    else:
        get_default_logger().critical("로그인에 실패하였습니다.\nrequest response current status code : {LOGIN_RQ_RESPONSE.status_code}")
        return False
'''
#크로미움 사용하는 새 로그인함수
#TODO: exe화 했을때 작동하는지 확인 안함.
def Login(session, bot_account):
    driver = webdriver.Chrome() #크롬 사용
    driver.get("https://arca.live/u/login")
    
    #로그인 화면이 뜰때까지 기다리기
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID,'idInput')) and
        EC.presence_of_element_located((By.ID,'idPassword')) 
    )
    try: 
        #TODO: 1. 여기서 유저가 값기입/버튼 클릭을 못하게 할 필요가 있음
        #      2. 비밀번호 입력후 캡챠를 입력하시오라는 메시지를 띄우기
        driver.find_element(By.ID,'idInput').send_keys(bot_account.get("ID"))#자동으로 아이디 기입
        time.sleep(2)
        driver.find_element(By.XPATH,'//*[@id="stage-1"]/div[4]/button').click()#버튼 클릭
        time.sleep(1)
        driver.find_element(By.ID,'idPassword').send_keys(bot_account.get("PW"))#자동으로 비밀번호 기입
        time.sleep(2)
        driver.find_element(By.XPATH,'//*[@id="stage-2"]/div[4]/button').click()#버튼 클릭
    finally:
            
        try:
            loginSuccess=False
            WebDriverWait(driver, 120).until(
                EC.url_to_be("https://arca.live/") or
                #아카 UI 업데이트 이후 이전기록이 없음 이 페이지로 이동함 
                EC.url_to_be("https://arca.live/u/null")
            )
            try:
                #TODO: 봇은 아니십니까? 메시지 창을 검증하는 루틴 필요
                #html 요소로 판단하게 할려고 했는데 잘 안되는것 같음
                capcha_test=driver.find_elements(By.ID, "hcaptcha-form")#봇캡챠 id 넣을것
                WebDriverWait(driver, 120).until(
                    EC.staleness_of((By.ID, "hcaptcha-form"))#봇캡챠
                )
            finally:
                time.sleep(2)
                for cookie in driver.get_cookies():
                    c = {cookie['name'] : cookie['value']}
                    print(c)
                    session.cookies.update(c)
                    if cookie['name']=='campaign.session':
                        loginSuccess=True
                driver.quit()
                return loginSuccess
        except Exception as e:
            return False


class Notification(QThread):

    error = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, url, use_desktop, use_mobile, email, passwd, keyword_list, session, bot_account, parent=None):
        super().__init__(parent)
        self.url = url
        self.use_desktop = use_desktop
        self.use_mobile = use_mobile
        self.email = email
        self.passwd = passwd
        self.keyword_list = keyword_list
        self.session = session
        self.bot_account = bot_account
        self.logger = get_default_logger()
        self.event_flag = False
        self.flag = True

        attrs = dict(url=url, use_desktop=use_desktop, use_mobile=use_mobile,
                        email=email, passwd=passwd, keyword_list=keyword_list)
        self.logger.debug(f'Notification init: {attrs}')

    def run(self):
        try:
            toast_setup()
            if self.setup():
                self.logger.info('알림 시작')
                self.done.emit(True)
                result = True
                while self.flag:
                    if self.check_event():
                        result = self.new_article_action()
                    elif not result:
                        self.logger.info('실패한 이벤트 처리 재시도')
                        result = self.new_article_action()
                    time.sleep(3)
            else:
                return
        except Exception as e:
            self.logger.critical('알 수 없는 오류로 스레드가 종료되었습니다.', exc_info=e)
            self.error.emit('알 수 없는 오류로 스레드가 종료되었습니다.')
        else:
            self.logger.info('알림 중지')
            self.done.emit(False)

    def setup(self):
        # 채널 주소에서 채널 ID를 파싱하는 정규표현식 매칭
        self.url_parser = re.match(r"^http[s]?://arca[.]live(?P<location>/b/(?P<channel_id>[a-z0-9]+)(|/[0-9]+)/?($|[?].*))", self.url)
        if not self.url_parser:
            # 매칭이 되지 않으면 오류 메시지 출력 및 예외 처리
            self.logger.critical('채널 주소가 잘못되었습니다.')
            self.error.emit('채널 주소가 잘못되었습니다.')
            return False

        html = get_html(self.url, self.session, self.bot_account)
        if not isinstance(html, str):
            self.logger.critical('웹 페이지를 불러오지 못했습니다.', exc_info=html)
            self.error.emit('웹 페이지를 불러오지 못했습니다.')
            return False
        soup = BeautifulSoup(html, 'html.parser')

        # 받아온 html에서 게시글 주소만 파싱
        try:
            new_post = soup.find("div", class_="list-table").find_all('a', class_='vrow')
        except AttributeError:
            self.logger.critical('웹 페이지 파싱에 실패했습니다.')
            self.error.emit('웹 페이지 파싱에 실패했습니다.')
            return False

        # 채널 주소에서 origin을 제외한 location 추출
        location = self.url_parser.group('location')
        # 체널 주소에서 채널 ID만 추출
        self.channel_id = self.url_parser.group('channel_id')
        # 게시글 주소에서 글 번호만 추출하는 정규표현식 정의
        self.p_post_id = re.compile(self.channel_id + r"/(?P<post_id>[\d]+)[?]?")

        # recent 변수에 현재 최신 글 번호를 저장
        self.recent = 0
        for n in new_post:
            # 공지 게시글 제외
            if 'notice' in n.attrs['class']:
                continue
            post_link = n.attrs['href']
            # 게시글 주소에서 정규표현식 매칭
            s_post_id = self.p_post_id.search(post_link)
            if s_post_id:
                # 매칭이 되면 글 번호만 추출
                self.recent = int(s_post_id.group('post_id'))
                break

        self.last_check = self.recent
        self.logger.info(f'최신 글 번호 추출 성공: {self.recent}')
        self.event_listener = WebSocketEventListener(location)
        self.event_listener.send_event.connect(self.receive_event)
        self.finished.connect(self.event_listener.stop)
        self.event_listener.start()
        return True

    def new_article_action(self):
        self.logger.info(f'새글 파싱 시도')
        html = get_html(self.url, self.session, self.bot_account)
        if not isinstance(html, str):
            self.logger.error('웹 페이지를 불러오지 못했습니다.', exc_info=html)
            return False
        soup = BeautifulSoup(html, 'html.parser')

        # 게시글 주소
        try:
            new_post = soup.find("div", class_="list-table").find_all('a', class_='vrow')
        except AttributeError:
            self.logger.error('웹 페이지 파싱에 실패했습니다.')
            return False

        # 새로 가져온 리스트의 글 번호들을 비교
        for n in reversed(new_post):
            if not self.flag:
                break
            # 공지 게시글 제외
            if 'notice' in n.attrs['class']:
                continue
            post_link = n.attrs['href']
            # 게시글 주소에서 정규표현식 매칭
            s_post_id = self.p_post_id.search(post_link)
            if not s_post_id:
                continue
            # 매칭이 되면 글 번호만 추출하여 정수형으로 저장
            post_id = int(s_post_id.group('post_id'))
            # 새로 가져온 글 번호가 더 크다면, 새로운 글 이라는 뜻
            if (post_id > self.recent):
                try:
                    title = n.find("span", class_="title").text.strip()         # 제목
                except AttributeError:
                    title = 'Unknown'
                try:
                    author = n.find("span", class_="col-author").text.strip()   # 작성자
                except AttributeError:
                    author = 'Unknown'

                header = n.find_all("span", class_="badge")                     # 글머리
                header = [hd.text.strip() for hd in header]

                header_f = ' '.join([f'[{hd}]' for hd in header if hd != ''])
                title_f = f'{header_f} {title}'.strip().replace('\n', '\t')

                if post_id > self.last_check:
                    self.last_check = post_id
                    self.logger.info(f'새글 파싱 성공: {post_id}')
                    self.logger.debug(f'new article data: {dict(title=title_f, author=author)}')

                # 키워드=off 일 경우, 바로 토스트 메시지로 표시
                if self.keyword_list is None:
                    self.logger.debug('키워드 비활성화 상태')
                    self.notification_action(title_f, author, post_id)
                    self.recent = post_id
                # 키워드=on 일 경우, 체크된 기준(제목 혹은 작성자)에 키워드가 포함 되어있다면 토스트 메시지로 표시
                else:
                    for keyword in self.keyword_list:
                        if (ex.k_titleCB.isChecked() and keyword in title_f) or (ex.k_authorCB.isChecked() and keyword in author):
                            if post_id < self.last_check:
                                self.logger.info(f'변경글 파싱 성공: {post_id}')
                                self.logger.debug(f'updated article data: {dict(title=title_f, author=author)}')
                            self.logger.debug('키워드 매칭 성공')
                            self.notification_action(title_f, author, post_id)
                            self.recent = post_id
                            break
        return True

    def notification_action(self, title_f, author, post_id):
        full_link = f'https://arca.live/b/{self.channel_id}/{post_id}'
        if self.use_desktop:
            e = show_toast(title_f, author, full_link)
            if e is None:
                self.logger.info(f'윈도우 알림 생성 성공')
            else:
                self.logger.error('윈도우 알림 생성에 실패했습니다.', exc_info=e)
        if self.use_mobile:
            subject = '[ArcaAlarm] new post'
            content = f'Title: {title_f}\nAuthor: {author}\n\n{full_link}'
            e = send_email(subject, content, self.email, self.passwd)
            if e is None:
                self.logger.info(f'이메일 알림 전송 성공')
            else:
                self.logger.error('이메일 알림 전송에 실패했습니다.', exc_info=e)

    def check_event(self):
        event_flag = self.event_flag
        self.event_flag = False
        return event_flag

    def receive_event(self):
        self.event_flag = True

    def stop(self):
        self.flag = False

class MyApp(QWidget):

    stop = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.thread = None

    def get_main_UI(self):
        widget = QWidget(self)
        grid = QGridLayout(widget)

        self.urlLE = QLineEdit('', self)
        self.urlLb = QLabel('채널 주소')
        self.urlLb.setAlignment(Qt.AlignTop)
        self.m_versionLb = QLabel(f'버전 : {version}')
        self.m_versionLb.setAlignment(Qt.AlignTop)

        # 시작/중지 버튼
        self.startBtn = QPushButton('시작', self)
        self.startBtn.clicked.connect(self.startNotification)
        self.startBtn.clicked.connect(self.updateKeywordGroupState)

        self.keywordLb = QLabel('키워드')
        self.keywordLW = QListWidget(self)

        # 키워드 온/오프 버튼
        self.k_onRB = QRadioButton('ON', self)
        self.k_offRB = QRadioButton('OFF', self)
        self.k_group = QButtonGroup(self)
        self.k_group.addButton(self.k_onRB)
        self.k_group.addButton(self.k_offRB)
        self.k_onRB.clicked.connect(self.updateOptionState)
        self.k_offRB.clicked.connect(self.updateOptionState)

        # 키워드 제목/작성자 선택 버튼
        self.isTitleLb = QLabel('기준')
        self.k_titleCB = QCheckBox('제목', self)
        self.k_authorCB = QCheckBox('작성자', self)

        # 추가할 키워드 적는 칸
        self.newItemLE = QLineEdit('', self)

        # 키워드 추가/삭제 버튼
        self.k_appendBtn = QPushButton('추가', self)
        self.k_appendBtn.clicked.connect(self.k_append)
        self.k_removeBtn = QPushButton('삭제', self)
        self.k_removeBtn.clicked.connect(self.k_remove)

        # 설정 저장, 기타 설정 버튼
        self.saveCrntBtn = QPushButton('저장', self)
        self.saveCrntBtn.clicked.connect(self.currentConfigSave)
        self.settingBtn = QPushButton('기타 설정', self)
        self.settingBtn.clicked.connect(self.toSettingPage)

        # 위에서 선언한 위젯들의 위치를 지정
        grid.addWidget(self.urlLb, 0, 0)
        grid.addWidget(self.m_versionLb, 0, 6)
        grid.addWidget(self.urlLE, 1, 0, 1, 7)
        grid.addWidget(self.startBtn, 2, 0, 1, 7)
        grid.addWidget(self.keywordLb, 3, 0)
        grid.addWidget(self.k_onRB, 3, 1)
        grid.addWidget(self.k_offRB, 3, 2)
        grid.addWidget(self.isTitleLb, 3, 4)
        grid.addWidget(self.k_titleCB, 3, 5)
        grid.addWidget(self.k_authorCB, 3, 6)
        grid.addWidget(self.newItemLE, 4, 0, 1, 6)
        grid.addWidget(self.keywordLW, 5, 0, 3, 6)
        grid.addWidget(self.k_appendBtn, 4, 6)
        grid.addWidget(self.k_removeBtn, 5, 6)
        grid.addWidget(self.saveCrntBtn, 6, 6)
        grid.addWidget(self.settingBtn, 7, 6)

        return widget

    def get_setting_UI(self):
        widget = QWidget(self)
        grid = QGridLayout(widget)

        self.settingLb = QLabel('기타 설정')
        self.settingLb.setAlignment(Qt.AlignTop)
        self.s_versionLb = QLabel(f'버전 : {version}')
        self.s_versionLb.setAlignment(Qt.AlignTop)

        self.nt_typeLb = QLabel('알림 방식')

        # 알림 방식 선택 버튼
        self.nt_desktopRB = QRadioButton('데스크톱', self)
        self.nt_mobileRB = QRadioButton('모바일', self)
        self.nt_bothRB = QRadioButton('모두', self)
        self.nt_group = QButtonGroup(self)
        self.nt_group.addButton(self.nt_desktopRB)
        self.nt_group.addButton(self.nt_mobileRB)
        self.nt_group.addButton(self.nt_bothRB)

        self.arcaidLb = QLabel('아이디')
        self.arcapasswdLb = QLabel('비밀번호')

        self.arcaidLE = QLineEdit('', self)
        self.arcapasswdLE = QLineEdit('', self)
        self.arcapasswdLE.setEchoMode(QLineEdit.Password)

        self.emailLb = QLabel('이메일')
        self.passwdLb = QLabel('비밀번호')

        self.emailLE = QLineEdit('', self)
        self.passwdLE = QLineEdit('', self)
        self.passwdLE.setEchoMode(QLineEdit.Password)

        self.configLW = QListWidget(self)
        self.configLW.itemDoubleClicked.connect(self.configEdit)
        self.configLW.itemClicked.connect(self.configChanged)
        self.configLW.itemChanged.connect(self.configChanged)
        self.configLW.currentItemChanged.connect(lambda cur, prev: self.configChanged(prev))

        # 저장/불러오기 버튼
        self.saveBtn = QPushButton('저장', self)
        self.saveBtn.clicked.connect(self.configSave)
        self.loadBtn = QPushButton('불러오기', self)
        self.loadBtn.clicked.connect(self.configLoad)

        # 초기화, 나가기 버튼
        self.resetBtn = QPushButton('초기화', self)
        self.resetBtn.clicked.connect(self.currentConfigReset)
        self.mainBtn = QPushButton('나가기', self)
        self.mainBtn.clicked.connect(self.toMainPage)

        # 위에서 선언한 위젯들의 위치를 지정
        grid.addWidget(self.settingLb, 0, 0)
        grid.addWidget(self.s_versionLb, 0, 4)
        grid.addWidget(self.nt_typeLb, 1, 0)
        grid.addWidget(self.nt_desktopRB, 1, 1)
        grid.addWidget(self.nt_mobileRB, 1, 2)
        grid.addWidget(self.nt_bothRB, 1, 3)
        grid.addWidget(self.arcaidLb, 2, 0)
        grid.addWidget(self.arcaidLE, 2, 1, 1, 1)
        grid.addWidget(self.arcapasswdLb, 3, 0)
        grid.addWidget(self.arcapasswdLE, 3, 1, 1, 1)
        grid.addWidget(self.emailLb, 2, 2)
        grid.addWidget(self.emailLE, 2, 3, 1, 2)
        grid.addWidget(self.passwdLb, 3, 2)
        grid.addWidget(self.passwdLE, 3, 3, 1, 2)
        grid.addWidget(self.configLW, 4, 0, 4, 4)
        grid.addWidget(self.saveBtn, 4, 4)
        grid.addWidget(self.loadBtn, 5, 4)
        grid.addWidget(self.resetBtn, 6, 4)
        grid.addWidget(self.mainBtn, 7, 4)

        return widget

    # UI 설정
    def initUI(self):
        config_data = load_config()
        save_config(config_data)

        self.layout = QStackedLayout()

        self.main_page = self.get_main_UI()
        self.setting_page = self.get_setting_UI()

        self.set_config(config_data[0])

        self.layout.addWidget(self.main_page)
        self.layout.addWidget(self.setting_page)

        self.setLayout(self.layout)

        self.setWindowTitle('아카라이브 새글 알리미')
        self.setWindowIcon(QIcon(resource_path('icon.png')))
        self.setFixedSize(self.sizeHint())
        self.center()
        self.show()

    def get_config(self):
        use_desktop = self.nt_desktopRB.isChecked() or self.nt_bothRB.isChecked()
        use_mobile = self.nt_mobileRB.isChecked() or self.nt_bothRB.isChecked()
        keyword_opt_title = self.k_titleCB.isChecked()
        keyword_opt_author = self.k_authorCB.isChecked()
        current_config = dict()
        current_config['config_name'] = self.config_name
        current_config['channel_url'] = self.urlLE.text()
        current_config['use_filtering'] = self.k_onRB.isChecked()
        current_config['filtering_type'] = {'Title': keyword_opt_title, 'Author': keyword_opt_author}
        current_config['keyword_list'] = [self.keywordLW.item(i).text() for i in range(self.keywordLW.count())]
        current_config['notify_type'] = {'Desktop': use_desktop, 'Mobile': use_mobile}
        current_config['email'] = self.emailLE.text()
        current_config['passwd'] = self.passwdLE.text()
        current_config['arcaid'] = self.arcaidLE.text()
        current_config['arcapasswd'] = self.arcapasswdLE.text()
        return current_config

    def set_config(self, init_config):
        self.config_name = init_config['config_name']
        self.urlLE.setText(init_config['channel_url'])
        self.keywordLW.clear()
        self.keywordLW.addItems(init_config['keyword_list'])
        if init_config['use_filtering']:
            self.k_onRB.setChecked(True)
            self.k_titleCB.setEnabled(True)
            self.k_authorCB.setEnabled(True)
        else:
            self.k_offRB.setChecked(True)
            self.k_titleCB.setEnabled(False)
            self.k_authorCB.setEnabled(False)
        self.newItemLE.clear()
        if init_config['filtering_type']['Title']:
            self.k_titleCB.setChecked(True)
        if init_config['filtering_type']['Author']:
            self.k_authorCB.setChecked(True)
        if init_config['notify_type']['Mobile']:
            if init_config['notify_type']['Desktop']:
                self.nt_bothRB.setChecked(True)
            else:
                self.nt_mobileRB.setChecked(True)
        else:
            self.nt_desktopRB.setChecked(True)
        self.emailLE.setText(init_config['email'])
        self.passwdLE.setText(init_config['passwd'])
        self.arcaidLE.setText(init_config['arcaid'])
        self.arcapasswdLE.setText(init_config['arcapasswd'])

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def error(self, e):
        QMessageBox.warning(self, "오류", str(e))
        self.startBtn.setText('시작')

    def done(self, flag):
        if flag:
            QMessageBox.information(self, "실행", "알림이 시작 되었습니다.")
            self.startBtn.setText('중지')
        else:
            QMessageBox.information(self, "중지", "알림이 중지 되었습니다.")
            self.startBtn.setText('시작')

    # 시작/중지 버튼
    def startNotification(self):
        if self.startBtn.text() == '중지':
            self.stop.emit()
        elif self.thread is None or self.thread.isFinished():
            channel_url = self.urlLE.text()
            use_desktop = self.nt_desktopRB.isChecked() or self.nt_bothRB.isChecked()
            use_mobile = self.nt_mobileRB.isChecked() or self.nt_bothRB.isChecked()
            email, passwd = self.emailLE.text(), self.passwdLE.text()
            session = get_session.create_new() # 세션 초기화
            bot_account = {
                "ID": self.arcaidLE.text(),
                "PW": self.arcapasswdLE.text()
            }
            
            if self.k_onRB.isChecked():
                keyword_list = [self.keywordLW.item(i).text() for i in range(self.keywordLW.count())]
            else:
                keyword_list = None
            
            login=Login(session, bot_account)
            if not login:
                QMessageBox.warning(self, "로그인 실패", "로그인에 실패했습니다.\n비로그인상태에서는 성인전용 게시판의 알림이 오지 않습니다.\n\n팁)봇 감지에 걸렸을수도 있습니다. 다른 브라우저 창에서 캡챠를 해결해보세요.")
            
            self.thread = Notification(channel_url, use_desktop, use_mobile, email, passwd, keyword_list, session, bot_account, parent=self)
            self.thread.error.connect(self.error)
            self.thread.done.connect(self.done)
            self.stop.connect(self.thread.stop)
            self.thread.start()

    def updateKeywordGroupState(self):
        if self.startBtn.text() == '중지':
            for button in self.k_group.buttons():
                button.setEnabled(True)
            self.k_titleCB.setEnabled(True)
            self.k_authorCB.setEnabled(True)
        else:
            for button in self.k_group.buttons():
                button.setEnabled(False)
            self.k_titleCB.setEnabled(False)
            self.k_authorCB.setEnabled(False)

    def updateOptionState(self):
        if self.k_onRB.isChecked():
            self.k_titleCB.setEnabled(True)
            self.k_authorCB.setEnabled(True)
        else:
            self.k_titleCB.setEnabled(False)
            self.k_authorCB.setEnabled(False)

    # 키워드 추가 버튼
    def k_append(self):
        if self.newItemLE.text() != '':
            self.keywordLW.addItem(self.newItemLE.text())

    # 키워드 삭제 버튼
    def k_remove(self):
        select = self.keywordLW.currentRow()
        self.keywordLW.takeItem(select)

    # 설정 저장 버튼
    def currentConfigSave(self):
        self.config_name = 'default'
        current_config = self.get_config()
        config_data = load_config()
        config_data[0] = current_config
        save_config(config_data)
        QMessageBox.information(self, "저장", "설정이 저장 되었습니다.")

    # 기타 설정 버튼
    def toSettingPage(self):
        config_data = load_config()

        self.configLW.clear()
        matched = False
        for i in range(len(config_data)):
            self.configLW.addItem(config_data[i]['config_name'])
            if self.configLW.currentRow() == -1 and config_data[i]['config_name'] == self.config_name:
                self.configLW.setCurrentRow(i)
                matched = True
        self.configLW.addItem('')
        if not matched:
            self.configLW.setCurrentRow(0)

        self.layout.setCurrentIndex(1)

    def configEdit(self, item):
        current_row = self.configLW.indexFromItem(item).row()
        if current_row == self.configLW.count()-1:
            self.configLW.openPersistentEditor(item)
        else:
            current_config_name = item.text()
            answer = QMessageBox.question(self, "삭제", f"{current_config_name} 설정을 삭제하시겠습니까?")

            if answer == QMessageBox.Yes:
                config_data = load_config()

                for i in range(len(config_data)):
                    if config_data[i]['config_name'] == current_config_name:
                        config_data.pop(i)
                        break

                save_config(config_data)
                self.toSettingPage()
                QMessageBox.information(self, "삭제", "설정이 삭제되었습니다.")

    def configChanged(self, item):
        if self.configLW.isPersistentEditorOpen(item):
            self.configLW.closePersistentEditor(item)
            if item.text() != '':
                self.configLW.addItem('')

    # 설정 저장 버튼 (기타 설정)
    def configSave(self):
        current_config_name = self.configLW.currentItem().text()
        if current_config_name == '':
            return

        answer = QMessageBox.question(self, "저장", f"설정을 {current_config_name}에 저장하시겠습니까?")
        if answer == QMessageBox.Yes:
            self.config_name = current_config_name
            current_config = self.get_config()
            config_data = load_config()

            matched = False
            for i in range(len(config_data)):
                if config_data[i]['config_name'] == current_config_name:
                    config_data[i] = current_config
                    matched = True
                    break
            if not matched:
                config_data.append(current_config)

            save_config(config_data)
            self.toSettingPage()
            QMessageBox.information(self, "저장", "설정이 저장되었습니다.")

    # 설정 불러오기 버튼 (기타 설정)
    def configLoad(self):
        current_config_name = self.configLW.currentItem().text()
        if current_config_name == '':
            return

        answer = QMessageBox.question(self, "불러오기", f"설정 {current_config_name}을 불러오시겠습니까?")
        if answer == QMessageBox.Yes:
            config_data = load_config()

            matched = False
            for i in range(len(config_data)):
                if config_data[i]['config_name'] == current_config_name:
                    init_config = config_data[i]
                    matched = True
                    break

            if matched:
                self.set_config(init_config)
                self.toSettingPage()
                QMessageBox.information(self, "불러오기", "설정을 성공적으로 불러왔습니다.")
            else:
                self.toSettingPage()
                QMessageBox.warning(self, "불러오기", "설정을 불러오는데 실패하였습니다.")

    # 설정 초기화 버튼 (기타 설정)
    def currentConfigReset(self):
        answer = QMessageBox.question(self, "초기화", "현재 설정을 초기화하시겠습니까?")
        if answer == QMessageBox.Yes:
            default_config = get_default_config()
            default_config['config_name'] = self.config_name
            self.set_config(default_config)
            QMessageBox.information(self, "초기화", "현재 설정이 초기화되었습니다.")

    # 나가기 버튼 (기타 설정)
    def toMainPage(self):
        self.layout.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
