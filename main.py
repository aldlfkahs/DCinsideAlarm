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
from PyQt5.QtGui import QIcon
import requests
import time
import threading
import webbrowser
from bs4 import BeautifulSoup
import zroya
import tkinter
from tkinter import filedialog
import re

version = '1.5.1'
status = zroya.init(
    app_name="ArcaliveAlarm",
    company_name="python",
    product_name="python",
    sub_product="python",
    version=f"v{version}"
)
user_agent = {'User-agent': 'Mozilla/5.0'}

# url로 get 요청을 보내는 함수
def get_html(url):
    _html = ""
    suc = False
    while(suc == False):
        try:
            resp = requests.get(url,headers=user_agent)
        except requests.exceptions.RequestException as e:
            time.sleep(3)
            continue

        if resp.status_code == 200:
            suc = True
            _html = resp.text
        else:
            suc = True
            _html = "<tbody><td>잘못된 주소 입니다.</td></tbody>"
    return _html

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def show_notify(title, body, link):
    template = zroya.Template(zroya.TemplateType.ImageAndText3)
    if os.path.exists(resource_path("arca_image.ico")):
        template.setImage(resource_path("arca_image.ico"))
    template.setFirstLine(title)
    template.setSecondLine(body)
    def onClickHandler(notification_id):
        webbrowser.open_new(link)
    zroya.show(template, on_click=onClickHandler)

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self._thread = None
        self._lock = threading.Lock()

    # UI 설정
    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        self.addr = QLineEdit("", self)
        self.addr.setText("https://arca.live/b/singbung")

        text1 = QLabel('채널 주소')
        togomi = QLabel(f'버전 : {version}')

        # 시작/중지 버튼
        btn1 = QPushButton('시작', self)
        btn1.clicked.connect(self.button1Function)
        btn2 = QPushButton('중지', self)
        btn2.clicked.connect(self.button2Function)

        text2 = QLabel('키워드')

        global keyword
        keyword = QListWidget()

        # 키워드 온/오프 버튼
        global k_on, k_off
        k_on = QRadioButton('ON', self)
        k_off = QRadioButton('OFF', self)
        k_off.setChecked(True)

        # 추가할 키워드 적는 칸
        global newItem
        newItem = QLineEdit()

        # 키워드 추가/삭제 버튼
        btn3 = QPushButton('추가', self)
        btn3.clicked.connect(self.button3Function)
        btn4 = QPushButton('삭제', self)
        btn4.clicked.connect(self.button4Function)

        # 키워드 저장/불러오기 버튼
        btn5 = QPushButton('저장', self)
        btn5.clicked.connect(self.button5Function)
        btn6 = QPushButton('불러오기', self)
        btn6.clicked.connect(self.button6Function)

        # 위에서 선언한 위젯들의 위치를 지정
        grid.addWidget(text1, 0, 0)
        grid.addWidget(togomi, 0, 4)
        grid.addWidget(self.addr, 1, 0, 1, 5)
        grid.addWidget(btn1, 2, 0, 1, 4)
        grid.addWidget(btn2, 2, 4)
        grid.addWidget(text2, 3, 0)
        grid.addWidget(k_on, 3, 1)
        grid.addWidget(k_off, 3, 2)
        grid.addWidget(newItem, 3, 3)
        grid.addWidget(keyword, 4, 0, -1, 4)
        grid.addWidget(btn3, 4, 4)
        grid.addWidget(btn4, 5, 4)
        grid.addWidget(btn5, 6, 4)
        grid.addWidget(btn6, 7, 4)

        self.setWindowTitle('아카라이브 새글 알리미')
        self.setWindowIcon(QIcon(resource_path('icon.png')))
        #self.setFixedSize(380, 200)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 시작 버튼
    def button1Function(self):
        global channel_id
        global recent
        global flag
        global url

        flag = True
        addr_text = self.addr.text().lower()

        # 채널 주소에서 채널 ID를 파싱하는 정규표현식 매칭
        m_channel_id = re.match(r"^http[s]?://arca[.]live/b/(?P<channel_id>[a-z\d]+)/?($|[?].*)", addr_text)
        if not m_channel_id:
            # 매칭이 되지 않으면 오류 메시지 출력 및 예외 처리
            QMessageBox.about(self, "오류", "채널 주소가 잘못되었습니다.")
            return

        html = get_html(addr_text)
        soup = BeautifulSoup(html, 'html.parser')

        # 받아온 html에서 게시글 주소만 파싱
        try:
            l = soup.find("div", class_="list-table").find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['vrow'])
        except AttributeError:
            QMessageBox.about(self, "오류", "채널 주소가 잘못되었습니다.")
            return

        self._lock.acquire()
        # 체널 주소에서 채널 ID만 추출
        channel_id = m_channel_id.group('channel_id')
        # 게시글 주소에서 글 번호만 추출하는 정규표현식 정의
        p_post_id = re.compile(channel_id + r"/(?P<post_id>[\d]+)[?]?")

        # recent 변수에 현재 최신 글 번호를 저장
        recent = 0
        for n in l:
            post_link = n.attrs['href']
            # 게시글 주소에서 정규표현식 매칭
            s_post_id = p_post_id.search(post_link)
            if s_post_id:
                # 매칭이 되면 글 번호만 추출
                recent = int(s_post_id.group('post_id'))
                break

        url = addr_text
        self._lock.release()
        QMessageBox.about(self, "실행", "알림이 시작 되었습니다.\n이 창을 닫으셔도 좋습니다.")

        # 알리미 수행 도중에도 중지 버튼을 누를 수 있게 쓰레드로 구현
        def run():
            global channel_id
            global recent
            global flag
            global url
            # 중지버튼으로 flag가 false가 되기 전까지 계속 수행
            while flag == True:
                # 1초 간격으로 get_html() 호출
                time.sleep(1)
                self._lock.acquire()

                html = get_html(url)
                soup = BeautifulSoup(html, 'html.parser')
                new_post = soup.find("div", class_="list-table")

                # 게시글 주소 (정확히 vrow라는 이름의 class만 가져오기 위해 lambda로 구현)
                new_link = new_post.find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['vrow'])

                # 새로 가져온 리스트의 글 번호들을 비교
                for n in reversed(new_link):
                    if flag == False:
                        break
                    post_link = n.attrs['href']
                    # 게시글 주소에서 정규표현식 매칭
                    s_post_id = p_post_id.search(post_link)
                    if not s_post_id:
                        continue
                    # 매칭이 되면 글 번호만 추출하여 정수형으로 저장
                    post_id = int(s_post_id.group('post_id'))
                    # 새로 가져온 글 번호가 더 크다면, 새로운 글 이라는 뜻
                    if (post_id > recent):
                        try:
                            title = n.find("span", class_="title").text.strip()             # 제목
                        except AttributeError:
                            title = 'Unknown'
                        try:
                            author = n.find("span", class_="vcol col-author").text.strip()  # 작성자
                        except AttributeError:
                            author = 'Unknown'

                        header = n.find_all("span", class_="badge badge-success")           # 글머리
                        header = [hd.text.strip() for hd in header]

                        header_f = ' '.join([f'[{hd}]' for hd in header if hd != ''])
                        title_f = f'{header_f} {title}'.strip()

                        full_link = f'https://arca.live/b/{channel_id}/{post_id}'
                        # 키워드=off 일 경우, 바로 토스트 메시지로 표시
                        if k_off.isChecked():
                            show_notify(title_f, author, full_link)
                            recent = post_id
                        # 키워드=on 일 경우, 제목에 키워드가 포함 되어있다면 토스트 메시지로 표시
                        if k_on.isChecked():
                            for key in range(keyword.count()):
                                if keyword.item(key).text() in title_f:
                                    show_notify(title_f, author, full_link)
                                    recent = post_id
                                    break
                self._lock.release()
                if flag == False:
                    break

        # 스레드가 없거나 종료되어 있을 때만 새로운 스레드 생성 및 실행
        if self._thread == None or not self._thread.is_alive():
            self._thread = threading.Thread(target=run, daemon=True)
            self._thread.start()

    # 중지 버튼
    def button2Function(self):
        global flag
        flag = False
        QMessageBox.about(self, "중지", "알림이 중지 되었습니다.")

    # 키워드 추가 버튼
    def button3Function(self):
        if newItem.text() != '':
            keyword.addItem(newItem.text())

    # 키워드 삭제 버튼
    def button4Function(self):
        select = keyword.currentRow()
        keyword.takeItem(select)

    # 키워드 저장 버튼
    def button5Function(self):
        root = tkinter.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(parent=root, title="키워드 저장", filetypes=(("text files", "*.txt"),("all files", "*.*")), defaultextension="txt")
        if file_path == "":
            # 저장이 안 됐을 시, 예외 처리
            return
        else:
            # 키워드를 파일로 저장
            f = open(file_path, 'w', encoding='utf-8')
            f.write("[채널 주소]\n")
            f.write(self.addr.text() + "\n")
            f.write("[키워드]\n")
            for key in range(keyword.count()):
                f.write(keyword.item(key).text() + "\n")
            f.close()

    # 키워드 불러오기 버튼
    def button6Function(self):
        root = tkinter.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(parent=root, title="키워드 불러오기", filetypes=(("text files", "*.txt"),("all files", "*.*")), defaultextension="txt")
        if file_path == "":
            # 아무것도 안 불러왔을 시, 예외 처리
            return
        else:
            f = open(file_path, 'r', encoding='utf-8')
            isURL = f.readline().rstrip('\n')
            # 채널 주소 불러오기
            if isURL != "[채널 주소]":
                # 첫 줄이 [채널 주소]가 아니라면, 잘못된 파일을 읽은 것으로 판단
                return
            else:
                self.addr.setText(f.readline().rstrip('\n'))

            # 키워드 불러오기
            isKeyword = f.readline().rstrip('\n')
            if isKeyword != "[키워드]":
                # [키워드]가 아니라면, 잘못된 파일을 읽은 것으로 판단
                return
            else:
                lines = f.readlines()
                keyword.clear() # 불러오기 전, 이전에 있던 키워드 삭제
                for line in lines:
                    keyword.addItem(line.rstrip('\n'))

            f.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
