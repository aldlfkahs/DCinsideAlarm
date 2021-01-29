'''
제작자 이메일 : aldlfkahs95@naver.com
참조 : https://github.com/jithurjacob/Windows-10-Toast-Notifications
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
'''
'''
사용 전 필수 설정사항

시작 -> 설정 -> 시스템 -> 알림 및 작업 
-> 앱 및 다른 보낸사람의 알림 받기 -> 켬
'''
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import requests
import time
import threading
import webbrowser
from bs4 import BeautifulSoup
from win10toast import ToastNotifier

toaster = ToastNotifier()
user_agent = {'User-agent': 'Mozilla/5.0'}
flag = True
recent = 1

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

class MyApp(QWidget):

  def __init__(self):
      super().__init__()
      self.initUI()

  def initUI(self):
      grid = QGridLayout()
      self.setLayout(grid)

      self.addr = QLineEdit("", self)
      self.addr.setText("https://gall.dcinside.com/mgallery/board/lists?id=aoegame")

      text1 = QLabel('갤러리 주소')
      togomi = QLabel('버전 : 1.3.2')

      btn1 = QPushButton('시작', self)
      btn1.clicked.connect(self.button1Function)
      btn2 = QPushButton('중지', self)
      btn2.clicked.connect(self.button2Function)

      text2 = QLabel('키워드')

      global keyword
      keyword = QListWidget()

      global k_on, k_off
      k_on = QRadioButton('ON', self)
      k_off = QRadioButton('OFF', self)
      k_off.setChecked(True)

      global newItem
      newItem = QLineEdit()

      btn3 = QPushButton('추가', self)
      btn3.clicked.connect(self.button3Function)
      btn4 = QPushButton('삭제', self)
      btn4.clicked.connect(self.button4Function)


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

      self.setWindowTitle('DC 새글 알리미')
      self.setWindowIcon(QIcon('icon.png'))
      #self.setFixedSize(380, 200)
      self.show()

  def center(self):
      qr = self.frameGeometry()
      cp = QDesktopWidget().availableGeometry().center()
      qr.moveCenter(cp)
      self.move(qr.topLeft())

  # 시작 버튼
  def button1Function(self):
      global flag
      flag = True

      html = get_html(self.addr.text())
      soup = BeautifulSoup(html, 'html.parser')

      # 받아온 html에서 글 번호만 파싱
      l = soup.find("tbody").find_all("td", class_="gall_num")

      # recent 변수에 현재 최신 글 번호를 저장
      global recent
      recent = 1

      for idx in l:
          if (not idx.text.isdecimal()):
              continue
          if (recent < int(idx.text)):
              recent = int(idx.text)

      QMessageBox.about(self, "실행", "알림이 시작 되었습니다.\n이 창을 닫으셔도 좋습니다.")

      # 알리미 수행 도중에도 중지 버튼을 누를 수 있게 쓰레드로 구현
      def run():
          global recent
          global link
          skip = False
          # 중지버튼으로 flag가 false가 되기 전까지 계속 수행
          while flag == True:
              # 3초 간격으로 get_html() 호출
              if not skip :
                  time.sleep(3)
              else:
                  skip = False

              html = get_html(self.addr.text())
              sp = BeautifulSoup(html, 'html.parser')
              new_post = sp.find("tbody")

              new_title = new_post.find_all("td", class_="gall_tit ub-word")
              new_name = new_post.find_all("td", class_="gall_writer ub-writer")
              new_num = new_post.find_all("td", class_="gall_num")

              # 새로 가져온 리스트의 글 번호들을 비교
              n_idx = 0
              size = len(new_num)
              for n in reversed(new_num):
                  if flag == False:
                      break
                  if (not n.text.isdecimal()):
                      n_idx = n_idx + 1
                      continue
                  # 새로 가져온 글 번호가 더 크다면, 새로운 글 이라는 뜻
                  if (int(n.text) > recent):
                      recent = int(n.text)
                      name = new_name[size-n_idx-1].text
                      title = new_title[size-n_idx-1].text
                      link = new_title[size-n_idx-1].a.attrs['href']
                      # 키워드=off 일 경우, 바로 토스트 메시지로 표시
                      if k_off.isChecked():
                          toaster.show_toast(title, name, icon_path="dc_image.ico", duration=3, callback_on_click=action)
                          skip = True
                      # 키워드=on 일 경우, 제목에 키워드가 포함 되어있다면 토스트 메시지로 표시
                      if k_on.isChecked():
                          for key in range(keyword.count()):
                              if keyword.item(key).text() in title:
                                  toaster.show_toast(title, name, icon_path="dc_image.ico", duration=3, callback_on_click=action)
                                  skip = True
                                  break
                  n_idx = n_idx + 1
              if flag == False:
                  break

      thread = threading.Thread(target=run)
      thread.start()

      # 클릭 시, 웹 브라우저로 연결해주는 함수
      def action():
          full_link = "https://gall.dcinside.com" + link
          webbrowser.open_new(full_link)

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

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MyApp()
  sys.exit(app.exec_())
