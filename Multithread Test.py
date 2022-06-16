from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

x = [1, 2, 3, 4]


def multi_predict(inputData, threadFunction):
    pool = Pool(cpu_count())
    results = pool.map(threadFunction, inputData)
    pool.close()
    pool.join()
    return results


def add_one(x):
    return x + 1


print(multi_predict(x, add_one))
