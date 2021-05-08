import rdflib

from .IdentityManager import IdentityManager


class BaseGraph:
    def __init__(self):
        """
        Creates a new instance of a basic graph
        """
        self.maya = rdflib.Namespace("https://maya.com#")
        self.fh = rdflib.Namespace("http://www.owl-ontologies.com/Ontology1172270693.owl#")
        self.id_manager = IdentityManager()
