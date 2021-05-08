from SPARQLWrapper import JSON, POST, GET

from MayaGraph import MayaGraph
from InitialGraph import InitialGraph




graph = MayaGraph("http://localhost:7200/repositories/Family-Health")

def test_get_living_winiks():
    winiks = list(graph.get_living_winiks())
    assert len(winiks) > 0

def test_get_all_winiks():
    winiks = list(graph.get_all_winiks())
    assert len(winiks) > 0

# print("Getting the health of winik/7")
# prop = graph.get_winik("file:/snippet/generated/winik/7", "maya:hasHealth")
# print(next(prop))

# print("Getting all of the families")
# families = graph.get_all_families()
# print(next(families))


def insert_test():
    query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX maya: <https://maya.com#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            INSERT {
                ?winik fh:hasAgeNew ?new_age .
            }
            WHERE {
                ?winik rdf:type fh:Person.
                ?winik maya:isAlive ?is_alive.
                ?winik maya:hasAge ?age.
                FILTER(?is_alive = True)
                BIND(?age + 1 as ?new_age)
            }
    """
    graph.sparql.setMethod(POST)
    graph.sparql.setReturnFormat(JSON)
    graph.sparql.setQuery(query)
    graph.sparql.query()

insert_test()
