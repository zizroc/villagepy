from villagepy.scripts.data_utils import DataManager

# This file generates plots that display resource counts for each
# family across time.

data_manager = DataManager("../../tests/history/")

# Start by getting a list of all the family identifiers
family_ids = data_manager.get_all_family_ids()

family_records = []
# Create a list to hold
for fam_id in family_ids:
    family_records.append({fam_id: data_manager.get_family_resources(fam_id)})

i = 0
for family_record in family_records:
    for key, value in family_record.items():
        fname = key.split("file:/snippet/generated/family/", 1)[1]
        value.to_csv(f"data/families/{fname}.csv")
