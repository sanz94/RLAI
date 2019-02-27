import csv

with open('pixels.csv', mode='w') as csv_file:
    fieldnames = ['red', 'green', 'blue']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'red': 2, 'green': 0, 'blue': 2})
    writer.writerow({'red': 10, 'green': 4, 'blue': 9})