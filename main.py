from __future__ import annotations
import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo, showerror
from itertools import product
from minesweeper_model import MinesweeperModel
from stop_watch import StopWatch


class ControlPanel(tk.Frame):
    def __init__(self, master: MineSweeper, **options):
        super().__init__(master, **options)
        self.master: MineSweeper = master
        # A vezérlőpanel sáv grafikus elemeinek létrehozása.
        common_options = dict(font=('Helvetica', 12, 'bold'))
        self.flag_counter_lbl = tk.Label(self, textvariable=self.master.flag_counter, bg='black', fg='yellow', width=5, **common_options)
        self.new_game_btn = tk.Button(self, text='ÚJ JÁTÉK', **common_options, command=self.master.start_new_game)
        self.new_game_btn.bind('<Button 3>', lambda event: self.master.size_new_gamefield())
        self.playing_time_lbl = tk.Label(self, textvariable=self.master.playing_time, bg='silver', fg='blue', width=7, **common_options)
        # A vezérlőpanel sáv grafikus elemeinek lehelyezése.
        self.flag_counter_lbl.grid(row=0, column=0, sticky='news')
        self.new_game_btn.grid(row=0, column=1, sticky='news')
        self.playing_time_lbl.grid(row=0, column=2, sticky='news')
        self.grid_columnconfigure([0, 2], weight=1, uniform='a', pad=0)
        self.grid_columnconfigure(1, weight=1)


class GameField(tk.Frame):
    def __init__(self, master: MineSweeper, **options):
        super().__init__(master, **options)
        self.master: MineSweeper = master
        # Az időmérő működésre kész induló állapotba hozása.
        self.stop_watch = self.master.stop_watch
        self.stop_watch.reset()
        # A masterből átvett, szükséges példányattribútumok.
        self.model = self.master.model
        self.rowcount, self.columncount = self.master.rowcount, self.master.columncount
        self.cell_size = self.master.cell_size
        self.flag_counter = self.master.flag_counter
        # Az egyéb szükséges példányattribútumok.
        self.current_widget = None  # Az aktuálisan kiválasztott cella widget-je.
        self.is_first_cell = True
        self.visited_coords = set()  # A már felfedezett (meglátogatott) cellák koordinátái.
        # Egy adott cella szomszédságában levő aknák számát jelző számjegyek színei.
        self.num_colors = {1: 'blue', 2: 'green', 3: 'red', 4: 'salmon', 5: 'orange', 6: 'brown', 7: 'black', 8: 'gray'}
        # Új játék indításához az előző tábla grafikus elemeit eltávolítjuk, ha voltak ilyenek.
        for widget in self.winfo_children():
            widget.destroy()
        # A cellák számának megfelelő mennyiségű Canvas példány létrehozása a meghatározott méretű négyzet alakban.
        canvas_configs = dict(bd=6, relief=tk.RAISED, highlightthickness=0)
        canvases = (tk.Canvas(self, width=self.cell_size, height=self.cell_size, **canvas_configs)
                    for _ in range(len(self.model)))
        # A Canvas példányok lehelyezése táblázatos elrendezésben, valamint a bal és jobb egérgomblenyomás
        # események és a meghívott eseményekezők hozzárendelése.
        for cnv, grid_coords in zip(canvases, product(range(self.rowcount), range(self.columncount))):
            ri, ci = grid_coords
            cnv.grid(row=ri, column=ci, sticky='news')
            cnv.bind('<Button 1>', self._on_cell_left_click)
            cnv.bind('<Button 3>', self._on_cell_right_click)
        # A táblázat sorai és oszlopai minimális méretének beállítása az aktuális cellaméret és a Canvas példány szegélyvastagsága alapján.
        self.grid_rowconfigure('all', minsize=self.cell_size + float(2 * canvas_configs.get('bd')))
        self.grid_columnconfigure('all', minsize=self.cell_size + float(2 * canvas_configs.get('bd')))
        # Az adott számú akna véletlenszerű elhelyezése a cellákban, és az aknaszám mint kezdőérték kiírása a zászlószámlálón.
        self.model.generate_mines_randomly()
        self.flag_counter.set(self.model.minecount)

    def _clear_cell_event_bindings(self):
        """A játékmező összes grafikus elemét eseményérzéketlenné teszi."""
        for wg in self.winfo_children():
            wg.unbind('<1>')
            wg.unbind('<3>')

    def _is_victory_condition_met(self):
        """True értékkel tér vissza, ha a győzelmi feltétel teljesül, vagyis a nem felfedett cellák száma megegyezik az aknák számával."""
        return len(self.model) - len(self.visited_coords) == self.model.minecount

    def _on_cell_left_click(self, event):
        """Bal egérgomb kattintás eseménykezelője."""
        # Azonosítjuk az eseménnyel érintett widgetet, és meghatározzuk a tartalmazó cella sor- és oszlopindexeit.
        self.current_widget = event.widget
        ri, ci = self.current_widget.grid_info().get('row'), self.current_widget.grid_info().get('column')

        if self.is_first_cell:
            if self.model.get_value(ri, ci):
                # Ha a kiválasztott mező az első és ezen akna van, akkor addig helyezzük újra az aknákat, hogy ezen a mezőn ne legyen.
                while self.model.gridcoords_to_virtual_list_index(ri, ci) in self.model.virtual_list_indexes_of_mines:
                    self.model.generate_mines_randomly()
            # A legelső cella kiválasztásakor indítjuk az időmérőt.
            self.stop_watch.start()
            self.is_first_cell = False

        if self.model.get_value(ri, ci):
            # Ha a kiválasztott mezőn akna van, akkor a játék vereséggel véget ér.
            self._end_game_defeat()
            return

        # A kiválasztott, azaz felfedett cellának megváltoztatjuk a kinézetét.
        self.current_widget.config(relief=tk.SOLID, bd=1, bg='white')
        # A cellát megjelöljük felfedettnek (látogatottként) eltárolva a rácskoordinátáit.
        self.visited_coords.add((ri, ci))

        # Ha a kiválasztott cella szomszédai között van legalább egy akna, akkor a mezőre kiírjuk a szomszédos aknák számát.
        if mine_count := self.model.number_of_mines_in_adjacent_cells(ri, ci):
            self._show_minecount_on_current_cell(mine_count)
        else:
            # Ha a kiválasztott cella szomszédain nincs akna, akkor automatikusan felfedjük az összes cellát, amelyeken
            # nincs akna, mindaddig, amíg olyan cellákat nem találunk, amelyeknek a szomszédságában van legalább egy akna.
            # Az ilyen cellákra a szomszédos aknák száma kiírásra kerül.
            self._explore_safe_fields(ri, ci)

        # Ha az aktuális cellára kattintás után teljesül a nyerési feltétel, akkor a játék ennek megfelelően véget ér.
        if self._is_victory_condition_met():
            self._end_game_wictory()

    def _explore_safe_fields(self, ri, ci):
        """Felfedi az összes olyan cellát, amelyeken nincs akna, mindaddig, amíg olyan cellákat nem találunk, amelyeknek a
        szomszédságában van legalább egy akna. Az ilyen cellákra a szomszédos aknák száma kiírásra kerül.
        """
        # Az alkalmazott algoritmus:
        # 1. Nézd meg, hogy az aktuális, (ri, ci) rácskoordinátájú cella szomszédai tartalmaznak-e aknát.
        # 2a. Ha igen,
        # - írd ki az aktuális cellában a szomszédos aknák számát. Lépj ki az eljárásból és
        #   várj a köv. cellakiválasztásra.
        # 2b. Ha nem, azaz nincs a szomszédban akna, akkor
        # - vedd sorban egymás után az aktuális cella még fel nem fedett szomszédait,
        # - minden egyes szomszéd cellára, annak koordinátáját véve aktuális cellának
        #   ismételd meg az 1. ponttól. (vagyis hívd meg ezen koordinátákkal e metódust újra).

        adj_ri, adj_ci = ri, ci
        # Ha a kiválasztott cella szomszédai között van legalább egy akna, akkor a mezőre kiírjuk a
        # szomszédos aknák számát és visszatérünk e metódusból.
        if mine_count := self.model.number_of_mines_in_adjacent_cells(adj_ri, adj_ci):
            self._show_minecount_on_current_cell(mine_count)
        else:
            # Ha a szomszédok között nincs akna, akkor sorra vesszük a még nem felfedett szomszédokat, és megnézzük, hogy
            # azokban hány akna van. Ha azokban sincs akna, akkor tovább folytatjuk azok szomszédaival.
            for adj_ri, adj_ci in (set(self.model.adjacent_cells_coords(adj_ri, adj_ci)) - self.visited_coords):
                self.current_widget: tk.Canvas = self.grid_slaves(adj_ri, adj_ci)[0]
                # A felfedett cellának megváltoztatjuk a kinézetét.
                self.current_widget.config(relief=tk.SOLID, bd=1, bg='white')
                # A cellát megjelöljük felfedettnek eltárolva a rácskoordinátáit.
                self.visited_coords.add((adj_ri, adj_ci))
                # Ha a cella felfedése nyerő helyzetet terent, akkor kilépünk, egyébként pedig folytatjuk a cellák felfedését
                # az aktuális rácskoordinátájú cellától kiindulva.
                if self._is_victory_condition_met():
                    return
                else:
                    self._explore_safe_fields(adj_ri, adj_ci)

    def _end_game_wictory(self):
        """Sikeres játék esetén meghívott metódus, amely leállítja az időmérést, feldob egy üzenetablakot,
        és eseményérzéketlenné teszi a cellákat."""
        self.stop_watch.stop()
        showinfo('a játék eredménye'.upper(), 'NYERTÉL!', detail='Minden aknát feldezetél.')
        self._clear_cell_event_bindings()

    def _end_game_defeat(self):
        """Sikertelen játék esetén meghívott metódus, amely kirajzolja az aknát, leállítja az időmérést,
        feldob egy üzenetablakot, és eseményérzéketlenné teszi a cellákat."""
        self._draw_mine_symbol_in_current_cell()
        self.stop_watch.stop()
        self._clear_cell_event_bindings()
        showinfo('a játék eredménye'.upper(), 'Aknára léptél, ezért vesztettél!')

    def _draw_mine_symbol_in_current_cell(self):
        """Az aktuális cellában egy akna szimbólumot rajzol ki."""
        w, h = self.current_widget.winfo_width(), self.current_widget.winfo_height()
        r = w / 4
        cpx, cpy = w / 2, h / 2
        x1, y1 = w / 2 - r, h / 2 - r
        x2, y2 = w / 2 + r, h / 2 + r
        self.current_widget.create_oval((x1, y1), (x2, y2), fill='black')
        c = 1.4
        a = c * r * 3 ** 0.5
        self.current_widget.create_polygon((cpx, cpy - c * r), (cpx + a / 2, cpy + c * r / 2),
                                           (cpx - a / 2, cpy + c * r / 2), fill='black')
        self.current_widget.create_polygon((cpx, cpy + c * r), (cpx - a / 2, cpy - c * r / 2),
                                           (cpx + a / 2, cpy - c * r / 2), fill='black')

    def _show_minecount_on_current_cell(self, mine_count):
        """Az aktuális cellában egy címkén megjeleníti a szomszédos cellákban található aknák számát."""
        cnv_size = self.current_widget.winfo_height()
        lb = tk.Label(self.current_widget, text=str(mine_count), font=('Tahoma', round(cnv_size * 40 / 80), 'bold'),
                      fg=self.num_colors[mine_count], bg='white')
        # A címke Canvasra helyezéséhez egy window rajzelemet készítünk a Canvason, amibe a címkét tesszük.
        self.current_widget.create_window(cnv_size / 2, cnv_size / 2, window=lb, width=self.cell_size, height=self.cell_size)
        self.current_widget.unbind('<Button 1>')  # Az aktuális felfedett cellát eseményérzéketlenné tesszük.

    def _on_cell_right_click(self, event):
        """Jobb egérgomb kattintás eseménykezelője.
        Kattintásra az aktuális cellában megjelenít egy zászlót és a zászló számlálót, ami a még nem megjelenített
        zászlók számát tartja nyílván, eggyel csökkenti. Egy újabb kattintásra a zászló eltávolításra kerül és
        a zászló számláló eggyel nö."""
        current_widget: tk.Canvas = event.widget if type(event.widget) is tk.Canvas else event.widget.master
        cnv_size = current_widget.winfo_height()

        if not current_widget.gettags('flagwindow'):
            # Ha még nincs, a Canvas példányon egy címkét helyezünk le, ami egy zászló karakter ábrázol. Ehhez egy window
            # rajzelemet készítünk a Canvason, amibe a címkét tesszük.
            lb = tk.Label(current_widget, text=chr(0x1F6A9), font=('Courier', round(self.cell_size * 40 / 80), 'bold'))
            lb.bind('<Button 3>', self._on_cell_right_click)
            current_widget.create_window(cnv_size / 2, cnv_size / 2, height=self.cell_size, width=self.cell_size, window=lb,
                                         tags=('flagwindow',))
            # A flag számolót, ami a még nem megjelenített zászlók számát tartja nyílván, eggyel csökkentjük.
            self.flag_counter.set(self.flag_counter.get() - 1)
        else:
            # Ha a Canvas példányon már van zászlócímke egy window elemben, akkor azt töröljük.
            current_widget.delete('flagwindow')
            # A flag számolót eggyel visszanöveljük.
            self.flag_counter.set(self.flag_counter.get() + 1)


class MineSweeper(tk.Tk):
    def __init__(self, row_count=8, column_count=8, mine_count=None):
        super().__init__()
        self.title('Aknakereső')
        self.resizable(False, False)
        # A modellobjektum létrehozása.
        self.model = MinesweeperModel(row_count, column_count, mine_count)
        self.rowcount, self.columncount, self.minecount = row_count, column_count, self.model.minecount
        # Az aknajelölés (zászlók) számlálójának és a játékidő megjelenítés kontrollváltozók létrehozása.
        self.flag_counter = tk.IntVar(self, value=0, name='flagcounter')
        self.playing_time = tk.StringVar(self, value='00:00', name='playingtime')
        # A játékidőmérő létrehozása.
        self.stop_watch = StopWatch(self, self.playing_time)
        # A vezérlőpanel létrehozása és lehelyezése a főablakban.
        self.control_panel = ControlPanel(self, name='controlpanel', bd=10, relief=tk.RIDGE)
        self.control_panel.grid(row=0, column=0, sticky='news')
        # Az aktuális cellaméret meghatározása és a játékterület létrehozása és lehelyezése a főablakban.
        self.cell_size = self.calc_cell_size(self.rowcount, self.columncount)
        self.game_field = GameField(self, name='gamefield', bd=10, relief=tk.RIDGE)
        self.game_field.grid(row=1, column=0, sticky='news')

    @staticmethod
    def calc_cell_size(row_count, column_count):
        """Az aktuális sor- és oszlopszám alapján kiszámolja és visszaadja az alkalmazandó cellaméretet pixelben.
        Referencia az alapértelmezett 8 sorhoz és 8 oszlophoz tartozó méret."""
        return 40 * 8 / min(row_count, column_count)

    def start_new_game(self):
        """Új játék indítása. Leállítja az időmérőt, az aktuális modelladatok (sor-, oszlop-, aknaszám) alapján
        létrehozza az új játékterületet, véletlenszerűen elhelyezi a mezőcellákban az aknákat, és a zászlószámláló
        kezdőértékét az aknaszámra állítja.
        """
        self.stop_watch.stop()
        self.game_field = GameField(self, name='gamefield', bd=10, relief=tk.RIDGE)
        self.game_field.grid(row=1, column=0, sticky='news')

        self.model.generate_mines_randomly()
        self.flag_counter.set(self.model.minecount)

    def size_new_gamefield(self):
        """A megjelenő párbeszédablakban a játékterület méreteit (sor- és oszlopszám) és opcionálisan az aknák számát
        lehet megadni. Ha az aknaszám nincs megadva, akkor a megadott sor- és oszlopszámból kiadódó cellaszám egy, a modellben
        meghatározott aránya lesz az aknaszám. Alapértelmezett játékterület 8x8 méretű 10 aknával, ez jelenik meg a párbeszédablakban
        kezdőértékként. Az adatok helytelen megadása esetén egy felugró üzenetablak figyelmeztet erre.
        """
        self.stop_watch.stop()
        default = '8, 8, 10'
        input_string = askstring('A játékjellemzők meghatározása'.upper(),
                                 'Add meg vesszővel elválasztva a sor és oszlopszámot, valamint az aknák számát (opcionális)',
                                 initialvalue=default)
        txt = input_string if input_string else default
        try:  # Input szintaxis ellenőrzése.
            self.rowcount, self.columncount, *minecount = (int(c) for c in txt.strip(',').split(','))
            self.minecount = int(minecount[0]) if minecount else None
        except ValueError:
            showerror(f'játékjellemző megadási hiba'.upper(), 'Hibás sor-, oszlop-, vagy aknaszám megadás.')
            return
        try:  # Csak a modell szerint helyes adatokkal indul újra a játék.
            self.model = MinesweeperModel(self.rowcount, self.columncount, self.minecount)
            self.cell_size = self.calc_cell_size(self.rowcount, self.columncount)
            self.start_new_game()
        except ValueError as exc:
            showerror(f'játékjellemző értékadási hiba'.upper(), 'Nem megfelelő sor-, oszlop-, vagy aknaszám.',
                      detail=exc)

    def run(self):
        self.mainloop()


MineSweeper().run()
