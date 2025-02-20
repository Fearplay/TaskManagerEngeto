import mysql.connector
from mysql.connector import Error as err
from mysql.connector import errorcode

# Název databáze a tabulky používané v aplikaci
DB_NAME = "engeto"
TABLE_NAME = "ukoly"

# Globální slovník pro ukládání úkolů (může sloužit i k internímu sledování)
ukoly = {}


def zadny_ukol():
    """
    Vypíše informaci, že seznam úkolů je prázdný.
    Používá se jako upozornění, když není co zobrazit nebo mazat.
    """
    print("Seznam úkolů je prázdný. Pro smazání nebo zobrazení úkolu tento seznam nesmí být prázdný.")
    print()


def neplatna_volba():
    """
    Obecná hláška, která se volá, když uživatel zadá neplatnou volbu.
    """
    print("Neplatná volba, zkuste to znovu!")
    print()


def zobrazit_vsechny_ukoly():
    """
    Načte a vypíše všechny úkoly z databáze.
    Pokud tabulka obsahuje nějaká data, vypíše je; pokud ne, zavolá funkci zadny_ukol.
    Vrací True, pokud byly nějaké úkoly nalezeny, jinak False.
    """
    cursor = dataBase.cursor()
    try:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        pocet_data = cursor.fetchall()
        if len(pocet_data) != 0:
            # Vypíše každý záznam (řádek) z tabulky
            for row in pocet_data:
                print(row)
            print()
            return True
        else:
            zadny_ukol()
            return False
    except err:
        print(f"Chyba při načítání dat: {err}")
        print()
    cursor.close()


def pripojeni_db():
    """
    Naváže spojení s MySQL serverem a vybere databázi.
    Pokud databáze neexistuje, vytvoří ji.
    """
    global dataBase

    dataBase = mysql.connector.connect(
        host="localhost",
        user="", # doplnit sve udaje
        password="",
    )
    cursor = dataBase.cursor()
    try:
        # Pokusí se použít databázi
        cursor.execute(f"USE {DB_NAME}")
    except mysql.connector.Error as err:
        print(f"Database {DB_NAME} does not exists.")
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            try:
                # Vytvoří databázi, pokud neexistuje
                cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
            except err:
                print(f"Failed creating database: {err}")
                exit(1)
            print(f"Database {DB_NAME} created successfully.")
            print()
            dataBase.database = DB_NAME
        else:
            print(err)
            exit(1)
    cursor.close()


def vytvoreni_tabulky():
    """
    Vytvoří tabulku s názvem TABLE_NAME pro ukládání úkolů.
    Pokud tabulka již existuje, informuje o tom uživatele.
    """
    cursor = dataBase.cursor()
    try:
        print(f"Creating table {TABLE_NAME}")
        cursor.execute(f'''
        CREATE TABLE {TABLE_NAME} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev_ukol VARCHAR(14) NOT NULL,
            popis_ukol VARCHAR(100) NOT NULL,
            stav_ukol VARCHAR(14) NOT NULL       
        )
        ''')
        cursor.close()
    except mysql.connector.Error as err:
        # Pokud tabulka již existuje, vypíše příslušnou hlášku
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table already exists.")
            print()
        else:
            print(err.msg)
            print()


def pridat_ukol():
    """
    Načte od uživatele název a popis úkolu (interaktivně přes input).
    Pokud jsou obě pole vyplněna, vloží úkol do databáze a uloží jej do globálního slovníku.
    V opačném případě vypíše chybovou hlášku.
    """
    cursor = dataBase.cursor()
    # Získá vstupy od uživatele
    nazev_ukol = str(input("Zadejte název úkolu: "))
    popis_ukol = str(input("Zadejte popis úkolu: "))
    if len(nazev_ukol) == 0 or len(popis_ukol) == 0:
        # Upozornění, pokud chybí některý vstup
        print("Úkol nemohl být přidán. Chybí popis nebo název úkolu.")
        print()
    else:
        try:
            # Vloží data do tabulky a uloží změnu v databázi
            data = (nazev_ukol, popis_ukol, "Nezahájeno")
            cursor.execute(f"INSERT INTO {TABLE_NAME} (nazev_ukol, popis_ukol, stav_ukol) VALUES (%s, %s, %s)", data)
            dataBase.commit()
            # Uloží úkol do globálního slovníku
            ukoly.update({nazev_ukol: popis_ukol})
            print(f"Úkol '{nazev_ukol}' byl přidán.")
            print()
        except mysql.connector.Error as err:
            print(f"Chyba při vkládání dat: {err}")
            print()

    cursor.close()


def zobrazit_ukoly():
    """
    Vypíše všechny úkoly, které mají stav 'Nezahájeno' nebo 'Probíhá'.
    Pokud žádné takové úkoly nejsou, zavolá funkci zadny_ukol.
    Vrací True, pokud jsou úkoly nalezeny, jinak False.
    """
    cursor = dataBase.cursor()
    try:
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE stav_ukol IN ('Nezahájeno', 'Probíhá')")
        zobrazit_data = cursor.fetchall()
        if len(zobrazit_data) != 0:
            for row in zobrazit_data:
                print(row)
            print()
            return True
        else:
            zadny_ukol()
            return False
    except err:
        print(f"Chyba při načítání dat: {err}")
        print()

    cursor.close()


def aktualizovat_ukol():
    """
    Umožní uživateli aktualizovat stav úkolu.
    Nejprve vypíše všechny úkoly, poté požaduje zadání ID úkolu a nového stavu.
    Aktualizuje záznam v databázi a informuje o úspěšné změně.
    """
    # Zobrazí všechny úkoly – pokud jsou, pokračuje
    if zobrazit_vsechny_ukoly():
        cursor = dataBase.cursor()
        # Smyčka pro ověření správného zadání existujícího ID
        while True:
            try:
                aktualizovat_ukol_id = int(input("Zadejte ID úkolu, který chcete aktualizovat: "))
            except ValueError:
                print("Neplatný vstup. Zadejte prosím číslo.")
                print()
                continue

            # Kontrola existence úkolu s daným ID
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = %s", (aktualizovat_ukol_id,))
            ziskat_data = cursor.fetchall()
            if len(ziskat_data) == 0:
                print("Úkol s tímto ID neexistuje, zkuste to prosím znovu.")
                print()
            else:
                break
        # Smyčka pro ověření správné volby nového stavu
        while True:
            try:
                aktualizovat_ukol_stav = int(input(
                    "Zadejte číslo pro nový stav Vašeho úkolu, který chcete aktualizovat 1 - Probíhá a 2 - Hotovo: "))
                if aktualizovat_ukol_stav != 1 and aktualizovat_ukol_stav != 2:
                    print("Musíte zadat číslo 1 nebo 2")
                    print()
                else:
                    try:
                        # Přiřazení textové hodnoty na základě volby uživatele
                        if aktualizovat_ukol_stav == 1:
                            aktualizovat_ukol_stav = "Probíhá"
                        elif aktualizovat_ukol_stav == 2:
                            aktualizovat_ukol_stav = "Hotovo"
                        data = (aktualizovat_ukol_stav, aktualizovat_ukol_id)
                        cursor.execute(f"UPDATE {TABLE_NAME} SET stav_ukol = %s WHERE id = %s", data)
                        dataBase.commit()
                        print("Záznam byl aktualizován.")
                        print()
                    except mysql.connector.Error as err:
                        print(f"Chyba při aktualizaci dat: {err}")
                        print()
                    break
            except ValueError:
                print("Neplatný vstup. Zadejte prosím číslo.")
                print()
                continue


def odstranit_ukol():
    """
    Umožňuje uživateli odstranit úkol podle jeho ID.
    Nejprve se ověří, zda existují nějaké úkoly, a pokud ano, požádá o zadání ID.
    Pokud je ID platné, záznam se smaže.
    """
    if zobrazit_vsechny_ukoly():
        cursor = dataBase.cursor()
        # Smyčka pro ověření zadání platného ID
        while True:
            try:
                smazat_ukol_id = int(input("Zadejte ID úkolu, který chcete odstranit: "))
            except ValueError:
                print("Neplatný vstup. Zadejte prosím číslo.")
                print()
                continue

            # Ověření existence úkolu s daným ID
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = %s", (smazat_ukol_id,))
            ziskat_data = cursor.fetchall()
            if len(ziskat_data) == 0:
                print("Úkol s tímto ID neexistuje, zkuste to prosím znovu.")
                print()
            else:
                break

        try:
            # Smazání záznamu
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = {smazat_ukol_id}")
            dataBase.commit()
            print("Záznam byl smazán.")
            print()

        except mysql.connector.Error as err:
            print(f"Chyba při mazání dat: {err}")
            print()

        except ValueError:
            neplatna_volba()

        cursor.close()


def hlavni_menu():
    """
    Hlavní menu aplikace – zobrazuje možnosti pro práci s úkoly.
    Na základě volby uživatele volá odpovídající funkce (přidání, zobrazení, aktualizaci, odstranění).
    Program běží, dokud uživatel nevybere ukončení.
    """
    pripojeni_db()  # Naváže spojení s DB a zvolí správnou databázi
    vytvoreni_tabulky()  # Vytvoří tabulku pro úkoly, pokud ještě neexistuje
    while True:
        print("Správce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Konec programu")
        try:
            choice = int(input("Vyberte možnost (1-5): "))  # Získá číselný vstup od uživatele
            print()
            if choice == 1:
                pridat_ukol()
                continue
            elif choice == 2:
                zobrazit_ukoly()
                continue
            elif choice == 3:
                aktualizovat_ukol()
                continue
            elif choice == 4:
                odstranit_ukol()
                continue
            elif choice == 5:
                print("Konec programu")
                dataBase.close()  # Uzavře připojení k DB
                break
            else:
                print("Vyberte znovu!")
                print()
                continue
        except ValueError:
            neplatna_volba()


if __name__ == '__main__':
    hlavni_menu()  # Spustí hlavní menu pouze při přímém spuštění souboru
