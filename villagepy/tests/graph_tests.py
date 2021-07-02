import logging
import uuid
from villagepy.lib.Model import Model

log = "log.txt"
logging.basicConfig(filename=log, level=logging.DEBUG, format='%(asctime)s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
m = Model("http://localhost:7200/repositories/Tests2", "admin", "password")

#m.partnership()
#m.handle_calorie_deficit("file:/snippet/generated/family/A", 1, 2)
# a = m.get_calorie_emergency("file:/snippet/generated/family/A")
# print(a)
#m.get_family_calories("file:/snippet/generated/family/A")
#for res in m.get_living_winiks_in_family("file:/snippet/generated/family/A"):
#print(res)
#m.connect_calorie_emergency("<file:/snippet/generated/family/A>", "<file:/snippet/generated/calorieEmergency/1>")
#m.create_calorie_emergency(True, 10)
#m.daily_resource_adjustments()
#m.get_family_calories("file:/snippet/generated/family/A")
#m.update_value("file:/snippet/generated/resource/121", "maya:hasQuantity", 777)
#m.kill_winik("file:/snippet/generated/winik/215")
#m.update_health("file:/snippet/generated/winik/215", 250)
#m.reset_resources("file:/snippet/generated/family/A")
#m.job_adjustments("file:/snippet/generated/family/A")
#m.run(100)
#name = str(uuid.uuid4())
#a = m.create_child("file:/snippet/generated/winik/48",
#                   "file:/snippet/generated/winik/35",
#                   "test",
#                   "file:/snippet/generated/family/I",
#                   name)
m.run(3650)
