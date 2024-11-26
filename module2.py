
bluesky_draw_code = """
# 필요한 라이브러리를 가져옵니다.
import requests  # HTTP 요청을 보내기 위한 requests 모듈
import datetime  # 날짜와 시간을 처리하기 위한 datetime 모듈
import random  # 무작위 추첨을 위한 random 모듈
import json  # JSON 파일 입출력에 사용할 json 모듈
from atprototools import Session  # Bluesky API와의 세션 관리를 위한 Session 클래스

# BlueskyDraw 클래스 정의, 추첨 기능을 수행
class BlueskyDraw:
    # 클래스 초기화 함수, 로그인 정보와 URL을 통해 추첨을 위한 환경을 설정
    def __init__(self, username, password, url):
        self.username = username  # 로그인할 사용자명
        self.password = password  # 로그인할 비밀번호
        self.url = url  # 추첨 대상 URL
        if username and password and url:
            self.session = self.create_session()  # 세션 생성
            self.rkey = self.extract_rkey()  # URL에서 리소스 키 추출
        else:
            self.rkey = None  # 로그인 정보가 없으면 리소스 키를 None으로 설정

    # 세션을 생성하는 함수
    def create_session(self):
        try:
            return Session(self.username, self.password)  # Session 객체 생성 및 반환
        except ValueError:
            # 로그인 실패 시 예외 발생
            raise ValueError("로그인 실패. 비밀번호 또는 핸들을 확인해주세요.")

    # URL에서 리소스 키(rkey)를 추출하는 함수
    def extract_rkey(self):
        return self.url.split('/')[-1]  # URL의 마지막 부분을 리소스 키로 반환

    # 특정 게시물을 리포스트한 사용자 정보를 가져오는 함수
    def get_reposted_by(self, cursor=None):
        headers = {"Authorization": "Bearer " + self.session.ATP_AUTH_TOKEN}  # 인증 토큰 설정
        params = {
            "uri": f'at://{self.session.DID}/app.bsky.feed.post/{self.rkey}',  # 게시물 URI 설정
            "limit": 50  # 한 번에 가져올 리포스트한 사용자 수
        }
        if cursor:
            params['cursor'] = cursor  # 페이지네이션을 위한 커서 설정
        resp = requests.get(
            self.session.ATP_HOST + "/xrpc/app.bsky.feed.getRepostedBy",  # 리포스트한 사용자 목록 가져오기 API 호출
            headers=headers,
            params=params
        ).json()
        return resp  # 결과 반환

    # 리포스트한 모든 사용자 정보를 가져오는 함수
    def get_all_reposted_by(self):
        reposted_by = []
        cursor = None
        while True:
            resp = self.get_reposted_by(cursor)
            # 'repostedBy' 키에서 사용자 정보 리스트를 추가
            reposted_by += resp.get('repostedBy', [])

            if 'cursor' not in resp:
                break  # 다음 페이지가 없으면 종료
            cursor = resp['cursor']

        return reposted_by  # 전체 리포스트한 사용자 목록 반환

    # 특정 게시물을 좋아요한 사용자 정보를 가져오는 함수
    def get_likes(self, cursor=None):
        headers = {"Authorization": "Bearer " + self.session.ATP_AUTH_TOKEN}
        params = {
            "uri": f'at://{self.session.DID}/app.bsky.feed.post/{self.rkey}',
            "limit": 50
        }
        if cursor:
            params['cursor'] = cursor

        try:
            resp = requests.get(
                self.session.ATP_HOST + "/xrpc/app.bsky.feed.getLikes",
                headers=headers,
                params=params
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return {}

    # 좋아요한 모든 사용자 정보를 가져오는 함수
    def get_all_likes(self):
        liked_by = []
        cursor = None
        while True:
            resp = self.get_likes(cursor)
            # 'likes' 키에서 각 사용자 정보를 'actor'로 접근하여 리스트에 추가
            likes_data = resp.get('likes', [])
            liked_by += [like['actor'] for like in likes_data]  # 'actor' 정보만 추출하여 리스트에 추가

            if 'cursor' not in resp:
                break  # 다음 페이지가 없으면 종료
            cursor = resp['cursor']

        return liked_by  # 전체 좋아요한 사용자 목록 반환

    # 당첨자를 JSON 파일에 저장하는 함수
    def save_winner(self, winner, target_type, filename='bluesky_winner.json'):
        # 'displayName'이 없는 경우에는 '알 수 없음' 처리
        if not winner.get('displayName'):
            winner['displayName'] = "알 수 없음"  # displayName이 없으면 '알 수 없음'으로 대체

        # 타겟 타입에 따라 다른 파일로 저장
        if target_type == "likes":
            filename = 'bluesky_likes_winner.json'  # 좋아요 추첨은 별도의 파일에 저장
        elif target_type == "reposted":
            filename = 'bluesky_reposted_winner.json'  # 리트윗 추첨은 별도의 파일에 저장

        try:
            with open(filename, 'r+', encoding='utf-8') as f:
                try:
                    winners = json.load(f)  # 기존의 당첨자 목록을 불러옴
                except json.JSONDecodeError:
                    winners = []  # 파일이 비어있을 경우 빈 리스트로 초기화

                # 중복된 당첨자가 이미 있는지 확인하고 없으면 추가
                if not any(existing_winner['handle'] == winner['handle'] for existing_winner in winners):
                    winners.append(winner)  # 새로운 당첨자 추가

                f.seek(0)  # 파일의 시작 위치로 이동
                json.dump(winners, f, ensure_ascii=False, indent=4)  # 리스트를 JSON 형식으로 저장
                f.truncate()  # 파일의 나머지 부분을 지워서 덮어쓰기
        except FileNotFoundError:
            # 파일이 없을 경우 새로 생성하여 당첨자 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([winner], f, ensure_ascii=False, indent=4)  # 첫 당첨자 저장



    # 기존 당첨자 목록을 불러오는 함수
    def load_winners(self, target_type, filename='bluesky_winner.json'):
        # 타겟 타입에 따라 파일명을 다르게 설정
        if target_type == "likes":
            filename = 'bluesky_likes_winner.json'
        elif target_type == "reposted":
            filename = 'bluesky_reposted_winner.json'

        try:
            # 파일이 존재할 경우 내용을 읽어 JSON 형식으로 반환
            with open(filename, 'r', encoding='utf-8') as f:
                winners = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            winners = []  # 파일이 없거나 JSON 형식이 아닐 경우 빈 리스트 반환
        return winners  # 당첨자 목록 반환


    def random_pick(self, target_type="reposted"):
        # target_type에 따라 추첨 대상을 설정
        if target_type == "likes":
            pool = [user for user in self.get_all_likes() if user['handle'] != self.username]  # 좋아요 누른 사용자
        elif target_type == "reposted":
            pool = [user for user in self.get_all_reposted_by() if user['handle'] != self.username]  # 리트윗한 사용자
        else:
            raise ValueError("잘못된 추첨 타입입니다. 'likes' 또는 'reposted'만 가능합니다.")

        # pool이 비어 있으면 사용자에게 경고를 표시
        if not pool:
            raise ValueError("참여자가 없습니다. 목록을 확인하세요.")

        # 중복 당첨을 방지하여 아직 당첨되지 않은 사용자들만 추출
        picked_winners = self.load_winners(target_type)
        pool = [user for user in pool if user['handle'] not in [winner['handle'] for winner in picked_winners]]

        if not pool:
            raise ValueError("당첨자가 없습니다. 본인을 제외하고 모두 당첨되었습니다.")
        
        return random.choice(pool)  # 무작위로 한 명 선택

    # 당첨 결과를 게시하는 함수
    def post_result(self, draw_type):
        if draw_type == "likes":
            result_type = "좋아요 추첨 결과"
        elif draw_type == "reposted":
            result_type = "리트윗 추첨 결과"
        else:
            raise ValueError("추첨 타입이 잘못되었습니다.")

        user = self.random_pick(target_type=draw_type)  # 무작위로 당첨자 추첨
        display_name = user.get('displayName', user['handle'])  # 당첨자의 표시 이름 가져오기
        print(f"{result_type}: {display_name} (@{user['handle']})")  # 콘솔에 당첨자 정보 출력

        # 당첨자가 '알 수 없음'인 경우, 다른 값으로 대체
        if display_name == "알 수 없음" or not display_name:
            display_name = user['handle']  # '알 수 없음'인 경우 handle로 대체

        # 축하 메시지 작성
        txt = f"축하드립니다! {display_name} (@{user['handle']}) {result_type} 당첨되셨습니다!!"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')  # 현재 시간을 UTC로 표시

        headers = {"Authorization": "Bearer " + self.session.ATP_AUTH_TOKEN}  # 인증 토큰 설정
        data = {
            "collection": "app.bsky.feed.post",  # 게시물 타입 설정
            "$type": "app.bsky.feed.post",
            "repo": self.session.DID,  # 현재 계정의 DID 설정
            "record": {
                "$type": "app.bsky.feed.post",
                "createdAt": timestamp,
                "text": txt
            }
        }

        resp = requests.post(
            self.session.ATP_HOST + "/xrpc/com.atproto.repo.createRecord",  # Bluesky API를 통해 게시물 작성
            json=data,
            headers=headers
        )

        if resp.status_code == 200:  # 게시 성공 시
            rkey = resp.json()['uri'].split('/')[-1]
            print(f"축하드립니다!: https://bsky.app/profile/{self.username}/post/{rkey}")  # 게시물 링크 출력

            # 당첨자 정보를 파일에 저장
            self.save_winner({"platform": "Bluesky", "handle": user['handle'], "displayName": display_name}, target_type=draw_type)

            return {"text": txt, "handle": user['handle']}  # 결과 반환
        else:
            raise Exception("결과 게시에 실패했습니다.")  # 게시 실패 시 예외 발생






"""

#bluesky_draw.py를 저장
with open('bluesky_draw.py', 'w', encoding='utf-8') as f:
    f.write(bluesky_draw_code.strip())