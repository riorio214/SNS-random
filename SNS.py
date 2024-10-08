import random
import tkinter as tk
from tkinter import messagebox
from googleapiclient.discovery import build
import json

# 유튜브 API 키
API_KEY = 'AIzaSyB_WGp4tCe7GZ0T8w-e5MOEc6jQ4Yc67Gs'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# 유튜브 클라이언트 생성
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_comments(video_id):
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

def show_winners_window():
    winners = load_winners()
    winners_window = tk.Toplevel(root)  # 새 창 생성
    winners_window.title("당첨자 목록")

    if winners:
        winners_list = "\n".join([f"당첨자: {winner['name']}, 댓글: {winner['comment']}" for winner in winners])
    else:
        winners_list = "당첨자가 없습니다."

    # 텍스트 위젯에 당첨자 목록 표시
    text_widget = tk.Text(winners_window, wrap=tk.WORD, width=50, height=20)
    text_widget.pack(padx=10, pady=10)
    text_widget.insert(tk.END, winners_list)
    text_widget.config(state=tk.DISABLED)  # 읽기 전용

    # 닫기 버튼 추가
    close_button = tk.Button(winners_window, text="닫기", command=winners_window.destroy)
    close_button.pack(pady=5)

def reset_winners():
    with open('winners.json', 'w') as f:
        f.write("")
    messagebox.showinfo("초기화", "당첨자 목록이 초기화되었습니다.")

def pick_winner():
    video_id = video_id_entry.get()
    comments = get_comments(video_id)

    if not comments:  # 댓글이 없는 경우 처리
        messagebox.showwarning("경고", "댓글이 없습니다.")
        return

    picked_winners = load_winners()  # 이미 당첨된 사람 불러오기

    # 중복 제거
    available_comments = [c for c in comments if c[0] not in [winner['name'] for winner in picked_winners]]

    if available_comments:
        winner = random.choice(available_comments)
        save_winner({"name": winner[0], "comment": winner[1]})
        messagebox.showinfo("당첨자", f"당첨자: {winner[0]}\n댓글: {winner[1]}")
    else:
        messagebox.showwarning("경고", "모든 댓글이 이미 당첨되었습니다.")

# GUI 설정
root = tk.Tk()
root.title("유튜브 추첨기")

# 비디오 ID 입력
tk.Label(root, text="비디오 ID 입력:").pack(pady=10)
video_id_entry = tk.Entry(root, width=50)
video_id_entry.pack(pady=10)

# 추첨 버튼
pick_button = tk.Button(root, text="추첨하기", command=pick_winner)
pick_button.pack(pady=20)

# 당첨자 목록 보기 버튼
show_button = tk.Button(root, text="당첨자 목록 보기", command=show_winners_window)
show_button.pack(pady=5)

# 초기화 버튼
reset_button = tk.Button(root, text="당첨자 목록 초기화", command=reset_winners)
reset_button.pack(pady=5)

# GUI 실행
root.mainloop()
