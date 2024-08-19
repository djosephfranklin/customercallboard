import random
import json
from faker import Faker
import datetime
import numpy as np

# Define the start and end date range
start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2024, 7, 31)

faker = Faker()

# Pre-defined values
countries = ["sg", "it", "fr", "us", "de", "au", "jp", "in", "cn", "br"]
quick_hints = ["Buy-1", "Buy-8", "Sell-1", "Sell-3", "Hold-2", "Buy-5"]
actionables = ["Missed Lead:1", "Potential Lead:2", "Completed:3", "Follow-up:4"]
scores = ["Recommended", "Not Recommended"]
activestatus = ['Online - MBOL', '4hrs ago', '4 days ago', '1 month ago']
category = ['Citi Gold', 'Citi Private Bank', 'Citi Private Client']

num_customers=100

# Function to generate a random date
def get_random_date(start, end):
    time_between_dates = end - start
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start + datetime.timedelta(days=random_number_of_days)

# Function to generate a single record
def generate_sample(index):
    uuid_suffix = f"-{index:03d}"
    return {
        "UUID": f"CUS{faker.random_number(digits=5)}-30{uuid_suffix}",
        "country": random.choice(countries),
        "CustomerID": f"C{faker.random_number(digits=5)}",
        "RelationshipID": f"R{faker.random_number(digits=4)}",
        "Customername": faker.name(),
        "Date": get_random_date(start_date, end_date),
        "Quick Hint": random.choice(quick_hints),
        "Actionable": random.choice(actionables),
        "Score": random.choice(scores),
        "rmAdvisoryScore": np.random.randint(3, 10)*10,
        "customerUnderstandingScore": np.random.randint(3, 10)*10,
        "rmUnderstandingScore": np.random.randint(3, 10)*10,
        "customerAppreciationValue": np.random.randint(3, 10)*10,
        "rmKnowledgeScore": np.random.randint(3, 10)*10,
        "overallCallQualityScore": np.random.randint(3, 10)*10
    }

def generate_sample_customer_listing(index):
    uuid_suffix = f"-{index:03d}"
    return {
        "UUID": f"CUS{faker.random_number(digits=5)}-30{uuid_suffix}",
        "country": random.choice(countries),
        "customerid": f"C{faker.random_number(digits=5)}",
        "RelationshipID": f"R{faker.random_number(digits=4)}",
        "Customername": faker.name(),
        "mail" : faker.email(),
        "phone" : faker.phone_number(),
        "age" : faker.random_number(digits=2),
        "id" : index,
        "activestatus" : random.choice(activestatus),
        "Quick Hint": random.choice(quick_hints),
        "infer": random.choice(actionables),
        "category" : random.choice(category),
        "category-count" : faker.random_number(digits=1),
        "Score": random.choice(scores),
        "rmAdvisoryScore": np.random.randint(3, 10)*10,
        "customerUnderstandingScore": np.random.randint(3, 10)*10,
        "rmUnderstandingScore": np.random.randint(3, 10)*10,
        "customerAppreciationValue": np.random.randint(3, 10)*10,
        "rmKnowledgeScore": np.random.randint(3, 10)*10,
        "overallCallQualityScore": np.random.randint(3, 10)*10
    }

# Generate 100 samples
samples = [generate_sample(i) for i in range(num_customers)]
samples_customer = [generate_sample_customer_listing(i) for i in range(1,10)]

# Convert to JSON format for printing
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


samples_json = json.dumps(samples, indent=4, sort_keys=True, default=str)
samples_customer_json = json.dumps(samples_customer, indent=4, sort_keys=True, default=str)

# Print the generated samples
print(samples_customer)

# If you want to save it to a file, you can uncomment the lines below:
# with open('samples.json', 'w') as file:
#     json.dump(samples, file, indent=4)

