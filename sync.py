import requests
import time
import random
import urllib3
from datetime import datetime, timedelta

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_server_time(url):
    response = requests.head(url, verify=False)  # SSL 검증 비활성화
    server_date = response.headers['Date']
    # 서버 시간을 UTC로 파싱
    server_time_utc = datetime.strptime(server_date, "%a, %d %b %Y %H:%M:%S %Z")
    # UTC 시간을 KST로 변환 (9시간 더하기)
    server_time_kst = server_time_utc + timedelta(hours=9)
    # Epoch 시간으로 변환
    server_epoch = server_time_kst.timestamp()
    return server_epoch

def sync_with_server_minimal_error(url, attempts=20, min_delay=0.05, max_delay=0.15, update_label=None):
    best_offset = None
    smallest_error = float('inf')
    last_second = None

    for current_attempt in range(attempts):
        start_local = time.time()
        server_time = get_server_time(url)
        end_local = time.time()

        # 왕복 시간 계산 및 지연 보정
        round_trip_time = (end_local - start_local) / 2
        adjusted_server_time = server_time + round_trip_time
        local_time = (start_local + end_local) / 2

        # 로컬 시간과 조정된 서버 시간 간의 오프셋 계산
        offset = adjusted_server_time - local_time

        # 초가 변경되었는지 확인하고 오차 계산
        current_second = int(server_time) % 60
        if last_second is not None and current_second != last_second:
            error = abs(adjusted_server_time % 1)  # closer to .000 is better
            if error < smallest_error:
                smallest_error = error
                best_offset = offset

        last_second = current_second

        # 시도 중... 라벨 업데이트
        if update_label:
            update_label(f"시도 중... {current_attempt + 1}/{attempts}")

        # 최소 및 최대 딜레이 사이의 랜덤 지연 사용
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    return best_offset if best_offset is not None else offset
