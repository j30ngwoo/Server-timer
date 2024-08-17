import requests
import time
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
    largest_offset = -float('inf')
    last_second = None
    delay = max_delay

    for current_attempt in range(attempts):
        local_time = time.time()
        server_time = get_server_time(url)
        offset = server_time - local_time

        # 초가 변경되었는지 확인하고 오차 계산
        current_second = int(server_time) % 60
        if last_second is not None and current_second != last_second:
            print(f"[DEBUG] 시도 {current_attempt + 1}/{attempts}")
            print(f"[DEBUG] 로컬 시간: {local_time}, 서버 시간: {server_time}, 오프셋: {offset}")
            print(f"[DEBUG] 오차 계산: 현재 초: {current_second}, 이전 초: {last_second}")
            delay = min_delay
            if largest_offset < offset:
                largest_offset = offset
                print(f"[DEBUG] 새로운 최적 오프셋 발견: {largest_offset}")

            time.sleep(0.7)

        last_second = current_second

        # 시도 중... 라벨 업데이트
        if update_label:
            update_label(f"동기화 중... {current_attempt + 1}/{attempts}")

        # 지수적으로 줄어드는 딜레이 계산
        # delay = min_delay + (max_delay - min_delay) * math.exp(-3 * current_attempt / (attempts - 1))
        print(f"[DEBUG] 다음 요청 딜레이: {delay}초 (시도 {current_attempt + 1}/{attempts})")
        print("---------------------")
        time.sleep(delay)

    # 결과 로그
    print(f"[DEBUG] 최종 최적 오프셋: {largest_offset}")
    return largest_offset if largest_offset != -float('inf') else offset

def validate_best_offset(url, best_offset, threshold, update_label):
    # 첫 번째 검증: 측정한 시간이 XX.VALIDATION_THRESHOLD초일 때 전송, 응답이 XX초인지 확인
    last_second = int(time.time() + best_offset) % 60  # 이전 초값 저장
    while True:
        current_time = time.time() + best_offset
        current_second = int(current_time) % 60  # 현재 초값 계산
        if current_second != last_second and current_time % 1 >= 1 - threshold:
            break
        time.sleep(0.001)

    # 첫 번째 전송 시점의 초 및 밀리초 값 저장
    first_send_time = time.time()
    first_server_time = get_server_time(url)

    first_expected_second = int(first_send_time + best_offset) % 60
    first_expected_millisecond = int(((first_send_time + best_offset) % 1) * 1000)
    print(f"[DEBUG] 첫 번째 전송 시점: {first_expected_second}.{first_expected_millisecond:03d}초")

    first_server_second = int(first_server_time) % 60
    print(f"[DEBUG] 첫 번째 응답 시간: {first_server_second}초")
    # 첫 번째 검증 결과
    first_check = first_server_second == first_expected_second

    update_label(f"요청: {first_expected_second}.{first_expected_millisecond:03d} -> 응답: {first_server_second}", "green" if first_check else "red")
    time.sleep(0.5)

    # 두 번째 검증: XX.00초 직후에 전송, 응답이 xx초인지 확인
    last_second = int(time.time() + best_offset) % 60  # 이전 초값 저장
    while True:
        current_time = time.time() + best_offset
        current_second = int(current_time) % 60  # 현재 초값 계산
        if current_second != last_second and current_time % 1 >= 0.000:
            break
        time.sleep(0.001)

    # 두 번째 전송 시점의 초 및 밀리초 값 저장
    second_send_time = time.time()
    second_server_time = get_server_time(url)
    second_expected_second = int(second_send_time + best_offset) % 60
    second_expected_millisecond = int(((second_send_time + best_offset) % 1) * 1000)
    print(f"[DEBUG] 두 번째 전송 시점: {second_expected_second}.{second_expected_millisecond:03d}초")

    # 서버 시간 가져오기 (RTT를 고려하지 않음)
    second_server_second = int(second_server_time) % 60
    print(f"[DEBUG] 두 번째 응답 시간: {second_server_second}초")

    # 두 번째 검증 결과
    second_check = second_server_second == second_expected_second

    update_label(f"요청: {second_expected_second}.{second_expected_millisecond:03d} -> 응답: {second_server_second}", "green" if second_check else "red")
    time.sleep(0.5)
    
    
    return first_check and second_check


def sync_with_server_and_validate(url, attempts, min_delay, max_delay, threshold, validation_attempts, update_label=None):
    best_offset = sync_with_server_minimal_error(url, attempts, min_delay, max_delay, update_label)
    for valid_trial in range(1, validation_attempts + 1):
        update_label(f"검증 중...({valid_trial}/{validation_attempts})", "orange")
        if not validate_best_offset(url, best_offset, threshold, update_label):
            update_label("검증 실패: 잠시 후 재시도하세요", "red")
            return None
    return best_offset