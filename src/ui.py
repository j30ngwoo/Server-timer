import webbrowser
import tkinter as tk
from tkinter import ttk
from constants import (
    SYNC_ATTEMPTS,
    MAX_DELAY,
    MIN_DELAY,
    VALIDATION_ATTEMPTS,
    VALIDATION_THRESHOLD,
    FONT_NAME
)

def initialize_main_window():
    """메인 창을 생성하고 기본 설정을 적용하는 함수"""
    root = tk.Tk()
    root.title("Server Time Sync")

    # 창 크기 변경 불가 설정
    root.resizable(False, False)

    # ttk 스타일 적용
    style = ttk.Style()
    style.configure("TButton", font=(FONT_NAME, 12), padding=10)
    style.configure("TLabel", font=(FONT_NAME, 12))
    style.configure("SelectedURL.TLabel", font=(FONT_NAME, 14, "bold"))

    return root

def setup_label_and_entry(root, label_text, default_value, row, width=10):
    """레이블과 엔트리를 설정하고 그리드에 배치하는 함수"""
    frame = ttk.Frame(root)
    frame.grid(row=row, column=0, columnspan=3, pady=10)

    label = ttk.Label(frame, text=label_text)
    label.grid(row=0, column=0, sticky="e")

    entry = ttk.Entry(frame, width=width)
    entry.insert(0, default_value)
    entry.grid(row=0, column=1, sticky="w")

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(2, weight=1)

    return entry

def setup_server_url_label(root):
    """서버 URL을 표시할 레이블을 설정하는 함수"""
    url_label = ttk.Label(root, text="서버 URL을 선택하세요", style="SelectedURL.TLabel", anchor="center")
    url_label.grid(row=0, column=0, columnspan=4, pady=10)
    return url_label

def setup_server_buttons(root, servers, select_server):
    """서버 선택 버튼을 생성하고 그리드에 배치하는 함수"""
    row = 1
    col = 0
    for name, url in sorted(servers.items()):
        button = ttk.Button(root, text=name, command=lambda u=url: select_server(u), width=15)
        button.grid(row=row, column=col, pady=5)
        col += 1
        if col > 2:
            col = 0
            row += 1

def setup_url_entry(root, select_server):
    """URL 직접 입력 필드와 버튼을 설정하는 함수"""
    set_url_button = ttk.Button(root, text="URL 직접 입력 ▶", command=lambda: select_server(url_entry.get()), width=15)
    set_url_button.grid(row=4, column=0, pady=10)

    url_entry = ttk.Entry(root, width=43)
    url_entry.grid(row=4, column=1, columnspan=2, pady=10)

    return url_entry

def setup_requests_frame(root):
    """동기화당 요청 횟수 입력 필드를 설정하는 함수"""
    return setup_label_and_entry(root, "동기화당 요청 횟수:", SYNC_ATTEMPTS, row=5)

def setup_delay_frames(root):
    """최소 및 최대 딜레이 입력 필드를 설정하는 함수"""
    min_delay_entry = setup_label_and_entry(root, "요청 간 최소 딜레이(s):", MIN_DELAY, row=6)
    max_delay_entry = setup_label_and_entry(root, "요청 간 최대 딜레이(s):", MAX_DELAY, row=7)
    return min_delay_entry, max_delay_entry

def setup_validation_controls(root):
    """검증 횟수 및 검증 기준 시간 입력 필드를 설정하는 함수"""
    validation_attempts_entry = setup_label_and_entry(root, "검증 횟수:", VALIDATION_ATTEMPTS, row=8)
    threshold_entry = setup_label_and_entry(root, "검증할 최대 오차(s):", VALIDATION_THRESHOLD, row=9)
    return threshold_entry, validation_attempts_entry

def setup_sync_controls(root, start_sync):
    """동기화 시작 버튼을 설정하는 함수"""
    start_button = ttk.Button(root, text="서버 시간 동기화 시작", command=start_sync, width=25)
    start_button.grid(row=10, column=0, columnspan=4, pady=10)
    return start_button

def setup_time_label(root):
    """타이머 레이블을 설정하는 함수"""
    time_label = ttk.Label(root, text="", font=(FONT_NAME, 24))
    time_label.grid(row=11, column=0, columnspan=4, pady=10)
    return time_label

def setup_server_time_test_button(root, test_function):
    """서버 시간 테스트 버튼을 생성하고 그리드에 배치하는 함수"""
    test_button = ttk.Button(root, text="현재 서버 시간 ▶", command=test_function, width=15)
    test_button.grid(row=12, column=0, pady=10)
    return test_button

def setup_test_result_label(root):
    """서버 시간 테스트 결과를 표시하는 레이블 생성 함수"""
    test_result_label = ttk.Label(root, text="", font=(FONT_NAME, 24))
    test_result_label.grid(row=12, column=1, columnspan=3, pady=10)
    return test_result_label

def open_link(event):
    webbrowser.open_new("https://github.com/j30ngwoo")

def on_enter(event):
    event.widget.config(foreground="light green")

def on_leave(event):
    event.widget.config(foreground="#4682B4")

def setup_footer(root):
    """하단에 클릭 가능한 푸터 레이블을 설정하는 함수"""
    footer_label = ttk.Label(root, text="by J30ngwoo", font=(FONT_NAME, 10, "bold"), anchor="e", foreground="#4682B4", cursor="hand2")
    footer_label.grid(row=13, column=2, sticky="e")

    # 레이블 클릭 시 링크 열기
    footer_label.bind("<Button-1>", open_link)

    # 마우스 이벤트 바인딩
    footer_label.bind("<Enter>", on_enter)  # 마우스를 올리면 색 변경
    footer_label.bind("<Leave>", on_leave)  # 마우스를 내리면 원래 색으로

    return footer_label