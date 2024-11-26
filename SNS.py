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

        # 블루스카이의 경우 리트윗 당첨자 파일도 초기화
        if "bluesky" in filename.lower():
            reposted_filename = filename.replace("likes", "reposted")  # "likes"를 "reposted"로 변경
            with open(reposted_filename, 'w', encoding='utf-8') as f:
                f.write("")  # 리트윗 파일도 초기화

        # 메시지 표시용 Label 생성
        if not hasattr(winners_window, "message_label"):
            winners_window.message_label = tk.Label(winners_window, text="초기화 되었습니다.")
            winners_window.message_label.pack()
        else:
            winners_window.message_label.config(text="초기화 되었습니다.")  # 기존 Label 업데이트

        # 초기화 후, 당첨자 목록을 새로 불러오기
        winners_window.after(1000, lambda: show_winners_window(winners_window.title().split()[0]))  # 1초 후 목록 새로고침

    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")



# 당첨자 목록을 보여주는 창
# 기존 당첨자 목록 창 참조를 저장할 변수
winner_windows = {}

# 당첨자 목록을 보여주는 창
def show_winners_window(platform):
    global winner_windows

    # 기존에 창이 열려 있다면 닫기
    if platform in winner_windows and winner_windows[platform].winfo_exists():
        winner_windows[platform].destroy()

    if platform == "Bluesky":
        likes_filename = "bluesky_likes_winner.json"
        reposted_filename = "bluesky_reposted_winner.json"
    else:
        likes_filename = "youtube_winner.json"
        reposted_filename = None  # 유튜브는 리트윗 파일이 없으므로 None 처리

    try:
        # 유튜브의 경우 댓글 당첨자만 읽음
        with open(likes_filename, 'r', encoding='utf-8') as f:
            likes_winners = json.load(f)  # JSON 파일에서 당첨자 데이터 읽기
    except (FileNotFoundError, json.JSONDecodeError):
        likes_winners = []  # 파일이 없거나 오류가 나면 빈 리스트로 초기화

    try:
        # 블루스카이의 경우 리트윗 당첨자 목록도 읽음
        if platform == "Bluesky" and reposted_filename:
            with open(reposted_filename, 'r', encoding='utf-8') as f:
                reposted_winners = json.load(f)  # JSON 파일에서 리트윗 당첨자 데이터 읽기
        else:
            reposted_winners = []  # 유튜브는 리트윗 당첨자가 없으므로 빈 리스트
    except (FileNotFoundError, json.JSONDecodeError):
        reposted_winners = []  # 파일이 없거나 오류가 나면 빈 리스트로 초기화

    winners_window = tk.Toplevel(root)  # 새로운 윈도우 생성
    winners_window.title(f"{platform} 당첨자 목록")
    winner_windows[platform] = winners_window  # 창 참조 저장

    text_widget = tk.Text(winners_window, width=80, height=20, wrap=tk.WORD, state=tk.DISABLED)  # 텍스트 위젯
    text_widget.pack(padx=20, pady=10)

    # 유튜브는 댓글 당첨자만 출력
    if platform == "YouTube" and likes_winners:
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, f"\n** {platform} 댓글 당첨자 **\n", "bold")
        for winner in likes_winners:
            name = winner.get('name', '알 수 없음')
            comment = winner.get('comment', '알 수 없음')
            winner_text = f"당첨자: {name} - 댓글: {comment}\n"
            text_widget.insert(tk.END, winner_text)
        text_widget.insert(tk.END, "\n")  # 구분선

    # 블루스카이와 유튜브의 리트윗 당첨자 목록 출력
    if reposted_winners:
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, f"\n** {platform} 리트윗 당첨자 **\n", "bold")
        for winner in reposted_winners:
            display_name = winner.get('displayName', '알 수 없음')
            handle = winner.get('handle', '알 수 없음')
            winner_text = f"당첨자: {display_name} (@{handle})\n"
            text_widget.insert(tk.END, winner_text)
        text_widget.insert(tk.END, "\n")  # 구분선

    # 당첨자가 없으면
    if not likes_winners and not reposted_winners:
        text_widget.insert(tk.END, "당첨자가 없습니다.\n")

    text_widget.config(state=tk.DISABLED)

    clear_button = tk.Button(winners_window, text="당첨자 목록 초기화", command=lambda: clean_winners_file(winners_window, likes_filename))
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

def post_to_bluesky(username, password, url, draw_type):
    try:
        bsky_draw = BlueskyDraw(username, password, url)

        # 추첨 대상 데이터를 가져오기
        if draw_type == "likes":
            result = bsky_draw.random_pick(target_type='likes')  # 무작위 추첨
        elif draw_type == "reposted":
            result = bsky_draw.random_pick(target_type='reposted')  # 무작위 추첨
        else:
            raise ValueError("추첨 타입이 잘못되었습니다.")

        # 결과 유효성 확인
        if result and 'handle' in result:
            result_window = tk.Toplevel(root)
            result_window.title("추첨 결과")
            result_window.attributes('-topmost', True)  # 결과 창 최상위로 설정

            # 결과 데이터 준비
            display_name = result.get('displayName', result['handle'])
            result_text = f"축하드립니다! 당첨자: {display_name} (@{result['handle']})"

            # 결과 표시
            tk.Label(result_window, text=result_text, padx=20, pady=20).pack()

            # 게시를 수행하는 버튼
            def post_winner():
                try:
                    # BlueskyDraw의 post_result 메서드 호출
                    post_result_response = bsky_draw.post_result()
                    print("게시물 생성 결과:", post_result_response)  # 디버깅을 위한 출력

                    # 성공 메시지 표시
                    messagebox.showinfo("성공", "추첨 결과가 성공적으로 게시되었습니다!")
                    result_window.destroy()
                except Exception as e:
                    messagebox.showerror("오류", f"게시 중 오류 발생: {str(e)}")
                        # 게시하지 않음 버튼 (게시하지 않고 당첨자 정보를 저장만 함)

            def cancel_post():
                try:
                    # 당첨자 정보를 JSON에 저장만 함
                    bsky_draw.save_winner({
                        "platform": "Bluesky", 
                        "handle": result['handle'], 
                        "displayName": display_name
                    }, target_type=draw_type)  # draw_type을 target_type으로 전달
                    print("게시하지 않고 당첨자 정보를 저장했습니다.")  # 디버깅용 메시지

                    # 취소 메시지 표시
                    messagebox.showinfo("정보", "추첨 결과가 저장되었습니다. 게시되지 않았습니다.")
                    result_window.destroy()
                except Exception as e:
                    messagebox.showerror("오류", f"저장 중 오류 발생: {str(e)}")


            # 게시 버튼 추가
            post_button = tk.Button(result_window, text="결과 게시하기", command=post_winner)
            post_button.pack(pady=10)

            cancel_button = tk.Button(result_window, text="게시하지 않기", command=cancel_post)
            cancel_button.pack(pady=5)
        else:
            messagebox.showwarning("경고", "결과를 가져올 수 없습니다. 추첨을 다시 시도해주세요.")  # 결과 없음 경고

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
