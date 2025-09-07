# src/app_sync.py
import time
import requests
from datetime import datetime, timedelta

def get_server_time(url):
    """서버에 head 요청을 보내 서버 시간을 Epoch 시간(KST)으로 리턴"""
    resp = requests.head(url, allow_redirects=True, timeout=5, verify=False)
    server_date = resp.headers.get("Date")
    if not server_date:
        raise RuntimeError("서버 응답에 Date 헤더가 없습니다.")
    server_time_utc = datetime.strptime(server_date, "%a, %d %b %Y %H:%M:%S %Z")
    server_time_kst = server_time_utc + timedelta(hours=9)
    return server_time_kst.timestamp()

def find_best_sync_offset(url, attempts, min_delay, max_delay, update_label):
    """로컬과 서버 시간의 offset을 찾아 리턴"""
    largest_offset = -float("inf")
    last_second = int(get_server_time(url)) % 60
    delay = max_delay

    for current_attempt in range(attempts):
        local_time = time.time()
        server_time = get_server_time(url)

        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(server_time))
        ms = int((server_time % 1) * 1000)
        print(f"[DEBUG] 시도: {current_attempt + 1}/{attempts}")
        print(f"[DEBUG] 서버 Date: {ts}.{ms:03d}")

        offset = server_time - local_time

        current_second = int(server_time) % 60
        if current_second != last_second:
            print(f"[DEBUG] 로컬 시간: {local_time}, 서버 시간: {server_time}, 오프셋: {offset}")
            print(f"[DEBUG] 오차 계산 - 현재 초: {current_second}, 이전 초: {last_second}")
            delay = min_delay
            if largest_offset < offset:
                largest_offset = offset
                print(f"[DEBUG] 새로운 최적 오프셋 발견: {largest_offset}")
            time.sleep(0.7)

        last_second = current_second

        if update_label:
            update_label(f"동기화 중... {current_attempt + 1}/{attempts}")

        print(f"[DEBUG] 다음 요청 딜레이: {delay}초")
        print("---------------------")
        time.sleep(delay)

    print(f"[DEBUG] 최종 최적 오프셋: {largest_offset}")
    return largest_offset

def verify_sync_accuracy(url, best_offset, threshold, update_label):
    """측정한 offset에 맞춰 요청을 전송하여 offset이 유효한지 확인"""
    last_second = int(time.time() + best_offset) % 60
    while True:
        current_time = time.time() + best_offset
        current_second = int(current_time) % 60
        if current_second != last_second and current_time % 1 >= 1 - threshold:
            break
        time.sleep(0.001)

    first_send_time = time.time()
    first_server_time = get_server_time(url)
    first_expected_second = int(first_send_time + best_offset) % 60
    first_expected_millisecond = int(((first_send_time + best_offset) % 1) * 1000)
    print(f"[DEBUG] 첫 번째 로컬 전송 시점: {first_expected_second}.{first_expected_millisecond:03d}초")

    first_server_second = int(first_server_time) % 60
    print(f"[DEBUG] 첫 번째 서버 응답 시간: {first_server_second}초")

    first_check = first_server_second == first_expected_second
    update_label(f"요청: {first_expected_second}.{first_expected_millisecond:03d} -> 응답: {first_server_second}",
                "green" if first_check else "red")
    time.sleep(1)

    last_second = int(time.time() + best_offset) % 60
    while True:
        current_time = time.time() + best_offset
        current_second = int(current_time) % 60
        if current_second != last_second and current_time % 1 >= 0.000:
            break
        time.sleep(0.001)

    second_send_time = time.time()
    second_server_time = get_server_time(url)
    second_expected_second = int(second_send_time + best_offset) % 60
    second_expected_millisecond = int(((second_send_time + best_offset) % 1) * 1000)
    print(f"[DEBUG] 두 번째 로컬 전송 시점: {second_expected_second}.{second_expected_millisecond:03d}초")

    second_server_second = int(second_server_time) % 60
    print(f"[DEBUG] 두 번째 서버 응답 시간: {second_server_second}초")

    second_check = second_server_second == second_expected_second
    update_label(f"요청: {second_expected_second}.{second_expected_millisecond:03d} -> 응답: {second_server_second}",
                "green" if second_check else "red")
    time.sleep(1)

    return first_check and second_check

def synchronize_and_verify(url, attempts, min_delay, max_delay, threshold, validation_attempts, update_label):
    """최적 offset을 찾고 검증"""
    best_offset = find_best_sync_offset(url, attempts, min_delay, max_delay, update_label)
    if best_offset == -float('inf'):
        print("[DEBUG] 동기화 불가능: offset이 갱신되지 않음")
        update_label("동기화가 불가능한 서버입니다.", "red")
        return None

    for valid_trial in range(1, validation_attempts + 1):
        update_label(f"검증 중...({valid_trial}/{validation_attempts})", "orange")
        if not verify_sync_accuracy(url, best_offset, threshold, update_label):
            update_label("검증 실패: 잠시 후 재시도하세요", "red")
            return None

    return best_offset
