
bluesky_draw_code = """
import requests
import datetime
import random
import json
from atprototools import Session

class BlueskyDraw:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        if username and password and url:
            self.session = self.create_session()
            self.rkey = self.extract_rkey()
        else:
            self.rkey = None

    def create_session(self):
        try:
            return Session(self.username, self.password)
        except ValueError:
            raise ValueError("로그인 실패. 비밀번호 또는 핸들을 확인해주세요.")

    def extract_rkey(self):
        return self.url.split('/')[-1]

    def get_reposted_by(self, cursor=None):
        headers = {"Authorization": "Bearer " + self.session.ATP_AUTH_TOKEN}
        params = {
            "uri": f'at://{self.session.DID}/app.bsky.feed.post/{self.rkey}',
            "limit": 50
        }
        if cursor:
            params['cursor'] = cursor
        resp = requests.get(
            self.session.ATP_HOST + "/xrpc/app.bsky.feed.getRepostedBy",
            headers=headers,
            params=params
        ).json()
        return resp

    def get_all_reposted_by(self):
        reposted_by = []
        cursor = None
        while True:
            resp = self.get_reposted_by(cursor)
            reposted_by += resp['repostedBy']
            if 'cursor' not in resp:
                break
            cursor = resp['cursor']
        return reposted_by

    def save_winner(self, winner, filename='bluesky_winner.json'):
        try:
            with open(filename, 'r+', encoding='utf-8') as f:
                try:
                    winners = json.load(f)
                except json.JSONDecodeError:
                    winners = []  # Initialize as empty list if file is empty
                
                winners.append(winner)  # Add new winner
                
                f.seek(0)  # Move to the start of the file
                json.dump(winners, f, ensure_ascii=False, indent=4)  # Save as a formatted array
                f.truncate()  # Remove any remaining content
        except FileNotFoundError:
            # Create a new file if it does not exist
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([winner], f, ensure_ascii=False, indent=4)  # Initialize with the first winner


    def load_winners(self, filename='bluesky_winner.json'):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                winners = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            winners = []
        return winners
        
    def random_pick(self):
        pool = [user for user in self.get_all_reposted_by() if user['handle'] != self.username]
        picked_winners = self.load_winners()

        # Check for duplicate winners
        pool = [user for user in pool if user['handle'] not in [winner['handle'] for winner in picked_winners]]

        if not pool:
            raise ValueError("당첨자가 없습니다. 본인을 제외하고 모두 당첨되었습니다.")
        return random.choice(pool)

    def post_result(self):
        user = self.random_pick()
        display_name = user.get('displayName', user['handle'])
        print(f"Draw result: {display_name} (@{user['handle']})")

        txt = f"축하드립니다! {display_name} (@{user['handle']}) 당첨되셨습니다!!"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

        headers = {"Authorization": "Bearer " + self.session.ATP_AUTH_TOKEN}
        data = {
            "collection": "app.bsky.feed.post",
            "$type": "app.bsky.feed.post",
            "repo": self.session.DID,
            "record": {
                "$type": "app.bsky.feed.post",
                "createdAt": timestamp,
                "text": txt
            }
        }

        resp = requests.post(
            self.session.ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
            json=data,
            headers=headers
        )

        if resp.status_code == 200:
            rkey = resp.json()['uri'].split('/')[-1]
            print(f"축하드립니다!: https://bsky.app/profile/{self.username}/post/{rkey}")
            
            # Save winner
            self.save_winner({"platform": "Bluesky", "handle": user['handle'], "displayName": display_name})
            
            return {"text": txt, "handle": user['handle']}  # Return result
        else:
            raise Exception("결과 게시에 실패했습니다.")




"""

#bluesky_draw.py를 저장
with open('bluesky_draw.py', 'w', encoding='utf-8') as f:
    f.write(bluesky_draw_code.strip())