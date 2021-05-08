import rdflib


class IdentityManager:
    def __init__(self):
        self.counts = {'resource': 0, 'winik': 0, 'family': 0}

    def get_id(self, property_name: str) -> rdflib.URIRef:
        """
        Generates an identifier for a new node. For example,

        If the property name is 'Winik', and there are 10 'Winiks' that already exist
        this will return Winik/10

        :param property_name: The name of the property (resource, winik, family)
        :return: A compliant, unique URI
         """
        if property_name in self.counts:
            self.counts[property_name] += 1
            return rdflib.URIRef(f'{property_name}/{str(self.counts[property_name])}')
