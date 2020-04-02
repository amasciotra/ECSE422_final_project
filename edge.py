class Edge(object):
    def __init__(self, vertice_1, vertice_2, cost, reliability):
        self.vertice_1 = vertice_1
        self.vertice_2 = vertice_2
        self.cost = cost
        self.reliability = reliability

    def __repr__(self):
        return 'endpoints: {}, cost: {}, reliability: {} \n'.format(self.vertice_1 + "<->" + self.vertice_2,
                                                                    self.cost,
                                                                    self.reliability)

    def getCost(self):
        return self.cost

    def getReliability(self):
        return self.reliability

    def getVertex1(self):
        return self.vertice_1

    def getVertex2(self):
        return self.vertice_2
