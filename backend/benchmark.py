import matplotlib.pyplot as plt
import numpy as np
import time
from des import DES
from memory_profiler import memory_usage


BYTE = 8
KILOBYTE = 1000 * BYTE
MEGABYTE = 1_000_000 * BYTE


def benchmark_method(des, method, pad_message=False):
    if pad_message:
        des.mode.pad_text()

    start_mem = memory_usage(max_usage=True)
    start_time = time.time()
    method()
    end_time = time.time()
    end_mem = memory_usage(max_usage=True)

    if pad_message:
        des.mode.unpad_text()

    time_elapsed = end_time - start_time
    memory_used = end_mem - start_mem

    return time_elapsed, memory_used

def benchmark():
    plaintext = np.ones((MEGABYTE,), dtype=np.uint8)
    des = DES(plaintext)
    
    des.mode.pad_text()
    results = {
        "ECB": benchmark_method(des, des.mode.ecb, True),
        "CBC": benchmark_method(des, des.mode.cbc, True),
        "CFB": benchmark_method(des, des.mode.cfb),
        "OFB": benchmark_method(des, des.mode.ofb),
        "CTR": benchmark_method(des, des.mode.ctr)
    }

    return results


if __name__ == "__main__":
    benchmark_results = benchmark()

    methods = list(benchmark_results.keys())
    times = [result[0] for result in benchmark_results.values()]
    memory = [result[1] for result in benchmark_results.values()]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    ax1.bar(methods, times, color="blue")
    ax1.set_title("DES Encryption Time Benchmarks")
    ax1.set_xlabel("Encryption Method")
    ax1.set_ylabel("Time (seconds)")

    ax2.bar(methods, memory, color="green")
    ax2.set_title("DES Encryption Memory Usage")
    ax2.set_xlabel("Encryption Method")
    ax2.set_ylabel("Memory Usage (MB)")

    plt.tight_layout()
    plt.show()

