import tkinter as tk
from tkinter import messagebox, ttk
from game import get_random_word, save_game, get_categories
import sqlite3
import hashlib

DB_NAME = "hangman.db"

SZARY = "#333333"
BIALY = "#FFFFFF"
CZERWONY = "#FF5555"
KOLPRZYCISKU = "#555555"

class HangmanApp:
    """
    Główna klasa aplikacji gry w wisielca.

    Zarządza interfejsem graficznym, logiką gry oraz komunikacją z bazą danych.
    """
    def __init__(self, root):
        """
        Inicjalizuje aplikację gry w wisielca.

        Args:
            root: Główne okno aplikacji Tkinter.
        """
        self.root = root
        self.root.title("Gra w Wisielca")
        self.root.geometry("400x600")
        self.root.configure(bg=SZARY)
        self.word = ""
        self.guessed = []
        self.mistakes = 0
        self.max_mistakes = 6
        self.user_id = None
        self.category = None
        self.canvas = None
        self.letters_buttons = {}
        self.game_mode = "classic"

        self.style = ttk.Style()
        self.style.configure('TCombobox', fieldbackground=SZARY, background=SZARY, foreground=BIALY)
        self.style.map('TCombobox', fieldbackground=[('readonly', SZARY)])
        self.style.map('TCombobox', selectbackground=[('readonly', KOLPRZYCISKU)])
        self.style.map('TCombobox', selectforeground=[('readonly', BIALY)])

        self.ekran_logowania()

    def ekran_logowania(self):
        """
        Tworzy i wyświetla ekran logowania z polami na nazwę użytkownika i hasło.
        """
        self.reset_okienka()
        frame = tk.Frame(self.root, bg=SZARY)
        frame.pack(expand=True, pady=50)

        tk.Label(frame, text="Nazwa użytkownika:", bg=SZARY, fg=BIALY, font=("Arial", 12)).pack(pady=(0, 5))
        self.username_entry = tk.Entry(frame, bg=SZARY, fg=BIALY, insertbackground=BIALY)
        self.username_entry.pack(pady=(0, 15))

        tk.Label(frame, text="Hasło:", bg=SZARY, fg=BIALY, font=("Arial", 12)).pack(pady=(0, 5))
        self.password_entry = tk.Entry(frame, show="*", bg=SZARY, fg=BIALY, insertbackground=BIALY)
        self.password_entry.pack(pady=(0, 20))

        btn_frame = tk.Frame(frame, bg=SZARY)
        btn_frame.pack(pady=10)

        login_btn = tk.Button(btn_frame, text="Zaloguj", command=self.login,
                              bg=KOLPRZYCISKU, fg=BIALY, activebackground=SZARY, activeforeground=BIALY)
        login_btn.pack(side=tk.LEFT, padx=10)

        register_btn = tk.Button(btn_frame, text="Zarejestruj", command=self.register,
                                 bg=KOLPRZYCISKU, fg=BIALY, activebackground=SZARY, activeforeground=BIALY)
        register_btn.pack(side=tk.LEFT, padx=10)

    def encrypt(self, password):
        """
        Szyfruje hasło użytkownika za pomocą algorytmu SHA-256.

        Args:
            password: Hasło w formie tekstowej.

        Returns:
            str: Zaszyfrowane hasło w postaci heksadecymalnej.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        """
        Obsługuje proces logowania użytkownika.

        Weryfikuje dane logowania z bazą danych i przechodzi do wyboru trybu gry,
        jeśli dane są poprawne. W przeciwnym razie wyświetla komunikat o błędzie.
        """
        username = self.username_entry.get()
        password = self.encrypt(self.password_entry.get())
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.user_id = user[0]
            self.wybierz_tryb()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowe dane logowania")

    def register(self):
        """
        Obsługuje proces rejestracji nowego użytkownika.

        Tworzy nowego użytkownika w bazie danych, jeśli nazwa użytkownika nie jest zajęta.
        W przeciwnym razie wyświetla komunikat o błędzie.
        """
        username = self.username_entry.get()
        password = self.encrypt(self.password_entry.get())
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Sukces", "Rejestracja zakończona pomyślnie")
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Nazwa użytkownika już istnieje")
        conn.close()

    def wybierz_tryb(self):
        """
        Wyświetla ekran wyboru trybu gry.

        Pozwala użytkownikowi wybrać między trybem klasycznym a "Uratuj wisielca".
        """
        self.reset_okienka()

        frame = tk.Frame(self.root, bg=SZARY)
        frame.pack(fill=tk.BOTH, expand=True, pady=40)

        tk.Label(frame, text="Wybierz tryb gry", font=("Arial", 18, "bold"),
                 bg=SZARY, fg=BIALY).pack(pady=20)

        modes_frame = tk.Frame(frame, bg=SZARY)
        modes_frame.pack(pady=20)

        classic_frame = tk.Frame(modes_frame, bg=SZARY)
        classic_frame.pack(pady=15)
        tk.Button(classic_frame, text="Klasyczny Wisielec",
                  command=lambda: self.ustaw_tryb("classic"),
                  font=("Arial", 12), width=20, bg=KOLPRZYCISKU, fg=BIALY,
                  activebackground=SZARY, activeforeground=BIALY).pack()
        tk.Label(classic_frame, text="Tradycyjny rysunek wisielca z 6 dozwolonymi błędami.",
                 font=("Arial", 10), bg=SZARY, fg=BIALY).pack()

        arrow_frame = tk.Frame(modes_frame, bg=SZARY)
        arrow_frame.pack(pady=15)
        tk.Button(arrow_frame, text="Uratuj wisielca",
                  command=lambda: self.ustaw_tryb("arrow"),
                  font=("Arial", 12), width=20, bg=KOLPRZYCISKU, fg=BIALY,
                  activebackground=SZARY, activeforeground=BIALY).pack()
        tk.Label(arrow_frame, text="Strzała zbliża się do ludzika z każdym błędem.",
                 font=("Arial", 10), bg=SZARY, fg=BIALY).pack()

    def ustaw_tryb(self, mode):
        """
        Ustawia wybrany tryb gry i przechodzi do ekranu wyboru kategorii.

        Args:
            mode: Wybrany tryb gry ("classic" lub "arrow").
        """
        self.game_mode = mode
        self.wybierz_kategorie()

    def wybierz_kategorie(self):
        """
        Wyświetla ekran wyboru kategorii słów.

        Pozwala użytkownikowi wybrać kategorię słów do odgadywania
        z dostępnych kategorii w bazie danych.
        """
        self.reset_okienka()

        frame = tk.Frame(self.root, bg=SZARY)
        frame.pack(pady=20)

        mode_text = "Klasyczny Wisielec" if self.game_mode == "classic" else "Uratuj wisielca"
        tk.Label(frame, text=f"Tryb gry: {mode_text}",
                 font=("Arial", 12), bg=SZARY, fg=BIALY).pack()
        tk.Label(frame, text="Wybierz kategorię:",
                 font=("Arial", 14), bg=SZARY, fg=BIALY).pack(pady=10)

        categories = get_categories()

        self.category_var = tk.StringVar(value="")
        category_dropdown = ttk.Combobox(frame, textvariable=self.category_var, values=categories,
                                         state="readonly", width=30)
        category_dropdown.pack(pady=5)

        self.error_label = tk.Label(frame, text="Wybierz kategorię, aby rozpocząć grę!",
                                    fg=CZERWONY, bg=SZARY, font=("Arial", 10))
        self.error_label.pack_forget()

        btn_frame = tk.Frame(frame, bg=SZARY)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Rozpocznij grę", command=self.start_game,
                  bg=KOLPRZYCISKU, fg=BIALY, activebackground=SZARY,
                  activeforeground=BIALY).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="Pokaż statystyki", command=self.statystyki,
                  bg=KOLPRZYCISKU, fg=BIALY, activebackground=SZARY,
                  activeforeground=BIALY).pack(side=tk.LEFT, padx=10)

        tk.Button(frame, text="Zmień tryb gry", command=self.wybierz_tryb,
                  bg=KOLPRZYCISKU, fg=BIALY, activebackground=SZARY,
                  activeforeground=BIALY).pack(pady=10)

    def start_game(self):
        """
        Rozpoczyna nową grę w wisielca po wybraniu kategorii.

        Inicjalizuje interfejs gry, losuje słowo z wybranej kategorii
        i przygotowuje planszę do odgadywania oraz wirtualną klawiaturę.
        Jeśli kategoria nie została wybrana, wyświetla komunikat o błędzie.
        """
        selected_category = self.category_var.get() if hasattr(self, 'category_var') else None

        if not selected_category:
            self.error_label.pack(pady=5)
            return

        self.reset_okienka()
        self.word = get_random_word(selected_category)
        self.guessed = ["_"] * len(self.word)
        self.mistakes = 0
        self.used_letters = set()

        main_frame = tk.Frame(self.root, bg=SZARY)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = tk.Frame(main_frame, bg=SZARY)
        top_frame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)

        tk.Label(top_frame, text=f"Kategoria: {selected_category}",
                 font=("Arial", 12), bg=SZARY, fg=BIALY).pack(pady=(0, 10))

        self.canvas = tk.Canvas(top_frame, width=280, height=220, bg="white")
        self.canvas.pack(pady=5)

        if self.game_mode == "classic":
            self.szubienica()
        else:
            self.scena_strzaly()

        middle_frame = tk.Frame(main_frame, bg=SZARY)
        middle_frame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10)

        self.word_label = tk.Label(middle_frame, text=" ".join(self.guessed),
                                   font=("Arial", 24), bg=SZARY, fg=BIALY)
        self.word_label.pack(pady=15)

        bottom_frame = tk.Frame(main_frame, bg=SZARY)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=10, pady=10)

        letters_frame = tk.Frame(bottom_frame, bg=SZARY)
        letters_frame.pack(fill=tk.X)

        self.letters_buttons = {}
        all_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        row_length = 9

        keyboard_container = tk.Frame(letters_frame, bg=SZARY)
        keyboard_container.pack(expand=True, fill=tk.X)

        for row_idx in range((len(all_letters) + row_length - 1) // row_length):
            row_frame = tk.Frame(keyboard_container, bg=SZARY)
            row_frame.pack(pady=2)

            start_idx = row_idx * row_length
            end_idx = min(start_idx + row_length, len(all_letters))

            padding = (row_length - (end_idx - start_idx)) / 2
            if padding > 0:
                tk.Frame(row_frame, width=padding*30, bg=SZARY).pack(side=tk.LEFT)

            for i in range(start_idx, end_idx):
                letter = all_letters[i]
                btn = tk.Button(row_frame, text=letter, width=2, height=1,
                                command=lambda l=letter: self.zgadnij_litere(l),
                                font=("Arial", 12), bg=KOLPRZYCISKU, fg=BIALY,
                                activebackground=SZARY, activeforeground=BIALY)
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                self.letters_buttons[letter] = btn

        tk.Button(bottom_frame, text="Powrót", command=self.wybierz_kategorie,
                  font=("Arial", 10), bg=KOLPRZYCISKU, fg=BIALY,
                  activebackground=SZARY, activeforeground=BIALY).pack(pady=(15, 0))

    def szubienica(self):
        """
        Rysuje szubienicę w trybie klasycznym.

        Tworzy początkowy rysunek szubienicy na płótnie Canvas.
        """
        self.canvas.create_line(20, 230, 180, 230, width=3)
        self.canvas.create_line(60, 230, 60, 30, width=3)
        self.canvas.create_line(60, 30, 130, 30, width=3)
        self.canvas.create_line(130, 30, 130, 50, width=3)

    def wisielec(self):
        """
        Rysuje elementy ciała wisielca w zależności od liczby popełnionych błędów.

        Dodaje kolejne części ciała postaci wisielca na szubienicy po każdym błędzie.
        """
        if self.mistakes >= 1:
            self.canvas.create_oval(115, 50, 145, 80, width=2)
        if self.mistakes >= 2:
            self.canvas.create_line(130, 80, 130, 150, width=2)
        if self.mistakes >= 3:
            self.canvas.create_line(130, 90, 100, 120, width=2)
        if self.mistakes >= 4:
            self.canvas.create_line(130, 90, 160, 120, width=2)
        if self.mistakes >= 5:
            self.canvas.create_line(130, 150, 100, 200, width=2)
        if self.mistakes >= 6:
            self.canvas.create_line(130, 150, 160, 200, width=2)

    def scena_strzaly(self):
        """
        Rysuje scenę w trybie "Uratuj wisielca".

        Tworzy postać ludzika oraz ustawia początkową pozycję strzały.
        """

        self.canvas.create_oval(130, 50, 170, 90, width=2)
        self.canvas.create_line(150, 90, 150, 160, width=2)
        self.canvas.create_line(150, 110, 130, 140, width=2)
        self.canvas.create_line(150, 110, 170, 140, width=2)
        self.canvas.create_line(150, 160, 130, 200, width=2)
        self.canvas.create_line(150, 160, 170, 200, width=2)

        self.arrow_x = 20
        self.arrow_y = 125
        self.strzala()

    def strzala(self):
        """
        Rysuje strzałę w trybie "Uratuj wisielca".

        Aktualizuje pozycję strzały w zależności od liczby popełnionych błędów.
        Im więcej błędów, tym bliżej ludzika znajduje się strzała.
        """
        self.canvas.delete("arrow")

        arrow_position = 20 + (self.mistakes * 20)

        self.canvas.create_line(arrow_position, 125, arrow_position + 30, 125, width=2, tags="arrow")
        self.canvas.create_line(arrow_position + 25, 120, arrow_position + 30, 125, width=2, tags="arrow")
        self.canvas.create_line(arrow_position + 25, 130, arrow_position + 30, 125, width=2, tags="arrow")

        if self.mistakes == 0:
            self.canvas.create_line(120, 125, 120, 125, width=1, tags="arrow")

        if self.mistakes >= 4:
            self.canvas.itemconfig("arrow", fill="red")

        if self.mistakes >= self.max_mistakes:
            self.canvas.create_line(150, 125, 170, 125, width=3, fill="red", tags="arrow")
            self.canvas.create_text(150, 190, text="KONIEC GRY!", fill="red", font=("Arial", 14, "bold"), tags="arrow")

    def zgadnij_litere(self, letter):
        """
        Obsługuje naciśnięcie przycisku z literą podczas gry.

        Sprawdza, czy wybrana litera występuje w haśle do odgadywania.
        Aktualizuje stan gry, rysunki i sprawdza warunki końcowe (wygrana/przegrana).

        Args:
            letter: Wybrana litera.
        """
        if letter in self.used_letters:
            return

        self.used_letters.add(letter)
        self.letters_buttons[letter].config(state=tk.DISABLED)

        if letter in self.word:
            for i, l in enumerate(self.word):
                if l == letter:
                    self.guessed[i] = letter
            self.word_label.config(text=" ".join(self.guessed))

            if "_" not in self.guessed:
                save_game(self.user_id, self.word, self.mistakes, True)
                messagebox.showinfo("Wygrana", "Odgadłeś słowo!")
                self.wybierz_kategorie()
        else:
            self.mistakes += 1

            if self.game_mode == "classic":
                self.wisielec()
            else:
                self.strzala()

            if self.mistakes >= self.max_mistakes:
                save_game(self.user_id, self.word, self.mistakes, False)
                messagebox.showinfo("Przegrana", f"Przegrałeś! Słowo to: {self.word}")
                self.wybierz_kategorie()

    def statystyki(self):
        """
        Wyświetla statystyki użytkownika.

        Pokazuje informacje o rozegranych grach, wygranych, procentowym wskaźniku
        zwycięstw oraz szczegółową historię gier z możliwością przewijania.
        """
        self.reset_okienka()

        stats_frame = tk.Frame(self.root, bg=SZARY)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tk.Label(stats_frame, text="Twoje statystyki gry",
                 font=("Arial", 16, "bold"), bg=SZARY, fg=BIALY).pack(pady=10)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM games WHERE user_id=?", (self.user_id,))
        total_games = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM games WHERE user_id=? AND won=1", (self.user_id,))
        total_wins = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(mistakes) FROM games WHERE user_id=?", (self.user_id,))
        avg_mistakes = cursor.fetchone()[0]

        win_percentage = (total_wins / total_games * 100) if total_games > 0 else 0

        summary_frame = tk.Frame(stats_frame, bg=SZARY)
        summary_frame.pack(pady=5, fill=tk.X)

        tk.Label(summary_frame, text=f"Łącznie gier: {total_games}",
                 font=("Arial", 11), bg=SZARY, fg=BIALY).pack(anchor="w")
        tk.Label(summary_frame, text=f"Wygranych: {total_wins}",
                 font=("Arial", 11), bg=SZARY, fg=BIALY).pack(anchor="w")
        tk.Label(summary_frame, text=f"Procent wygranych: {win_percentage:.1f}%",
                 font=("Arial", 11), bg=SZARY, fg=BIALY).pack(anchor="w")
        tk.Label(summary_frame, text=f"Średnia błędów: {avg_mistakes:.1f}" if avg_mistakes else "Średnia błędów: 0.0",
                 font=("Arial", 11), bg=SZARY, fg=BIALY).pack(anchor="w")

        tk.Label(stats_frame, text="Ostatnie gry:",
                 font=("Arial", 14), bg=SZARY, fg=BIALY).pack(pady=(10, 5))

        col_widths = [10, 5, 8]

        table_container = tk.Frame(stats_frame, bg=SZARY)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        headers_frame = tk.Frame(table_container, bg=SZARY)
        headers_frame.pack(fill=tk.X)

        headers = ["Słowo", "Błędy", "Wynik"]
        for i, header in enumerate(headers):
            tk.Label(headers_frame, text=header, font=("Arial", 10, "bold"),
                     width=col_widths[i], borderwidth=1, relief="solid",
                     bg=KOLPRZYCISKU, fg=BIALY).grid(row=0, column=i, padx=1)

        canvas_frame = tk.Frame(table_container, bg=SZARY)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, borderwidth=0, highlightthickness=0,
                           bg=SZARY)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)

        data_frame = tk.Frame(canvas, bg=SZARY)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas_window = canvas.create_window((0, 0), window=data_frame, anchor="nw", tags="data_frame")

        def config_canvas(event):
            canvas.itemconfig("data_frame", width=canvas.winfo_width())

        canvas.bind("<Configure>", config_canvas)

        def scroll_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        data_frame.bind("<Configure>", scroll_config)

        cursor.execute("""
            SELECT word, mistakes, won FROM games
            WHERE user_id=?
            ORDER BY id DESC
        """, (self.user_id,))
        games = cursor.fetchall()

        for i, game in enumerate(games):
            word, mistakes, won = game
            tk.Label(data_frame, text=word, width=col_widths[0], borderwidth=1, relief="solid",
                     bg=SZARY, fg=BIALY).grid(row=i, column=0, padx=1, pady=1)
            tk.Label(data_frame, text=str(mistakes), width=col_widths[1], borderwidth=1, relief="solid",
                     bg=SZARY, fg=BIALY).grid(row=i, column=1, padx=1, pady=1)
            tk.Label(data_frame, text="Wygrana" if won else "Przegrana", width=col_widths[2],
                     borderwidth=1, relief="solid", bg=SZARY,
                     fg="lightgreen" if won else CZERWONY).grid(row=i, column=2, padx=1, pady=1)

        conn.close()

        def scroll(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", scroll)

        tk.Button(stats_frame, text="Powrót do kategorii", command=self.wybierz_kategorie,
                  bg=KOLPRZYCISKU, fg=BIALY, activebackground=SZARY,
                  activeforeground=BIALY).pack(pady=10)

    def reset_okienka(self):
        """
        Czyści wszystkie widżety z głównego okna aplikacji.

        Służy do przygotowania ekranu na wyświetlenie nowego widoku.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
