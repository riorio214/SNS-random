# GUI와 멀티스레딩을 위한 라이브러리를 가져옵니다.
import tkinter as tk  # GUI 애플리케이션을 구축하기 위한 tkinter 모듈
import threading  # GUI의 비동기 작업을 위해 사용할 threading 모듈
from tkinter import messagebox, Menu  # tkinter의 메시지 박스와 메뉴 기능
import json  # 당첨자 정보를 JSON 파일로 관리하기 위한 json 모듈
from youtube_draw import YouTubeDraw  # 유튜브 추첨 기능을 담은 YouTubeDraw 클래스
from bluesky_draw import BlueskyDraw  # 블루스카이 추첨 기능을 담은 BlueskyDraw 클래스

# 유튜브 API 키
YOUTUBE_API_KEY = "AIzaSyB_WGp4tCe7GZ0T8w-e5MOEc6jQ4Yc67Gs"

# 당첨자 목록 초기화 함수
def clean_winners_file(winners_window, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("")  # 파일을 비웁니다.
        tk.Label(winners_window, text="초기화 되었습니다.").pack()
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")

# 당첨자 목록을 표시하는 함수
def show_winners_window(platform):
    # 각 플랫폼에 맞는 당첨자 파일을 선택
    filename = "youtube_winner.json" if platform == "YouTube" else "bluesky_winner.json"
    try:
        # JSON 파일을 열어 당첨자 목록을 읽어옴
        with open(filename, 'r', encoding='utf-8') as f:
            winners = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        winners = []  # 파일이 없거나 비어있을 경우 빈 리스트로 초기화

    # 새 창 생성
    winners_window = tk.Toplevel(root)
    winners_window.title(f"{platform} 당첨자 목록")

    # 읽기 전용 Text 위젯 생성
    text_widget = tk.Text(winners_window, width=80, height=20, wrap=tk.WORD, state=tk.DISABLED)
    text_widget.pack(padx=20, pady=10)

    # 당첨자가 있을 경우
    if winners:
        for winner in winners:
            # 유튜브일 경우 이름과 댓글 정보 출력
            if platform == "YouTube":
                name = winner.get('name', '알 수 없음')
                comment = winner.get('comment', '알 수 없음')
                winner_text = f"{platform} 당첨자: {name} - 댓글: {comment}\n"
            else:  # 블루스카이일 경우 이름과 핸들 정보 출력
                display_name = winner.get('displayName', '알 수 없음')
                handle = winner.get('handle', '알 수 없음')
                winner_text = f"{platform} 당첨자: {display_name} (@{handle})\n"
            
            # Text 위젯에 당첨자 정보 삽입 (읽기 전용 상태에서는 삽입이 불가능하므로, 상태를 변경)
            text_widget.config(state=tk.NORMAL)  # 쓰기 가능 상태로 설정
            text_widget.insert(tk.END, winner_text)  # 당첨자 정보 삽입
            text_widget.config(state=tk.DISABLED)  # 다시 읽기 전용 상태로 설정
    else:
        # 당첨자가 없을 경우 안내 메시지 출력
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, "당첨자가 없습니다.\n")
        text_widget.config(state=tk.DISABLED)

    # 당첨자 목록 초기화 버튼 생성
    clear_button = tk.Button(winners_window, text="당첨자 목록 초기화", command=lambda: clean_winners_file(winners_window, filename))
    clear_button.pack(pady=5)
    
# 유튜브 추첨을 위한 GUI 함수
def pick_youtube_winner_gui():
    video_id = video_id_entry.get()  # 입력란에서 비디오 ID 가져오기
    if not video_id:
        messagebox.showwarning("경고", "비디오 ID를 입력하세요.")  # 비디오 ID가 없을 경우 경고 메시지
        return

    try:
        yt_draw = YouTubeDraw(YOUTUBE_API_KEY)  # 유튜브 추첨 객체 생성
        winner_data = yt_draw.pick_youtube_winner(video_id)  # 추첨 실행
        winner_name, winner_comment = winner_data  # 당첨자와 댓글을 분리하여 받기
        if winner_name is None:
            messagebox.showinfo("정보", winner_comment)  # 당첨자가 없을 경우 안내 메시지
        else:
            messagebox.showinfo("당첨자", f"당첨자: {winner_name} - 댓글: {winner_comment}")  # 당첨자 정보 표시
    except Exception as e:
        messagebox.showerror("오류", f"추첨 중 오류 발생: {str(e)}")  # 추첨 중 오류 발생 시 메시지 표시


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

# 블루스카이 추첨 실행 함수 (스레드 시작)
def start_bluesky_draw():
    username = bsky_username_entry.get()  # 사용자 이름 가져오기
    password = bsky_password_entry.get()  # 비밀번호 가져오기
    url = bsky_url_entry.get()  # 추첨할 URL 가져오기

    if not username or not password or not url:
        messagebox.showwarning("경고", "모든 필드를 입력하세요.")  # 필드가 비어있으면 경고
        return

    # 별도의 스레드에서 Bluesky 추첨 함수 실행
    threading.Thread(target=post_to_bluesky, args=(username, password, url)).start()

# 메인 GUI를 생성하는 함수
def create_main_gui():
    global root
    root = tk.Tk()  # 메인 윈도우 생성
    root.title("유튜브 및 블루스카이 추첨기")  # 창 제목 설정
    root.geometry("1000x600")  # 창 크기 설정

    menu_bar = Menu(root)  # 메뉴바 생성

    # 유튜브 메뉴 설정
    youtube_menu = Menu(menu_bar, tearoff=0)
    youtube_menu.add_command(label="유튜브 추첨하기", command=open_youtube)  # 유튜브 추첨 메뉴
    youtube_menu.add_command(label="당첨자 목록 보기", command=lambda: show_winners_window("YouTube"))  # 유튜브 당첨자 목록 보기
    menu_bar.add_cascade(label="유튜브", menu=youtube_menu)

    # 블루스카이 메뉴 설정
    bluesky_menu = Menu(menu_bar, tearoff=0)
    bluesky_menu.add_command(label="블루스카이 추첨하기", command=open_bluesky)  # 블루스카이 추첨 메뉴
    bluesky_menu.add_command(label="당첨자 목록 보기", command=lambda: show_winners_window("Bluesky"))  # 블루스카이 당첨자 목록 보기
    menu_bar.add_cascade(label="블루스카이", menu=bluesky_menu)

    root.config(menu=menu_bar)  # 메뉴바 추가

    create_youtube_interface(root)  # 초기 유튜브 인터페이스 생성

    return root  # 메인 윈도우 반환

# 유튜브 입력란 및 버튼 생성 함수
def create_youtube_interface(root):
    global video_id_label, video_id_entry, pick_youtube_button

    video_id_label = tk.Label(root, text="비디오 ID 입력:")  # 비디오 ID 입력란 레이블
    video_id_entry = tk.Entry(root, width=50)  # 비디오 ID 입력란
    pick_youtube_button = tk.Button(root, text="유튜브 추첨하기", command=pick_youtube_winner_gui)  # 유튜브 추첨 버튼

    video_id_label.pack(pady=10)
    video_id_entry.pack(pady=10)
    pick_youtube_button.pack(pady=20)

# 블루스카이 입력란 및 버튼 생성 함수
def create_bluesky_interface(root):
    global bsky_username_label, bsky_username_entry, bsky_password_label, bsky_password_entry, bsky_url_label, bsky_url_entry, bsky_pick_button

    bsky_username_label = tk.Label(root, text="블루스카이 사용자 이름:")  # 사용자 이름 레이블
    bsky_username_entry = tk.Entry(root, width=50)  # 사용자 이름 입력란
    bsky_password_label = tk.Label(root, text="블루스카이 비밀번호:")  # 비밀번호 레이블
    bsky_password_entry = tk.Entry(root, width=50, show="*")  # 비밀번호 입력란
    bsky_url_label = tk.Label(root, text="포스트 URL:")  # 포스트 URL 레이블
    bsky_url_entry = tk.Entry(root, width=50)  # URL 입력란
    bsky_pick_button = tk.Button(root, text="블루스카이 추첨하기", command=start_bluesky_draw)  # 블루스카이 추첨 버튼

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
    
    # 유튜브 인터페이스 생성
    create_youtube_interface(root)

# 블루스카이 인터페이스 생성 함수
def open_bluesky():
    # 기존 위젯 제거 (메뉴바 제외)
    for widget in root.winfo_children():
        if isinstance(widget, tk.Menu):
            continue  # 메뉴바는 제거하지 않음
        widget.destroy()
    
    # 블루스카이 인터페이스 생성
    create_bluesky_interface(root)

# 메인 함수
if __name__ == "__main__":
    root = create_main_gui()  # 메인 GUI 생성
    root.mainloop()  # 이벤트 루프 실행
