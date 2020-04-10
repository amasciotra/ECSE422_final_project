# The input file is in the format:
# Number of cities: A B C D ...(N cities)
# Cost/Reliability matrix: A-B,A-C,A-D...B-C,B-D...C-D....(N(N-1)/2)
import edge_generator
from edge import Edge
import itertools


def find(parent, i):
    # find root
    root = i
    while root != parent[i]:
        root = parent[i]

    # path compress
    while i != root:
        nextNode = parent[i]
        parent[i] = root
        i = nextNode
    return root


def isConnected(parent, vertex1, vertex2):
    rootNode1 = find(parent, vertex1)
    rootNode2 = find(parent, vertex2)
    if rootNode1 == rootNode2:
        return True
    else:
        return False


def union(parent, rank, vertex1, vertex2):
    # union by ranking (which root tree has more elements, stored in rank list
    vertex1Root = find(parent, vertex1)
    vertex2Root = find(parent, vertex2)

    if rank[vertex1Root] < rank[vertex2Root]:
        parent[vertex1Root] = vertex2Root
    elif rank[vertex1Root] > rank[vertex2Root]:
        parent[vertex2Root] = vertex1Root
    else:
        parent[vertex2Root] = vertex1Root
        rank[vertex1Root] += 1


def doKruskalMST(city_list, edge_list, doMax):
    # this will do either a min or max spanning tree, order lists in either increasing cost or decreasing reliabilit

    mst_graph = []  # store list of edges
    total_reliability = 1  # to store totalCost of spanning tree or totalReliability of spanning tree
    total_cost = 0
    i = 0  # index in sorted edge_list
    k = 0  # index in mst_graph

    sorted_list = []
    if doMax == 1:
        sorted_list = sorted(edge_list, key=lambda edge: edge.getReliability(), reverse=True)
    else:
        sorted_list = sorted(edge_list, key=lambda edge: edge.getCost(), reverse=False)

    parent = []
    rank = []

    # create subsets
    for j in range(len(city_list)):
        # convert Letter to number
        parent.append(j)
        rank.append(0)

    # make tree with n-1 edges
    while k < (len(city_list) - 1):
        temp_edge = sorted_list[i]  # same temporary Edge object
        weight = 0
        if doMax == 1:
            weight = temp_edge.getReliability()
        else:
            weight = temp_edge.getCost()
        i += 1

        # find parent node of each vertex
        vertex1 = ord(temp_edge.getVertex1()) - 65  # convert back to digit
        vertex2 = ord(temp_edge.getVertex2()) - 65  # convert back to digit

        # if rootNodes are not the same, means they are not yet connected in graph
        if not isConnected(parent, vertex1, vertex2):
            k += 1  # increment index of result graph to know when we are at n-1 nodes
            mst_graph.append(temp_edge)
            union(parent, rank, vertex1, vertex2)
        # if they have the same root, node already connected in tree, find another node

    # calculate totalReliability and totalcost of MST

    for edge in mst_graph:
        total_reliability *= edge.getReliability()
        total_cost += edge.getCost()

    return mst_graph, total_reliability, total_cost


def calculateCost(edge_list):
    total_cost = 0
    for edge in edge_list:
        total_cost += edge.getCost()
    return total_cost


def isGraphConnected(graph, city_list):
    visited = []  # will store visited nodes
    ordered_graph = sorted(graph, key=lambda edge: edge.getVertex1())
    first_vertex = ordered_graph[0].getVertex1()
    # start at first vertex, this one is therefore visited
    visited.append(first_vertex)

    for edge in ordered_graph:
        current = edge.getVertex1()
        neighbor = edge.getVertex2()
        # we have an undirected graph, so can either go from current to neighbor or from neighbor to current
        if current in visited:
            if neighbor not in visited:
                visited.append(neighbor)
        if neighbor in visited:
            if current not in visited:
                visited.append(current)

    if len(visited) == len(city_list):
        return True
    else:
        return False


def calculateReliability(graph, city_list):
    total_reliability = 0
    # use itertools to generatre all possible combinations of a working connected graph depending on number of edges
    all_possible_graph_combinations = list(itertools.product([0, 1], repeat=len(graph)))

    # need to remove all possibilities where there is less than (n-1) edges as imposisble to be all connected
    parsed_possible_graph_combinations = []
    for combination in all_possible_graph_combinations:
        if sum(combination) >= (len(city_list) - 1):
            parsed_possible_graph_combinations.append(combination)

    # now need to check if the combinations are valid (ie form an actual graph where all connected)
    for combination in parsed_possible_graph_combinations:
        test_graph = []
        # create a subgraph of possible nodes, converting combination tuple into list of edges
        for i in range(len(combination)):
            if combination[i] == 1:
                test_graph.append(graph[i])

        # now need to check if the testGraph is valid
        if isGraphConnected(test_graph, city_list):
            partial_reliability = 1
            for i in range(len(combination)):
                if combination[i] == 1:
                    partial_reliability *= graph[i].getReliability()
                else:
                    partial_reliability *= (1 - graph[i].getReliability())

            total_reliability += partial_reliability

    return total_reliability


def makeReliabilityTreeGivenReliabilityGoal(city_list, edge_list, reliability_goal):
    # using Kruskal algorithm to find max reliability tree
    #
    mst_graph, mst_reliability, mst_cost = doKruskalMST(city_list, edge_list, 1)

    # if reliability of mst meets the goal given, return
    if mst_reliability >= float(reliability_goal):
        return mst_graph, mst_reliability, mst_cost

    # check possible remaining edges left (n(n-1)/2 - (n-1) = (n-1)(n-2) / 2
    remaining_edge_list = []
    for edge in edge_list:
        if not edge in mst_graph:
            remaining_edge_list.append(edge)

    remaining_edge_list.sort(key=lambda edge: edge.getReliability(), reverse=True)

    graph = mst_graph.copy()
    total_cost = 0
    total_reliability = 0

    while True:
        highest_reliability_edge = Edge
        highest_reliability = 0
        for edge in remaining_edge_list:
            temp_reliability = 0
            temp_graph = graph.copy()
            temp_graph.append(edge)
            temp_reliability = calculateReliability(temp_graph, city_list)
            if temp_reliability > highest_reliability:
                highest_reliability = temp_reliability
                highest_reliability_edge = edge

        graph.append(highest_reliability_edge)
        remaining_edge_list.remove(highest_reliability_edge)
        if highest_reliability > float(reliability_goal):
            total_cost = calculateCost(graph)
            total_reliability = highest_reliability
            return graph, total_reliability, total_cost

        if len(remaining_edge_list) == 0:
            graph = None
            total_reliability = 0
            total_cost = 0
            return graph, total_reliability, total_cost


def maximizeReliabilitySubjectToCost(city_list, edge_list, cost_constraint):
    mst_graph_cost, mst_reliability_cost, mst_cost_cost = doKruskalMST(city_list, edge_list, 0)

    mst_graph_reliability, mst_reliability_reliability, mst_cost_reliability = doKruskalMST(city_list, edge_list, 1)

    if mst_cost_reliability <= mst_cost_cost:  # we mine as well start with the MSTReliability tree to maximize afterwards
        mst_graph = mst_graph_reliability
        mst_reliability = mst_reliability_reliability
        mst_cost = mst_reliability_cost
    else:  # start with minimum cost spanning tree
        mst_graph = mst_graph_cost
        mst_reliability = mst_reliability_cost
        mst_cost = mst_cost_cost

    graph = mst_graph.copy()
    total_cost = 0
    total_reliability = 0

    if mst_cost <= float(cost_constraint):
        # we have a valid solution, incase we cannot optimize
        total_cost = mst_cost
        total_reliability = mst_reliability
    else:
        graph = None
        return graph, total_reliability, total_cost

        # check possible remaining edges left (n(n-1)/2 - (n-1) = (n-1)(n-2) / 2
    remaining_edge_list = []
    for edge in edge_list:
        if not edge in mst_graph:
            remaining_edge_list.append(edge)

    remaining_edge_list.sort(key=lambda edge: edge.getCost(), reverse=False)

    highest_possible_cost = 0
    for edge in edge_list:
        highest_possible_cost += edge.getCost()

    while True:
        highest_reliability_edge = Edge
        highest_reliability = 0
        lowest_cost = highest_possible_cost  # set to highest possible
        flag = 0  # flag to check if there was one more possible solution by adding another edge coming in under cost
        for edge in remaining_edge_list:
            temp_reliability = 0
            temp_cost = 0
            temp_graph = graph.copy()
            temp_graph.append(edge)
            temp_reliability = calculateReliability(temp_graph, city_list)
            temp_cost = calculateCost(temp_graph)
            if temp_cost <= float(cost_constraint) and temp_cost <= lowest_cost:
                if temp_reliability > highest_reliability:
                    flag = 1
                    highest_reliability = temp_reliability
                    highest_reliability_edge = edge
                    lowest_cost = temp_cost
        if flag == 1:
            graph.append(highest_reliability_edge)
            remaining_edge_list.remove(highest_reliability_edge)
        else:
            total_cost = calculateCost(graph)
            total_reliability = calculateReliability(graph, city_list)
            return graph, total_reliability, total_cost


def UI():
    file_path = input("Please set input file path (eg:input.txt): ")
    prompt_reliability_goal = input("Please enter reliability goal between 0 and 1 for part A, leave empty and "
                                    "press enter to skip this part: ")
    if prompt_reliability_goal == "":
        print("NO RELIABILITY GIVEN, CANNOT DO PART A")
        reliability_goal = None
    else:
        if prompt_reliability_goal.replace('.', '', 1).isdigit():
            reliability_goal = float(prompt_reliability_goal)
            if reliability_goal > 1:
                while True:
                    prompt_reliability_goal = input("Invalid Reliability, enter a new one: ")
                    if prompt_reliability_goal.replace('.', '', 1).isdigit():
                        reliability_goal = float(prompt_reliability_goal)
                        if reliability_goal <= 1:
                            break
        else:
            while True:
                prompt_reliability_goal = input("Invalid Reliability, enter a new one: ")
                if prompt_reliability_goal.replace('.', '', 1).isdigit():
                    reliability_goal = float(prompt_reliability_goal)
                    if reliability_goal <= 1:
                        break

    prompt_cost_goal = input("Please enter Cost constraint for part B, leave empty and "
                             "press enter to skip this part: ")
    if prompt_cost_goal == "":
        print("NO COST GIVEN, CANNOT DO PART B")
        cost_constraint = None
    else:
        if prompt_cost_goal.isdigit():
            cost_constraint = prompt_cost_goal
        else:
            while True:
                prompt_cost_goal = input("Invalid Cost, enter a new one: ")
                if prompt_cost_goal.isdigit():
                    cost_constraint = prompt_cost_goal
                    break

    return file_path, reliability_goal, cost_constraint


# def PrintToFile(filename, graph, reliability, cost):
#     put your stuff in here
#
#
#
#
#

def main():
    graph = []
    total_cost = 0
    total_reliability = 0

    file_path, reliability_goal, cost_constraint = UI()

    city_list, edge_list = edge_generator.generate(file_path)

    #
    if not reliability_goal == None:
        graph, total_reliability, total_cost = makeReliabilityTreeGivenReliabilityGoal(city_list, edge_list,
                                                                                       reliability_goal)
        if graph is not None:
            print(graph)
            print(total_reliability)
            print(total_cost)
            # HERE IS WHERE YOU PRINT TO TEXTFILE and can organize the printing to console above call method
            # PrintToFile("PartASolution.txt", graph, total_reliability, total_cost)
        else:
            print("NO POSSIBLE SOLUTION FOR GIVEN RELIABILITY")

    if not cost_constraint == None:
        graph, total_reliability, total_cost = maximizeReliabilitySubjectToCost(city_list, edge_list, cost_constraint)

        if graph is not None:
            print(graph)
            print(total_reliability)
            print(total_cost)
            # HERE IS WHERE YOU PRINT TO TEXTFILE call method
            # PrintToFile("PartBSolution.txt", graph, total_reliability, total_cost)
        else:
            print("NO POSSIBLE SOLUTION FOR GIVEN COST")


main()
