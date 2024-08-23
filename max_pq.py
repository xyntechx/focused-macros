from queue import PriorityQueue


class MaxPQ(PriorityQueue):
    def put(self, item):
        priority, data = item
        PriorityQueue.put(self, (-priority, data))

    def get(self, *args, **kwargs):
        priority, data = PriorityQueue.get(self, *args, **kwargs)
        return -priority, data
