from itertools import product
from random import randint


class MinesweeperModel:
    """Az aknakereső játék cellamezőit modellező osztály bináris mátrixként megvalósítva, ahol az 1 értékek az
    elhelyezett aknákat jelentik.
    """

    def __init__(self, row_count: int, column_count: int, mine_count: int | None = None):
        # A sor és oszlopok száma 8 vagy nagyobb egész szám, az aknák száma pozitív egész, ami kisebb, mint a cellák száma.
        if not isinstance(row_count, int) or not isinstance(column_count, int) or row_count < 8 or column_count < 8:
            raise ValueError('A sorok és oszlopok száma egy legalább 8 értékű egész szám kell, hogy legyen.')
        if mine_count is not None and (not isinstance(mine_count, int) or mine_count <= 0):
            raise ValueError('Az aknák száma pozitív egész szám kell, hogy legyen.')
        self.rowcount, self.columncount = row_count, column_count
        # Ha nincs megadva aknaszám, akkor ez a cellaszámmal úgy lesz arányos, ahogy a 10 akna a 8x8-as tábla 64 cellájával.
        minecount = int(len(self) * 10 / 64) if mine_count is None else mine_count
        if minecount >= len(self):
            raise ValueError('Az aknák száma kisebb kell, hogy legyen a cellák számánál.')
        self.minecount = minecount
        self.virtual_list_indexes_of_mines = set()  # Az aknák indexei a bináris mátrixot leképező virtuális listában.

    def __str__(self):
        return ''.join([str(self.get_value(*self.virtual_list_index_to_gridcoords(i))) + ('\n' if (i + 1) % self.columncount == 0 else ' ')
                        for i in range(len(self))])

    def _check_indexes(self, row_index: int, column_index: int):
        """A sor- és oszlopindexek helyességét ellenőrző segédmetódus."""
        if not isinstance(row_index, int):
            raise TypeError('A sorindex nem egész szám.')
        if not isinstance(column_index, int):
            raise TypeError('Az oszlopindex nem egész szám.')
        if row_index not in range(self.rowcount):
            raise IndexError(f'A sorindex a 0..{self.rowcount - 1} tartományon kívül esik.')
        if column_index not in range(self.columncount):
            raise IndexError(f'Az oszlopindex a 0..{self.columncount - 1} tartományon kívül esik.')

    def generate_mines_randomly(self):
        """Adott számú akna véletlenszerű elhelyezése a cellákban."""
        self.virtual_list_indexes_of_mines.clear()
        while len(self.virtual_list_indexes_of_mines) != self.minecount:
            self.virtual_list_indexes_of_mines.add(randint(0, len(self) - 1))

    def gridcoords_to_virtual_list_index(self, row_index, column_index) -> int:
        """A cellarács koordinátáinak (sor- és oszlopindex pár) megfelelő virtuális listaindexszel tér vissza."""
        self._check_indexes(row_index, column_index)
        return self.columncount * row_index + column_index

    def virtual_list_index_to_gridcoords(self, virtual_list_index) -> tuple:
        """A virtuális listaindexnek megfelelő cellarács koordinátákkal (sor- és oszlopindex pár) tér vissza."""
        if virtual_list_index not in range(len(self)):
            raise ValueError("Érvénytelen virtuális lista index.")
        return divmod(virtual_list_index, self.columncount)

    def adjacent_cells_coords(self, row_index, column_index) -> list[tuple[int, int]]:
        """Az argumentumban megadott sor- és oszlopindexekkel azonosított cella szomszédainak sor- és oszlopindexeit
        tartalmazó tuple-okat adja vissza egy listában.
        """
        self._check_indexes(row_index, column_index)
        return [(ri, ci) for ri, ci in product(range(row_index - 1, row_index - 1 + 3), range(column_index - 1, column_index - 1 + 3))
                if ri in range(self.rowcount) and ci in range(self.columncount) and (ri, ci) != (row_index, column_index)]

    def number_of_mines_in_adjacent_cells(self, row_index, column_index) -> int:
        """Visszaadja, hogy az argumentumban megadott sor- és oszlopindexekkel azonosított cella szomszédai
        összesen hány aknát tartalmaznak.
        """
        self._check_indexes(row_index, column_index)
        return sum(self.get_value(*cell_coords) for cell_coords in self.adjacent_cells_coords(row_index, column_index))

    def get_value(self, row_index, column_index):
        """Visszaadja megadott sor- és oszlopindexekkel azonosított cella értékét."""
        self._check_indexes(row_index, column_index)
        return 1 if self.gridcoords_to_virtual_list_index(row_index, column_index) in self.virtual_list_indexes_of_mines else 0

    def __len__(self):
        """Visszaadja cellák számát."""
        return self.columncount * self.rowcount


# TEST
if __name__ == '__main__':
    model = MinesweeperModel(12, 24, 30)

    print(model)

    print(sorted(model.virtual_list_indexes_of_mines))
    print(*[model.virtual_list_index_to_gridcoords(i) for i in sorted(model.virtual_list_indexes_of_mines)])
    print(model.adjacent_cells_coords(4, 7))
    print(model.gridcoords_to_virtual_list_index(1, 7))
