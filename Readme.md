

### How to Use

This software requires a database to hold the simulation data. It also
re

#### Setting up GraphDB

1. Visit
   [Ontotext](https://www.ontotext.com/products/graphdb/graphdb-free/)
   and get GraphDB
2. Install it and make sure you can view it at `http://localhost:7200/import`
3. [Create a new repository](https://graphdb.ontotext.com/documentation/free/creating-a-repository.html)


#### Creating the Initial Graph

When starting from the winik and resource csv files, it's necessary to
create the initial state.

1. run `./scripts/create_initial_graph.py`
2. Note that `scripts/initial_graph.ttl`has been created
3. Visit `http://localhost:7200/import`
4. Click `Import RDF Text Snippet` & paste the graph inside
5. Click `Import`

 
#### Running the Model


### Directories

`./data/`: Holds the initial winik and resource files
 
`./lib`: Classes responsible for 
 
`./onto/`: Holds any external ontologies that are used

`./scripts/`: Helper scripts for doing miscellaneous tasks

`./tests/`: Tests for sanity checking the classes