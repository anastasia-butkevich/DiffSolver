import requests
import threading
import os

from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv("API_URL")


class ResultsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.equation_names = []
        self.equation_data = {}
        self.selected_name = None

        self.setup_ui()
        self.fetch_equations()

    def setup_ui(self):
        selection_frame = ttk.Frame(self)
        selection_frame.pack(pady=5, fill="x", padx=10)

        ttk.Label(selection_frame, text="Select Equation:").grid(row=0, column=0, sticky="w")
        self.equation_combobox = ttk.Combobox(selection_frame, state="readonly")
        self.equation_combobox.grid(row=0, column=1, sticky="ew", padx=5)
        selection_frame.columnconfigure(1, weight=1)

        self.calculate_button = ttk.Button(selection_frame, text="Calculate", command=self.calculate)
        self.calculate_button.grid(row=0, column=2, padx=5)

        results_area = ttk.Frame(self)
        results_area.pack(pady=10, fill="both", expand=True, padx=10)

        tables_frame = ttk.LabelFrame(results_area, text="Results Tables")
        tables_frame.pack(side="left", fill="y", padx=5, pady=5)

        self.table1, _ = self._create_table(tables_frame, "Euler", row=0)
        self.table2, _ = self._create_table(tables_frame, "Euler-Cauchy", row=1)

        self.plot_frame = ttk.LabelFrame(results_area, text="Plot")
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        self.plot_placeholder()

    def _create_table(self, parent, title, row):
        """Helper method to create a table with a title label and vertical scrollbar."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Label(frame, text=title).pack(pady=2)
        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        table = ttk.Treeview(
            frame,
            columns=("x", "y"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10,
        )
        table.heading("x", text="x")
        table.heading("y", text="y")
        table.pack(side="left", fill="y", padx=5)
        scrollbar.config(command=table.yview)
        scrollbar.pack(side="left", fill="y")
        return table, scrollbar

    def fetch_equations(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            equations = response.json()

            self.equation_names = [eq['name'] for eq in equations]
            self.equation_data = {eq['name']: eq for eq in equations}

            self.equation_combobox['values'] = ["Select"] + self.equation_names
            self.equation_combobox.set("Select")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Could not fetch equations: {e}")
        except ValueError:
            messagebox.showerror("Error", "Received invalid data from server.")

    def calculate(self):
        self.selected_name = self.equation_combobox.get()
        if self.selected_name == "Select" or not self.selected_name:
            messagebox.showerror("Error", "Please select a valid equation.")
            return

        equation = self.equation_data.get(self.selected_name)
        if not equation:
            messagebox.showerror("Error", "Selected equation not found.")
            return

        try:
            url = f"{API_URL}{equation['id']}"
            response = requests.get(url)
            response.raise_for_status()
            results = response.json()
            self.display_results(results)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Calculation failed: {e}")

    def display_results(self, results):
        x1_res = results.get('x1_res', [])
        y1_res = results.get('y1_res', [])
        x2_res = results.get('x2_res', [])
        y2_res = results.get('y2_res', [])

        for table in [self.table1, self.table2]:
            table.delete(*table.get_children())

        for x, y in zip(x1_res, y1_res):
            self.table1.insert("", "end", values=(f"{x:.4f}", f"{y:.4f}"))
        for x, y in zip(x2_res, y2_res):
            self.table2.insert("", "end", values=(f"{x:.4f}", f"{y:.4f}"))

        self.plot_results(x1_res, y1_res, x2_res, y2_res)

    def plot_results(self, x1_res, y1_res, x2_res, y2_res):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(x1_res, y1_res, label="Euler method", marker="o", color="black")
        ax.plot(x2_res, y2_res, label="Euler-Cauchy method", marker="o", color="blue")
        func = self.equation_data[self.selected_name]['func']
        ax.set_title(rf"Euler curves for function: {func}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.minorticks_on()
        ax.set_xlim(min(x1_res) - 0.5, max(x1_res) + 0.5)
        ax.set_ylim(min(y1_res) - 0.5, max(y1_res) + 0.5)
        ax.grid(which='major', linewidth=1.2)
        ax.grid(which='minor', linewidth=0.5)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_placeholder(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title("No data available")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.minorticks_on()
        ax.grid(which='major', linewidth=1.2)
        ax.grid(which='minor', linewidth=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
