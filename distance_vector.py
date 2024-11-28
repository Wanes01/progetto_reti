# Autore: Emir Wanes Aouioua, matricola 0001027902
# Traccia di progetto n.2

# This class models a distance vector for a node X.
# The distance vector mantains a record for each reachable destination
# including the next hop (the next node to visit to reach the destination)
# and the cost of the minimum path from X to the destination
class DistanceVector:
    def __init__(self, name: str):
        self.name = name
        self.distance_vector = {
            name: (0, "")
        }  # Maps the destination to (cost, nextHop)

    # Updates the distance vector of this node with the informations of the
    # distance vector of another node
    # other: the distance vector of the adjacent node
    # weight: the weight of the edge connecting this node and the adjacent node
    # returns True if changes to this distance vector have been made, False otherwise
    def update_distance_vector(self, other: "DistanceVector", weight: int) -> bool:
        updated = False
        for dest, data in other.distance_vector.items():
            cost = data[0]
            # Updates the cost to a given destination only if the destination doesn't
            # exist yet or a cheaper path to the destination has been found
            if (
                dest not in self.distance_vector
                or cost + weight < self.distance_vector[dest][0]
            ):
                self.distance_vector[dest] = (cost + weight, other.name)
                updated = True
        return updated

    # Prints the distance vector in a table-like format
    def print_routing_table(self):
        titles = "| {:<12} | {:<7} | {:<7} |\n".format(
            "Destination", "Cost", "Next Hop"
        )
        bar = "-" * len(titles)
        s = bar + "\n"
        s += "| {:^33} |\n".format(f"[{self.name}] Routing table")
        s += bar + "\n"
        s += titles
        s += bar + "\n"
        for dest, data in self.distance_vector.items():
            cost = str(data[0])
            next_hop = str(data[1])
            s += "| {:<12} | {:<7} | {:<8} |\n".format(dest, cost, next_hop)
        s += bar
        print(s)

# A class modelling a bidirectional graph. Describes the topological
# organization of the graph.
class Graph:
    def __init__(self):
        # Maps the node_name to a list((destination, edge_weight))
        self.edges = {}
        # Maps the node_name to a DistanceVector
        self.vectors = {}

    # Adds a node to the graph, if not present
    def add_node(self, node: str):
        if node not in self.edges:
            self.edges[node] = []
            self.vectors[node] = DistanceVector(node)

    # Adds the weighted edge from src to dst.
    def add_edge(self, src: str, dst: str, weight: int):
        self.add_node(src)
        self.add_node(dst)
        self.edges[src].append((dst, weight))
        self.edges[dst].append((src, weight))

    # Returns the nodes in this graph ad a list
    def get_nodes(self) -> list[str]:
        return list(self.edges.keys())

    # Returns the edges that start from src as a list
    def get_edges_from(self, src: str) -> list[(str, int)]:
        return self.edges[src][:]


# ASCII caracters for text effects such as colors and styles
class ASCIIColor:
    PURPLE = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# APPLICATION ENTRY POINT
if __name__ == "__main__":
    # Script configuration. Makes the user choose if they want to use the preconfigured graph or make a new one
    # and if they want to see every distance vector update or just the final result of the calculations
    g = Graph()
    print(
        f"{ASCIIColor.BOLD + ASCIIColor.PURPLE + ASCIIColor.UNDERLINE}Welcome to the Distance Vector simulator{ASCIIColor.ENDC}"
    )
    presets = int(
        input(
            f"{ASCIIColor.CYAN}1) Would you like to use the default preset or insert a custom graph? [0=preset/1=custom]: "
        )
    )

    if presets == 0:
        # A preset graph
        g.add_edge("A", "B", 1)
        g.add_edge("A", "F", 3)
        g.add_edge("F", "B", 1)
        g.add_edge("F", "E", 2)
        g.add_edge("F", "D", 6)
        g.add_edge("E", "B", 5)
        g.add_edge("E", "D", 1)
        g.add_edge("B", "C", 3)
        g.add_edge("C", "D", 2)
    else:
        print(
            (
                'Insert the edges of the graph using the format "SRC DST COST" (example: A B 1).\n'
                'NOTE: the graph is bidirectional, so adding A B 1 automatically adds B A 1\n'
                'Type DONE when there are no more edges to add.\n'
            )
        )
        while True:
            edge = input("Insert an edge: ")
            if edge == "DONE":
                break
            try:
                src, dst, cost = edge.split()
                cost = int(cost)
                g.add_edge(src, dst, cost)
            except:
                print("Wrong format! Enter FIRST_NAME SECOND_NAME COST.")

    all_steps = int(
        input(
            "2) Would you like to see all the steps or just the final routing tables? [0=all steps/1=final result]: "
        )
    ) == 0
    print(f"{ASCIIColor.ENDC}")

    # Every node of the graph shares its distant vector with each of its
    # adjacent nodes. The nodes stop sharing their distance vector when no
    # new update to a distance vector happens in a full cycle of updates
    # (this means that no better path to a destination can be computed)
    while True:
        changes = False
        for src in g.get_nodes():
            src_dv = g.vectors[src]
            if all_steps:
                print(f"{ASCIIColor.BOLD + ASCIIColor.PURPLE}+ ROUTING TABLE TO SEND +")
                src_dv.print_routing_table()
                print(f"{ASCIIColor.ENDC}")
            # share the distance vector with all the adjacent nodes
            for edge in g.get_edges_from(src):
                dst, weight = edge
                dst_dv = g.vectors[dst]
                if all_steps:
                    print(
                        f"{ASCIIColor.YELLOW}Sending [{src}] routing table to [{dst}]. Updated [{dst}] routing table:{ASCIIColor.ENDC}"
                    )
                # if an update happens then another full cycle must be done
                if dst_dv.update_distance_vector(src_dv, weight):
                    if all_steps:
                        dst_dv.print_routing_table()
                    changes = True
                else:
                    if all_steps:
                        print(
                            f"{ASCIIColor.GREEN}No changes where made in [{dst}] routing table.{ASCIIColor.ENDC}\n"
                        )
        # No changes have been made in this full cycle. Stable configuration reached
        if not changes:
            break

    print(
        f"{ASCIIColor.RED + ASCIIColor.BOLD + ASCIIColor.UNDERLINE}+ FINAL ROUTING TABLES +{ASCIIColor.ENDC}"
    )
    for node in g.vectors:
        g.vectors[node].print_routing_table()
