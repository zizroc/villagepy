from villagepy.lib.InitialGraph import InitialGraph

# Generate the initial graph
initial_graph = InitialGraph("../data/fam_bam_06.csv", "../data/resources.csv")
initial_graph.create_initial_turtle()
