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
from PyQt5.QtCore import *
import requests
import time
import threading
import webbrowser
import logging
import yaml
import cerberus
from bs4 import BeautifulSoup
try:
    import zroya
except ImportError:
    zroya = None
import tkinter
from tkinter import filedialog

user_agent = {'User-agent': 'Mozilla/5.0'}
flag = True
recent = 1
version = '1.6.0'

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
        print(e)
        #get_default_logger().warning('WinToast 초기화에 실패했습니다.', exc_info=e)

def show_toast(title, body, link):
    try:
        if zroya:
            template = zroya.Template(zroya.TemplateType.ImageAndText3)
            if os.path.exists(resource_path("image.ico")):
                template.setImage(resource_path("image.ico"))
            template.setFirstLine(title)
            template.setSecondLine(body)
            # 클릭 시, 웹 브라우저로 연결해주는 함수
            def onClickHandler(notification_id):
                full_link = "https://gall.dcinside.com" + link
                webbrowser.open_new(full_link)
            zroya.show(template, on_click=onClickHandler)
    except SystemError as e:
        return e
    else:
        return None

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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

def load_config():
    if os.path.exists('config.yaml'):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as yaml_file:
                yaml_data = list(yaml.safe_load_all(yaml_file))
        except yaml.YAMLError as e:
            #get_default_logger().warning('yaml 파일을 불러오지 못했습니다.', exc_info=e)
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
                    print("검증에 실패한 config를 제외했습니다.")
                    #get_default_logger().warning('검증에 실패한 config를 제외했습니다.', exc_info=ValueError(f'Invalid Config: {yaml_data[i]}'))
            if len(config_data) == 0 or config_data[0]['config_name'] != 'default':
                config_data.insert(0, get_default_config())
            return config_data
    else:
        return [get_default_config()]

def save_config(config_data):
    with open('config.yaml', 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump_all(config_data, yaml_file, indent=2, sort_keys=False, default_flow_style=False, allow_unicode=True)

class get_validator(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            schema = {
                'config_name': {'type': 'string'},
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
            default_config['config_name'] = 'default'
            default_config['channel_url'] = 'https://gall.dcinside.com/mgallery/board/lists?id=aoegame'
            default_config['use_filtering'] = False
            default_config['keyword_list'] = []
            cls.instance = default_config
        return cls.instance

class MyApp(QWidget):

  def __init__(self):
      super().__init__()
      self.initUI()
      self._thread = None
      self._lock = threading.Lock()

  def set_config(self, init_config):
      self.config_name = init_config['config_name']
      self.addr.setText(init_config['channel_url'])
      self.keyword.clear()
      self.keyword.addItems(init_config['keyword_list'])
      if init_config['use_filtering']:
          self.k_on.setChecked(True)
      else:
          self.k_off.setChecked(True)
      self.newItem.clear()

  def get_config(self):
      current_config = dict()
      current_config['config_name'] = self.config_name
      current_config['channel_url'] = self.addr.text()
      current_config['use_filtering'] = self.k_on.isChecked()
      current_config['keyword_list'] = [self.keyword.item(i).text() for i in range(self.keyword.count())]
      return current_config

  # UI 설정
  def initUI(self):
      config_data = load_config()
      save_config(config_data)

      grid = QGridLayout()
      self.setLayout(grid)

      self.addr = QLineEdit("", self)
      self.addr.setText("https://gall.dcinside.com/mgallery/board/lists?id=aoegame")

      self.urlLb = QLabel('갤러리 주소')
      self.version = QLabel(f'버전 : {version}')
      self.urlLb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

      # 시작/중지 버튼
      self.startBtn = QPushButton('시작', self)
      self.startBtn.clicked.connect(self.startBtnFunction)
      self.stopBtn = QPushButton('중지', self)
      self.stopBtn.clicked.connect(self.stopBtnFunction)
      self.stopBtn.setEnabled(False)

      self.keywordLb = QLabel('키워드')

      self.keyword = QListWidget()
      self.keyword.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

      # 키워드 온/오프 버튼
      self.k_on = QRadioButton('ON', self)
      self.k_off = QRadioButton('OFF', self)
      self.k_off.setChecked(True)

      # 추가할 키워드 적는 칸
      self.newItem = QLineEdit()

      # 키워드 추가/삭제 버튼
      self.k_appendBtn = QPushButton('추가', self)
      self.k_appendBtn.clicked.connect(self.appendBtnFunction)
      self.k_removeBtn = QPushButton('삭제', self)
      self.k_removeBtn.clicked.connect(self.removeBtnFunction)

      # 설정 저장/불러오기 버튼
      self.saveCrntBtn = QPushButton('저장', self)
      self.saveCrntBtn.clicked.connect(self.saveCrntBtnFunction)
      self.resetBtn = QPushButton('초기화', self)
      self.resetBtn.clicked.connect(self.resetBtnFunction)

      # 위에서 선언한 위젯들의 위치를 지정
      grid.addWidget(self.urlLb, 0, 0)
      grid.addWidget(self.version, 0, 4)
      grid.addWidget(self.addr, 1, 0, 1, 5)
      grid.addWidget(self.startBtn, 2, 0, 1, 4)
      grid.addWidget(self.stopBtn, 2, 4)
      grid.addWidget(self.keywordLb, 3, 0)
      grid.addWidget(self.k_on, 3, 1)
      grid.addWidget(self.k_off, 3, 2)
      grid.addWidget(self.newItem, 3, 3)
      grid.addWidget(self.keyword, 4, 0, -1, 4)
      grid.addWidget(self.k_appendBtn, 4, 4)
      grid.addWidget(self.k_removeBtn, 5, 4)
      grid.addWidget(self.saveCrntBtn, 6, 4)
      grid.addWidget(self.resetBtn, 7, 4)

      #grid.setColumnStretch(0, 1)
      #grid.setRowStretch(1, 1)

      self.setWindowTitle('DC 새글 알리미')
      self.setWindowIcon(QIcon('icon.png'))
      #self.setFixedSize(380, 200)
      self.show()
      self.set_config(config_data[0])

  def center(self):
      qr = self.frameGeometry()
      cp = QDesktopWidget().availableGeometry().center()
      qr.moveCenter(cp)
      self.move(qr.topLeft())

  # 시작 버튼
  def startBtnFunction(self):
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
      self.startBtn.setEnabled(False)
      self.stopBtn.setEnabled(True)
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
                      if self.k_off.isChecked():
                          show_toast(title, name, link)
                          skip = True
                      # 키워드=on 일 경우, 제목에 키워드가 포함 되어있다면 토스트 메시지로 표시
                      if self.k_on.isChecked():
                          for key in range(self.keyword.count()):
                              if self.keyword.item(key).text() in title:
                                  show_toast(title, name, link)
                                  skip = True
                                  break
                  n_idx = n_idx + 1
              if flag == False:
                  break

      # 스레드가 없거나 종료되어 있을 때만 새로운 스레드 생성 및 실행
      if self._thread == None or not self._thread.is_alive():
          self._thread = threading.Thread(target=run, daemon=True)
          self._thread.start()

  # 중지 버튼
  def stopBtnFunction(self):
      global flag
      flag = False
      self.startBtn.setEnabled(True)
      self.stopBtn.setEnabled(False)
      QMessageBox.about(self, "중지", "알림이 중지 되었습니다.")

  # 키워드 추가 버튼
  def appendBtnFunction(self):
      if self.newItem.text() != '':
          self.keyword.addItem(self.newItem.text())

  # 키워드 삭제 버튼
  def removeBtnFunction(self):
      select = self.keyword.currentRow()
      self.keyword.takeItem(select)

  # 설정 저장 버튼
  def saveCrntBtnFunction(self):
      self.config_name = 'default'
      current_config = self.get_config()
      config_data = load_config()
      config_data[0] = current_config
      save_config(config_data)
      QMessageBox.information(self, "저장", "설정이 저장 되었습니다.")

  # 설정 초기화 버튼
  def resetBtnFunction(self):
      answer = QMessageBox.question(self, "초기화", "현재 설정을 초기화하시겠습니까?")
      if answer == QMessageBox.Yes:
          default_config = get_default_config()
          default_config['config_name'] = self.config_name
          self.set_config(default_config)
          QMessageBox.information(self, "초기화", "현재 설정이 초기화되었습니다.")

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MyApp()
  sys.exit(app.exec_())
