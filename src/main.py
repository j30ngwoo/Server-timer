import tkinter as tk
from tkinter import font
import time
import requests
import threading
import urllib3
import re
from constants import servers, FONT_NAME
from sync import synchronize_and_verify, get_server_time
from urllib.parse import urlparse
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
    setup_server_time_test_button,
    setup_test_result_label, 
    setup_footer
)

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

selected_url = None

def is_valid_url(url, timeout=3):
    """URL 유효성 검사"""

    if not url or url is None:
        return False
    
    url_pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// 또는 https://
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}'  # 도메인 이름
        r'(\/.*)?$'  # 경로 (선택 사항)
    )

    if not url_pattern.match(url):
        print(f"[DEBUG] 잘못된 URL 형식: {url}")
        return False

    try:
        result = requests.head(url, allow_redirects=True, timeout=timeout, verify=False)
        print(f"[DEBUG] Status code: {result.status_code}")
        return True
    except requests.exceptions.SSLError as ssl_err:
        print(f"[DEBUG] SSL 오류 발생: {ssl_err}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] URL validation error: {e}")
        return False
    except Exception as e:
        print(f"[DEBUG] 예상치 못한 오류 발생: {e}")
        return False


def shorten_url_by_pixel(url, max_pixels=350):
    """URL을 지정된 픽셀 길이에 맞춰 뒷부분을 없애고 축약"""
    label_font = font.Font(family=FONT_NAME, size=12)
    ellipsis_width = label_font.measure("...")
    if label_font.measure(url) <= max_pixels:
        return url
    while label_font.measure(url) + ellipsis_width > max_pixels:
        url = url[:-1]
    return url + "..."

def set_selected_server(server_url=None, max_len=30):
    """선택된 서버의 URL을 설정"""
    global selected_url
    selected_url = server_url if server_url else url_entry.get()
    if not selected_url.startswith(('http://', 'https://')):
        selected_url = 'https://' + selected_url
    shortened_url = shorten_url_by_pixel(selected_url)
    url_label.config(text=shortened_url, foreground="black")

def initiate_sync_process():
    """입력값을 검증하고 동기화 스레드를 시작"""
    global selected_url, time_offset, attempts, min_delay, max_delay, update_time_label_id, threshold, validation_attempts
    
    # 버튼 비활성화
    start_button.config(state=tk.DISABLED)

    # TODO: 작동 중 모든 버튼 비활성화 하기

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
        
        # 만약 도메인만 사용이 가능하다면, Full URL 대신 도메인만 사용
        parsed_url = urlparse(selected_url)
        domain = f'{parsed_url.scheme}://{parsed_url.netloc}'
        if is_valid_url(domain):
            selected_url = domain
            print(f"[DEBUG] 전체 URL 대신 도메인만 사용 가능: {domain}")

    except ValueError as e:
        url_label.config(text=str(e), foreground="red")
        print(f"[DEBUG] initiate_sync_process: {e}")
        start_button.config(state=tk.NORMAL)
        return  # 입력값이 유효하지 않으면 동기화 시작 중단
    except Exception as e:
        url_label.config(text=f"예상치 못한 오류 발생", foreground="red")
        print(f"[DEBUG] 예상치 못한 오류 발생: {e}")
        start_button.config(state=tk.NORMAL)
        return

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

def server_time_test():
    """테스트 버튼 클릭 시 호출되는 함수: 서버 시간의 초 부분을 테스트 결과 레이블에 표시"""
    def fetch_time():
        url = selected_url if selected_url else url_entry.get()
        if not url:
            root.after(0, lambda: test_result_label.config(text="URL을 선택하세요", foreground="red"))
            return
        if not url.startswith("http"):
            url = "https://" + url
        try:
            server_time = get_server_time(url)
            root.after(0, lambda: test_result_label.config(text=f"{time.strftime('%H:%M:%S', time.localtime(server_time))}.XXX", foreground="black"))
        except Exception as e:
            root.after(0, lambda: test_result_label.config(text=f"오류: {str(e)}", foreground="red"))
    threading.Thread(target=fetch_time).start()

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
test_button = setup_server_time_test_button(root, server_time_test)
test_result_label = setup_test_result_label(root)
footer_label = setup_footer(root)

# GUI 루프 시작
root.mainloop()

