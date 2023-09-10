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
import requests
import time
import logging
import threading
import webbrowser
from bs4 import BeautifulSoup
try:
    import zroya
except ImportError:
    zroya = None
import re
import yaml
import smtplib
import cerberus
from email.message import EmailMessage

version = '1.8.0'

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
                'gallery_url': {'type': 'string'},
                'use_filtering': {'type': 'boolean'},
                'filtering_type': {'type': 'dict', 'schema': {'Title': {'type': 'boolean'}, 'Author': {'type': 'boolean'}}},
                'keyword_list': {'type': 'list', 'schema': {'type': 'string'}},
                'notify_type': {'type': 'dict', 'schema': {'Desktop': {'type': 'boolean'}, 'Mobile': {'type': 'boolean'}}},
                'email': {'type': 'string'},
                'passwd': {'type': 'string'}
            }
            cls.instance = cerberus.Validator(schema, require_all=True)
        return cls.instance

class get_default_config(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            default_config = dict()
            default_config['config_name'] = 'default'
            default_config['gallery_url'] = 'https://gall.dcinside.com/mgallery/board/lists?id=aoegame'
            default_config['use_filtering'] = False
            default_config['filtering_type'] = {'Title': True, 'Author': False}
            default_config['keyword_list'] = []
            default_config['notify_type'] = {'Desktop': True, 'Mobile': False}
            default_config['email'] = ''
            default_config['passwd'] = ''
            cls.instance = default_config
        return cls.instance

class get_session(object):
    @classmethod
    def create_new(cls):
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        cls.instance = session
        return cls()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.create_new()
        return cls.instance

# url로 요청을 보내는 함수
def get_html(url):
    try:
        resp = get_session().get(url, timeout=5)
    except requests.exceptions.RequestException as e:
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
                app_name="DCinsideAlarm",
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

class Notification(QThread):

    error = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, url, use_desktop, use_mobile, email, passwd, keyword_list, parent=None):
        super().__init__(parent)
        self.url = url
        self.use_desktop = use_desktop
        self.use_mobile = use_mobile
        self.email = email
        self.passwd = passwd
        self.keyword_list = keyword_list
        self.logger = get_default_logger()
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
                while self.flag:
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
        # 갤러리 주소에서 갤러리 ID를 파싱하는 정규표현식 매칭
        self.url_parser = re.match(r"^http[s]?://gall[.]dcinside[.]com(?P<gallery_type>/|/mgallery/|/mini/)board/(lists|view)/?[?](.*?)id=(?P<gallery_id>[a-zA-Z0-9_]+)($|&.*)", self.url)
        if not self.url_parser:
            # 매칭이 되지 않으면 오류 메시지 출력 및 예외 처리
            self.logger.critical('갤러리 주소가 잘못되었습니다.')
            self.error.emit('갤러리 주소가 잘못되었습니다.')
            return False

        html = get_html(self.url)
        if not isinstance(html, str):
            self.logger.critical('웹 페이지를 불러오지 못했습니다.', exc_info=html)
            self.error.emit('웹 페이지를 불러오지 못했습니다.')
            return False
        soup = BeautifulSoup(html, 'html.parser')

        # 받아온 html에서 게시글 목록 파싱
        try:
            new_post = soup.find("table", class_="gall_list").find("tbody").find_all('tr', class_='ub-content us-post')
        except AttributeError:
            self.logger.critical('웹 페이지 파싱에 실패했습니다.')
            self.error.emit('웹 페이지 파싱에 실패했습니다.')
            return False

        # 갤러리 주소에서 갤러리 ID만 추출
        self.gallery_id = self.url_parser.group('gallery_id')
        # 갤러리 주소에서 갤러리 유형 식별
        self.gallery_type = self.url_parser.group('gallery_type')

        # recent 변수에 현재 최신 글 번호를 저장
        self.recent = 0
        for n in new_post:
            gall_num = n.find('td', class_='gall_num').text.strip()
            if (not gall_num.isdecimal()):
                continue
            post_id = int(gall_num)
            if (post_id > self.recent):
                self.recent = post_id

        self.last_check = self.recent
        self.logger.info(f'최신 글 번호 추출 성공: {self.recent}')
        return True

    def new_article_action(self):
        html = get_html(self.url)
        if not isinstance(html, str):
            self.logger.error('웹 페이지를 불러오지 못했습니다.', exc_info=html)
            return False
        soup = BeautifulSoup(html, 'html.parser')

        # 게시글 목록
        try:
            # us-post 클래스로 운영자의 글을 제외한 일반 사용자 글만 파싱
            new_post = soup.find("table", class_="gall_list").find("tbody").find_all('tr', class_='ub-content us-post')
        except AttributeError:
            self.logger.error('웹 페이지 파싱에 실패했습니다.')
            return False

        # 새로 가져온 리스트의 글 번호들을 비교
        for n in reversed(new_post):
            if not self.flag:
                break
            # 글 번호 추출
            gall_num = n.find('td', class_='gall_num').text.strip()
            # 글 번호가 숫자로 이루어지지 않은 글은 스킵
            if (not gall_num.isdecimal()):
                continue
            # 추출한 글 번호를 정수형으로 저장
            post_id = int(gall_num)
            # 새로 가져온 글 번호가 더 크다면, 새로운 글 이라는 뜻
            if (post_id > self.recent):
                try:
                    title = n.find("td", class_="gall_tit").text.strip()        # 제목
                except AttributeError:
                    title = 'Unknown'
                try:
                    author = n.find("td", class_="gall_writer").text.strip()    # 작성자
                except AttributeError:
                    author = 'Unknown'

                try:
                    # 말머리가 존재하는 경우 말머리 추출
                    gall_subject = n.find('td', class_='gall_subject')
                    # 말머리가 단축되어 있는 경우 풀네임 추출
                    subject_inner = gall_subject.find('p', class_='subject_inner')
                    hd = subject_inner.text.strip() if subject_inner else gall_subject.text.strip()
                    header = f'[{hd}]'
                except AttributeError:
                    header = ''

                title_f = f'{header} {title}'.strip().replace('\n', '\t')

                if post_id > self.last_check:
                    self.last_check = post_id
                    self.logger.info(f'새글 파싱 성공: {post_id}')
                    self.logger.debug(f'new article data: {dict(title=title_f, author=author)}')

                # 키워드=off 일 경우, 바로 토스트 메시지로 표시
                if self.keyword_list is None:
                    self.logger.debug('키워드 비활성화 상태')
                    self.notification_action(title_f, author, post_id)
                    self.recent = post_id
                # 키워드=on 일 경우, 체크된 기준(제목 혹은 글쓴이)에 키워드가 포함 되어있다면 토스트 메시지로 표시
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
        full_link = f'https://gall.dcinside.com{self.gallery_type}board/view?id={self.gallery_id}&no={post_id}'
        if self.use_desktop:
            e = show_toast(title_f, author, full_link)
            if e is None:
                self.logger.info(f'윈도우 알림 생성 성공')
            else:
                self.logger.error('윈도우 알림 생성에 실패했습니다.', exc_info=e)
        if self.use_mobile:
            subject = '[DC_Alarm] new post'
            content = f'Title: {title_f}\nAuthor: {author}\n\n{full_link}'
            e = send_email(subject, content, self.email, self.passwd)
            if e is None:
                self.logger.info(f'이메일 알림 전송 성공')
            else:
                self.logger.error('이메일 알림 전송에 실패했습니다.', exc_info=e)

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
        self.urlLb = QLabel('갤러리 주소')
        self.urlLb.setAlignment(Qt.AlignTop)
        self.m_versionLb = QLabel(f'버전 : {version}')
        self.m_versionLb.setAlignment(Qt.AlignTop)

        # 시작/중지 버튼
        self.startBtn = QPushButton('시작', self)
        self.startBtn.clicked.connect(self.startNotification)
        self.startBtn.clicked.connect(self.updateKeywordGroupState)

        # 키워드 온/오프 버튼
        self.keywordLb = QLabel('키워드')
        self.keywordLW = QListWidget(self)
        self.k_onRB = QRadioButton('ON', self)
        self.k_offRB = QRadioButton('OFF', self)
        self.k_group = QButtonGroup(self)
        self.k_group.addButton(self.k_onRB)
        self.k_group.addButton(self.k_offRB)
        self.k_onRB.clicked.connect(self.updateOptionState)
        self.k_offRB.clicked.connect(self.updateOptionState)

        # 키워드 제목/글쓴이 선택 버튼
        self.isTitleLb = QLabel('기준')
        self.k_titleCB = QCheckBox('제목', self)
        self.k_authorCB = QCheckBox('글쓴이', self)

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
        grid.addWidget(self.emailLb, 2, 0)
        grid.addWidget(self.emailLE, 2, 1, 1, 4)
        grid.addWidget(self.passwdLb, 3, 0)
        grid.addWidget(self.passwdLE, 3, 1, 1, 4)
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

        self.setWindowTitle('DC 새글 알리미')
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
        current_config['gallery_url'] = self.urlLE.text()
        current_config['use_filtering'] = self.k_onRB.isChecked()
        current_config['filtering_type'] = {'Title': keyword_opt_title, 'Author': keyword_opt_author}
        current_config['keyword_list'] = [self.keywordLW.item(i).text() for i in range(self.keywordLW.count())]
        current_config['notify_type'] = {'Desktop': use_desktop, 'Mobile': use_mobile}
        current_config['email'] = self.emailLE.text()
        current_config['passwd'] = self.passwdLE.text()
        return current_config

    def set_config(self, init_config):
        self.config_name = init_config['config_name']
        self.urlLE.setText(init_config['gallery_url'])
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
            gallery_url = self.urlLE.text()
            use_desktop = self.nt_desktopRB.isChecked() or self.nt_bothRB.isChecked()
            use_mobile = self.nt_mobileRB.isChecked() or self.nt_bothRB.isChecked()
            email, passwd = self.emailLE.text(), self.passwdLE.text()
            if self.k_onRB.isChecked():
                keyword_list = [self.keywordLW.item(i).text() for i in range(self.keywordLW.count())]
            else:
                keyword_list = None
            self.thread = Notification(gallery_url, use_desktop, use_mobile, email, passwd, keyword_list, parent=self)
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
