import os
import pandas as pd
from rdflib import Graph


class DataManager:
    """
    A class that's used to load and query data from the simulation.
    """

    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.current_record: Graph = None
        path, dirs, files = next(os.walk(data_directory))
        # DEVNOTE: These aren't actually properly sorted. Avoid using for now
        self.files = sorted(files)
        self.record_count = len(files)
        # There should be more than 0 data files
        assert self.record_count > 0

    def load_file(self, filename):
        """
        Loads a graph record into rdflib and sets the current record to it.

        :param filename: The name of the file holding the graph. It should include the .ttl extension
        :return:
        """
        self.current_record = Graph()
        self.current_record.parse(f'{self.data_directory}/{filename}', format="turtle")

    def get_family_resources(self, family_id, step=None):
        """
        Gets a list of data frames that contain the counts of each resource for a particular
        family.

        :param family_id:
        :param step: The timestep to get the data for. If None, it will iterate over all data files
        :return: A list of .....
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?name ?quantity WHERE {
                    BIND(<"""+str(family_id)+"""> AS ?family)
                    ?resource rdf:type maya:Resource .
                    ?family maya:hasResource ?resource .
                    ?resource maya:hasName ?name .
                    ?resource maya:hasQuantity ?quantity .
                }
                """
        if not step:

            records = []

            for file in self.files:
                self.load_file(file)
                results = self.current_record.query(query)
                rows = []
                row_record = {}
                for row in results:
                    row_record.update({str(row[0]): float(row[1])}.copy())
                records.append(row_record)
            records = pd.DataFrame.from_records(records)
            return records
        else:
            self.load_file(0)

            results = self.current_record.query(query)
            assert len(results["results"]["bindings"])
            family_resources = results["results"]["bindings"][0]

    def get_all_winiks(self):
        """
        Returns a list of winiks with their properties.

        :return: A list of data frames (winiks)
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT * WHERE {
                    ?winik rdf:type fh:Person.
                    ?winik ?predicate ?predicate_value.
                }
                """
        self.current_record.query(query)

    def get_all_winiks_range(self):
        """
        Gets records of all the winiks between the start and end of a simulation.

        :return:
        """
        winiks = []
        for file in self.files:
            self.load_file(file)
            winiks += [self.get_all_winiks()]
        return winiks

    def get_winiks_step(self, family_id, step):
        """
        Gets winiks in a family at a particular time step

        :param family_id: The family containing the winiks
        :param step:
        :return:
        """
        # Load the file into a graph
        graph = Graph()
        graph.parse(f'{self.data_directory}/graph_{step}.ttl', format="turtle")

        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT * WHERE {
                    ?winik rdf:type fh:Person.

                }
        """
        res = graph.query(query)
        print(res)

    def get_all_family_ids(self):
        """
        Returns a list of all of the identifiers of the families IN THE INITIAL CONDITION
        :return:
        """
        # Load the initial state
        self.load_file(self.files[0])
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?family WHERE {
                    ?family rdf:type maya:Family.
                }
        """
        identifiers = []
        results = self.current_record.query(query)
        for row in results:
            identifiers += row
        return identifiers

    def resource_records_to_df(self, records):
        """
        Takes a [[{name:count],[name:count]] list of lists of dicts and turns it into a
        data frame.

        :param records:
        :return:
        """
        record = pd.DataFrame()
        for time_step in records:
            records = pd.DataFrame.from_records(time_step)
            print(records)
            record.merge(records)
            print(record)
