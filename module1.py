youtube_draw_code = """
import random
import json
from googleapiclient.discovery import build

# 유튜브 API 키
YOUTUBE_API_KEY = 'AIzaSyB_WGp4tCe7GZ0T8w-e5MOEc6jQ4Yc67Gs'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# 유튜브 클라이언트 생성
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

def get_youtube_comments(video_id):
    comments = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100
        ).execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append((author, comment))

        while 'nextPageToken' in response:
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=100,
                pageToken=response['nextPageToken']
            ).execute()
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                comments.append((author, comment))

    except Exception as e:
        print(f"오류 발생: {e}")

    return comments

def save_winner(winner):
    try:
        with open('winners.json', 'a') as f:
            json.dump(winner, f)
            f.write("\n")
    except Exception as e:
        print(f"저장 오류: {e}")

def load_winners():
    winners = []
    try:
        with open('winners.json', 'r') as f:
            for line in f:
                winners.append(json.loads(line))
    except FileNotFoundError:
        pass
    return winners

def pick_youtube_winner(video_id):
    comments = get_youtube_comments(video_id)

    if not comments:
        return None, "댓글이 없습니다."

    picked_winners = load_winners()
    available_comments = [c for c in comments if c[0] not in [winner['name'] for winner in picked_winners]]

    if available_comments:
        winner = random.choice(available_comments)
        save_winner({"name": winner[0], "comment": winner[1]})
        return winner, None
    else:
        return None, "모든 댓글이 이미 당첨되었습니다."
"""

#youtube_draw.py를 저장
with open('youtube_draw.py', 'w', encoding='utf-8') as f:
    f.write(youtube_draw_code.strip())