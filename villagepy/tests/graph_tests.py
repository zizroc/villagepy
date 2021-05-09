from villagepy.lib.MayaGraph import MayaGraph
from villagepy.lib.Model import Model

m = Model("http://localhost:7200/repositories/Age-Test", "admin", "password")
for winik in m.graph.get_all_winiks():
    print(winik)
#m.partnership()


# Connect two winiks
#m.partner_winiks("file:/snippet/generated/winik/50", "file:/snippet/generated/winik/51")

# Get all of the winiks that have a partner. If things are run properly, this should not return the empty set
"""
PREFIX maya: <https://maya.com#>
select * where { 
	?winik maya:hasPartner ?partner.
} 
"""

# Get the partner of winik 100
"""
PREFIX maya: <https://maya.com#>
select * where { 
	<file:/snippet/generated/winik/100> maya:hasPartner ?partner.
} 
"""