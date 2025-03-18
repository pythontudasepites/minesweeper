from time import time, strftime, gmtime
import tkinter as tk
from typing import TypeAlias

GraphicalObject: TypeAlias = tk.Tk | tk.Toplevel | tk.Widget


class StopWatch:
    def __init__(self, master: GraphicalObject, controll_variable: tk.StringVar):
        self.start_time = 0
        self.master = master
        self.control_var = controll_variable
        self.id = None

    def start(self):
        """Időmérés indítása."""
        self.start_time = time()  # Az indításkori idő az epoch-tól számítva másodpercben.
        self._measure_time()  # Az idő mérésének megkezdése.

    def _measure_time(self):
        """Az indítástól eltelt időt méri folyamatosan.
        A kontrollváltozó értékét 1 másodpercenként aktualizálja az eltelt időt 00:00 (perc, másodperc)
        formátumú karakterláncként átadva.
        """
        elapsed_time = time() - self.start_time  # Az indítástól eltelt idő másodpercben.
        self.control_var.set(f'{strftime("%M:%S", gmtime(elapsed_time))}')
        # E metódus hívása 1000 ms eltelte után.
        # A visszaadott azonosító az ütemezett hívás after_cancel() metódussal való törléséhez
        # mint argumentum szükséges (ld. stop() metódusban)
        self.id = self.master.after(1000, self._measure_time)

    def stop(self):
        """Időmérés leállítása."""
        # Az after() metódussal indított, adott azonosítójú ütemezett hívás törlése.
        self.master.after_cancel(self.id)

    def reset(self):
        self.start()
        self.stop()


