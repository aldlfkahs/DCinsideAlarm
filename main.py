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
from bs4 import BeautifulSoup
from win10toast_for_pip_bigger_10 import ToastNotifier

toaster = ToastNotifier()
user_agent = {'User-agent': 'Mozilla/5.0'}
flag = True
recent = 1

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


      btn1 = QPushButton('시작', self)
      btn1.resize(50, 50)
      btn1.clicked.connect(self.button1Function)

      btn2 = QPushButton('중지', self)
      btn2.resize(50, 50)
      btn2.clicked.connect(self.button2Function)

      grid.addWidget(self.addr, 0, 0, 1, 2)
      grid.addWidget(btn1, 1, 0)
      grid.addWidget(btn2, 1, 1)

      self.setWindowTitle('DC 새글 알리미')
      self.setWindowIcon(QIcon('icon.png'))
      self.setFixedSize(380, 100)
      self.center()
      self.show()

  def center(self):
      qr = self.frameGeometry()
      cp = QDesktopWidget().availableGeometry().center()
      qr.moveCenter(cp)
      self.move(qr.topLeft())

  # btn_1이 눌리면 작동할 함수
  def button1Function(self):
      global flag
      flag = True
      #print("switch on")

      html = get_html(self.addr.text())
      soup = BeautifulSoup(html, 'html.parser')

      l = soup.find("tbody").find_all("td", class_="gall_num")

      global recent
      recent = 1


      for idx in l:
          if (idx.text == "AD" or idx.text == "이슈" or idx.text == "뉴스" or idx.text == "공지"):
              continue
          if (recent < int(idx.text)):
              recent = int(idx.text)


      QMessageBox.about(self, "실행", "알림이 시작 되었습니다.\n이 창을 닫으셔도 좋습니다.")

      def run():
          global recent
          while flag == True:
              time.sleep(5)
              html = get_html(self.addr.text())
              sp = BeautifulSoup(html, 'html.parser')
              new_post = sp.find("tbody")

              new_title = new_post.find_all("td", class_="gall_tit ub-word")
              new_name = new_post.find_all("td", class_="gall_writer ub-writer")
              new_num = new_post.find_all("td", class_="gall_num")

              n_idx = 0

              for n in new_num:
                  if (n.text == "AD" or n.text == "이슈" or n.text == "뉴스" or n.text == "공지"):
                      n_idx = n_idx + 1
                      continue
                  if (int(n.text) > recent):
                      recent = int(n.text)

                      name = new_name[n_idx].text
                      title = new_title[n_idx].text
                      toaster.show_toast(title,
                                         name,
                                         icon_path="dc_image.ico",
                                         duration=5)
                  n_idx = n_idx + 1
              if flag == False:
                  break

      thread = threading.Thread(target=run)
      thread.start()





      # btn_2가 눌리면 작동할 함수
  def button2Function(self):
      #print("switch off")
      global flag
      flag = False
      QMessageBox.about(self, "중지", "알림이 중지 되었습니다.")


if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MyApp()
  sys.exit(app.exec_())
