import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://127.0.0.1:8000/api/v1/services/"
TOTAL_REQUESTS = 50
CONCURRENT_USERS = 10

def request():
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(URL, timeout=10) as response:
            response.read()
            elapsed = time.perf_counter() - start
            return response.status, elapsed
    except Exception:
        return 0, time.perf_counter() - start

start = time.perf_counter()

with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
    futures = [executor.submit(request) for _ in range(TOTAL_REQUESTS)]
    results = [f.result() for f in as_completed(futures)]

total_time = time.perf_counter() - start
successful = [t for s, t in results if s == 200]
failed = len(results) - len(successful)

print("\n=== LOAD TEST RESULT ===")
print("Endpoint: Service Search")
print("Total Requests:", TOTAL_REQUESTS)
print("Concurrent Users:", CONCURRENT_USERS)
print("Successful:", len(successful))
print("Failed:", failed)
print("Failure Rate:", round((failed / TOTAL_REQUESTS) * 100, 2), "%")
print("Average Response Time:", round(sum(t for t in successful) / len(successful) * 1000, 2), "ms")
print("Requests/Second:", round(TOTAL_REQUESTS / total_time, 2))
print("Total Test Time:", round(total_time, 2), "seconds")
