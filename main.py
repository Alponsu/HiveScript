from components.gui.ide import HiveScriptIDE
import tkinter as tk


def toggle_fullscreen(event=None):
    # Toggle fullscreen state
    current_state = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not current_state)


def end_fullscreen(event=None):
    # Exit fullscreen by pressing Escape key
    root.attributes("-fullscreen", False)


if __name__ == "__main__":
    root = tk.Tk()
    ide = HiveScriptIDE(root)

    root.geometry("800x600")  # Optional: Set initial window size before toggling fullscreen
    root.bind("<F11>", toggle_fullscreen)  # Press F11 to toggle fullscreen
    root.bind("<Escape>", end_fullscreen)  # Press Escape to exit fullscreen

    root.mainloop()
