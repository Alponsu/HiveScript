from components.gui.ide import HiveScriptIDE
import tkinter as tk


def toggle_fullscreen(event=None):
    current_state = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not current_state)


def end_fullscreen(event=None):
    root.attributes("-fullscreen", False)


if __name__ == "__main__":
    root = tk.Tk()
    ide = HiveScriptIDE(root)

    root.geometry("800x600")
    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", end_fullscreen)

    root.mainloop()
