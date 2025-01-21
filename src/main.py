ukoly = {}


def hlavni_menu():
    while True:
        print("Správce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Odstranit úkol")
        print("4. Konec programu")
        choice = int(input("Vyberte možnost (1-4): "))
        print()
        if choice == 1:
            pridat_ukol()

            continue
        elif choice == 2:
            zobrazit_ukoly()
            continue
        elif choice == 3:
            odstranit_ukol()
            continue
        elif choice == 4:
            print("Konec programu")
            break
        else:
            print("Vyberte znovu!")
            continue


def pridat_ukol():
    nazev_ukol = str(input("Zadejte název úkolu: "))
    popis_ukol = str(input("Zadejte popis úkolu: "))
    ukoly.update({nazev_ukol: popis_ukol})
    print(f"Úkol '{nazev_ukol}' byl přidán.")
    print()


def zobrazit_ukoly():
    i = 0
    print("Seznam úkolů:")
    for nazev_ukol, popis_ukol in ukoly.items():
        i += 1
        print(str(i) + ". " + nazev_ukol + " - " + popis_ukol)
    print()


def odstranit_ukol():
    zobrazit_ukoly()
    i = 1
    smazat_ukol = int(input("Zadejte číslo úkolu, který chcete odstranit: "))
    for nazev_ukol in ukoly.keys():
        if i == smazat_ukol:
            ukoly.pop(nazev_ukol)
            print(f"Úkol '{nazev_ukol}' byl odstraněn.")
            break
        i += 1

    print()


hlavni_menu()
