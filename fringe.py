class Fringe():
    def __init__(self, max_size=5000):
        self.frontiers = {} # separate frontiers by heuristic score
        self.heuristics = [] # contains all non-empty heuristic scores (keys) in fringe
        self.max_heuristic = 0 # for optimization purposes
        self.size = 0 # current size of fringe
        self.max_size = max_size # for optimization (and interestingly planning speed) purposes

    def push(self, item, id, heuristic):
        if heuristic not in self.heuristics:
            self.frontiers[heuristic] = {}
            self.heuristics.append(heuristic)
            self.max_heuristic = max(self.max_heuristic, heuristic)

        self.frontiers[heuristic][id] = item
        self.size += 1

        if self.size > self.max_size:
            self.pop(heuristic=self.max_heuristic)

    def pop(self, heuristic=None, id=None):
        if heuristic == None:
            heuristic = min(self.heuristics)

        assert heuristic in self.heuristics

        self.size -= 1

        if id == None:
            # this loop will only run once because we're breaking on the first item found
            for id in self.frontiers[heuristic]:
                item = self.frontiers[heuristic].pop(id)
                break
        else:
            item = self.frontiers[heuristic].pop(id)

        if len(self.frontiers[heuristic]) == 0:
            # if frontier with this heuristic is now empty
            self.heuristics.remove(heuristic)
            if heuristic == self.max_heuristic:
                self.max_heuristic = max(self.heuristics) if self.heuristics else 0

        return *item, heuristic

    def update(self, new_item, id, new_heuristic):
        for i in self.heuristics:
            if id in self.frontiers[i]: # if id is in the fringe
                if new_heuristic < i: # if new_heuristic is better
                    self.pop(heuristic=i, id=id) # remove old copy
                    self.push(new_item, id, new_heuristic) # replace it with better copy
                break
        else: # if id is not in the fringe
            self.push(new_item, id, new_heuristic) # just add it normally
