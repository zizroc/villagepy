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
        results = self.sparql.query().convert()
        return results

    def post(self, query: str) -> None:
        endpoint = SPARQLWrapper(f'{self.endpoint}/statements')
        endpoint.setHTTPAuth(DIGEST)
        endpoint.setCredentials(self.username, self.password)
        endpoint.setMethod(POST)
        endpoint.setQuery(query)
        endpoint.query()
