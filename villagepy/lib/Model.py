from typing import List
from random import randrange, randint
import logging

from villagepy.lib.MayaGraph import MayaGraph


class Model:
    def __init__(self, graph_endpoint, username, password):
        self.graph = MayaGraph(graph_endpoint, username, password)

    def run(self, length: int):
        for step in range(length):
            print(f"Day {step}")
            self.graph.save(f'graph_{step}.rdf')
            self.increase_winik_age()
            self.check_calorie_emergency(step)
            self.daily_resource_adjustments(step)

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
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX maya: <https://maya.com#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
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

    def birth_subsystem(self, family_id) -> None:
        """
        Logic for the birth system. When a female winik
            1. Is partnered
            2. Has less than 5 children
            3. Has not had a child in at least 365 days
        she will have a new child.
        :return:
        """
        query = """
                SELECT ?winik ?age ?partner ?child ?child_age WHERE {
                    ?winik rdf:type fh:Person.
                    ?winik maya:hasFamily <"""+family_id+""" .
                    ?winik maya:hasAge ?age .
                    ?winik maya:hasPartner ?partner .
                    ?winik maya:hasLastName ?last_name .
                    OPTIONAL {
                        ?child fh:has_natural_mother ?winik .
                        ?child maya:hasAge ?child_age .
                        FILTER(?child_age > 365)
                        }
                }
        """
        results = self.graph.query.get(query)

        # For every winik that is able to have a child
        for result in results["results"]["bindings"]:
            winik_id = str(result["winik"]["value"])
            partner_id = str(result["partner"]["value"])
            last_name = str(result["last_name"]["value"])
            # Create the new winik
            age = int(result["age"]["value"])
            if age > 1:
                self.create_child(winik_id, partner_id, last_name, family_id)

    def create_child(self, mother_id, father_id, last_name, family_id, gender, profession) -> str:
        """
        Creates a winik that has parents.

        :param mother_id: The mother's identifier
        :param father_id: The father's identifier
        :return: The identifier of the child
        """
        profession= "none"
        gender_prob = randint(0, 1)
        if gender_prob:
            gender="F"
        else:
            gender="M"

        new_winik_id = self.new_winik(gender, profession, last_name, family_id, 0)

        self.connect_child(mother_id, father_id, new_winik_id)

    def new_winik(self, gender, profession, last_name, family_id, age) -> str:
        """
        Creates a new winik node

        :return: The identifier of the new winik
        """
        if gender == "F":
            gender_class = "fh:Person_Female"
        else:
            gender_class = "fh:Person_Male"
        winik_identifier = self.graph.get_winik_id()
        query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
            PREFIX maya: <https://maya.com#>
            INSERT {
                <"""+winik_identifier+""" rdf:type """+gender_class+""" .
                <"""+winik_identifier+""" maya:hasFirstName ?father_id .
                <"""+winik_identifier+""" maya:hasFamily <"""+family_id+"""> .
                <"""+winik_identifier+""" maya:hasLastName """+last_name+""" .
                <"""+winik_identifier+""" maya:hasGender """+gender+""" .
                <"""+winik_identifier+""" maya:hasProfession """+profession+""" .
                <"""+winik_identifier+""" maya:isAlive True .
                <"""+winik_identifier+""" maya:hasAge """+age+""" . 
            }
        """
        self.graph.query.post(query)
        return winik_identifier

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

    def daily_resource_adjustments(self, date):
        """
        Adjusts the resources and handles consumption/production of them for each family.

        :param date: The date
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
        for family in results["results"]["bindings"]:
            family_id = family["family"]["value"]
            new_garden_resources = int(family["farmer_count"]["value"]) * 9
            new_coast_resources = int(family["forager_count"]["value"]) * randrange(1, 5)
            new_marine_resources = int(family["fisher_count"]["value"]) * 9

            # Get the total number of each resource that the family has access to.
            # To do this, query the graph to get the totals left over from the previous
            # day (which is the starting amount today) and then add the new counts to each.
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
                # There's a deficit
                logging.info(f"Calorie deficit for family {family_id}")
                self.handle_calorie_deficit(family_id, available_calories, family_required_calories, date)
                # Set the count of all the resources to 0 since they've been eaten
                self.reset_resources(family_id)
            else:
                # There's a surplus of food
                logging.info(f"Calorie surplus for family {family_id}")
                # First, consume coast and ag calories
                # temp_cals is the amount of calories required from fish
                temp_cals = 100 * family_required_calories - 250 * available_garden_resources - \
                            10 * available_coast_resources
                self.update_resource(resources["garden"]["id"], 0)
                self.update_resource(resources["coast"]["id"], 0)

                # Now determine how many calories need to be contributed by fish
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

            # Handle job changes
            self.job_adjustments(family_id)
            # Handle any births
            self.birth_subsystem(family_id)

    def handle_calorie_surplus(self, faimily_id: str) -> None:
        """
        Adds '5' to each winik's health in particular family

        :param family_id: The identifier of the family that has a surplus
        :return: None
        """
        # Query to get the health of each winik in the family
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
        for result in results["results"]["bindings"]:
            winik_id = result["winik"]["value"]
            health = int(result["health"]["value"]) + 5
            # If the winik's health is over 100, reset to 100
            if health >= 100:
                health = 100
            self.update_health(winik_id, health)

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
            gender = str(result["gender"]["value"])
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
                logging.info(f'Failed to find a calorie requirement for winik {str(result["winik"]["value"])}, returning 0')
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
                               required_calories: int, date):
        """
        Contains the logic for handling the event where a family doesn't have enough
        calories to feed all of the family members.

        :return: None
        """
        # Calculate how many 'hitpoints' a the winiks lose
        if available_calories / required_calories > 0.75:
            health_loss = 2
        elif available_calories / required_calories > 0.5:
            health_loss = 5
        elif available_calories / required_calories > 0.25:
            health_loss = 7
        else:
            health_loss = 15

        winiks = self.get_living_winiks_in_family(family_id)
        for winik in winiks:
            if float(winik[1]) > 0:
                new_health = float(winik[1]) - health_loss
                if new_health <= 0:
                    logging.info(f"Villager {winik[0]} has died from starvation!")
                    self.kill_winik(winik[0])
                self.update_health(winik[0], new_health)

        # Determine if any of the winiks have a 'critical' health value, which is lower than 75.
        health_critical = """
                PREFIX maya: <https://maya.com#>
                SELECT (count(?health) as ?hungry_winiks)
                WHERE {
                    ?winik maya:hasFamily <"""+family_id+""">.
                    ?winik maya:isAlive True.
                    ?winik maya:hasHealth ?health.
                    FILTER(?health < 75)
                    FILTER(?health > 0)
                }
        """
        results = self.graph.query.get(health_critical)
        res = results["results"]["bindings"]
        if len(res) == 0:
            critical_count = 0
        else:
            critical_count = res[0]["hungry_winiks"]["value"]

        current_calorie_emergency = self.get_calorie_emergency(family_id)
        res = current_calorie_emergency["results"]["bindings"]
        if critical_count and not len(res):
            # Then there are hungry winiks and there isn't an emergency; create one
            self.create_calorie_emergency(True, date)

    def get_calorie_emergency(self, family_id):
        """
        Gets the current state of a calorie emergency for a family.

        :param family_id: The identifier of the family being checked
        :return: Information about the emergency
        """
        query = """
        PREFIX maya: <https://maya.com#>
        SELECT ?emergency ?is_active ?start_date
        WHERE {
            <"""+family_id+"""> maya:hasCalorieEmergency ?emergency .
            ?emergency maya:isActive ?is_active .
            ?emergency maya:hasStartDate ?start_date .
        }
        """
        return self.graph.query.get(query)

    def create_calorie_emergency(self, start, is_active=True) -> str:
        """
        Creates a node that represents a calorie emergency.

        :param start: The start date for the emergency
        :param is_active: Whether the emergency is active
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
                """+id+""" maya:isActive True .
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

    def update_health(self, winik_id, new_health) -> None:
        """
        Deletes the current health value for a particular winik and replaces it with a
        new value

        :param winik_id: The identifier of the winik
        :param new_health: The new health value
        :return: None
        """

        delete_query = """
            PREFIX maya: <https://maya.com#>
            DELETE WHERE {
                 <"""+winik_id+"""> maya:hasHealth ?health .
            }
        """
        self.graph.query.post(delete_query)
        query = """
            PREFIX maya: <https://maya.com#>
            INSERT {
                <"""+winik_id+"""> maya:hasHealth ?new_health .
            } WHERE {
                BIND("""+str(new_health)+""" as ?new_health)
            }
        """
        self.graph.query.post(query)

    def get_living_winiks_in_family(self, family_id) -> tuple:
        """
        Returns the identifier and health of each winik in a family

        :param family_id: The identifier of the family whose winiks are being retrieved
        :return:
        """
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX maya: <https://maya.com#>
                PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                SELECT ?winik ?health WHERE {
                    ?winik rdf:type fh:Person.
                    ?winik maya:isAlive ?is_alive.
                    ?winik maya:hasFamily <"""+family_id+""">.
                    ?winik maya:hasHealth ?health.
                    FILTER(?is_alive = True).
                }
        """
        results = self.graph.query.get(query)

        for result in results["results"]["bindings"]:
            yield (result["winik"]["value"], result["health"]["value"])

    def kill_winik(self, winik_id):
        """
        Kills a winik. Sets 'alive' to false and the health to 0

        :param winik_id: The winik's identifier
        :return: None
        """
        query = """
            PREFIX maya: <https://maya.com#>
            DELETE WHERE {
                <"""+winik_id+"""> maya:hasHealth ?health .
                <"""+winik_id+"""> maya:isAlive ?alive.
            }
        """
        self.graph.query.post(query)

        query = """
            PREFIX maya: <https://maya.com#>
            INSERT {
                ?winik maya:hasHealth 0 .
                ?winik maya:isAlive False .
            }
            WHERE {
                BIND(<"""+winik_id+"""> as ?winik)
            }
        """
        self.graph.query.post(query)

    def reset_resources(self, family_id):
        """
        Sets the resource count to 0 for all resources in a particular family.

        :param family_id:
        :return:
        """
        # First get all of the resource ids
        query = """
        PREFIX maya: <https://maya.com#>
        SELECT ?resource
        WHERE {
            <"""+family_id+"""> maya:hasResource ?resource .
        }
        """
        results = self.graph.query.get(query)
        for result in results["results"]["bindings"]:
            self.update_resource(result["resource"]["value"], 0)

    def check_calorie_emergency(self, date, limit=20):
        """
        First check, to see if each family has a calorie deficit. If it is present, check to see
        if it needs to expire

        :param date: The current date
        :param limit: The maximum number of days that the emergency is valid for
        :return:
        """
        # Query to get all families that have a calorie emergency node
        query = """
        PREFIX maya: <https://maya.com#>
        SELECT ?emergency ?is_active ?start_date
        WHERE {
            ?family maya:hasCalorieEmergency ?emergency .
            ?emergency maya:isActive ?is_active .
            ?emergency maya:hasStartDate ?start_date .
        }
        """
        res = self.graph.query.get(query)
        # For each family, check if it's active
        for result in res["results"]["bindings"]:
            if result["is_active"]["value"]:
                # If it is, check if it's time to delete it
                if date - result["start_date"]["value"] >= limit:
                    self.delete_calorie_emergency(result["family"]["value"])

    def delete_calorie_emergency(self, family_id):
        """
        Deletes a calorie emergency.
        DEVNOTE: We should be deleting the calorie emergency node!!!

        :param family_id: The identifier of the family whose calorie emergency is being deleted
        :return:
        """
        delete_query = """
            PREFIX maya: <https://maya.com#>
            DELETE WHERE {
                 <"""+family_id+"""> maya:hasCalorieEmergency ?emergency .
            }
        """
        self.graph.query.post(delete_query)

    def job_adjustments(self, family_id):
        """

        :return:
        """
        # Check to see if there's a calorie emergency
        emergency = self.get_calorie_emergency(family_id)
        emergency_event = emergency["results"]["bindings"]
        # Get all of the winiks in the family
        query = """
            PREFIX maya: <https://maya.com#>
            SELECT ?id ?age ?gender ?profession
            WHERE {
                ?winik maya:hasFamily <"""+family_id+"""> .
                ?winik maya:isAlive ?alive .
                ?winik maya:hasAge ?age .
                ?winik maya:hasGender ?gender .
                ?winik maya:hasProfession ?profession .
                FILTER (?alive = True)
            }
        """
        res = self.graph.query.get(query)
        for result in res["results"]["bindings"]:
            age = int(result["age"]["value"])
            gender = str(result["gender"]["value"])
            current_profession = str(result["profession"]["value"])
            new_profession = current_profession
            if age > 14610:
                new_profession = 'forager'
            elif age > 3287 and gender == 'M':  # What if self.age > 3287 and self.gender == 'Female'?
                new_profession = 'fisher'
            elif age > 5113 and gender == 'F':
                new_profession = 'farmer'
            elif age > 3287:
                new_profession = 'fisher'
            elif age > 1826:
                new_profession = 'forager'

            if len(emergency_event) and emergency_event["is_active"]["value"]:
                new_profession = "farmer"

            # Update the profession if it changed
            if new_profession != current_profession:
                logging.info("Got a new profession!")
                query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX maya: <https://maya.com#>
                    PREFIX fh: <http://www.owl-ontologies.com/Ontology1172270693.owl#>
                    DELETE {
                        ?winik maya:hasProfession ?profession .
                    }
                    INSERT {
                        ?winik maya:hasProfession <"""+new_profession+"""> .
                    } WHERE {
                        ?winik rdf:type fh:Person .
                        ?winik maya:isAlive ?is_alive .
                        ?winik maya:hasAge ?age .
                        FILTER(?is_alive = True)
                        BIND(?age + 1 AS ?new_age)
                    }
                """
                self.graph.query.post(query)
