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


if __name__ == '__main__':
    root = tk.Tk()
    # Több órát is lehet egyidejüleg függetlenül működtetni, és leállítani.
    var1, var2 = tk.StringVar(root), tk.StringVar(root)
    sw1, sw2 = StopWatch(root, var1), StopWatch(root, var2)
    tk.Label(root, textvariable=var1).pack()
    tk.Label(root, textvariable=var2).pack()
    tk.Button(root, text='Stop1', command=sw1.stop).pack()
    tk.Button(root, text='Stop2', command=sw2.reset).pack()
    sw1.start()
    sw2.start()
    root.mainloop()

# Ez nem valódi rekurzió:
# https://stackoverflow.com/questions/44710233/tkinters-after-and-recursion
# Az after használható animációra is: https://stackoverflow.com/questions/51227992/using-tkinter-after-to-produce-an-animation
# https://flylib.com/books/en/2.723.1/time_tools_threads_and_animation.html
