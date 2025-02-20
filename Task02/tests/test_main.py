import pytest
import mysql.connector


# Fixture pro nastavení testovacího prostředí – připojení k DB a vytvoření testovací tabulky
@pytest.fixture(scope="function")
def db_setup():
    """
    Připojí se k databázi "test" a vytvoří tabulku "test_ukoly".
    Po skončení testu provede úklid (smaže tabulku a uzavře spojení).
    """
    # Připojení k databázi (nastav svůj host, uživatele, heslo a databázi)
    conn = mysql.connector.connect(
        host="localhost",
        user="", #  doplnit sve udaje
        password="",
        database="test"
    )
    cursor = conn.cursor()

    # Vytvoření testovací tabulky, pokud ještě neexistuje
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS test_ukoly (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nazev_ukol VARCHAR(14) NOT NULL,
        popis_ukol VARCHAR(100) NOT NULL,
        stav_ukol VARCHAR(14) NOT NULL       
    )
    ''')
    conn.commit()

    # Předáme připojení a kurzor testům
    yield conn, cursor

    # Po skončení testů smažeme testovací tabulku, aby se prostředí vyčistilo
    cursor.execute("DROP TABLE IF EXISTS test_ukoly")
    conn.commit()

    # Uzavření kurzoru a spojení
    cursor.close()
    conn.close()


def test_zadat_valid_data(db_setup):
    """
    Testuje vložení validních dat do tabulky.
    Ověří, že se vložený záznam objeví v databázi.
    """
    conn, cursor = db_setup

    # Vložíme záznam s platnými hodnotami
    cursor.execute(
        "INSERT INTO test_ukoly (nazev_ukol, popis_ukol, stav_ukol) VALUES (%s, %s, %s)",
        ("Ukol", "Nic", "Nezahájeno")
    )
    conn.commit()


def test_zadat_invalid_data(db_setup):
    """
    Testuje vložení nevalidních dat – příliš dlouhý text pro sloupec.
    Očekává, že MySQL vyhodí chybu "Data too long for column".
    """
    conn, cursor = db_setup

    with pytest.raises(mysql.connector.Error, match="Data too long for column"):
        cursor.execute(
            "INSERT INTO test_ukoly (nazev_ukol, popis_ukol, stav_ukol) VALUES (%s, %s, %s)",
            ('a' * 101, "man", "sa")
        )
        conn.commit()


def test_aktualizovat_valid_id(db_setup):
    """
    Pozitivní test aktualizace záznamu.
    Vložíme řádek a následně změníme jeho stav z "Nezahájeno" na "Hotovo".
    Ověříme, že se změna v DB skutečně projevila.
    """
    conn, cursor = db_setup

    # Vložení testovacího záznamu
    cursor.execute(
        "INSERT INTO test_ukoly (nazev_ukol, popis_ukol, stav_ukol) VALUES (%s, %s, %s)",
        ("Ukol", "sssss", "Nezahájeno")
    )
    conn.commit()

    # Aktualizace záznamu s id=1 – předpokládáme, že první vložený záznam má id 1
    cursor.execute("UPDATE test_ukoly SET stav_ukol = 'Hotovo' WHERE id = 1")
    conn.commit()

    # Ověření, že se stav změnil na "Hotovo"
    cursor.execute("SELECT popis_ukol, stav_ukol FROM test_ukoly WHERE id = 1")
    result = cursor.fetchone()
    assert result[1] == "Hotovo"


def test_aktualizovat_invalid_id(db_setup):
    """
    Negativní test aktualizace – pokusíme se aktualizovat záznam, který neexistuje.
    Očekáváme, že se nic nezmění, protože záznam s id=2 neexistuje.
    """
    conn, cursor = db_setup

    # Vložíme jeden řádek, který bude mít pravděpodobně id 1
    cursor.execute(
        "INSERT INTO test_ukoly (nazev_ukol, popis_ukol, stav_ukol) VALUES (%s, %s, %s)",
        ("Ukol", "sssss", "Nezahájeno")
    )
    conn.commit()

    # Pokusíme se aktualizovat řádek s id=2 (který neexistuje)
    cursor.execute("UPDATE test_ukoly SET stav_ukol = 'Hotovo' WHERE id = 2")
    conn.commit()

    # Ověříme, že pro id=2 neexistuje žádný řádek
    cursor.execute("SELECT popis_ukol FROM test_ukoly WHERE id = 2")
    result = cursor.fetchone()
    assert result is None, "Row with ID=2 should not exist, so it cannot be updated."


def test_smazat_valid_id(db_setup):
    """
    Pozitivní test mazání – vložíme řádek, poté jej smažeme a ověříme, že byl skutečně odstraněn.
    """
    conn, cursor = db_setup

    # Vložíme testovací záznam
    cursor.execute(
        "INSERT INTO test_ukoly (nazev_ukol, popis_ukol, stav_ukol) VALUES (%s, %s, %s)",
        ("Smazat", "Promazani", "Nezahájeno")
    )
    conn.commit()

    # Získáme ID vloženého záznamu podle názvu
    cursor.execute(
        "SELECT id FROM test_ukoly WHERE nazev_ukol = %s",
        ("Smazat",)
    )
    result = cursor.fetchone()
    assert result is not None, "Řádek by měl být vložen před smazáním."
    row_id = result[0]

    # Smažeme řádek s daným ID
    cursor.execute("DELETE FROM test_ukoly WHERE id = %s", (row_id,))
    conn.commit()

    # Ověříme, že řádek již neexistuje
    cursor.execute("SELECT * FROM test_ukoly WHERE id = %s", (row_id,))
    result_after = cursor.fetchone()
    assert result_after is None, "Řádek by měl být smazán."


def test_smazat_invalid_id(db_setup):
    """
    Negativní test mazání – pokusíme se smazat záznam s neexistujícím id (např. 9999).
    Ověříme, že se tabulka nezměnila (zůstává prázdná).
    """
    conn, cursor = db_setup

    # Pokus o smazání řádku, který neexistuje
    cursor.execute("DELETE FROM test_ukoly WHERE id = %s", (9999,))
    conn.commit()

    # Ověříme, že tabulka je prázdná, tj. žádné řádky nebyly smazány, protože žádné neexistovaly
    cursor.execute("SELECT * FROM test_ukoly")
    results = cursor.fetchall()
    assert len(results) == 0, "Tabulka by měla zůstat prázdná."
