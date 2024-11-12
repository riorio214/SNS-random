import tkinter as tk
import threading
from tkinter import messagebox, Menu
import json
from youtube_draw import YouTubeDraw  # 유튜브 추첨을 위한 모듈
from bluesky_draw import BlueskyDraw  # 블루스카이 추첨을 위한 모듈

# 유튜브 API 키
YOUTUBE_API_KEY = "AIzaSyB_WGp4tCe7GZ0T8w-e5MOEc6jQ4Yc67Gs"

# 당첨자 목록 초기화 함수
def clean_winners_file(winners_window, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("")  # 파일 내용 초기화
        if not hasattr(clean_winners_file, "message_label"):
            clean_winners_file.message_label = tk.Label(winners_window, text="초기화 되었습니다.")
            clean_winners_file.message_label.pack()  # 메시지 표시
        else:
            clean_winners_file.message_label.config(text="초기화 되었습니다.")  # 기존 메시지 업데이트
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")

# 당첨자 목록을 보여주는 창
def show_winners_window(platform):
    filename = "youtube_winner.json" if platform == "YouTube" else "bluesky_winner.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            winners = json.load(f)  # JSON 파일에서 당첨자 데이터 읽기
    except (FileNotFoundError, json.JSONDecodeError):
        winners = []  # 파일이 없거나 오류가 나면 빈 리스트로 초기화

    winners_window = tk.Toplevel(root)  # 새로운 윈도우 생성
    winners_window.title(f"{platform} 당첨자 목록")
    text_widget = tk.Text(winners_window, width=80, height=20, wrap=tk.WORD, state=tk.DISABLED)  # 텍스트 위젯
    text_widget.pack(padx=20, pady=10)

    if winners:
        for winner in winners:
            # 유튜브와 블루스카이의 당첨자 출력 형식이 다르므로 구분
            if platform == "YouTube":
                name = winner.get('name', '알 수 없음')
                comment = winner.get('comment', '알 수 없음')
                winner_text = f"{platform} 당첨자: {name} - 댓글: {comment}\n"
            else:
                display_name = winner.get('displayName', '알 수 없음')
                handle = winner.get('handle', '알 수 없음')
                winner_text = f"{platform} 당첨자: {display_name} (@{handle})\n"

            text_widget.config(state=tk.NORMAL)
            text_widget.insert(tk.END, winner_text)  # 당첨자 정보 삽입
            text_widget.config(state=tk.DISABLED)
    else:
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, "당첨자가 없습니다.\n")  # 당첨자가 없으면 알림
        text_widget.config(state=tk.DISABLED)

    clear_button = tk.Button(winners_window, text="당첨자 목록 초기화", command=lambda: clean_winners_file(winners_window, filename))
    clear_button.pack(pady=5)  # 초기화 버튼

# 유튜브 추첨하기 버튼 클릭 시 실행되는 함수
def pick_youtube_winner_gui():
    video_id = video_id_entry.get()  # 입력된 비디오 ID 가져오기
    if not video_id:
        messagebox.showwarning("경고", "비디오 ID를 입력하세요.")  # 비디오 ID가 없으면 경고 메시지
        return

    try:
        yt_draw = YouTubeDraw(YOUTUBE_API_KEY)
        winner_data = yt_draw.pick_youtube_winner(video_id)  # 유튜브 추첨
        winner_name, winner_comment = winner_data
        if winner_name is None:
            messagebox.showinfo("정보", winner_comment)  # 당첨자가 없으면 메시지
        else:
            messagebox.showinfo("당첨자", f"당첨자: {winner_name} - 댓글: {winner_comment}")  # 당첨자 표시
    except Exception as e:
        messagebox.showerror("오류", f"추첨 중 오류 발생: {str(e)}")  # 오류 처리

# 블루스카이 추첨 결과를 포스트하는 함수
def post_to_bluesky(username, password, url, draw_type):
    try:
        bsky_draw = BlueskyDraw(username, password, url)
        
        # 추첨 결과 얻기
        result = bsky_draw.post_result()
        
        # target_type에 따라 좋아요 또는 리포스트 추첨
        if draw_type == "likes":
            result = bsky_draw.random_pick(target_type='likes')
        elif draw_type == "reposted":
            result = bsky_draw.random_pick(target_type='reposted')
        else:
            raise ValueError("추첨 타입이 잘못되었습니다.")
        

        # result가 유효한지 확인 후 결과 창에 표시
        if result and 'handle' in result:
            result_window = tk.Toplevel(root)
            result_window.title("추첨 결과")
            result_window.attributes('-topmost', True)  # 결과 창을 최상위로 설정

            # 당첨자 이름과 핸들을 포함한 결과 텍스트 생성
            display_name = result.get('displayName', result['handle'])
            result_text = f"축하드립니다! 당첨자: {display_name} (@{result['handle']})"

            tk.Label(result_window, text=result_text, padx=20, pady=20).pack()

            # 당첨자 정보를 JSON 파일에 저장
            bsky_draw.save_winner({"platform": "Bluesky", "displayName": display_name, "handle": result['handle']}, "bluesky_winner.json")
        else:
            messagebox.showwarning("경고", "결과를 가져올 수 없습니다. 추첨을 다시 시도해주세요.")  # 결과가 없으면 경고 메시지

    except ValueError as ve:
        messagebox.showerror("오류", f"로그인 실패: {str(ve)}")
    except Exception as e:
        messagebox.showerror("오류", f"오류 발생: {str(e)}")

# 블루스카이 추첨 스레드 시작 함수
def start_bluesky_draw():
    username = bsky_username_entry.get()
    password = bsky_password_entry.get()
    url = bsky_url_entry.get()
    draw_type = bsky_draw_type.get()

    if not username or not password or not url:
        messagebox.showwarning("경고", "모든 필드를 입력하세요.")  # 필드가 비어 있으면 경고
        return

    threading.Thread(target=post_to_bluesky, args=(username, password, url, draw_type)).start()  # 별도의 스레드에서 실행

# 메인 GUI를 설정하는 함수
def create_main_gui():
    global root
    root = tk.Tk()
    root.title("유튜브 및 블루스카이 추첨기")
    root.geometry("1000x600")

    menu_bar = Menu(root)  # 메뉴 바 생성

    youtube_menu = Menu(menu_bar, tearoff=0)
    youtube_menu.add_command(label="유튜브 추첨하기", command=open_youtube)  # 유튜브 추첨 메뉴
    youtube_menu.add_command(label="당첨자 목록 보기", command=lambda: show_winners_window("YouTube"))  # 유튜브 당첨자 목록 메뉴
    menu_bar.add_cascade(label="유튜브", menu=youtube_menu)

    bluesky_menu = Menu(menu_bar, tearoff=0)
    bluesky_menu.add_command(label="블루스카이 추첨하기", command=open_bluesky)  # 블루스카이 추첨 메뉴
    bluesky_menu.add_command(label="당첨자 목록 보기", command=lambda: show_winners_window("Bluesky"))  # 블루스카이 당첨자 목록 메뉴
    menu_bar.add_cascade(label="블루스카이", menu=bluesky_menu)

    root.config(menu=menu_bar)

    create_youtube_interface(root)  # 초기 화면은 유튜브 인터페이스로 설정

    return root

# 유튜브 인터페이스 생성
def create_youtube_interface(root):
    global video_id_label, video_id_entry, pick_youtube_button

    video_id_label = tk.Label(root, text="비디오 ID 입력:")
    video_id_entry = tk.Entry(root, width=50)
    pick_youtube_button = tk.Button(root, text="유튜브 추첨하기", command=pick_youtube_winner_gui)

    video_id_label.pack(pady=10)
    video_id_entry.pack(pady=10)
    pick_youtube_button.pack(pady=20)

# 블루스카이 인터페이스 생성
def create_bluesky_interface(root):
    global bsky_username_label, bsky_username_entry, bsky_password_label, bsky_password_entry, bsky_url_label, bsky_url_entry, bsky_pick_button, bsky_draw_type

    bsky_username_label = tk.Label(root, text="블루스카이 사용자 이름:")
    bsky_username_entry = tk.Entry(root, width=50)
    bsky_password_label = tk.Label(root, text="블루스카이 비밀번호:")
    bsky_password_entry = tk.Entry(root, width=50, show="*")
    bsky_url_label = tk.Label(root, text="블루스카이 URL:")
    bsky_url_entry = tk.Entry(root, width=50)
    
    bsky_draw_type = tk.StringVar()
    bsky_draw_type.set("likes")  # 기본값 설정
    
    likes_radio = tk.Radiobutton(root, text="좋아요 추첨", variable=bsky_draw_type, value="likes")
    repost_radio = tk.Radiobutton(root, text="리트윗 추첨", variable=bsky_draw_type, value="reposted")
    
    bsky_pick_button = tk.Button(root, text="블루스카이 추첨하기", command=start_bluesky_draw)

    bsky_username_label.pack(pady=5)
    bsky_username_entry.pack(pady=5)
    bsky_password_label.pack(pady=5)
    bsky_password_entry.pack(pady=5)
    bsky_url_label.pack(pady=5)
    bsky_url_entry.pack(pady=5)
    likes_radio.pack(pady=5)
    repost_radio.pack(pady=5)
    bsky_pick_button.pack(pady=20)

# 유튜브 인터페이스를 여는 함수
def open_youtube():
    clear_interface()  # 기존 인터페이스를 지우고 새로운 인터페이스로 변경
    create_youtube_interface(root)  # 유튜브 인터페이스 생성

# 블루스카이 인터페이스를 여는 함수
def open_bluesky():
    clear_interface()  # 기존 인터페이스를 지우고 새로운 인터페이스로 변경
    create_bluesky_interface(root)  # 블루스카이 인터페이스 생성

# 기존 인터페이스를 지우는 함수
def clear_interface():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Menu):
            continue  # 메뉴바는 제거하지 않음
        widget.destroy()  # 나머지 위젯들은 제거

if __name__ == "__main__":
    root = create_main_gui()  # 메인 GUI 실행
    root.mainloop()  # GUI 루프 시작
