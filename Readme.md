# villagepy
A graph-backed simulation of ancient villages.

## Directories

`./data/`: Holds the data used to generate the initial state
(triplification)
 
`./lib`: Classes that make up the model & triplification
 
`./onto/`: Holds any external ontologies that are used

`./scripts/`: Helper scripts for doing miscellaneous tasks

`./tests/`: Tests for sanity checking the classes

## The Model

### Running the Model

#### Create a Repository & Load Data

##### Installing GraphDB
GraphDB acts as the database; this will have to be running in the
background for the experiment to run. There are a number of ways to run
GraphDB-the desktop application is probably the most straightforward
one.

1. Visit
   [Ontotext](https://www.ontotext.com/products/graphdb/graphdb-free/)
   and get GraphDB
2. Install it and make sure you can view it at `http://localhost:7200/import`
3. [Create a new repository](https://graphdb.ontotext.com/documentation/free/creating-a-repository.html)
4. Set a password for the admin account under the settings tab

##### Loading Initial State
1. run `./scripts/create_initial_graph.py`
2. Note that `scripts/initial_graph.ttl`has been created
3. Visit `http://localhost:7200/import`
4. Click `Import RDF Text Snippet` & paste the graph inside
5. Click `Import`

 
#### Run the Model

#### Saving & Running Later

Because the data is stored in the graph database,we can stop the
simulation at any time and continue later. There are two ways to do this

##### 1: Setting Small Timesteps (recomended)
Set small simulation lengths and pickup where you left off. This works
because the experiment will end after the last day, opposed to the
method below.

##### 2: Exiting mid-experiment
One way to exit and load later is by stopping the experiment midway
through. If the experiment were to continue, it's possible to get in a
weird state. To avoid this, delete the repository in GraphDB and load
the last graph file downloaded.

## Visualizing the Results
There are pre-canned methods for obtaining data about winiks/families.

### Time Series of Resources

### Time Series of Winik Properties

### Misc

## Architecture

### Database-Model Interaction

### Model
