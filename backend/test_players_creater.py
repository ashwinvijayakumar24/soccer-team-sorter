import csv
import random
from datetime import datetime, timedelta

# Helper functions
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_birthday(min_age, max_age):
    end_date = datetime.now() - timedelta(days=min_age*365)
    start_date = datetime.now() - timedelta(days=max_age*365)
    return random_date(start_date, end_date)

# Data
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Margaret", "Susan", "Dorothy", "Lisa"]
genders = ["M", "F"]
skill_levels = ["Beginner", "Average", "Very Good", "Advanced"]
practice_locations = ["Far East", "West 288", "Silverlake/East 288", "Blue Ridge Soccer Park (South Houston)", "Hwy 6 South"]
schools = ["Oak Elementary", "Maple Middle School", "Pine High School", "Cedar Academy", "Birch School", "Willow Elementary", "Elm Middle School", "Spruce High", "Aspen Charter School", "Redwood Preparatory", "Sycamore Elementary", "Chestnut Middle School", "Magnolia High", "Poplar Academy", "Cypress School"]
parent_hcs = ["Y", "N"]
parent_acs = ["Y", "N"]
# Generate data
data = []
for _ in range(500):
    last_name = random.choice(last_names)
    first_name = random.choice(first_names)
    gender = random.choice(genders)
    birthday = random_birthday(4, 17).strftime("%Y-%m-%d")
    skill_level = random.choice(skill_levels)
    practice_location = random.choices(practice_locations, weights=[1, 4, 4, 1, 1])[0]
    school = random.choice(schools)
    parent_hc = random.choices(parent_hcs, weights=[1,5])[0]
    parent_ac = random.choices(parent_acs, weights=[1,5])[0]
    
    data.append([last_name, first_name, gender, birthday, skill_level, practice_location, school, parent_hc, parent_ac])

# Write to CSV
with open('players.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Last Name", "First Name", "Gender", "Birthday", "Skill Level", "Preferred Practice Location", "School", "Parent HC", "Parent AC"])
    writer.writerows(data)

print("players.csv file has been created successfully.")