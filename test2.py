import requests
import datetime
import random
from atprototools import Session
import getpass

# 사용자 정보 입력
bsky_username = input("블루스카이 사용자 이름을 입력하세요: ")
bsky_password = getpass.getpass("블루스카이 비밀번호를 입력하세요: ")
url = input("포스트 URL을 입력하세요: ")

# 세션 생성
try:
    session = Session(bsky_username, bsky_password)
except ValueError:
    print("로그인에 실패했습니다. 핸들과 앱 패스워드를 다시 확인해주세요.")
    exit()

# URL에서 rkey 추출
rkey = url.split('/')[-1]
at_uri = f'at://{session.DID}/app.bsky.feed.post/{rkey}'

def get_reposted_by(cursor=None):
    headers = {"Authorization": "Bearer " + session.ATP_AUTH_TOKEN}
    params = {
        "uri": at_uri,
        "limit": 50
    }
    if cursor:
        params['cursor'] = cursor
    resp = requests.get(
        session.ATP_HOST + "/xrpc/app.bsky.feed.getRepostedBy",
        headers=headers,
        params=params
    ).json()
    return resp

def get_all_reposted_by():
    reposted_by = []
    cursor = None
    while True:
        resp = get_reposted_by(cursor)
        reposted_by += resp['repostedBy']
        if 'cursor' not in resp:
            break
        cursor = resp['cursor']
    return reposted_by

def random_pick():
    pool = [user for user in get_all_reposted_by() if user['handle'] != bsky_username]
    assert pool, "자기 자신을 제외한 리포스트 수가 0이라 추첨을 진행할 수 없습니다."
    user = random.choice(pool)
    return user

def post():
    user = random_pick()

    display_name = user.get('displayName', user['handle'])
    print(f"추첨 결과: {display_name} (@{user['handle']})")

    txt = f"RT 추첨 결과{display_name}님 (@{user['handle']}) 당첨을 축하드립니다! "
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

    headers = {"Authorization": "Bearer " + session.ATP_AUTH_TOKEN}

    data = {
        "collection": "app.bsky.feed.post",
        "$type": "app.bsky.feed.post",
        "repo": session.DID,
        "record": {
            "$type": "app.bsky.feed.post",
            "createdAt": timestamp,
            "text": txt
        }
    }


post()
