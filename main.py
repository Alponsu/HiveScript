from components.gui.ide import HiveScriptIDE
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    ide = HiveScriptIDE(root)
    root.geometry("800x600")
    root.mainloop()
