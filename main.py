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
import cerberus

version = '1.7.2'

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
                'channel_url': {'type': 'string'},
                'use_filtering': {'type': 'boolean'},
                'keyword_list': {'type': 'list', 'schema': {'type': 'string'}},
            }
            cls.instance = cerberus.Validator(schema, require_all=True)
        return cls.instance

class get_default_config(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            default_config = dict()
            default_config['channel_url'] = 'https://arca.live/b/singbung'
            default_config['use_filtering'] = False
            default_config['keyword_list'] = []
            cls.instance = default_config
        return cls.instance

class get_scraper(object):
    @classmethod
    def create_new(cls):
        browsers = ['chrome', 'firefox']
        platforms = ['linux', 'windows', 'darwin']
        if platform.system().lower() in platforms:
            platforms.insert(0, platforms.pop(platforms.index(platform.system().lower())))
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
def get_html(url, method='GET', params=None, data=None):
    try:
        resp = get_scraper().request(method=method, url=url, params=params, data=data, timeout=5)
    except requests.exceptions.RequestException as e:
        return e
    except cloudscraper.exceptions.CloudflareException as e:
        return e
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
            if os.path.exists(resource_path("arca_image.ico")):
                template.setImage(resource_path("arca_image.ico"))
            template.setFirstLine(title)
            template.setSecondLine(body)
            def onClickHandler(notification_id):
                webbrowser.open_new(link)
            zroya.show(template, on_click=onClickHandler)
    except SystemError as e:
        return e
    else:
        return None

def load_config():
    if os.path.exists('config.yaml'):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)
        except yaml.YAMLError as e:
            get_default_logger().warning('yaml 파일을 불러오지 못했습니다.', exc_info=e)
            return get_default_config()
        else:
            if get_validator().validate(yaml_data):
                return yaml_data
            else:
                get_default_logger().warning('불러온 데이터의 검증에 실패했습니다.', exc_info=ValueError(f'Invalid Config: {yaml_data}'))
                return get_default_config()
    else:
        return get_default_config()

def save_config(config_data):
    with open('config.yaml', 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(config_data, yaml_file, indent=2, sort_keys=False, default_flow_style=False, allow_unicode=True)

class Notification(QThread):

    error = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, url, keyword_list, parent=None):
        super().__init__(parent)
        self.url = url.lower()
        self.keyword_list = keyword_list
        self.logger = get_default_logger()
        self.flag = True
        attrs = dict(url=url, keyword_list=keyword_list)
        self.logger.debug(f'Notification init: {attrs}')


    def run(self):
        try:
            toast_setup()
            if self.setup():
                self.logger.info('알림 시작')
                self.done.emit(True)
                asyncio.run(self.websocket_event_listener())
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
        self.url_parser = re.match(r"^http[s]?://arca[.]live(?P<location>/b/(?P<channel_id>[a-z\d]+)/?($|[?].*))", self.url)
        if not self.url_parser:
            # 매칭이 되지 않으면 오류 메시지 출력 및 예외 처리
            self.logger.critical('채널 주소가 잘못되었습니다.')
            self.error.emit('채널 주소가 잘못되었습니다.')
            return False

        html = get_html(self.url)
        if not isinstance(html, str):
            self.logger.critical('웹 페이지를 불러오지 못했습니다.', exc_info=html)
            self.error.emit('웹 페이지를 불러오지 못했습니다.')
            return False
        soup = BeautifulSoup(html, 'html.parser')

        # 받아온 html에서 게시글 주소만 파싱
        try:
            l = soup.find("div", class_="list-table").find_all('a', class_='vrow')
        except AttributeError:
            self.logger.critical('웹 페이지 파싱에 실패했습니다.')
            self.error.emit('웹 페이지 파싱에 실패했습니다.')
            return False

        # 채널 주소에서 origin을 제외한 location 추출
        self.location = self.url_parser.group('location')
        # 체널 주소에서 채널 ID만 추출
        self.channel_id = self.url_parser.group('channel_id')
        # 게시글 주소에서 글 번호만 추출하는 정규표현식 정의
        self.p_post_id = re.compile(self.channel_id + r"/(?P<post_id>[\d]+)[?]?")

        # recent 변수에 현재 최신 글 번호를 저장
        self.recent = 0
        for n in l:
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

        self.logger.info(f'최신 글 번호 추출 성공: {self.recent}')
        return True

    async def websocket_event_listener(self):
        while self.flag:
            try:
                async with websockets.connect('wss://arca.live/arcalive',
                                                subprotocols=['arcalive'],
                                                origin='https://arca.live',
                                                extra_headers=get_scraper().headers) as websocket:
                    try:
                        self.logger.info('웹소켓 연결 성공')
                        await websocket.send('hello')
                        await websocket.send(f'c|{self.location}')
                        while self.flag:
                            try:
                                message = await asyncio.wait_for(websocket.recv(), timeout=1)
                                if message == 'na':
                                    self.logger.info('새글 이벤트 감지')
                                    self.new_article_action()
                            except asyncio.TimeoutError:
                                pass
                    except websockets.ConnectionClosed as e:
                        self.logger.warning('웹소켓 연결이 종료되었습니다.', exc_info=e)
            except (websockets.InvalidURI, websockets.InvalidHandshake) as e:
                self.logger.warning('웹소켓 연결에 실패했습니다.', exc_info=e)
            finally:
                if self.flag:
                    await asyncio.sleep(3)

    def new_article_action(self):
        html = get_html(self.url)
        if not isinstance(html, str):
            self.logger.error('웹 페이지를 불러오지 못했습니다.', exc_info=html)
            self.notification_action('Unknown', 'Unknown', '')
            return
        soup = BeautifulSoup(html, 'html.parser')
        new_post = soup.find("div", class_="list-table")

        # 게시글 주소
        try:
            new_link = new_post.find_all('a', class_='vrow')
        except AttributeError:
            self.logger.error('웹 페이지 파싱에 실패했습니다.')
            self.notification_action('Unknown', 'Unknown', '')
            return

        # 새로 가져온 리스트의 글 번호들을 비교
        for n in reversed(new_link):
            if self.flag == False:
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
                title_f = f'{header_f} {title}'.strip()

                self.logger.info(f'새글 파싱 성공: {post_id}')
                self.logger.debug(f'new article data: {dict(title=title_f, author=author)}')

                # 키워드=off 일 경우, 바로 토스트 메시지로 표시
                if self.keyword_list is None:
                    self.logger.debug('키워드 비활성화 상태')
                    self.notification_action(title_f, author, post_id)
                    self.recent = post_id
                # 키워드=on 일 경우, 제목에 키워드가 포함 되어있다면 토스트 메시지로 표시
                else:
                    for keyword in self.keyword_list:
                        if keyword in title_f:
                            self.logger.debug('키워드 매칭 성공')
                            self.notification_action(title_f, author, post_id)
                            self.recent = post_id
                            break

    def notification_action(self, title_f, author, post_id):
        full_link = f'https://arca.live/b/{self.channel_id}/{post_id}'
        e = show_toast(title_f, author, full_link)
        if e is None:
            self.logger.info(f'윈도우 알림 생성 성공')
        else:
            self.logger.error('윈도우 알림 생성에 실패했습니다.', exc_info=e)

    def stop(self):
        self.flag = False

class MyApp(QWidget):

    stop = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.thread = None

    def get_main_UI(self):
        grid = QGridLayout(self)

        self.urlLE = QLineEdit('', self)
        self.urlLb = QLabel('채널 주소')
        self.urlLb.setAlignment(Qt.AlignTop)
        self.m_versionLb = QLabel(f'버전 : {version}')
        self.m_versionLb.setAlignment(Qt.AlignTop)

        # 시작/중지 버튼
        self.startBtn = QPushButton('시작', self)
        self.startBtn.clicked.connect(self.startNotification)

        self.keywordLb = QLabel('키워드')
        self.keywordLW = QListWidget(self)

        # 키워드 온/오프 버튼
        self.k_onRB = QRadioButton('ON', self)
        self.k_offRB = QRadioButton('OFF', self)
        self.k_group = QButtonGroup(self)
        self.k_group.addButton(self.k_onRB)
        self.k_group.addButton(self.k_offRB)

        # 추가할 키워드 적는 칸
        self.newItemLE = QLineEdit('', self)

        # 키워드 추가/삭제 버튼
        self.k_appendBtn = QPushButton('추가', self)
        self.k_appendBtn.clicked.connect(self.k_append)
        self.k_removeBtn = QPushButton('삭제', self)
        self.k_removeBtn.clicked.connect(self.k_remove)

        # 설정 저장, 불러오기, 초기화 버튼
        self.saveCrntBtn = QPushButton('저장', self)
        self.saveCrntBtn.clicked.connect(self.currentConfigSave)
        self.loadCrntBtn = QPushButton('불러오기', self)
        self.loadCrntBtn.clicked.connect(self.currentConfigLoad)
        self.resetCrntBtn = QPushButton('초기화', self)
        self.resetCrntBtn.clicked.connect(self.currentConfigReset)

        # 위에서 선언한 위젯들의 위치를 지정
        grid.addWidget(self.urlLb, 0, 0)
        grid.addWidget(self.m_versionLb, 0, 4)
        grid.addWidget(self.urlLE, 1, 0, 1, 5)
        grid.addWidget(self.startBtn, 2, 0, 1, 5)
        grid.addWidget(self.keywordLb, 3, 0)
        grid.addWidget(self.k_onRB, 3, 1)
        grid.addWidget(self.k_offRB, 3, 2)
        grid.addWidget(self.newItemLE, 3, 3)
        grid.addWidget(self.resetCrntBtn, 3, 4)
        grid.addWidget(self.keywordLW, 4, 0, 4, 4)
        grid.addWidget(self.k_appendBtn, 4, 4)
        grid.addWidget(self.k_removeBtn, 5, 4)
        grid.addWidget(self.saveCrntBtn, 6, 4)
        grid.addWidget(self.loadCrntBtn, 7, 4)

        return grid

    # UI 설정
    def initUI(self):
        config_data = load_config()
        save_config(config_data)

        self.layout = self.get_main_UI()

        self.set_config(config_data)

        self.setLayout(self.layout)

        self.setWindowTitle('아카라이브 새글 알리미')
        self.setWindowIcon(QIcon(resource_path('icon.png')))
        self.setFixedSize(self.sizeHint())
        self.center()
        self.show()

    def get_config(self):
        current_config = dict()
        current_config['channel_url'] = self.urlLE.text()
        current_config['use_filtering'] = self.k_onRB.isChecked()
        current_config['keyword_list'] = [self.keywordLW.item(i).text() for i in range(self.keywordLW.count())]
        return current_config

    def set_config(self, init_config):
        self.urlLE.setText(init_config['channel_url'])
        self.keywordLW.clear()
        self.keywordLW.addItems(init_config['keyword_list'])
        if init_config['use_filtering']:
            self.k_onRB.setChecked(True)
        else:
            self.k_offRB.setChecked(True)
        self.newItemLE.clear()

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
        if self.startBtn.text() == '시작':
            channel_url = self.urlLE.text()
            if self.k_onRB.isChecked():
                keyword_list = [self.keywordLW.item(i).text() for i in range(self.keywordLW.count())]
            else:
                keyword_list = None
            self.thread = Notification(channel_url, keyword_list, parent=self)
            self.thread.error.connect(self.error)
            self.thread.done.connect(self.done)
            self.stop.connect(self.thread.stop)
            self.thread.start()
        else:
            self.stop.emit()

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
        save_config(self.get_config())
        QMessageBox.information(self, "저장", "설정이 저장 되었습니다.")

    # 설정 불러오기 버튼
    def currentConfigLoad(self):
        self.set_config(load_config())
        QMessageBox.information(self, "불러오기", "설정을 성공적으로 불러왔습니다.")

    # 설정 초기화 버튼
    def currentConfigReset(self):
        self.set_config(get_default_config())
        QMessageBox.information(self, "초기화", "현재 설정이 초기화되었습니다.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
