# SNS Random Picker

이 프로젝트는 유튜브와 블루스카이 API를 사용하여 특정 조건에 따라 무작위 추첨을 수행하고, 당첨자를 저장 및 표시하는 데 중점을 둡니다.

## 🌟 주요 기능
- **유튜브**: 댓글 또는 좋아요를 기반으로 추첨
- **블루스카이**: 리트윗 또는 좋아요를 기반으로 추첨
- **JSON 파일 저장**: 당첨자 데이터를 JSON 파일로 저장 및 조회 가능

---

## 📥 설치 방법

1. **의존성 설치**  
   아래 명령어를 실행하여 필요한 라이브러리를 설치합니다:
   ```bash
   pip install -r requirements.txt
API 키 설정
유튜브와 블루스카이 API 키 및 인증 정보를 설정하세요.
config.json 파일 예시:
json
코드 복사
{
  "youtube_api_key": "YOUR_YOUTUBE_API_KEY",
  "bluesky_credentials": {
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
  }
}
🚀 사용 방법
GUI 실행
아래 명령어를 사용하여 애플리케이션을 실행합니다:

bash
코드 복사
python main_gui.py
스크린샷
주요 기능 화면 예시:

추첨 창
당첨자 목록 보기
🤝 기여 방법
이 저장소를 포크합니다.
새로운 브랜치를 생성합니다:
bash
코드 복사
git checkout -b feature/새로운기능
변경 사항을 커밋합니다:
bash
코드 복사
git commit -m "Add 새로운 기능"
브랜치를 푸시합니다:
bash
코드 복사
git push origin feature/새로운기능
Pull Request를 생성합니다.
