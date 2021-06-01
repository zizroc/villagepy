from villagepy.lib.Model import Model

m = Model("http://localhost:7200/repositories/Food-Production-Test", "admin", "password")

#m.partnership()
#m.handle_calorie_deficit("file:/snippet/generated/family/A", 1, 2)
# a = m.get_calorie_emergency("file:/snippet/generated/family/A")
# print(a)
m.connect_calorie_emergency("<file:/snippet/generated/family/A>", "<file:/snippet/generated/calorieEmergency/1>")
#m.create_calorie_emergency(True, 10)
#m.daily_resource_adjustments()
#m.get_family_calories("file:/snippet/generated/family/A")
#m.update_value("file:/snippet/generated/resource/121", "maya:hasQuantity", 777)