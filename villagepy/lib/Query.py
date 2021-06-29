import logging
from SPARQLWrapper import JSON, DIGEST, POST, SPARQLWrapper

class Query:
    def __init__(self, endpoint: str, username: str, password: str):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.sparql = SPARQLWrapper(endpoint)

    def get(self, query: str) -> dict:
        self.sparql.setMethod("GET")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        logging.debug("Sending SPARQL GET")
        results = self.sparql.query().convert()
        logging.debug("Retrieved SPARQL GET")
        return results

    def post(self, query: str) -> None:
        endpoint = SPARQLWrapper(f'{self.endpoint}/statements')
        endpoint.setHTTPAuth(DIGEST)
        endpoint.setCredentials(self.username, self.password)
        endpoint.setMethod(POST)
        endpoint.setQuery(query)
        logging.debug("Sending SPARQL POST")
        endpoint.query()
        logging.debug("Retrieved SPARQL POST")
