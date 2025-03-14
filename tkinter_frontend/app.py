import threading
import os

import tkinter as tk

from tkinter import ttk
from dotenv import load_dotenv

from results_tab import ResultsTab
from post_tab import PostTab


load_dotenv()

API_URL = os.getenv("API_URL")


class CalculatorApp:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.title("ODE Calculator")
        self.main_window.geometry("1000x700")

        self.main_window.minsize(800, 600)
  
        self.style = ttk.Style(self.main_window)
        self.style.theme_use('clam')
        
        self.tab_control = ttk.Notebook(self.main_window)
        
        self.res_tab = ResultsTab(self.tab_control, self)
        self.post_tab = PostTab(self.tab_control, self)
        
        self.tab_control.add(self.res_tab, text="Calculate")
        self.tab_control.add(self.post_tab, text="Create Entry")
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
        self.main_window.mainloop()


if __name__ == "__main__":
    CalculatorApp()
    