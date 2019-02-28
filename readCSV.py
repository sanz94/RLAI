import csv

with open('pixels.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(row)
            line_count += 1
        else:
            print(row)
            line_count += 1
    print 'Processed',line_count,'lines.'