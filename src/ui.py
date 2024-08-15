import tkinter as tk
from tkinter import ttk
from constants import SYNC_ATTEMPTS, MAX_DELAY, MIN_DELAY, VALIDATION_ATTEMPTS, VALIDATION_THRESHOLD

def create_main_window():
    root = tk.Tk()
    root.title("Server Time Sync")
    
    # 창 크기를 위젯에 맞게 자동 조정
    root.grid_propagate(True)
    root.pack_propagate(True)
    
    # 창 크기 변경 불가 설정
    root.resizable(False, False)

    # ttk 스타일 적용
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10)
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("SelectedURL.TLabel", font=("Helvetica", 14, "bold"))

    return root

def setup_server_url_label(root):
    # 선택된 서버 URL만 표시
    url_label = ttk.Label(root, text="서버 URL을 선택하세요", style="SelectedURL.TLabel", anchor="center")
    url_label.grid(row=0, column=0, columnspan=4, pady=10)  # 여백 추가
    return url_label

def setup_server_buttons(root, servers, select_server):
    row = 1
    col = 0
    for name, url in sorted(servers.items()):
        button = ttk.Button(root, text=name, command=lambda u=url: select_server(u), width=15)
        button.grid(row=row, column=col, pady=5)  # 각 버튼에 위아래 여백 추가
        col += 1
        if col > 2:
            col = 0
            row += 1

def setup_url_entry(root, select_server):
    # "기타 서버 설정" 버튼을 0열에 배치
    set_url_button = ttk.Button(root, text="URL 직접 입력 ▶", command=lambda: select_server(url_entry.get()), width=15)
    set_url_button.grid(row=4, column=0, pady=10)  # 위아래 여백 추가

    # 엔트리를 1~2열에 배치
    url_entry = ttk.Entry(root, width=43)
    url_entry.grid(row=4, column=1, columnspan=2, pady=10)

    return url_entry

def setup_requests_frame(root):
    # 시도 횟수 입력 (첫 번째 줄)
    requests_frame = ttk.Frame(root)
    requests_frame.grid(row=5, column=0, columnspan=3, pady=10)  # 3칸 차지

    requests_label = ttk.Label(requests_frame, text="동기화당 요청 횟수:")
    requests_label.grid(row=0, column=0, sticky="e")
    attempts_entry = ttk.Entry(requests_frame, width=10)
    attempts_entry.insert(0, SYNC_ATTEMPTS)
    attempts_entry.grid(row=0, column=1, sticky="w")

    # 가운데 정렬을 위해 빈 셀 추가
    requests_frame.grid_columnconfigure(0, weight=1)
    requests_frame.grid_columnconfigure(2, weight=1)

    return attempts_entry

def setup_delay_frames(root):
    # 최소 딜레이 입력 (두 번째 줄)
    min_delay_frame = ttk.Frame(root)
    min_delay_frame.grid(row=6, column=0, columnspan=3, pady=10)  # 3칸 차지

    min_delay_label = ttk.Label(min_delay_frame, text="요청 간 최소 딜레이(s):")
    min_delay_label.grid(row=0, column=0, sticky="e")
    min_delay_entry = ttk.Entry(min_delay_frame, width=10)
    min_delay_entry.insert(0, MIN_DELAY)
    min_delay_entry.grid(row=0, column=1, sticky="w")

    # 가운데 정렬을 위해 빈 셀 추가
    min_delay_frame.grid_columnconfigure(0, weight=1)
    min_delay_frame.grid_columnconfigure(2, weight=1)

    # 최대 딜레이 입력 (세 번째 줄)
    max_delay_frame = ttk.Frame(root)
    max_delay_frame.grid(row=7, column=0, columnspan=3, pady=10)  # 3칸 차지

    max_delay_label = ttk.Label(max_delay_frame, text="요청 간 최대 딜레이(s):")
    max_delay_label.grid(row=0, column=0, sticky="e")
    max_delay_entry = ttk.Entry(max_delay_frame, width=10)
    max_delay_entry.insert(0, MAX_DELAY)
    max_delay_entry.grid(row=0, column=1, sticky="w")

    # 가운데 정렬을 위해 빈 셀 추가
    max_delay_frame.grid_columnconfigure(0, weight=1)
    max_delay_frame.grid_columnconfigure(2, weight=1)

    return min_delay_entry, max_delay_entry

def setup_validation_controls(root):
    # 검증 횟수 입력 (네 번째 줄)
    attempts_frame = ttk.Frame(root)
    attempts_frame.grid(row=8, column=0, columnspan=3, pady=10)  # 3칸 차지

    attempts_label = ttk.Label(attempts_frame, text="검증 횟수:")
    attempts_label.grid(row=0, column=0, sticky="e")
    attempts_entry = ttk.Entry(attempts_frame, width=10)
    attempts_entry.insert(0, VALIDATION_ATTEMPTS)
    attempts_entry.grid(row=0, column=1, sticky="w")

    # 가운데 정렬을 위해 빈 셀 추가
    attempts_frame.grid_columnconfigure(0, weight=1)
    attempts_frame.grid_columnconfigure(2, weight=1)

    # 검증 기준 시간 입력 (다섯 번째 줄)
    validation_frame = ttk.Frame(root)
    validation_frame.grid(row=9, column=0, columnspan=3, pady=10)  # 3칸 차지

    threshold_label = ttk.Label(validation_frame, text="검증할 최소 오차(s):")
    threshold_label.grid(row=0, column=0, sticky="e")
    threshold_entry = ttk.Entry(validation_frame, width=10)
    threshold_entry.insert(0, VALIDATION_THRESHOLD)
    threshold_entry.grid(row=0, column=1, sticky="w")

    # 가운데 정렬을 위해 빈 셀 추가
    validation_frame.grid_columnconfigure(0, weight=1)
    validation_frame.grid_columnconfigure(2, weight=1)

    return threshold_entry, attempts_entry

def setup_sync_controls(root, start_sync):
    start_button = ttk.Button(root, text="서버 시간 동기화 시작", command=start_sync, width=25)
    start_button.grid(row=10, column=0, columnspan=4, pady=10)  # 위아래 여백 추가
    return start_button

def setup_time_label(root):
    time_label = ttk.Label(root, text="", font=("Helvetica", 24))
    time_label.grid(row=11, column=0, columnspan=4, pady=10)  # 타이머가 더 위로 올라오고, 여백 추가
    return time_label

def setup_footer(root):
    footer_label = ttk.Label(root, text="by J30ngwoo", font=("Helvetica", 8, "bold"), anchor="e", foreground="#4682B4")
    footer_label.grid(row=12, column=2, sticky="e")  # 오른쪽 하단에 위치
    return footer_label