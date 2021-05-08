from villagepy.lib.MayaGraph import MayaGraph
from SPARQLWrapper import JSON, POST, GET


class Model:
    def __init__(self):
        self.graph = MayaGraph("http://localhost:7200/repositories/Age-Test")

    def run(self):
        for step in range(1):
            self.graph.save(f'graph_{step}.rdf')
            self.increase_winik_age()

    def partnership(self):
        """

        :return:
        """
        males = self.graph.get_partnerable_males()
        females = self.get_partnerable_females()
        # Check to make sure the're not related
        # Check age gap
        # If partner, update graph

    def increase_winik_age(self) -> None:
        """
        Increases the age of each winik that is alive by '1'
        :return: None
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                DELETE {
                    ?winik fh:hasAge ?age .
                }
                INSERT {
                    ?winik fh:hasAge ?new_age .
                }
                WHERE {
                    ?winik rdf:type fh:Person.
                    ?winik maya:isAlive ?is_alive.
                    ?winik maya:hasAge ?age.
                    FILTER(?is_alive = True)
                    BIND(?age + 1 as ?new_age)
                }
        """
        self.graph.sparql.setMethod(POST)
        self.graph.sparql.setReturnFormat(JSON)
        self.graph.sparql.setQuery(query)
        results = self.graph.sparql.query()


m = Model()
for i in range(10):
    m.graph.()
    # Increase the age of the winik
    m.increase_winik_age()
    # Check to see if any winiks can get partnered
    m.partnership()




