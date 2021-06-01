from typing import List
from random import randrange

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
        for result in results["results"]["bindings"]:
            yield (result["winik"]["value"], result["age"]["value"])

    def new_winik(self, gender):
        """
        Creates a new winik node

        :return:
        """
        winik_identifier = f'winik/something'


    def connect_child(self, mother_id, father_id, child_id) -> None:
        """
        Connects parents to a child, and a child to both parents.

        :param mother_id: The identifier of the child's mother's node
        :param father_id: The identifier of the child's father's node
        :param child_id: The identifier of the child's node
        :return: None
        """
        query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
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

    def daily_resource_adjustments(self):
        """
        Adjusts the resources for each family based on the amount
        :return:
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?family (count(distinct ?farmer) as ?farmer_count)
                               (count(distinct ?fisher) as ?fisher_count)
                               (count(distinct ?forager) as ?forager_count)
                WHERE {
                    ?farmer rdf:type fh:Person.
                    ?farmer maya:isAlive True.
                    ?farmer maya:hasProfession "farmer".
                    ?farmer maya:hasFamily ?family .
    
                    ?fisher rdf:type fh:Person.
                    ?fisher maya:isAlive True.
                    ?fisher maya:hasProfession "fisher".
                    ?fisher maya:hasFamily ?family .
    
                    ?forager rdf:type fh:Person.
                    ?forager maya:isAlive True.
                    ?forager maya:hasProfession "forager".
                    ?forager maya:hasFamily ?family
                } GROUP BY ?family
        """
        results = self.graph.query.get(query)

        # Handle the family's logic
        # "Forager" jobs -> coast resources
        # "Fisher" jobs -> marine resources
        # "Farmer" jobs -> ag resources
        for result in results["results"]["bindings"]:
            family_id = result["family"]["value"]

            # Get the amount of food units produced for each type of food resource
            new_garden_resources = int(result["farmer_count"]["value"]) * 9
            new_coast_resources = int(result["forager_count"]["value"]) * randrange(1, 5)
            new_marine_resources = int(result["fisher_count"]["value"]) * 9

            # Get the total number of each resource that the family has access to.
            # To do this, query the graph to get the totals left over from the previous
            # day and then add the new counts to each.
            resources = self.get_resources(family_id)
            available_coast_resources = resources["coast"]["quantity"] + new_coast_resources
            available_marine_resources = resources["marine"]["quantity"] + new_marine_resources
            available_garden_resources = resources["garden"]["quantity"] + new_garden_resources
            available_marine_b_resources = resources["marine-b"]["quantity"]
            available_marine_c_resources = resources["marine-c"]["quantity"]

            # The total number of calories available to the family
            available_calories = 3000.0 * (available_marine_resources + available_marine_b_resources +
                                           available_marine_c_resources) + 250.0 * available_garden_resources + \
                                 10.0 * available_coast_resources

            # How many calories does the family require?
            family_required_calories = self.get_family_calories(family_id)
            if available_calories - 100 * family_required_calories < 0:
                print("There's a calorie deficit for the family!")
                # If there are too few calories, handle a food deficit
                self.handle_calorie_deficit(available_calories, family_required_calories)
                # Set the count of all the resources to 0 since they've been eaten
                self.ag_resources = 0
                self.coast_resources = 0
                self.marine_b_resources = 0
                self.marine_c_resources = 0
                self.marine_resources = 0
            else:
                # Otherwise there's a surplus of food
                print("Calorie surplus!")
                # First, consume coast and ag calories
                temp_cals = 3000.00 * (available_marine_resources + available_marine_b_resources +
                                       available_marine_c_resources) + 250 * available_garden_resources + \
                            10 * available_coast_resources
                self.ag_resources = 0
                self.coast_resources = 0

                # Now determine how many calories need to be contributed by fish
                fish_cals = available_calories - temp_cals
                fish_newcals = 3000.0 * available_marine_resources
                fish_bcals = 3000.0 * available_marine_b_resources
                fish_ccals = 3000.0 * available_marine_c_resources
                surplus_cals = temp_cals - fish_newcals

                if surplus_cals > fish_bcals:
                    self.update_resource(resources["marine"]["id"], 0)
                    self.update_resource(resources["marine-b"]["id"], 0)
                    self.update_resource(resources["marine-c"]["id"], 0)
                elif surplus_cals > 0:
                    self.update_resource(resources["marine"]["id"], 0)
                    self.update_resource(resources["marine-b"]["id"], 0)
                    self.update_resource(resources["marine-c"]["id"], (fish_bcals - surplus_cals) / 3000.0)
                else:
                    self.update_resource(resources["marine"]["id"], 0)
                    self.update_resource(resources["marine-b"]["id"], int(-surplus_cals / 3000.0))
                    self.update_resource(resources["marine-c"]["id"], int(fish_bcals / 3000.0))

                self.handle_calorie_surplus(family_id)

    def handle_calorie_surplus(self, faimily_id: str) -> None:
        """
        Adds '5' to each winik's health in particular family

        :param family_id: The identifier of the family that has a surplus
        :return: None
        """

        # Get the health of each winik in the family
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?winik ?health
                WHERE {
                    ?winik rdf:type fh:Person.
                    ?winik maya:hasFamily <"""+faimily_id+"""> .
                    ?winik maya:isAlive True.
                    ?winik maya:hasHealth ?health.
                }
        """
        results = self.graph.query.get(query)

        # Delete the health
        for result in results["results"]["bindings"]:
            winik_id = result["winik"]["value"]
            health = int(result["health"]["value"]) + 5
            # If the winik's health is over 100, reset to 100
            if health >= 100:
                health = 100
            self.update_value(winik_id, "maya:hasHealth", health)

    def update_resource(self, resource_id: str, count: int) -> None:
        """
        Replaces the count that a resource has with a new count.

        :param resource_id: The identifier of the resource
        :param count: The new amount of that resource
        :return: None
        """
        delete_query = """
            PREFIX maya: <https://maya.com#>
            DELETE WHERE {
                 <"""+resource_id+"""> maya:hasQuantity ?old_count .
            }
        """
        self.graph.query.post(delete_query)
        query = """
            PREFIX maya: <https://maya.com#>
            INSERT {
                ?resource maya:hasQuantity ?new_count .
            }
            WHERE {
                BIND(<"""+resource_id+"""> as ?resource)
                BIND("""+str(count)+""" as ?new_count)
            }
        """
        self.graph.query.post(query)

    def get_resources(self, family_id) -> dict:
        """
        Gets all of the resources nodes for a given family.

        :param family_id: The identifier of the family
        :return: A dictionary of values {resource name: count}
        """
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX maya: <https://maya.com#>
        PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
        SELECT ?resource_name ?resource ?quantity
        WHERE {
            BIND (<"""+family_id+"""> as ?family)
            ?resource rdf:type maya:Resource.
            ?resource maya:hasName ?resource_name .
            ?family maya:hasResource ?resource .
            ?resource maya:hasQuantity ?quantity .
        }
        """
        results = self.graph.query.get(query)
        resource_info = {}
        for result in results["results"]["bindings"]:
            resource_info[result["resource_name"]["value"]] = {}
            resource_info[result["resource_name"]["value"]]["quantity"] = int(result["quantity"]["value"])
            resource_info[result["resource_name"]["value"]]["id"] = result["resource"]["value"]
        return resource_info

    def get_family_calories(self, family_id):
        """
        Gets the number of calories that a family needs for a particular day.
        :param family_id: The identifier of the family
        :return: The number of calories this family requires
        """
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX maya: <https://maya.com#>
        PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
        SELECT ?age ?gender ?winik
        WHERE {
            BIND(<"""+family_id+"""> as ?family)
            ?winik ?hasFamily ?family.
            ?winik maya:isAlive True.
            ?winik maya:hasAge ?age.
            ?winik maya:hasGender ?gender.
        }
        """
        results = self.graph.query.get(query)

        calories = 0
        for result in results["results"]["bindings"]:
            age = int(result["age"]["value"])
            gender = result["gender"]["value"]
            if 1825 >= age >= 730:
                calories += 12
            elif 3285 >= age >= 2190:
                if gender == "F":
                    calories += 18
                else:
                    calories += 20
            elif 5110 >= age >= 3650:
                if gender == "F":
                    calories += 22
                else:
                    calories += 25
            elif 12775 >= age >= 5475:
                if gender == "F":
                    calories += 24
                else:
                    calories += 30
            elif 25550 >= age >= 13140:
                if gender == "F":
                    calories += 22
                else:
                    calories += 27
            else:
                print("Failed to find a valid calorie requirement, returning 0")
                calories += 0

        return calories

    def update_value(self, subject, predicate, new_value):
        """
        Replaces a value with a new one

        :param subject:
        :param predicate:
        :param new_value:
        :return:
        """
        delete_query = """
            PREFIX maya: <https://maya.com#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            DELETE WHERE {
                 <"""+subject+"""> """+predicate+"""?old_count .
            }
        """
        self.graph.query.post(delete_query)

        query = """
            PREFIX maya: <https://maya.com#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            INSERT {
                ?subject maya:hasQuantity ?new_value .
            }
            WHERE {
                BIND(<"""+subject+"""> as ?subject)
                BIND("""+str(new_value)+""" as ?new_value)
            }
        """
        self.graph.query.post(query)

    def handle_calorie_deficit(self, family_id: str, available_calories: int,
                               required_calories: int):
        """

        :return:
        """
        if available_calories / required_calories > 0.75:
            health_loss = 2
        elif available_calories / required_calories > 0.5:
            health_loss = 5
        elif available_calories / required_calories > 0.25:
            health_loss = 7
        else:
            health_loss = 15

        health_critical = """
                PREFIX maya: <https://maya.com#>
                SELECT (count(?health) as ?hungry_winiks)
                WHERE {
                    ?winik maya:hasFamily <"""+family_id+""">.
                    ?winik maya:isAlive True.
                    ?winik maya:hasHealth ?health.
                    FILTER(?health < 75)
                }
        """
        results = self.graph.query.get(health_critical)
        res = results["results"]["bindings"]
        if len(res) == 0:
            hungry_count = 0
        else:
            hungry_count = res[0]["hungry_winiks"]["value"]

        calorie_emergency = """
        PREFIX maya: <https://maya.com#>
        SELECT (count(?health) as ?hungry_winiks)
            WHERE {
            <"""+family_id+"""> maya:hasCalorieEmergency ?calorie_emergency.
        }
        """
        current_calorie_emergency = self.get_calorie_emergency()
        res = current_calorie_emergency["results"]["bindings"]
        if len(res) == 0:
            pass
        else:
            res["is_active"]["value"]]["id"]
            is_active = res[""]
        # if current_calorie_emergency:
            #            if current_calorie_emergency[]
            #       self.create_calorie_emergency()


        if hungry_count:
            pass

        for winik in self.get_living_winiks():
            # Winik loses 10% of health
            winik.health = winik.health - health_loss
            if winik.health < 75 and not self.calorie_emergency['active']:
                # If the winik drops below 75 health, start a calorie emergency event
                # if one doesn't already exist
                print("At least one winik has dropped below 75 health.")
                self.calorie_emergency['active'] = True
                self.calorie_emergency['start'] = time_step
            # If the winik's health drops to 0, set them to dead
            if winik.health < 0:
                print("A villager has died from starvation!")
                winik.alive = False

    def get_calorie_emergency(self, family_id):
        """
        Gets the current state of a calorie emergency for a family.

        :param family_id: The identifier of the family being checked
        :return: Information about the emergency
        """
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX maya: <https://maya.com#>
        PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
        SELECT ?emergency ?is_active ?start_date
        WHERE {
            <"""+family_id+"""> maya:hasCalorieEmergency ?emergency .
            ?emergency maya:isActive ?is_active .
            ?emergency maya:hasStartDate ?start_date .
        }
        """
        return self.graph.query.get(query)

    def create_calorie_emergency(self, is_active, start) -> str:
        """
        Creates a node that represents a calorie emergency

        :return:
        """
        emergency_id = self.graph.id_manager.get_id("calorieEmergency")
        id = f"<file:/snippet/generated/{emergency_id}>"
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            PREFIX maya: <https://maya.com#>
            INSERT {
                """+id+""" rdf:type maya:calorieEmergency .
                """+id+""" maya:isActive False .
                """+id+""" maya:start 1 .
            } WHERE {}
        """
        self.graph.query.post(query)
        return id

    def connect_calorie_emergency(self, family_id: str, calorie_emergency_id: str) -> None:
        """
        Creates a node that represents a calorie emergency

        :return:
        """
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            PREFIX maya: <https://maya.com#>
            INSERT {
                """+family_id+""" maya:hasCalorieEmergency """+calorie_emergency_id+"""
            } WHERE {}
        """
        self.graph.query.post(query)
