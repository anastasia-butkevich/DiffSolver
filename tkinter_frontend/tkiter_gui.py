import requests
import threading
import os

import tkinter as tk
import sympy as sp

from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv("API_URL")


class CalculatorApp:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.title("ODE Calculator")
        self.main_window.geometry("1000x700")
        self.tab_control = ttk.Notebook(self.main_window)

        self.res_tab = ResultsTab(self.tab_control, self)
        self.post_tab = PostTab(self.tab_control, self)

        self.tab_control.add(self.res_tab, text="Calculate")
        self.tab_control.add(self.post_tab, text="Create Entry")
        self.tab_control.pack(expand=1, fill="both")

        self.main_window.mainloop()


class ResultsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.equation_names = []
        self.equation_data = {}

        self.setup_ui()
        self.fetch_equations()

    def setup_ui(self):
        ttk.Label(self, text="Select Equation:").pack(pady=5)

        self.equation_combobox = ttk.Combobox(self, state="readonly")
        self.equation_combobox.pack(pady=5)

        self.calculate_button = ttk.Button(self, text="Calculate", command=self.calculate)
        self.calculate_button.pack(pady=10)

        # Results Frame
        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10, fill="both", expand=True)

        # Table container frame
        self.table_container = ttk.Frame(self.results_frame)
        self.table_container.pack(side="left", fill="y", padx=5, pady=5)

        # Table 1
        self.table_frame1 = ttk.Frame(self.table_container)
        self.table_frame1.pack(side="top", pady=5)

        self.label1 = ttk.Label(self.table_frame1, text="Euler")
        self.label1.pack(side="top", pady=2)

        self.scrollbar1_y = ttk.Scrollbar(self.table_frame1, orient="vertical")
        self.table1 = ttk.Treeview(
            self.table_frame1,
            columns=("x", "y"),
            show="headings",
            yscrollcommand=self.scrollbar1_y.set,
            height=10,
        )
        self.table1.heading("x", text="x")
        self.table1.heading("y", text="y")
        self.scrollbar1_y.config(command=self.table1.yview)
        self.table1.pack(side="left", fill="y", padx=5)
        self.scrollbar1_y.pack(side="left", fill="y")

        # Table 2
        self.table_frame2 = ttk.Frame(self.table_container)
        self.table_frame2.pack(side="top", pady=5)

        self.label2 = ttk.Label(self.table_frame2, text="Euler-Cauchy")
        self.label2.pack(side="top", pady=2)

        self.scrollbar2_y = ttk.Scrollbar(self.table_frame2, orient="vertical")
        self.table2 = ttk.Treeview(
            self.table_frame2,
            columns=("x", "y"),
            show="headings",
            yscrollcommand=self.scrollbar2_y.set,
            height=10,
        )
        self.table2.heading("x", text="x")
        self.table2.heading("y", text="y")
        self.scrollbar2_y.config(command=self.table2.yview)
        self.table2.pack(side="left", fill="y", padx=5)
        self.scrollbar2_y.pack(side="left", fill="y")

        # Plot frame
        self.plot_frame = ttk.Frame(self.results_frame)
        self.plot_frame.pack(side="right", fill="both", padx=10, pady=5)

        self.plot_placeholder()

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

        self.table1.delete(*self.table1.get_children())
        for x, y in zip(x1_res, y1_res):
            self.table1.insert("", "end", values=(f"{x:.4f}", f"{y:.4f}"))

        self.table2.delete(*self.table2.get_children())
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
        ax.set_title(rf"Euler curves for function: {self.equation_data[self.selected_name]['func']}")
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
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title("No data available")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.minorticks_on()
        ax.grid(which='major', linewidth=1.2)
        ax.grid(which='minor', linewidth=0.5)

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class PostTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Create New Entry", font=("Arial", 14)).pack(pady=10)

        self.fields = {
            "name": tk.StringVar(),
            "func": tk.StringVar(),
            "x0": tk.StringVar(),
            "y0": tk.StringVar(),
            "b": tk.StringVar(),
            "h": tk.StringVar(),
        }

        labels = ["Entry Name:", "Function:", "Value of x0:", "Value of y0:", "End value:", "Step size:"]

        for field, var in zip(labels, self.fields.values()):
            frame = ttk.Frame(self)
            frame.pack(pady=5, fill="x", anchor="center")  

            label = ttk.Label(frame, text=field)
            label.pack(side="top", padx=5)

            entry = ttk.Entry(frame, width=30, textvariable=var)
            entry.pack(side="top", padx=5, pady=5)

        self.submit_button = ttk.Button(self, text="Submit", command=self.submit_entry)
        self.submit_button.pack(pady=10)

        self.feedback_label = ttk.Label(self, text="", foreground="red")
        self.feedback_label.pack()

    def submit_entry(self):
        data = {key: var.get() for key, var in self.fields.items()}
    
        # Validate required
        errors = []
        for field, value in data.items():
            if not value:  
                errors.append(f"{field.capitalize() if len(field) > 2 else field} is required.")

        # Validate numeric fields
        try:
            x0 = float(data['x0']) if data['x0'] else None
        except ValueError:
            errors.append("x0 must be a valid number.")
        else:
            data['x0'] = x0

        try:
            y0 = float(data['y0']) if data['y0'] else None
        except ValueError:
            errors.append("y0 must be a valid number.")
        else:
            data['y0'] = y0

        try:
            b = float(data['b']) if data['b'] else None
        except ValueError:
            errors.append("b must be a valid number.")
        else:
            data['b'] = b

        try:
            h = float(data['h']) if data['h'] else None
        except ValueError:
            errors.append("h must be a valid number.")
        else:
            data['h'] = h

        # Check for unique name
        name = data["name"]
        if name in self.app.res_tab.equation_names:
            errors.append("Name must be unique.")

        # Validate function 
        func = data["func"]
        if func:
            try:
                expression = sp.sympify(func)

                free_vars = expression.free_symbols
                required_vars = {sp.symbols("x"), sp.symbols("y")}
                if not required_vars.issubset(free_vars):
                    errors.append("Function must contain 'x' and 'y' as variables.")
            except (sp.SympifyError, TypeError):
                errors.append("Function is not a valid mathematical expression.")

        if h is not None and h <= 0:
            errors.append("Step size 'h' must be a positive value.")
        if b is not None and x0 is not None and b <= x0:
            errors.append("'b' must be greater than 'x0'.")

        if errors:
            self.feedback_label.config(text="\n".join(errors), foreground="red")
            return
        
        submission_data = {
            "name": name,
            "func": func,
            "x0": x0,
            "y0": y0,
            "b": b,
            "h": h,
        }

        try:
            response = requests.post(API_URL, json=submission_data)
            response.raise_for_status()
            self.feedback_label.config(text="Entry successfully created!", foreground="green")
            self.app.res_tab.fetch_equations()
        except requests.exceptions.RequestException as e:
            self.feedback_label.config(text=f"Error: {e}", foreground="red")


if __name__ == "__main__":
    CalculatorApp()
