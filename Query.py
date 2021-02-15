#Python script to read database data and produce a query
#Coded by Josué
#27/06/2018

import sys
import time
import datetime
import sqlite3
import os
from decimal import Decimal

# os.remove("Selección.db")

db_conn = sqlite3.connect("Selección.db")

def file_clean_up():
    '''
    -no-param

    A function that takes the raw output from a 500MB database and
    picks out elements from it, writing these to a new file.

    The information in this new file will be used in another function
    '''

    os.remove("VentasFormat.txt")
    
    # Clean-up text file
    try:
        f = open("Ventas.txt", "r")
        f1 = open("VentasFormat.txt", "w")
        data = []

        # Extract valuable data from file
        for line in f:
            cursor = 0
            date = ""
            totalprod = ""
            totalimp = ""
            total = ""
            log = []
            for char in line:
                if char == ";":
                    cursor += 1
                elif cursor == 13:
                    date += char
                elif cursor == 20:
                    totalprod += char
                elif cursor == 22:
                    totalimp += char
                elif cursor == 23:
                    total += char
            log.append(date[0:9].strip(' '))
            log.append (totalprod[0:-3].strip(' '))
            log.append(totalimp[0:-3].strip(' '))
            log.append(total[0:-3].strip(' '))
            data.append(log)
            
        # Write new file
        for entry in data:
            f1.write(str(entry) + "\n")

    finally:
        f.close()
        f1.close()
        print("\nLa operación se llevó a cabo con éxito")


def formatted_output():

    try:
        # Read new file
        f = open("VentasFormat.txt", "r")

        # Check dates with procedure
        def validate(date_str):
            datetime.datetime.strptime(date_str, "%d/%m/%Y")

        while True:
            try:
                # Ask user for date range
                lowerBound = input("\nPor favor, introduzca la fecha desde la que quiere filtrar: ")
                upperBound = input("\nPor favor, introduzca la fecha hasta la que quiere filtrar: ")

                validate(lowerBound)
                validate(upperBound)
                break
                
            except ValueError:
                print("\nPor favor, introduzca una fecha en el formato (D)D/(M)M/AAAA")
                continue

        output = []
        counter = 0
        fro = 0
        to = 0

        raw_data = []
        
        for line in f.readlines():
            line = line[1:-2]
            raw_data.append(line.split(','))

        for entry in raw_data:
            counter += 1
            if entry[0][1:-1] == lowerBound:
                fro = counter
                break

        counter = 0
        
        for entry in raw_data:
            counter += 1
            if entry[0][1:-1] == upperBound:
                to = counter
                break

        sumprod = 0
        sumimp = 0
        sumtotal =  0
        currentdate = raw_data[fro-1][0]

        # Total all values per day
        for entry in range(fro-1, to):

            if raw_data[entry][0] != currentdate:
                output.append([currentdate, round(sumprod, 2), round(sumimp, 2), round(sumtotal, 2)])
                sumprod = float(raw_data[entry][1][2:-1]) / 100
                sumimp = float(raw_data[entry][2][2:-1]) / 100
                sumtotal = float(raw_data[entry][3][2:-1]) / 100
                currentdate = raw_data[entry][0]
            else:
                sumprod += float(raw_data[entry][1][2:-1]) / 100
                sumimp += float(raw_data[entry][2][2:-1]) / 100
                sumtotal += float(raw_data[entry][3][2:-1]) / 100
            
        # Write output into an external file (database)

        try:
            db_conn.execute("CREATE TABLE Ventas(ID INTEGER PRIMARY KEY "
                            "AUTOINCREMENT NOT NULL, Fecha TEXT NOT NULL, Total_Importe FLOAT,"
                            "Total_Impuestos FLOAT, Total_Ticket FLOAT)")

        except sqlite3.OperationalError:
            print("\nError en la operación")

        db_conn.commit()

        
        for entry in output:
            db_conn.execute("INSERT INTO Ventas(Fecha, Total_Importe, Total_Impuestos, Total_Ticket)"
                        " VALUES({}, {}, {}, {})".format(entry[0], str(entry[1]), str(entry[2]), str(entry[3])))
            db_conn.commit()

        T_Import = 0
        T_Impuest = 0
        T_Ticket = 0

        # Totals
        try:
            db_conn.execute("CREATE TABLE Ventas_Totales(Suma_Importe TEXT, Suma_Impuestos TEXT,"
                            "Suma_Ticket TEXT)")
            db_conn.commit()

            for entry in output:
                T_Import += entry[1]
                T_Impuest += entry[2]
                T_Ticket += entry[3]

            db_conn.execute("INSERT INTO Ventas_Totales(Suma_Importe, Suma_Impuestos, Suma_Ticket)"
                            " VALUES({}, {}, {})".format(T_Import, T_Impuest, T_Ticket))
            db_conn.commit()
            
        except sqlite3.OperationalError:
            print("\nError en la operación")

    finally:
        f.close()
        db_conn.close()
        print("\nLa operación se completó con éxito")
    
def main():
    
    while True:
        try:
            print("\nConsola de impresión de ventas:\n\n\
                  1: Limpiar archivo.txt (se recomienda ejecutar este comando primero)\n\
                  2: Sacar importes totales\n\
                  3: Salir del programa")
            user_input = int(input("\nIntroduzca su elección: "))
            assert(1 <= user_input <= 3)
            
        except AssertionError:
            print("\nPor favor, introduzca solo las opciones que ve en pantalla")
            continue

        if user_input == 1:
            file_clean_up()
            break

        elif user_input == 2:
            formatted_output()
            break

        elif user_input == 3:
            print("\nCerrando el programa...")
            time.sleep(1)
            sys.exit()
            break

if __name__ == "__main__":
    main()
