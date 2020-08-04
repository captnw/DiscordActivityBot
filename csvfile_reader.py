from tempfile import NamedTemporaryFile
import shutil
import csv

filename = "private_data.csv"
fields = ["name", "status"]
temp_file = NamedTemporaryFile('w+t', newline='', delete=False)
dumpo = {"name": 'b', "status": 'a'}


def write_header() -> None:
    ''' Deletes the whole .csv file apparently '''
    with open(filename, "w+", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()


def write_into(lista : list) -> None:
    ''' Inserts a new row (name, status) ... replaces an existing row if the name already exists'''
    with open(filename, "r", newline='') as csv_file, temp_file:
        # First check if the data exists in .csv file
        reader = csv.DictReader(csv_file, fieldnames=fields)
        temp_writer = csv.DictWriter(temp_file, fieldnames=fields)
        writer = csv.DictWriter(csv_file, fieldnames=fields)

        for row in reader:
            #if row["name"] == lista[0]:
            #    row["name"], row["status"] = lista[0], lista[1]
            #row = {"name": row["name"], "status": row["status"]}
            temp_writer.writerow(row)
        shutil.move(temp_file.name, filename)
        
        # <Purpose> writes data into the csv
        writer.writerow({"name": lista[0], "status": lista[1]})
        

write_header()
write_into(['phat','online'])
write_into(['captnw', 'dnd'])
write_into(['phat', 'stupid'])