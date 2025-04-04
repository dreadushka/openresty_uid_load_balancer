import requests
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import argparse
from collections import defaultdict

# Конфигурация
URL = "http://localhost:8080"
TEST_UIDS = ["user123", "special_uid", "test_user"]
RANDOM_UIDS = 100000
SPECIAL_PERCENT = 20
REQUESTS = 10000
THREADS = 50
TIMEOUT = 10  # Увеличен таймаут до 10 секунд

def generate_uids():
    special_count = REQUESTS * SPECIAL_PERCENT // 100
    normal_count = REQUESTS - special_count
    
    special = []
    while len(special) < special_count:
        special += TEST_UIDS
    special = special[:special_count]
    
    random_uids = [f"random_{i}" for i in range(RANDOM_UIDS)]
    normal = random.choices(random_uids, k=normal_count)
    
    all_uids = special + normal
    random.shuffle(all_uids)
    return all_uids

# Метрики
stats = defaultdict(int)
latencies = []
lock = threading.Lock()
start_time = time.time()

def make_request(uid):
    try:
        req_start = time.time()
        response = requests.get(f"{URL}?uid={uid}", timeout=TIMEOUT)
        latency = time.time() - req_start
        
        with lock:
            stats['total'] += 1
            latencies.append(latency)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    instance = str(data.get('instance_number', 'unknown'))
                    stats[instance] += 1
                    stats['success'] += 1
                except Exception as e:
                    stats['parse_errors'] += 1
                    print(f"Parse error: {str(e)}")
            else:
                stats['http_errors'] += 1
                
    except Exception as e:
        with lock:
            stats['connection_errors'] += 1
            stats['total'] += 1

def monitor_progress():
    while True:
        elapsed = time.time() - start_time
        if elapsed < 1:
            continue
        current_rps = stats['total'] / elapsed
        print(f"\rRequests: {stats['total']}/{REQUESTS} | "
              f"RPS: {current_rps:.2f} | "
              f"App1: {stats.get('1', 0)} | "
              f"App2: {stats.get('2', 0)} | "
              f"Errors: {stats.get('http_errors', 0)}/{stats.get('parse_errors', 0)}/{stats.get('connection_errors', 0)}", 
              end="")
        time.sleep(0.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default=URL)
    parser.add_argument('--requests', type=int, default=REQUESTS)
    parser.add_argument('--threads', type=int, default=THREADS)
    parser.add_argument('--special', type=int, default=SPECIAL_PERCENT)
    args = parser.parse_args()

    URL = args.url
    REQUESTS = args.requests
    THREADS = args.threads
    SPECIAL_PERCENT = args.special

    uids = generate_uids()
    if len(uids) != REQUESTS:
        raise ValueError(f"Ошибка генерации UID: {len(uids)} != {REQUESTS}")

    threading.Thread(target=monitor_progress, daemon=True).start()

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(make_request, uid) for uid in uids]
        for future in futures:
            future.result()

    total_time = time.time() - start_time
    rps = REQUESTS / total_time if total_time > 0 else 0
    error_rate = (stats.get('http_errors', 0) + 
                 stats.get('parse_errors', 0) + 
                 stats.get('connection_errors', 0)) / REQUESTS * 100 if REQUESTS else 0

    print("\n\n--- Результаты тестирования ---")
    print(f"Время теста: {total_time:.2f} сек")
    print(f"RPS: {rps:.2f} запросов/сек")
    print(f"Средняя задержка: {sum(latencies)/len(latencies)*1000:.2f} мс")
    print(f"99-й перцентиль: {sorted(latencies)[int(len(latencies)*0.99)]*1000:.2f} мс")
    print(f"Ошибки: {error_rate:.2f}%")
    print(f"Запросы на app1: {stats.get('1', 0)}")
    print(f"Запросы на app2: {stats.get('2', 0)}")
    print(f"HTTP-ошибки: {stats.get('http_errors', 0)}")
    print(f"Ошибки парсинга: {stats.get('parse_errors', 0)}")
    print(f"Сетевые ошибки: {stats.get('connection_errors', 0)}")
