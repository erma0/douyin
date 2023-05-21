import json
import time

import ujson


def benchmark(name, dump, load):
    start = time.time()
    for i in range(1000):
        with open('1.json', 'r', encoding='utf-8') as f:
            m = load(f)
        with open('1.json', 'w', encoding='utf-8') as f:
            dump(m, f, ensure_ascii=False)
    print(name, time.time() - start)


if __name__ == "__main__":

    benchmark("Python", json.dump, json.load)
    benchmark("ujson", ujson.dump, ujson.load)
