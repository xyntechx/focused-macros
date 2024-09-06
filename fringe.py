class Fringe():
    def __init__(self):
        self.frontiers = {} # separate frontiers by heuristic score
        self.heuristics = []

    def push(self, item, id, heuristic):
        if heuristic not in self.frontiers:
            self.frontiers[heuristic] = {}
            self.heuristics.append(heuristic)
        self.frontiers[heuristic][id] = item

    def pop(self, heuristic=None):
        if heuristic in self.frontiers and self.frontiers[heuristic]:
            for id in self.frontiers[heuristic]:
                return *self.frontiers[heuristic].pop(id), heuristic

        heuristics = self.heuristics[:]
        min_heuristic = min(heuristics)
        while heuristics:
            if self.frontiers[min_heuristic]:
                for id in self.frontiers[min_heuristic]:
                    return *self.frontiers[min_heuristic].pop(id), min_heuristic
            heuristics.remove(min_heuristic)
            min_heuristic = min(heuristics)

        return None

    def update(self, new_item, id, new_heuristic):
        for i in self.heuristics:
            if id in self.frontiers[i]:
                if new_heuristic < i:
                    self.frontiers[i].pop(id)
                    self.push(new_item, id, new_heuristic)
                break
        else:
            self.push(new_item, id, new_heuristic)
