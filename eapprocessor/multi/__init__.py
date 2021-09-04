import multiprocessing

NUM_CORES = multiprocessing.cpu_count()
# MULTI_ENABLED = bool(NUM_CORES > 1)
MULTI_ENABLED = False

if MULTI_ENABLED:
    NUM_CORES = NUM_CORES - 1
