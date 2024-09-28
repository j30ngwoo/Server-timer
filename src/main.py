import tkinter as tk
import time
import requests
import threading
from constants import servers
from sync import synchronize_and_verify
from ui import (
    initialize_main_window, 
    setup_server_url_label, 
    setup_server_buttons, 
    setup_url_entry, 
    setup_sync_controls,
    setup_requests_frame,
    setup_delay_frames,
    setup_validation_controls,
    setup_time_label,
    setup_footer
)

def is_valid_url(url, timeout=3):
    """URL 유효성 검사"""
    if not url:
        return False
    try:
        result = requests.head(url, allow_redirects=True, timeout=timeout)
        return result.status_code in [200, 301, 302, 405]
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] URL validation error: {e}")
        return False

def set_selected_server(server_url=None):
    """선택된 서버의 URL을 설정"""
    global selected_url
    if server_url or url_entry.get():
        selected_url = server_url if server_url else url_entry.get()
        if not selected_url.startswith(('http://', 'https://')):
            selected_url = 'https://' + selected_url
        url_label.config(text=selected_url, foreground="black")  # 선택된 URL을 검은색으로 표시

def initiate_sync_process():
    """입력값을 검증하고 동기화 스레드를 시작"""
    global time_offset, attempts, min_delay, max_delay, update_time_label_id, threshold, validation_attempts
    start_button.config(state=tk.DISABLED)

    # 입력값 검증
    try:
        attempts = int(requests_entry.get())
        min_delay = float(min_delay_entry.get())
        max_delay = float(max_delay_entry.get())
        threshold = float(threshold_entry.get())
        validation_attempts = int(validation_attempts_entry.get())

        if not is_valid_url(selected_url):
            raise ValueError("유효하지 않은 URL.")
        if attempts <= 1:
            raise ValueError("요청 횟수는 1보다 커야 함.")
        if min_delay > max_delay:
            raise ValueError("최소 딜레이가 최대 딜레이보다 클 수 없음.")
        if validation_attempts <= 0:
            raise ValueError("검증 횟수는 0보다 커야 함.")
        if not (0 < threshold < 1):
            raise ValueError("검증할 최대 오차는 0 초과 1 미만이어야 함.")
    except ValueError as e:
        url_label.config(text=str(e), foreground="red")
        start_button.config(state=tk.NORMAL)
        return  # 입력값이 유효하지 않으면 동기화 시작 중단

    # 기존 타이머 업데이트 중지
    if update_time_label_id is not None:
        root.after_cancel(update_time_label_id)
        update_time_label_id = None

    # 현재 시도 횟수 표시
    time_label.config(text=f"동기화 중... 0/{attempts}")
    
    # 동기화 시도 실행
    threading.Thread(target=perform_sync_operations).start()

def perform_sync_operations():
    """서버와 동기화를 수행하고 시간 정보를 갱신"""
    global time_offset

    # 서버 동기화 및 시도 업데이트
    time_offset = None
    time_offset = synchronize_and_verify(
        selected_url, 
        attempts, 
        min_delay, 
        max_delay,
        threshold, 
        validation_attempts,
        update_label=set_time_label_text
    )

    if time_offset is not None:
        # 타이머 업데이트 시작
        refresh_time_display()

    # 동기화 버튼 다시 활성화
    start_button.config(state=tk.NORMAL)

def set_time_label_text(text, color="black"):
    """시간 레이블의 텍스트를 업데이트"""
    if time_label.winfo_exists():
        time_label.config(text=text, foreground=color)
        root.update()

def refresh_time_display():
    """현재 시간을 실시간으로 표시"""
    global update_time_label_id
    if time_label.winfo_exists():  # time_label이 유효한지 확인
        current_time = time.time() + time_offset
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time)) + \
                         ".%03d" % (int((current_time % 1) * 1000))
        time_label.config(text=formatted_time, foreground="green")
        
        # 다음 업데이트 예약
        update_time_label_id = root.after(1, refresh_time_display)
    else:
        update_time_label_id = None


# 초기 설정
selected_url = None
update_time_label_id = None

# 메인 GUI 설정
root = initialize_main_window()
url_label = setup_server_url_label(root)

setup_server_buttons(root, servers, set_selected_server)
url_entry = setup_url_entry(root, set_selected_server)
requests_entry = setup_requests_frame(root)
min_delay_entry, max_delay_entry = setup_delay_frames(root)
threshold_entry, validation_attempts_entry = setup_validation_controls(root)
start_button = setup_sync_controls(root, initiate_sync_process)
time_label = setup_time_label(root)
footer_label = setup_footer(root)

# GUI 루프 시작
root.mainloop()
