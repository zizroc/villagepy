from villagepy.lib.Model import Model


mayan_model = Model("http://localhost:7200/repositories/Age-Test", "admin", "password")
for i in range(10):
    mayan_model.graph.save(f'history/data_{i}.ttl')
    # Increase the age of the winik
    mayan_model.increase_winik_age()
    # Check to see if any winiks can be partnered
    mayan_model.partnership()
    # See if any children should be created
    mayan_model.birth_subsystem()
    # Handle updating the resource counts
    mayan_model.daily_resource_adjustments()
    # Check to see if there's any starvation
    mayan_model.daily_calorie_adjustments()
    # Handle any calorie emergency events
    mayan_model.calorie_emergency()
