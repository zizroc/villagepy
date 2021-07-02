import logging
import requests
from .BaseGraph import BaseGraph
from .Query import Query


class MayaGraph(BaseGraph):
    def __init__(self, endpoint, username, password):
        self.query = Query(endpoint, username, password)
        super().__init__()

    def get_all_families(self):
        query = """
        PREFIX maya: <https://maya.com#>
                SELECT DISTINCT ?family_id
                WHERE {
                    ?family_id rdf:type maya:Family .
                }
        """
        results = self.query.get(query)

        for result in results["results"]["bindings"]:
            yield result["family_id"]["value"]

    def get_living_winiks(self):
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT * WHERE {
                    ?winik rdf:type fh:Person.
                    ?winik maya:isAlive ?is_alive.
                    FILTER(?is_alive = True).
                }
        """
        results = self.query.get(query)

        for result in results["results"]["bindings"]:
            yield result["winik"]["value"]

    def get_winik(self, winik_id, property):
        """
        Gets information about a particular winik.
        :param winik_id: The winik's identifier
        :param property: The property being checked (ie fh:hasHealth)
        :return:
        """
        query = """
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT * WHERE {
                    <"""+winik_id+"""> """+property+""" ?val.
                }
        """
        # ?winik maya:isAlive ?is_alive.
        #
        results = self.query.get(query)

        for result in results["results"]["bindings"]:
            yield result["val"]["value"]

    def get_all_winiks(self):
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?winik WHERE {
                    ?winik rdf:type fh:Person.
                }
        """
        results = self.query.get(query)

        for result in results["results"]["bindings"]:
            yield result["winik"]["value"]

    def get_all_subclasses(self):
        """
        Gets all of the subclasses
        :return:
        """
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            select * where { 
                ?winik_id rdf:type fh:Person .
            }
        """
        res = self.database.query(query)
        for row in res:
            return row[0]

    def get_living_with_ages(self) -> tuple:
        """
        Gets all of the winiks that are alive and their age.
        :return: A tuple of values, (winik ID, health)
        """
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
        results = self.query.get(query)
        for result in results["results"]["bindings"]:
            yield (result["winik"]["value"], result["age"]["value"])

    def get_partnerable_winiks(self) -> tuple:
        """
        Gets all of the male and female winiks that can be partnered.
        The conditions are:
            1. The winiks need to be more than 5844 days old
            2. The winiks need to be single
            3. The winiks cannot come from the same family
            4. The winiks need to be within 1460 days old of each other
        :return: A tuple of winiks that can be paired
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT DISTINCT ?winik_male ?male_age ?male_family ?winik_female ?female_age ?female_family WHERE {
                    ?winik_male rdf:type fh:Person_Male.
                    ?winik_male maya:hasAge ?male_age.
                    ?winik_male maya:hasFamily ?male_family.
                    ?winik_female rdf:type fh:Person_Female.
                    ?winik_female maya:hasAge ?female_age.
                    ?winik_female maya:hasFamily ?female_family.
                    BIND( EXISTS { ?winik_male maya:hasPartner ?male_partner } as ?male_partnered )
                    BIND( EXISTS { ?winik_female maya:hasPartner ?female_partner } as ?female_partnered )
                    FILTER(?male_age > 5844)
                    FILTER(?female_age > 5844)
                    FILTER(?male_partnered = False)
                    FILTER(?female_partnered = False)
                    FILTER(?female_family != ?male_family)
                    BIND(ABS(?male_age - ?female_age) as ?age_gap)
                    FILTER(?age_gap < 1460)
                }
        """
        results = self.query.get(query)

        for result in results["results"]["bindings"]:
            print(result)
#            male_data.append([result["winik_male"]["value"], result["male_age"]["value"],
#                             result["male_partnered"]["value"], result["male_last_name"]["value"]])
#            female_data.append([result["winik_female"]["value"], result["female_age"]["value"],
#                                result["female_partnered"]["value"], result["female_last_name"]["value"]])

        return 1, 2

    def update_partner(self, winik, new_partner):
        """
        :param winik: The winik with the new partner
        :param new_partner: The winik's new partner
        :return:
        """
        pass

    def save(self, path) -> None:
        """
        Saves the graph to disk
        :param path: The path on disk where the graph is written to
        :return: None
        """
        logging.info(f"Saving graph to {path}")
        headers = {
            'Accept': 'text/turtle',
        }

        params = (
            ('infer', 'false'),
            ('context', 'null'),
            ('infer', 'true')
        )
        response = requests.get(f'{self.query.endpoint}/statements', headers=headers, params=params)
        with open(path, "w") as f:
            f.write(response.text)

    def delete(self) -> None:
        """
        Deletes the contents of the graph

        :return: None
        """
        query = """
        DELETE {
            ?s ?p ?o .
        } WHERE {
            ?s ?p ?o .
        }
        """
        self.query.post(query)

    def get_winik_id(self) -> str:
        """
        Gets a new identifier for a winik

        :return: A new, unique identifier
        """
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
        SELECT (COUNT(?s) as ?total_count)
        WHERE
        {
            ?s rdf:type fh:Person .
        }
        """
        results = self.query.get(query)
        assert len(results["results"]["bindings"])
        res = results["results"]["bindings"][0]
        new_count = int(res["total_count"]["value"]) + 1
        return f'file:/snippet/generated/{self.id_manager.get_graph_id("winik", new_count)}'
