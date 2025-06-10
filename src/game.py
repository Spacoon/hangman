import sqlite3

DB_NAME = "hangman.db"

def get_random_word(category=None):
    """
    Zwraca losowe słowo z bazy danych z wybranej kategorii.
    :param category: nazwa kategorii, po której będziemy szukać w bazie danych
    :return: słowo wielkimi litegami
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT word FROM words WHERE category=? ORDER BY RANDOM() LIMIT 1", (category,))
    result = cursor.fetchone()
    word = result[0] if result else None
    conn.close()
    return word.upper() if word else None

def get_categories():
    """
    Wyszukuje i zwraca nazwy wszystkich kategorii w liście
    :return: Nazwy kategorii w liście
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM words")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def save_game(user_id, word, mistakes, won):
    """
    Dodaje to tabeli 'games' informacje o grze. Informacje te podajemy w parametrach
    :param user_id:
    :param word:
    :param mistakes:
    :param won:
    :return:
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO games (user_id, word, mistakes, won) VALUES (?, ?, ?, ?)",
                   (user_id, word, mistakes, int(won)))
    conn.commit()
    conn.close()
