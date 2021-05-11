from villagepy.lib.MayaGraph import MayaGraph
from SPARQLWrapper import JSON, POST, DIGEST, BASIC, SPARQLWrapper


class Model:
    def __init__(self, graph_endpoint, username, password):
        self.graph = MayaGraph(graph_endpoint, username, password)

    def run(self):
        for step in range(1):
            self.graph.save(f'graph_{step}.rdf')
            self.increase_winik_age()

    def partnership(self) -> None:
        """
        Runs the subsystem that dictates the partnership interaction
        between winiks.

        :return: None
        """

        males, females = self.graph.get_partnerable_winiks()
        # Logic to figure out which winiks SHOULD be partnered

        pairs = [(1,1)] # Should be a list of tuples (bride, groom) of the winiks that will be partnered
        for bride, groom in pairs:
            self.partner_winiks(bride, groom)

    def increase_winik_age(self) -> None:
        """
        Increases the age of each winik that is alive by '1'.

        :return: None
        """
        query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            PREFIX schema: <http://schema.org/>
            PREFIX maya: <https://maya.com#>
            DELETE {
                ?winik maya:hasAge ?age .
            }
            INSERT {
                ?winik maya:hasAge ?new_age .
            } WHERE {
                ?winik rdf:type fh:Person.
                ?winik maya:isAlive ?is_alive.
                ?winik maya:hasAge ?age.
                FILTER(?is_alive = True)
                BIND(?age + 1 AS ?new_age)
            }
        """
        self.graph.query.post(query)

    def partner_winiks(self, bride, groom):
        """
        Partners two winiks together.

        :param bride: The female wink's identifier
        :param groom: The male winik's identifier
        :return: None
        """
        query = """
            PREFIX maya: <https://maya.com#>
            INSERT {
                ?bride maya:hasPartner ?groom.
                ?groom maya:hasPartner ?bride.
            }
            WHERE {
                BIND(<"""+bride+"""> as ?bride)
                BIND(<"""+groom+"""> as ?groom)
            }
        """
        self.graph.query.post(query)

    def birth_subsystem(self) -> None:
        """
        Logic for the birth system. When a female winik
            1. Is partnered
            2. Has less than 5 children
            3. Has not had a child in at least 365 days
        she will have a new child.
        :return:
        """
        # Get all of the female winiks
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?winik ?age WHERE {
                    ?winik rdf:type fh:Person.
                    ?winik maya:isAlive ?is_alive.
                    ?winik maya:hasAge ?age.
                    FILTER(?is_alive = True).
                }
        """
        results = self.graph.query.get(query)
        print(results)
        for result in results["results"]["bindings"]:
            yield (result["winik"]["value"], result["age"]["value"])

    def add_child(self, mother_id, father_id, child_id) -> None:
        """
        Connnects parents to a child, and a child to both parents.

        :param mother_id: The identifier of the child's mother's node
        :param father_id: The identifier of the child's father's node
        :param child_id: The identifier of the child's node
        :return: None
        """
        query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            PREFIX schema: <http://schema.org/>
            PREFIX maya: <https://maya.com#>
            INSERT {
                ?mother_id maya:hasChild ?new_age .
                ?father_id maya:hasChild ?new_age .
                ?child_id maya:hasMother ?mother_id .
                ?child_id maya:hasFather ?father_id .
            } WHERE {
                BIND(<"""+father_id+"""> AS ?father_id)
                BIND(<"""+mother_id+"""> AS ?mother_id)
                BIND(<"""+child_id+"""> AS ?child_id)
            }
        """
        self.graph.query.post(query)
