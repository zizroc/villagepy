import rdflib
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from IdentityManager import IdentityManager
from BaseGraph import BaseGraph


class MayaGraph(BaseGraph):

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.sparql = SPARQLWrapper(endpoint)
        super().__init__()

    def get_all_families(self):
        query = """
        PREFIX maya: <https://maya.com#>
                SELECT DISTINCT ?family_id
                WHERE {
                    ?family_id rdf:type maya:Family .
                }
        """
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            print(result)
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
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()

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
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
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
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
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
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        print(results)
        for result in results["results"]["bindings"]:
            yield (result["winik"]["value"], result["age"]["value"])

    def get_partnerable_winiks(self):
        """
        Gets all of the males that can be partnered


        Female may need TO BE OPTIONAL
        :return:
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?winik_male ?male_age ?male_partnered ?winik_female ?female_age ?female_partnered WHERE {
                    ?winik_male rdf:type fh:Person_Male.
                    ?winik_female rdf:type fh:Person_Female.
                    ?winik_male maya:hasAge ?age.
                    ?winik_female maya:hasAge ?age.
                    BIND( EXISTS { ?winik_male maya:hasPartner ?male_partner } as ?male_partnered )
                    BIND( EXISTS { ?winik_female maya:hasPartner ?female_partner } as ?female_partnered )
                    FILTER(?male_age > 5844)
                    FILTER(?female_age > 5844)
                }
        """
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        for result in results["results"]["bindings"]:
            yield (result["winik"]["value"], result["age"]["value"], result["partnered"]["value"])

    def get_partnerable_females(self):
        """
        Gets all of the females that can be partnered
        :return:
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?winik ?age ?partnered WHERE {
                    ?winik rdf:type fh:Person_Female.
                    ?winik maya:hasAge ?age.
                    BIND( EXISTS { ?winik maya:hasPartner ?partner } as ?partnered )
                    FILTER(?age > 5844)
                }
        """
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        for result in results["results"]["bindings"]:
            yield (result["winik"]["value"], result["age"]["value"], result["partnered"]["value"])


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
        :param path:
        :return:
        """
        pass