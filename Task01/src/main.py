ukoly = {}  # Globální slovník pro ukládání úkolů


def zadny_ukol():
    """
    Vypíše informaci o tom, že seznam úkolů je prázdný.
    """
    print("Seznam úkolů je prázdný. Pro smazání úkolu tento seznam nesmí být prázdný.")
    print()


def neplatna_volba():
    """
    Obecná hláška pro upozornění na neplatný vstup od uživatele.
    """
    print("Neplatná volba, zkuste to znovu!")
    print()


def hlavni_menu():
    """
    Zobrazí hlavní menu a zpracovává volbu uživatele.
    Podle vybrané volby volá přidání, zobrazení nebo odstranění úkolu,
    případně ukončí program.
    """
    while True:
        print("Správce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Odstranit úkol")
        print("4. Konec programu")
        try:
            choice = int(input("Vyberte možnost (1-4): "))  # Zde získáme vstup od uživatele a převedeme jej na číslo
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
                # Pokud uživatel zadá číslo mimo rozsah 1-4
                print("Vyberte znovu!")
                continue
        except ValueError:  # Pokud se převod vstupu na int nepodaří (např. zadáno písmeno)
            neplatna_volba()


def pridat_ukol():
    """
    Vyžádá od uživatele název a popis úkolu.
    Pokud obě informace nejsou prázdné, úkol uloží do slovníku 'ukoly'.
    """
    nazev_ukol = str(input("Zadejte název úkolu: "))
    popis_ukol = str(input("Zadejte popis úkolu: "))
    if len(nazev_ukol) == 0 or len(popis_ukol) == 0:  # Kontrola, jestli uživatel zadal něco do obou polí
        print("Úkol nemohl být přidán. Chybí popis nebo název úkolu.")
        print()
    else:
        ukoly.update({nazev_ukol: popis_ukol})  # Uložení úkolu
        print(f"Úkol '{nazev_ukol}' byl přidán.")
        print()


def zobrazit_ukoly():
    """
    Vypíše seznam všech uložených úkolů. Pokud je seznam prázdný,
    zavolá funkci 'zadny_ukol'.
    """
    if len(ukoly) == 0:
        zadny_ukol()
    else:
        i = 0
        print("Seznam úkolů:")
        for nazev_ukol, popis_ukol in ukoly.items():  # Projde všechny položky ve slovníku 'ukoly' a zobrazí je s číslem
            i += 1
            print(str(i) + ". " + nazev_ukol + " - " + popis_ukol)
        print()


def odstranit_ukol():
    """
    Umožňuje uživateli odstranit konkrétní úkol.
    Pokud je seznam prázdný, zavolá 'zadny_ukol'.
    Pokud uživatel zadá neplatné číslo, funkce vypíše chybovou hlášku
    a vyzve uživatele k zadání znovu.
    """
    if len(ukoly) == 0:
        zadny_ukol()
    else:
        while True:
            zobrazit_ukoly()  # Nejprve zobrazíme seznam úkolů před odstraněním
            i = 1
            ukol_nalezen = False
            try:
                smazat_ukol = int(input("Zadejte číslo úkolu, který chcete odstranit: "))  # Uživatel zadá číslo úkolu, který chce smazat
                for nazev_ukol in ukoly.keys():  # Procházíme všechny názvy úkolů a hledáme číslo pro daný úkol
                    if i == smazat_ukol:
                        ukoly.pop(nazev_ukol)
                        print(f"Úkol '{nazev_ukol}' byl odstraněn.")
                        ukol_nalezen = True
                        break
                    i += 1
                if ukol_nalezen:
                    print()
                    break
                else:
                    print("Zadejte číslo existujícího úkolu!")
                    print()

            except ValueError:
                neplatna_volba()


hlavni_menu()  # Spuštění programu
