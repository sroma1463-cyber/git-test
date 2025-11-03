import chess
import chess.engine
import pyautogui
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import os


class ChessComBot:
    def __init__(self):
        self.player_color = None
        self.engine_path = "/usr/games/stockfish"
        self.engine = None
        self.board = chess.Board()
        self.gui = None

        self.board_coords = {
            'left': 354, 'top': 190, 'right': 1124, 'bottom': 952,
            'square_width': 96, 'square_height': 95
        }

    def create_gui(self):
        self.gui = tk.Tk()
        self.gui.title("Шахматный Бот")
        self.gui.geometry("500x550")
        self.gui.configure(bg='#2b2b2b')
        self.gui.attributes('-topmost', True)

        style = ttk.Style()
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#e0e0e0')
        style.configure('TButton', background='#404040', foreground='#ffffff')

        title = ttk.Label(self.gui, text="Шахматный Бот", font=('Arial', 14, 'bold'))
        title.pack(pady=15)

        # ВЫБОР ЦВЕТА
        color_frame = ttk.Frame(self.gui)
        color_frame.pack(pady=10)
        ttk.Label(color_frame, text="Ваш цвет:", font=('Arial', 10)).pack(pady=5)

        color_btn_frame = ttk.Frame(color_frame)
        color_btn_frame.pack(pady=5)
        ttk.Button(color_btn_frame, text="Белые", command=self.set_white, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(color_btn_frame, text="Черные", command=self.set_black, width=12).pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(self.gui, text="Статус: Выберите цвет", font=('Arial', 11, 'bold'))
        self.status_label.pack(pady=10)

        # КНОПКИ
        btn_frame = ttk.Frame(self.gui)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Автоход", command=self.auto_move, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Лучший ход", command=self.suggest_move, width=15).pack(side=tk.LEFT, padx=5)

        # ПОЛЕ ВВОДА
        input_frame = ttk.Frame(self.gui)
        input_frame.pack(pady=15, fill=tk.X, padx=20)

        ttk.Label(input_frame, text="Ход противника (формат: e4, Nf3, h1 e4):",
                  font=('Arial', 9)).pack(anchor='w')
        input_row = ttk.Frame(input_frame)
        input_row.pack(fill=tk.X, pady=5)

        self.opponent_entry = ttk.Entry(input_row, width=15, background='#ffffff', foreground='#000000')
        self.opponent_entry.pack(side=tk.LEFT, padx=5)
        self.opponent_entry.bind('<Return>', lambda e: self.submit_opponent_move())

        ttk.Button(input_row, text="Ввести", command=self.submit_opponent_move, width=8).pack(side=tk.LEFT, padx=5)

        # ЛОГ
        log_frame = ttk.Frame(self.gui)
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        ttk.Label(log_frame, text="Лог действий:", font=('Arial', 10)).pack(anchor='w')

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            bg='#3a3a3a',
            fg='#e0e0e0',
            font=('Consolas', 8),
            insertbackground='white'
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self.gui.protocol("WM_DELETE_WINDOW", self.on_close)

        self.log("ШАХМАТНЫЙ БОТ ЗАПУЩЕН")
        self.log("Поддерживаемые форматы:")
        self.log("- Короткий: e4, Nf3, Bxc6, O-O")
        self.log("- Длинный: e2e4, g1f3, e7e5")
        self.log("- С пробелом: h1 e4, a7 a5")

        self.init_engine()

        # ФОКУС НА ПОЛЕ ВВОДА
        self.opponent_entry.focus_set()

        self.gui.mainloop()

    def set_white(self):
        self.player_color = 'white'
        self.log("Вы играете белыми")
        self.update_status()

    def set_black(self):
        self.player_color = 'black'
        self.log("Вы играете черными")
        self.update_status()

    def update_status(self):
        if not self.player_color:
            return
        self.status_label.config(text="Статус: Ваш ход" if self.is_my_turn() else "Статус: Ход противника")

    def convert_to_uci(self, move_input):
        """Конвертирует различные форматы ходов в UCI"""
        move_input = move_input.strip().lower()

        # Убираем пробелы и символы
        move_input = move_input.replace(" ", "").replace("x", "").replace("+", "").replace("#", "")

        # Если уже UCI формат (4 символа)
        if len(move_input) == 4 and move_input.isalpha():
            return move_input

        # Рокировка
        if move_input in ['oo', '0-0']:
            return 'e1g1' if self.player_color == 'white' else 'e8g8'
        if move_input in ['ooo', '0-0-0']:
            return 'e1c1' if self.player_color == 'white' else 'e8c8'

        # Короткая нотация (e4, Nf3, Bxc6)
        if len(move_input) in [2, 3, 4]:
            # Пешка (e4, exd5)
            if len(move_input) == 2 and move_input[0] in 'abcdefgh' and move_input[1] in '12345678':
                return self.find_pawn_move(move_input)

            # Фигура (Nf3, Bxc6, Qh4)
            if move_input[0] in 'NBRQK':
                return self.find_piece_move(move_input)

        return None

    def find_pawn_move(self, target_square):
        """Находит ход пешки по целевой клетке"""
        file_to = target_square[0]
        rank_to = int(target_square[1])

        # Определяем откуда могла пойти пешка
        if self.player_color == 'white':
            possible_ranks = [rank_to - 1, rank_to - 2] if rank_to in [3, 4] else [rank_to - 1]
        else:
            possible_ranks = [rank_to + 1, rank_to + 2] if rank_to in [4, 5] else [rank_to + 1]

        for rank_from in possible_ranks:
            if 1 <= rank_from <= 8:
                from_square = f"{file_to}{rank_from}"
                to_square = target_square
                move_uci = f"{from_square}{to_square}"

                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in self.board.legal_moves:
                        return move_uci
                except:
                    continue

        return None

    def find_piece_move(self, move_input):
        """Находит ход фигуры по короткой нотации"""
        piece_char = move_input[0]
        target_square = move_input[-2:]

        # Маппинг фигур
        piece_map = {'N': chess.KNIGHT, 'B': chess.BISHOP, 'R': chess.ROOK, 'Q': chess.QUEEN, 'K': chess.KING}
        piece_type = piece_map.get(piece_char)

        if not piece_type:
            return None

        # Ищем все легальные ходы этой фигурой на целевую клетку
        for move in self.board.legal_moves:
            if (self.board.piece_at(move.from_square) and
                    self.board.piece_at(move.from_square).piece_type == piece_type and
                    move.to_square == chess.parse_square(target_square)):
                return move.uci()

        return None

    def submit_opponent_move(self):
        move_input = self.opponent_entry.get().strip()
        if not move_input:
            return

        # Пробуем разные форматы
        move_uci = self.convert_to_uci(move_input)

        if not move_uci:
            # Если автоматическая конвертация не удалась, пробуем как есть
            move_uci = move_input.lower().replace(" ", "")

        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.log(f"Ход противника: {move_uci} ({move_input})")
                self.update_status()
                self.opponent_entry.delete(0, tk.END)

                if self.is_my_turn():
                    self.log("Делаю ответный ход...")
                    threading.Thread(target=self.delayed_auto_move, daemon=True).start()
            else:
                self.log(f"Неверный ход: {move_input}")
                self.log("Попробуй:")
                self.log("- e2e4 (полный формат)")
                self.log("- e4 (короткий для пешки)")
                self.log("- Nf3 (короткий для фигуры)")
                self.log("- O-O (рокировка)")
        except Exception as e:
            self.log(f"Ошибка формата: {move_input}")
            self.log("Доступные форматы: e4, Nf3, e2e4, O-O")

        self.opponent_entry.focus_set()

    def delayed_auto_move(self):
        time.sleep(1)
        self.auto_move()

    def init_engine(self):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            self.log("Stockfish загружен")
        except Exception as e:
            self.log(f"Ошибка Stockfish: {e}")

    def get_square_center(self, square):
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1

        if self.player_color == 'white':
            rank = 7 - rank

        x = self.board_coords['left'] + file * self.board_coords['square_width'] + self.board_coords[
            'square_width'] // 2
        y = self.board_coords['top'] + rank * self.board_coords['square_height'] + self.board_coords[
            'square_height'] // 2

        return x, y

    def make_move(self, move_uci):
        from_square = move_uci[:2]
        to_square = move_uci[2:4]

        self.log(f"Выполняю ход: {from_square} -> {to_square}")

        from_x, from_y = self.get_square_center(from_square)
        to_x, to_y = self.get_square_center(to_square)

        def move_mouse():
            pyautogui.moveTo(from_x, from_y, duration=0.2)
            time.sleep(0.1)
            pyautogui.mouseDown()
            time.sleep(0.1)
            pyautogui.moveTo(to_x, to_y, duration=0.3)
            time.sleep(0.1)
            pyautogui.mouseUp()
            time.sleep(0.5)

            self.log("Ход выполнен")
            self.update_status()
            self.gui.after(0, lambda: self.opponent_entry.focus_set())

        threading.Thread(target=move_mouse, daemon=True).start()

    def get_best_move(self):
        self.log("Stockfish анализирует...")
        try:
            result = self.engine.play(self.board, chess.engine.Limit(time=2.0))
            best_move = result.move
            self.log(f"Лучший ход: {best_move.uci()}")
            return best_move
        except Exception as e:
            self.log(f"Ошибка Stockfish: {e}")
            return None

    def is_my_turn(self):
        if not self.player_color:
            return False
        return (self.player_color == 'white') == self.board.turn

    def auto_move(self):
        if not self.player_color:
            self.log("Сначала выберите цвет")
            return

        best_move = self.get_best_move()
        if best_move:
            self.board.push(best_move)
            self.make_move(best_move.uci())

    def suggest_move(self):
        if not self.player_color:
            self.log("Сначала выберите цвет")
            return
        self.get_best_move()

    def on_close(self):
        if self.engine:
            self.engine.quit()
        self.gui.destroy()

    def log(self, message):
        if self.gui:
            self.log_area.insert(tk.END, f"{message}\n")
            self.log_area.see(tk.END)
        print(message)


if __name__ == "__main__":
    bot = ChessComBot()
    bot.create_gui()
