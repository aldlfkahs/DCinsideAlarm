# 아카라이브 새글 알리미
* 아카라이브 새글 알리미는 [__DC 새글 알리미__](https://github.com/aldlfkahs/DCinsideAlarm)를 기반으로 만들어졌습니다.

<img src="./img/1.png" alt="프로그램 창"></img><br/>
<img src="./img/2.png" alt="알림 예시"></img><br/>

아카라이브 특정 채널에 새로운 글이 올라오면 윈도우10 팝업 메시지로 알려주는 프로그램입니다.  
새 글 알림을 받고 싶은 채널의 메인 페이지 주소를 적은 뒤, 시작 버튼을 누르면 됩니다.  
__반드시 사용 전 설정사항과 주의사항을 읽으신 뒤에 사용해주세요!__  

[__다운로드__](https://drive.google.com/file/d/12KvWQxH9sYQ7Wpg6v8TmSr67ZNVq9MkQ/view?usp=sharing)  
(비밀번호 : 11037)  


### 사용법
1. 알림을 받고 싶은 채널의 메인 페이지 주소를 '채널 주소'칸에 적습니다.  
2. 시작 버튼을 누르면 알림이 시작 됩니다.  
3. 알림 메시지 클릭시 해당 글이 브라우저로 열립니다.  
##### 키워드 알리미 사용법
1. 키워드 옆에 ON 버튼을 클릭하여 키워드 기능을 활성화 합니다.  
2. ON/OFF 옆에 있는 텍스트 창에 추가하고 싶은 키워드를 적고, 추가 버튼을 누릅니다.  
3. 카테고리 별로 알림을 받고 싶은 경우 각 카테고리에 해당하는 글머리를 "[글머리]" 형식으로 키워드에 추가합니다.  
4. 삭제하고 싶은 키워드를 클릭 후, 삭제 버튼으로 삭제할 수 있습니다.  
##### 키워드 저장/불러오기 사용법
1. 저장 버튼을 누르면 현재 쓰여있는 채널 주소, 키워드를 저장할 수 있습니다. 해당 정보는 프로그램과 같은 경로에 config.yaml로 저장됩니다.
2. 프로그램 재시작 시, config.yaml 정보를 기반으로 자동으로 불러오기가 됩니다.
##### 모바일 알리미 사용법
1. 기타 설정버튼을 누릅니다.
2. 알림을 받고 싶은 이메일과 비밀번호를 적습니다.
3. 해당 정보를 저장/불러오기 하고싶다면 하단에 default를 클릭하고(혹은 새로운 이름을 적고) 저장/불러오기를 눌러주세요.
* 이메일/비밀번호 정보는 사용자 로컬 컴퓨터에만 저장되니 걱정하지 마세요!
##### 이메일 설정법
* 이메일 연동을 위해 사용하고자 하는 이메일 서비스에서 해당 계정의 IMAP/SMTP 설정을 활성화 해주셔야 합니다.  
* 해당 계정이 2단계 인증을 사용중인 경우 추가적으로 앱 비밀번호를 생성하여 알리미에 앱 비밀번호를 기입하여 사용하시면 됩니다.  
  * __단, 구글의 Gmail 같은 경우 2단계 인증 미사용시 계정 보안 설정에서 보안 수준이 낮은 앱의 액세스를 허용으로 바꿔줘야 되는데 이 방법은 보안상 권장하지 않으니 Gmail 사용자의 경우 계정 2단계 인증 후 앱 비밀번호를 설정하여 사용하시기 바랍니다.__  
* 대부분의 이메일 서비스는 연동이 가능하며 대표적으로 구글, 네이버, 다음의 고객센터 문서 기준 설정법은 각각 다음과 같습니다.  
  * 구글 앱 비밀번호 및 IMAP 설정: https://support.google.com/a/answer/9003945  
  * 네이버 IMAP 설정: https://help.naver.com/service/5632/contents/18534  
  * 네이버 앱 비밀번호 설정: https://help.naver.com/service/5640/contents/8584  
  * 다음 IMAP 설정: https://cs.daum.net/faq/43/9234.html?faqId=24099  
  * 다음 앱 비밀번호 설정: https://cs.daum.net/faq/43/9234.html?faqId=33671  
### 주의사항
* 채널 주소는 https:// 를 포함한 전체 주소를 써주세요.
* 현재 아카라이브에서 비정상적인 요청을 막기위해 cloudflare를 사용하고있습니다. 이 프로그램은 cloudfare를 우회하도록 구현되어있으며, __프로그램 사용으로인한 아카라이브 차단 등은 본인 책임입니다.__
다만, 현재 구현방식은 서버에 무리가 가지 않는 방식으로 구현되어있으므로 크게 걱정하지 않으셔도됩니다! (운영자피셜) (https://arca.live/b/request/59304597 참고)

### ★사용 전 설정사항★

__필수 설정 사항__  
시작->설정->시스템->알림 및 작업  
앱 및 다른 보낸사람의 알림 받기 -> 켬  
<img src="./img/4.png" width="800px" height="700px" alt="알림 켜기"></img><br/>

__전체 화면에서도 알림을 받고 싶다면?__  
시작->설정->시스템->집중 지원  
모든 설정 해제 및 끔으로 변경  
<img src="./img/5.png" width="700px" height="600px" alt="전체화면 알림 켜기"></img><br/>

__알림 소리를 끄고 싶다면?__  
알림 및 작업->알림이 소리를 재생하도록 허용 체크 해제  
<img src="./img/3.png" alt="소리 끄기"></img><br/>


### 배포 버전

1.4.0버전  
-DC새글알리미의 1.4.0버전을 기준으로 수정되었습니다.  

1.4.1버전  
-아이콘이 표시되도록 수정했습니다.  

1.4.2버전  
-32비트 윈도우10 버전과 64비트 윈도우10 버전이 분리되었습니다.  
-아이콘 파일이 같은 폴더에 있어야 아이콘이 제대로 보이는 문제점이 수정되었습니다.  
-중지 버튼을 누르지 않고 프로그램 종료시 스레드가 백그라운드에서 계속 돌아가는 버그가 수정되었습니다.  

1.4.3버전  
-과거 게시글이 삭제되는 경우 최신글을 제대로 받아오지 못하는 버그가 수정되었습니다.  

1.4.4버전  
-시작 버튼을 누를 때 마다 스레드가 새로 생기는 버그가 수정되었습니다.  
-게시글이 짧은 시간에 여러개 생성되는 경우 새로운 메시지로 연속해서 표시되게 변경되었습니다.  
-그 외 약간의 사용성이 개선되었습니다.  

1.4.5버전  
-게시글이 짧은 시간에 여러개 생성되는 경우 순차적으로 표시되게 변경되었습니다.  
-게시글 제목을 불러올 때 글머리 부분이 대괄호로 감싸지게 변경되었습니다. ex) "글머리 제목" -> "[글머리] 제목"  

1.4.6버전  
-키워드 저장 및 불러오기 기능이 유니코드 문자를 지원하지 않는 버그가 수정되었습니다.  

1.5.0버전  
-일부 채널에서 채널 주소를 정상적으로 불러오지 못하는 버그가 수정되었습니다.  
-권한없음 게시글이 있거나 종합채널일 때 글머리를 정상적으로 불러오지 못하는 버그가 수정되었습니다.  

1.5.1버전  
-키워드를 매칭할 때 글머리에 대괄호가 적용되지 않은 버그가 수정되었습니다.  
-알림이 윈도우10 알림 센터에 남아있도록 수정되었습니다.  

1.6.0버전  
-변경된 아카라이브 게시판 구조에 맞게 업데이트 했습니다.  

1.7.0버전  
-아카라이브에서 비정상적인 요청을 막기위해 사용하는 cloudflare를 우회하도록 변경했습니다. 이 프로그램 사용으로인한 아카라이브 차단 등은 본인 책임입니다.  

1.7.1버전  
-윈도우 32비트 버전과 64비트 버전 공용으로 통합되었습니다.  
-간혈적으로 알림 작동이 멈추거나 응답 없음 현상이 발생하는 버그가 수정되었습니다.  

1.7.2버전  
-코드가 리펙토링되었습니다.  
-키워드 저장 및 불러오기 기능이 설정 저장 및 불러오기 기능으로 확장되었습니다.  
-설정은 config.yaml 파일로 저장되며 프로그램 실행시 자동으로 불러와집니다.  
-로그 정보가 Notification.log 파일에 기록되도록 변경되었습니다.  
-웹소켓을 통한 새글 이벤트 감지로 웹 트래픽을 최소화했습니다.  

1.8.0버전  
-이메일 알림 기능이 추가되었습니다.  
-여러개의 설정을 관리할 수 있도록 설정 저장 및 불러오기 기능이 개선되었습니다.  

1.8.1버전  
-일부 환경에서 새글 이벤트 처리 첫 시도를 실패하고 Unknown 알림을 받는 현상이 수정되었습니다.  
-드믈게 새글 파싱까지 성공하였으나 모바일 알림이 보내지지 않는 현상이 완화되었습니다.  
-웹소켓 통신 중 네트워크 오류시 스레드가 완전히 종료되는 버그가 수정되었습니다.  

1.8.2버전  
-봇검사 오류시 HTTP 세션을 다시 생성하도록 변경되었습니다.  
-웹소켓 연결 재시도 중에도 중지 버튼 클릭시 즉시 중지되게 수정되었습니다.  

### 도움을 주신 분
RTFM

### 문의

이메일 : aldlfkahs95@naver.com  
블로그 : https://togomi.tistory.com/27  

버그 문의 시, Notification.log를 같이 첨부하여 보내주세요!
