import rdflib
import math as math
import pandas as pd

from .BaseGraph import BaseGraph


class InitialGraph(BaseGraph):
    """
    A class that represents the initial state of a simulation. It should be used to get
    the initial graph which can be uploaded to a graph database.
    """
    def __init__(self, winik_file, resource_file):
        """
        Creates a new graph that represents the initial condition
        """
        self.database = rdflib.Graph()
        self.database.parse("../onto/FamilyHealthHistory.owl")
        self.winik_file = winik_file
        self.resource_file = resource_file
        super().__init__()

    def create_initial_turtle(self) -> None:
        """
        Takes initial winik and resource csv files and creates a graph out of them.

        :return: None
        """

        if self.winik_file:
            self.add_winiks()
        if self.resource_file:
            self.add_resources()
        self.database.serialize("initial_state.ttl", format="turtle")

    def add_winiks(self) -> None:
        """
        Takes a file that defines winiks and family units and creates graph nodes out of them.

        :return: None
        """
        winik_frame = pd.read_csv(self.winik_file)
        family_ids = winik_frame['fam_id'].unique()
        for fam_id in family_ids:
            family_graph_id = rdflib.URIRef(f'family/{fam_id}')
            self.database.add((family_graph_id, rdflib.RDF.type, self.maya.Family))
            self.id_manager.counts["family"] = len(family_ids)

        # Loop over each row (a winik) in the winik data frame and create a node out of it
        for index, row in winik_frame.iterrows():
            winik_identifier = rdflib.URIRef(f'winik/{row["identifier"]}')

            # Use the Family Health History here
            if row['gender'] == "M":
                self.database.add((winik_identifier, rdflib.RDF.type, self.fh.Person_Male))
            else:
                self.database.add((winik_identifier, rdflib.RDF.type, self.fh.Person_Female))
            self.database.add((winik_identifier, self.maya.hasHealth, rdflib.Literal(row['health'])))
            self.database.add((winik_identifier, self.maya.hasFirstName, rdflib.Literal(row['first_name'])))
            self.database.add((winik_identifier, self.maya.hasLastName, rdflib.Literal(row['last_name'])))
            self.database.add((winik_identifier, self.maya.hasGender, rdflib.Literal(row['gender'])))
            self.database.add((winik_identifier, self.fh.has_natural_mother, rdflib.URIRef(f'winik/{row["mother_id"]}')))
            self.database.add((winik_identifier, self.fh.has_natural_father, rdflib.URIRef(f'winik/{row["father_id"]}')))
            self.database.add((winik_identifier, self.maya.hasProfession, rdflib.Literal(row['profession'])))
            self.database.add((winik_identifier, self.maya.isAlive, rdflib.Literal(row['alive'])))
            self.database.add((winik_identifier, self.maya.hasAge, rdflib.Literal(row['age'])))
            # Connect the winik to its family
            self.database.add((winik_identifier, self.maya.hasFamily, rdflib.URIRef(f'family/{row["fam_id"]}')))
            # Handle the winik's partner
            partner = row['partner']
            if partner and not math.isnan(partner):
                partner_uri = rdflib.URIRef(f'winik/{int(row["partner"])}')
                self.database.add((winik_identifier, self.maya.hasPartner, partner_uri))
                self.database.add((partner_uri, self.maya.hasPartner, winik_identifier))
        # Update the number of winiks
        self.id_manager.counts["winiks"] = len(winik_frame)

    def create_resource(self, name: str, quantity: int) -> rdflib.URIRef:
        """
        Creates a resource node

        :param name: The name of the resource
        :param quantity: The number of resources
        :return: The node identifier
        """
        res_id = self.id_manager.get_id("resource")
        self.database.add((res_id, rdflib.RDF.type, self.maya.Resource))
        self.database.add((res_id, self.maya.hasName, rdflib.Literal(name)))
        self.database.add((res_id, self.maya.hasQuantity, rdflib.Literal(quantity)))
        return res_id

    def add_resources(self) -> None:
        """
        Adds the default resources to each family. This assumes that
        each family has the same number of resources.

        :return: None
        """
        resource_frame = pd.read_csv(self.resource_file)

        for family_id in self.get_all_families():
            for index, row in resource_frame.iterrows():
                res_id = self.create_resource(row[0], row[1])
                self.database.add((family_id, self.maya.hasResource, res_id))

    def get_all_families(self,):
        query = """
        PREFIX maya: <https://maya.com#>
                SELECT DISTINCT ?family_id
        WHERE {
            ?family_id rdf:type maya:Family .
        }
        """
        res = self.database.query(query)
        for row in res:
            yield row[0]
