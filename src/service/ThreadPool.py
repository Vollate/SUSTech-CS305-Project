import threading
import queue


class ThreadPool:
    def __init__(self, num_threads):
        self.tasks = queue.Queue()
        self.threads = []
        self.num_threads = num_threads
        for _ in range(num_threads):
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.threads.append(thread)

    def worker(self):
        while True:
            func, args, kwargs = self.tasks.get()
            if func is None:
                break
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Exception in thread: {e}")
            finally:
                self.tasks.task_done()

    def submit(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))

    def stop(self):
        for _ in self.threads:
            self.submit(None, None, None)
        for thread in self.threads:
            thread.join()
