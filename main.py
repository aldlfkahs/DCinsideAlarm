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
      https://wikidocs.net/26
      https://pythonblog.co.kr/coding/11/
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
from win10toast_click import ToastNotifier
import tkinter
from tkinter import filedialog

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
      self._thread = None
      self._lock = threading.Lock()

  # UI 설정
  def initUI(self):
      grid = QGridLayout()
      self.setLayout(grid)

      self.addr = QLineEdit("", self)
      self.addr.setText("https://gall.dcinside.com/mgallery/board/lists?id=aoegame")

      text1 = QLabel('갤러리 주소')
      togomi = QLabel('버전 : 1.5.2')

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

      # 말머리 리스트 가져오기
      subject_list = []
      try:
          center_box = soup.find('div', attrs={'class': 'center_box'})
          for t in center_box.select('li'):
              subject_list.append(t.text)
      except AttributeError:
          print("말머리 없음")
      # 받아온 html에서 글 번호만 파싱
      try:
          init_check = soup.find("tbody").find_all("tr", class_="ub-content us-post")
      except AttributeError:
          QMessageBox.about(self, "오류", "갤러리 주소가 잘못되었습니다.")
          return
      # recent 변수에 현재 최신 글 번호를 저장
      global recent
      self._lock.acquire()
      recent = 1
      for idx in init_check:
          init_num = idx.select_one('td.gall_num').text
          if (not init_num.isdecimal()):
              continue
          if (recent < int(init_num)):
              recent = int(init_num)
      self._lock.release()
      QMessageBox.about(self, "실행", "알림이 시작 되었습니다.")

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

              new_subject = new_post.find_all("td", class_="gall_subject")
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
                  # 마이너 갤러리(말머리가 존재하는 갤러리)인데, 말머리에 포함되지 않는 글이라면,
                  # 디씨에서 자체적으로 올린 '설문'등의 글이라고 판단하여 스킵
                  if len(subject_list) != 0:
                      if (new_subject[size-n_idx-1].text not in subject_list):
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
                          toaster.show_toast(title, name, icon_path="image.ico", duration=3, callback_on_click=action)
                          skip = True
                      # 키워드=on 일 경우, 제목에 키워드가 포함 되어있다면 토스트 메시지로 표시
                      if k_on.isChecked():
                          for key in range(keyword.count()):
                              if keyword.item(key).text() in title:
                                  toaster.show_toast(title, name, icon_path="image.ico", duration=3, callback_on_click=action)
                                  skip = True
                                  break
                  n_idx = n_idx + 1
              if flag == False:
                  break

      # 스레드가 없거나 종료되어 있을 때만 새로운 스레드 생성 및 실행
      if self._thread == None or not self._thread.is_alive():
          self._thread = threading.Thread(target=run, daemon=True)
          self._thread.start()

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
          f.write("[갤러리 주소]\n")
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
          data = open(file_path, 'r', encoding='utf-8')
          isURL = data.readline().rstrip('\n')
          # 갤러리 주소 불러오기
          if isURL != "[갤러리 주소]":
              # 첫 줄이 [갤러리 주소]가 아니라면, 잘못된 파일을 읽은 것으로 판단
              return
          else:
              self.addr.setText(data.readline().rstrip('\n'))

          # 키워드 불러오기
          isKeyword = data.readline().rstrip('\n')
          if isKeyword != "[키워드]":
              # [키워드]가 아니라면, 잘못된 파일을 읽은 것으로 판단
              return
          else:
              lines = data.readlines()
              keyword.clear() # 불러오기 전, 이전에 있던 키워드 삭제
              for line in lines:
                  keyword.addItem(line.rstrip('\n'))

          data.close()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MyApp()
  sys.exit(app.exec_())
