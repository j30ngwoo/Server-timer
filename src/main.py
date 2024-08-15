import tkinter as tk
import time
from sync import sync_with_server_minimal_error
from ui import (
    create_main_window, 
    setup_server_url_label, 
    setup_server_buttons, 
    setup_url_entry, 
    setup_sync_controls, 
    setup_delay_and_attempts, 
    setup_time_label,
    setup_footer
)

def select_server(server_url=None):
    global selected_url
    if server_url or url_entry.get():
        selected_url = server_url if server_url else url_entry.get()
        url_label.config(text=selected_url, foreground="black")  # 선택된 URL을 검은색으로 표시
    else:
        selected_url = None
        url_label.config(text="URL을 선택하거나 입력하세요.", foreground="red")  # 경고 메시지 표시

def start_sync():
    global time_offset, attempts, min_delay, max_delay, update_time_label_id

    # 기존 타이머 업데이트 중지
    if update_time_label_id is not None:
        root.after_cancel(update_time_label_id)
        update_time_label_id = None

    if selected_url:
        attempts = int(attempts_entry.get())
        min_delay = float(min_delay_entry.get())
        max_delay = float(max_delay_entry.get())

        # 동기화 버튼 비활성화
        start_button.config(state=tk.DISABLED)

        # 현재 시도 횟수 표시
        time_label.config(text=f"시도 중... 0/{attempts}")
        
        # 동기화 시도 실행
        root.after(10, execute_sync)
    else:
        url_label.config(text="먼저 URL을 선택하세요.")  # URL이 선택되지 않은 경우 메시지 표시

def execute_sync():
    global time_offset

    # 서버 동기화 및 시도 업데이트
    time_offset = sync_with_server_minimal_error(
        selected_url, 
        attempts, 
        min_delay, 
        max_delay, 
        update_label=lambda text: update_time_label_text(text)
    )
    
    # 타이머 업데이트 시작
    update_time_label()

    # 동기화 버튼 활성화
    start_button.config(state=tk.NORMAL)

def update_time_label_text(text):
    # time_label이 여전히 유효한지 확인
    if time_label.winfo_exists():
        time_label.config(text=text)
        root.update()

def update_time_label():
    global update_time_label_id
    if time_label.winfo_exists():  # time_label이 유효한지 확인
        current_time = time.time() + time_offset
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time)) + \
                         ".%03d" % (int((current_time % 1) * 1000))
        time_label.config(text=formatted_time)
        
        # 다음 업데이트 예약
        update_time_label_id = root.after(1, update_time_label)
    else:
        update_time_label_id = None

# 초기 설정
selected_url = None
time_offset = 0
update_time_label_id = None

# 메인 GUI 설정
root = create_main_window()
url_label = setup_server_url_label(root)

servers = {
    "건국": "https://sugang.konkuk.ac.kr/",
    "가천": "https://sg.gachon.ac.kr/",
    "단국": "https://sugang.dankook.ac.kr/",
    "덕성": "https://sugang.duksung.ac.kr/sugang/lecture",
    "성신": "https://sugang.sungshin.ac.kr/",
    "홍익": "https://sugang.hongik.ac.kr/"
}

setup_server_buttons(root, servers, select_server)
url_entry = setup_url_entry(root, select_server)
attempts_entry, min_delay_entry, max_delay_entry = setup_delay_and_attempts(root)
start_button = setup_sync_controls(root, start_sync)
time_label = setup_time_label(root)
footer_label = setup_footer(root)

# GUI 루프 시작
root.mainloop()
