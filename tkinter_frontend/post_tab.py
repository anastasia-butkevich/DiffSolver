import requests
import threading
import os

import tkinter as tk
import sympy as sp

from tkinter import ttk
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv("API_URL")


class PostTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self)
        container.pack(expand=True)

        title_label = ttk.Label(container, text="Create New Entry", font=("Arial", 14))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.fields = {
            "name": tk.StringVar(),
            "func": tk.StringVar(),
            "x0": tk.StringVar(),
            "y0": tk.StringVar(),
            "b": tk.StringVar(),
            "h": tk.StringVar(),
        }

        field_info = {
            "name": ("Entry Name:", "Unique identifier for your entry."),
            "func": ("Function:", "Enter a valid math expression including x and y."),
            "x0": ("Value of x0:", "Starting value for x."),
            "y0": ("Value of y0:", "Starting value for y."),
            "b": ("End Value:", "Value must be greater than x0."),
            "h": ("Step Size:", "A positive number representing the step size."),
        }

        row_index = 2
        for key, var in self.fields.items():
            field_frame = ttk.Frame(container)
            field_frame.grid(row=row_index, column=0, columnspan=2, pady=5, padx=5)

            field_label = ttk.Label(field_frame, text=field_info[key][0])
            field_label.pack(anchor="center")

            entry_widget = ttk.Entry(field_frame, width=30, textvariable=var)
            entry_widget.pack(anchor="center", pady=2)

            help_label = ttk.Label(
                field_frame, 
                text=field_info[key][1], 
                font=("Arial", 8, "italic"), 
                foreground="gray"
            )
            help_label.pack(anchor="center")
            row_index += 1

        self.submit_button = ttk.Button(container, text="Submit", command=self.submit_entry)
        self.submit_button.grid(row=row_index, column=0, columnspan=2, pady=10)
        row_index += 1

        self.feedback_label = ttk.Label(container, text="", foreground="red")
        self.feedback_label.grid(row=row_index, column=0, columnspan=2)

    def submit_entry(self):
        friendly_names = {
            "name": "Entry Name",
            "func": "Function",
            "x0": "Value of x0",
            "y0": "Value of y0",
            "b": "End Value",
            "h": "Step Size"
        }
        data = {key: var.get() for key, var in self.fields.items()}

        errors = []
        missing_fields = [friendly_names[field] for field, value in data.items() if not value]
        if missing_fields:
            errors.append(", ".join(missing_fields) + (" are required." if len(missing_fields) > 1 else " is required."))

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
            errors.append("End value must be a valid number.")
        else:
            data['b'] = b

        try:
            h = float(data['h']) if data['h'] else None
        except ValueError:
            errors.append("Step size must be a valid number.")
        else:
            data['h'] = h

        name = data["name"]
        if name in self.app.res_tab.equation_names:
            errors.append("Name must be unique.")

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
            errors.append("Step size must be a positive value.")
        if b is not None and x0 is not None and b <= x0:
            errors.append("'End value' must be greater than 'x0'.")

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
