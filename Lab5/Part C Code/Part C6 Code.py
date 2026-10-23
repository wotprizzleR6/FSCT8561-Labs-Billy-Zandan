import csv

practice_records = [
    {"endpoint": "/", "status": 200},
    {"endpoint": "/example", "status": 404}
]

with open("practice_records.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["endpoint", "status"])
    writer.writeheader()
    writer.writerows(practice_records)

print("Saved practice_records.csv")