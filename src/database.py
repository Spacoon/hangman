from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
engine = create_engine("sqlite:///hangman.db")
Session = sessionmaker(bind=engine)

class User(Base):
    """
    Tabela użytkowników.
    Przechowuje dane użytkowników, takie jak
    nazwa użytkownika i hasło.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    games = relationship("Game", back_populates="user")

class Game(Base):
    """
    Tabela informacji o grach.
    Przechowuje informacje takie jak: słowo do odgadnięcia, liczba błędów,
    oraz czy gra została wygrana i klucz obcy do użytkownika.
    """
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(String, nullable=False)
    mistakes = Column(Integer, default=0)
    won = Column(Boolean, default=False)
    user = relationship("User", back_populates="games")

class Word(Base):
    """
    Tabela słów używanych w grze.

    Przechowuje słowa wraz z ich kategorią.
    """
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    category = Column(String, nullable=False)

def init_db():
    """
    Inicjalizuje bazę danych, tworząc wszystkie tabele i słowa (tylko na początku jeśli
    nie istnieją). Słowa są dodawane z pliku 'words.json'.
    """
    Base.metadata.create_all(engine)
    session = Session()

    if session.query(Word).count() == 0:    # SELECT COUNT(1) FROM words
        words = read_words_file('../words.json')
        for word in words:
            session.add(Word(**word))
        session.commit()

    session.close()

def read_words_file(file):
    """
    Czyta plik
    :param file: scieżka do pliku ze słowami i kategoriami
    :return: lista dict {'word': _, 'category': _}
    """
    import json

    data = []

    with open(file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    for category, words in json_data.items():
        for w in words:
            data.append({"word": w, "category": category})

    return data
