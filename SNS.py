import tkinter as tk
import threading
from tkinter import messagebox, Menu
import json
from youtube_draw import YouTubeDraw
from bluesky_draw import BlueskyDraw

YOUTUBE_API_KEY = "AIzaSyB_WGp4tCe7GZ0T8w-e5MOEc6jQ4Yc67Gs"

# 당첨자 목록 초기화 함수
def clean_winners_file(winners_window, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("")  # 파일을 비웁니다.
        tk.Label(winners_window, text="초기화 되었습니다.").pack()
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")

# 당첨자 목록 보기 함수 수정
def show_winners_window(platform):
    filename = "youtube_winner.json" if platform == "YouTube" else "bluesky_winner.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            winners = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        winners = []

    winners_window = tk.Toplevel(root)
    winners_window.title(f"{platform} 당첨자 목록")

    if winners:
        for winner in winners:
            if platform == "YouTube":
                name = winner.get('name', '알 수 없음')
                comment = winner.get('comment', '알 수 없음')
                winner_label = tk.Label(winners_window, text=f"{platform} 당첨자: {name} - 댓글: {comment}")
            else:  # Bluesky일 경우
                display_name = winner.get('displayName', '알 수 없음')
                handle = winner.get('handle', '알 수 없음')
                winner_label = tk.Label(winners_window, text=f"{platform} 당첨자: {display_name} (@{handle})")
            winner_label.pack()
    else:
        tk.Label(winners_window, text="당첨자가 없습니다.").pack()

    clear_button = tk.Button(winners_window, text="당첨자 목록 초기화", command=lambda: clean_winners_file(winners_window, filename))
    clear_button.pack(pady=5)


# 유튜브 추첨 함수
def pick_youtube_winner_gui():
    video_id = video_id_entry.get()
    if not video_id:
        messagebox.showwarning("경고", "비디오 ID를 입력하세요.")
        return

    try:
        yt_draw = YouTubeDraw(YOUTUBE_API_KEY)
        winner_data = yt_draw.pick_youtube_winner(video_id)
        if winner_data[0] is None:
            messagebox.showinfo("정보", winner_data[1])
        else:
            winner, comment = winner_data
            messagebox.showinfo("당첨자", f"당첨자: {winner[0]} - 댓글: {comment}")
    except Exception as e:
        messagebox.showerror("오류", f"추첨 중 오류 발생: {str(e)}")

# 블루스카이 추첨 실행 함수 (스레드 사용)
def post_to_bluesky(username, password, url):
    try:
        # BlueskyDraw 인스턴스 생성
        bsky_draw = BlueskyDraw(username, password, url)
        
        # 추첨 결과 얻기
        result = bsky_draw.post_result()

        # result가 None이 아니고, 'text' 키가 있는지 확인
        if result and 'text' in result:  
            result_window = tk.Toplevel(root)
            result_window.title("추첨 결과")
            result_window.attributes('-topmost', True)
    
            result_text = f"추첨 결과가 성공적으로 게시되었습니다!\n당첨자: {result['text']}"
            tk.Label(result_window, text=result_text, padx=20, pady=20).pack()

            # 당첨자 정보를 저장합니다.
            # 블루스카이 추첨 객체의 save_winner 메서드를 호출
            bsky_draw.save_winner({"platform": "Bluesky", "name": result['text'], "handle": result['handle']}, "bluesky_winner.json")
        else:
            # 결과가 없으면 에러 메시지 표시
            messagebox.showwarning("경고", "결과를 가져올 수 없습니다. 추첨을 다시 시도해주세요.")

    except ValueError as ve:
        # 로그인 오류 처리
        messagebox.showerror("오류", f"로그인 실패: {str(ve)}")
    except Exception as e:
        # 다른 오류 처리
        messagebox.showerror("오류", f"오류 발생: {str(e)}")

def start_bluesky_draw():
    username = bsky_username_entry.get()
    password = bsky_password_entry.get()
    url = bsky_url_entry.get()

    if not username or not password or not url:
        messagebox.showwarning("경고", "모든 필드를 입력하세요.")
        return

    threading.Thread(target=post_to_bluesky, args=(username, password, url)).start()

# GUI 설정
def create_main_gui():
    global root
    root = tk.Tk()
    root.title("유튜브 및 블루스카이 추첨기")
    root.geometry("1000x600")

    menu_bar = Menu(root)

    # 유튜브 메뉴
    youtube_menu = Menu(menu_bar, tearoff=0)
    youtube_menu.add_command(label="유튜브 추첨하기", command=open_youtube)
    youtube_menu.add_command(label="당첨자 목록 보기", command=lambda: show_winners_window("YouTube"))
    menu_bar.add_cascade(label="유튜브", menu=youtube_menu)

    # 블루스카이 메뉴
    bluesky_menu = Menu(menu_bar, tearoff=0)
    bluesky_menu.add_command(label="블루스카이 추첨하기", command=open_bluesky)
    bluesky_menu.add_command(label="당첨자 목록 보기", command=lambda: show_winners_window("Bluesky"))
    menu_bar.add_cascade(label="블루스카이", menu=bluesky_menu)

    root.config(menu=menu_bar)

    create_youtube_interface(root)

    return root

# 유튜브 입력란 및 버튼 설정
def create_youtube_interface(root):
    global video_id_label, video_id_entry, pick_youtube_button

    video_id_label = tk.Label(root, text="비디오 ID 입력:")
    video_id_entry = tk.Entry(root, width=50)
    pick_youtube_button = tk.Button(root, text="유튜브 추첨하기", command=pick_youtube_winner_gui)

    video_id_label.pack(pady=10)
    video_id_entry.pack(pady=10)
    pick_youtube_button.pack(pady=20)

# 블루스카이 입력란 및 버튼 설정
def create_bluesky_interface(root):
    global bsky_username_label, bsky_username_entry, bsky_password_label, bsky_password_entry, bsky_url_label, bsky_url_entry, bsky_pick_button

    bsky_username_label = tk.Label(root, text="블루스카이 사용자 이름:")
    bsky_username_entry = tk.Entry(root, width=50)
    bsky_password_label = tk.Label(root, text="블루스카이 비밀번호:")
    bsky_password_entry = tk.Entry(root, width=50, show="*")
    bsky_url_label = tk.Label(root, text="포스트 URL:")
    bsky_url_entry = tk.Entry(root, width=50)
    bsky_pick_button = tk.Button(root, text="블루스카이 추첨하기", command=start_bluesky_draw)

    bsky_username_label.pack(pady=10)
    bsky_username_entry.pack(pady=10)
    bsky_password_label.pack(pady=10)
    bsky_password_entry.pack(pady=10)
    bsky_url_label.pack(pady=10)
    bsky_url_entry.pack(pady=10)
    bsky_pick_button.pack(pady=20)

# 유튜브 인터페이스 생성 함수
def open_youtube():
    # 기존 위젯 제거 (메뉴바 제외)
    for widget in root.winfo_children():
        if isinstance(widget, tk.Menu):
            continue  # 메뉴바는 제거하지 않음
        widget.destroy()
    
    # YouTube 입력란 및 버튼 설정
    create_youtube_interface(root)

# Bluesky 인터페이스 생성 함수
def open_bluesky():
    # 기존 위젯 제거 (메뉴바 제외)
    for widget in root.winfo_children():
        if isinstance(widget, tk.Menu):
            continue  # 메뉴바는 제거하지 않음
        widget.destroy()
    
    # Bluesky 입력란 및 버튼 설정
    create_bluesky_interface(root)

if __name__ == "__main__":
    root = create_main_gui()
    root.mainloop()
