# 필요한 라이브러리를 가져옵니다.
import random  # 무작위 추첨을 위한 random 모듈
import json  # JSON 파일 입출력에 사용할 json 모듈
from googleapiclient.discovery import build  # YouTube API 호출을 위한 모듈

# YouTubeDraw 클래스 정의, 추첨 기능을 담고 있음
class YouTubeDraw:
    # 클래스 초기화 함수, API 키를 입력받아 YouTube API 클라이언트를 생성
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)  # API 키로 YouTube API 클라이언트 생성

    # 특정 비디오의 댓글을 가져오는 함수
    def get_youtube_comments(self, video_id):
        comments = []  # 댓글 정보를 담을 빈 리스트 생성
        try:
            # 댓글을 가져오기 위한 API 요청, 최대 100개의 댓글을 한 번에 가져옴
            response = self.youtube.commentThreads().list(
                part='snippet',  # 댓글 내용 관련 정보를 요청
                videoId=video_id,  # 조회할 비디오 ID
                textFormat='plainText',  # 텍스트 형식으로 댓글 가져오기
                maxResults=100  # 한 번에 가져올 댓글 수 설정
            ).execute()  # API 요청 실행

            # 각 댓글의 작성자와 내용을 comments 리스트에 추가
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                comments.append((author, comment))  # 작성자와 댓글 내용을 튜플로 리스트에 추가

            # 다음 페이지가 있는 경우 계속해서 댓글을 가져옴
            while 'nextPageToken' in response:
                response = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=100,
                    pageToken=response['nextPageToken']  # 다음 페이지 토큰을 이용하여 다음 댓글 요청
                ).execute()
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                    comments.append((author, comment))

        except Exception as e:
            # 오류 발생 시 메시지 출력
            print(f"오류 발생: {e}")

        # 모든 댓글을 반환
        return comments

    # 추첨된 당첨자를 JSON 파일에 저장하는 함수
    def save_winner(self, winner, filename='youtube_winner.json'):
        try:
            # 기존 파일을 읽어온 뒤 새 당첨자를 추가해 저장
            with open(filename, 'r+', encoding='utf-8') as f:
                try:
                    winners = json.load(f)  # 기존의 당첨자 목록을 불러옴
                except json.JSONDecodeError:
                    winners = []  # 파일이 비어있을 경우 빈 리스트로 초기화

                winners.append(winner)  # 새로운 당첨자를 리스트에 추가

                f.seek(0)  # 파일의 시작 위치로 이동
                json.dump(winners, f, ensure_ascii=False, indent=4)  # 리스트를 JSON 형식으로 저장
                f.truncate()  # 파일의 나머지 부분을 지워서 덮어쓰기

        except FileNotFoundError:
            # 파일이 없을 경우 새로 파일을 생성하고 당첨자 리스트를 초기화하여 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([winner], f, ensure_ascii=False, indent=4)  # 새로운 파일에 저장
        except Exception as e:
            # 저장 오류 발생 시 메시지 출력
            print(f"저장 오류: {e}")

    # 기존의 당첨자 목록을 불러오는 함수
    def load_winners(self, filename='youtube_winner.json'):
        try:
            # 파일이 존재할 경우 내용을 읽어 JSON 형식으로 반환
            with open(filename, 'r', encoding='utf-8') as f:
                winners = json.load(f)  # 전체 내용을 한 번에 불러옴
        except (FileNotFoundError, json.JSONDecodeError):
            winners = []  # 파일이 없거나 JSON 형식이 아닐 경우 빈 리스트 반환
        return winners  # 당첨자 목록 반환

    # 유튜브 비디오에서 랜덤으로 당첨자를 뽑는 함수
    def pick_youtube_winner(self, video_id):
        comments = self.get_youtube_comments(video_id)  # 해당 비디오의 댓글 목록을 불러옴
    
        if not comments:  # 댓글이 없으면 오류 메시지 반환
            return None, "댓글이 없습니다."
    
        # 기존 당첨자 목록을 불러옴
        picked_winners = self.load_winners()
        # 기존에 당첨되지 않은 댓글만 필터링하여 사용
        available_comments = [c for c in comments if c[0] not in [winner['name'] for winner in picked_winners]]
    
        if available_comments:  # 당첨 가능한 댓글이 있을 경우
            winner = random.choice(available_comments)  # 무작위로 댓글 선택
            winner_name = winner[0]  # 당첨자 이름
            winner_comment = winner[1]  # 댓글
            # 선택된 당첨자 정보를 저장
            self.save_winner({"platform": "YouTube", "name": winner_name, "comment": winner_comment})
            return winner_name, winner_comment  # (작성자, 댓글) 형식으로 반환
        else:
            # 모든 댓글이 이미 당첨되었을 경우
            return None, "모든 댓글이 이미 당첨되었습니다."