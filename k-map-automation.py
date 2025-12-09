import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import re
from sympy import symbols, SOPform, POSform
import tkinter.messagebox

# -------------------------
# Provided logic functions
# (integrated with small fixes to work inside the app)
# -------------------------

def detect_maxterm_minterm(take_function):
    # Determines whether the input is expressed as SOP (minterm) or POS (maxterm)
    operators = ['.','+']
    for each_char in take_function:
        if each_char == operators[0]:
            return True
        elif each_char == operators[1]:
            return False
    return None


def calculate_function(take_function):
    # note: this function expects a string like "(A.B)+(B.A)+C"
    possible_operations = [".","+","'"]

    # Spacize the take_function variable to support splitting
    take_function2 = ""
    for char in take_function:
        take_function2 += char + ' '

    # Splitting the function to gather the actual function variables
    splitted_func = take_function2.split()

    # Clean the function and remove every operator/paren
    for token in ['.', '+', "'", '(', ')']:
        while token in splitted_func:
            splitted_func.remove(token)

    # Convert the list into unique list
    splitted_func = list(set(splitted_func))
    if len(splitted_func) == 0:
        return None

    # Count the number of variables in the list
    no_of_var = len(splitted_func)
    final_bits = 1
    for x in range(1, no_of_var + 1):
        final_bits = final_bits * 2

    length_of_final_bits = len(bin(final_bits - 1)[2::])
    ultimate_bits = []

    # Generate all binary values up to the final_bits
    for bits in range(0, final_bits):
        ultimate_bits.append(bin(bits)[2::])

    # Fill the remaining 0s for items in ultimate_bits
    temp_index = 0
    for items in ultimate_bits:
        if len(items) != length_of_final_bits:
            length_to_concatenate = length_of_final_bits - len(items)
            for x in range(0, length_to_concatenate):
                ultimate_bits[temp_index] = '0' + ultimate_bits[temp_index]
        temp_index += 1

    # Make sure that A comes before B and so on.... (sorted variable names)
    splitted_func = sorted(splitted_func)

    # Dynamically define the variables as lists of their bit values
    for unique_var in splitted_func:
        globals()[unique_var] = []

    for unique_var in splitted_func:
        for items in ultimate_bits:
            index_of_var = splitted_func.index(unique_var)
            globals()[unique_var].append(items[index_of_var])

    # Return the Dynamically defined variables
    all_variable_in_one_list = []
    for unique_var in splitted_func:
        all_variable_in_one_list.append(globals()[unique_var])

    # Build final function values by evaluating for each bit assignment
    take_function_eval = take_function.replace('.', '&')
    take_function_eval = take_function_eval.replace('+', '|')

    variables_data = []
    for items in splitted_func:
        variables_data.append(eval(items))
    variable_names = splitted_func
    solution = take_function_eval

    instance = []
    for values_tuple in zip(*variables_data):
        new_instance_string = solution
        for name, value in zip(variable_names, values_tuple):
            str_value = str(value)
            new_instance_string = new_instance_string.replace(name, str_value)
        new_instance_string = new_instance_string.replace(name, str(value))

        # --- FIX: handle NOT before eval ---
        pattern = re.compile(r"(\d)'")
        new_instance_string = pattern.sub(lambda m: str(1 - int(m.group(1))), new_instance_string)
        instance.append(new_instance_string)

    pattern = re.compile(r"(\\d)'")

    processed_instance = []

    # Substitute inverted digits like 1' -> 0
    for expression in instance:
        def replace_inverse(match):
            number = int(match.group(1))
            inverted_value = 1 - number
            return str(inverted_value)
        new_expression = pattern.sub(replace_inverse, expression)
        processed_instance.append(new_expression)

    final_function = []
    for each_expression in processed_instance:
        final_function.append(eval(each_expression))

    all_variable_in_one_list.append(final_function)

    # Prepare sympy symbols and simplify
    symbolic_vars = []
    for var_name in splitted_func:
        sym = symbols(var_name)
        symbolic_vars.append(sym)

    minterm, maxterm = [], []
    min_or_max = detect_maxterm_minterm(take_function2)
    minmax = []

    if min_or_max:
        index = 0
        for bins in final_function:
            if bins == 1:
                minterm.append(index)
            index += 1
        simplified_expression = SOPform(symbolic_vars, minterm)
        minmax = minterm

    elif min_or_max == False:
        index = 0
        for bins in final_function:
            if bins == 0:
                maxterm.append(index)
            index += 1
        simplified_expression = POSform(symbolic_vars, maxterm)
        minmax = maxterm

    else:
        simplified_expression = None

    return splitted_func, all_variable_in_one_list, simplified_expression, min_or_max, minmax


# -------------------------
# Helper: Gray code and kmap layout
# -------------------------

def gray_code(n):
    if n == 0:
        return ['']
    if n == 1:
        return ['0', '1']
    prev = gray_code(n - 1)
    return ['0' + x for x in prev] + ['1' + x for x in reversed(prev)]


def kmap_layout_indices(num_vars):
    # split bits between rows and cols
    rows_bits = num_vars // 2
    cols_bits = num_vars - rows_bits
    row_codes = gray_code(rows_bits)
    col_codes = gray_code(cols_bits)

    layout = []
    for r in row_codes:
        for c in col_codes:
            layout.append(int(r + c, 2) if (r + c) != '' else 0)
    return layout, rows_bits, cols_bits


# -------------------------
# GUI builder functions
# -------------------------

def build_truth_table_frame(parent, variables, columns_data):
    frame = tk.Frame(parent, bd=2, relief="groove", padx=8, pady=8)
    title = tk.Label(frame, text="Truth Table", font=("Helvetica", 14, "bold"))
    title.grid(row=0, column=0, columnspan=len(variables) + 1, pady=(0, 6))

    # Headers
    for col, var in enumerate(variables):
        tk.Label(frame, text=var, font=("Helvetica", 12, "bold"), bd=1, relief="solid", width=6).grid(row=1, column=col)

    tk.Label(frame, text="F", font=("Helvetica", 12, "bold"), bd=1, relief="solid", width=6).grid(row=1, column=len(variables))

    rows = len(columns_data[0])
    for r in range(rows):
        for c in range(len(variables)):
            tk.Label(frame, text=str(columns_data[c][r]), bd=1, relief="solid", width=6).grid(row=r + 2, column=c)
        tk.Label(frame, text=str(columns_data[-1][r]), bd=1, relief="solid", width=6).grid(row=r + 2, column=len(variables))

    return frame


def minsop_description_frame(parent, is_minterm):
    frame = tk.Frame(parent, bd=2, relief="groove", padx=8, pady=8)
    if is_minterm:
        text = "It is a MINTERM because it is a Sum of Products (SOP)."
    else:
        text = "It is a MAXTERM because it is a Product of Sums (POS)."
    tk.Label(frame, text=text, font=("Helvetica", 12), wraplength=600).pack()
    return frame


def build_kmap_frame(parent, indexes, is_minterm, num_vars):
    frame = tk.Frame(parent, bd=2, relief="groove", padx=8, pady=8)
    tk.Label(frame, text="K-Map", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=8)

    total_cells = 2 ** num_vars
    layout, rows_bits, cols_bits = kmap_layout_indices(num_vars)
    # compute values
    values = [0] * total_cells
    if is_minterm:
        for i in indexes:
            if 0 <= i < total_cells:
                values[i] = 1
    else:
        for i in range(total_cells):
            if i not in indexes:
                values[i] = 1

    rows = 2 ** rows_bits if rows_bits > 0 else 1
    cols = 2 ** cols_bits if cols_bits > 0 else 1

    # place labels showing Gray order coordinates
    idx = 0
    for r in range(rows):
        for c in range(cols):
            mapped_index = layout[idx]
            tk.Label(frame, text=str(values[mapped_index]), font=("Helvetica", 14, "bold"), bd=1, relief="solid", width=4, height=2).grid(row=r + 1, column=c, padx=3, pady=3)
            idx += 1

    return frame


def simplified_equation_frame(parent, eq):
    frame = tk.Frame(parent, bd=2, relief="groove", padx=8, pady=8)
    tk.Label(frame, text="Simplified Equation", font=("Helvetica", 14, "bold")).pack(pady=4)
    tk.Label(frame, text=str(eq), font=("Helvetica", 12)).pack()
    return frame


# -------------------------
# Main Application
# -------------------------
class LogicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dynamic Truth Table & K-Map Generator")
        self.geometry("900x700")

        # Top entry frame
        top_frame = tk.Frame(self, pady=8)
        top_frame.pack(fill='x')

        tk.Label(top_frame, text="Enter boolean function (use . for AND, + for OR, ' for NOT). Example: (A.B)+(B.A)+C").pack(anchor='w', padx=8)
        entry_frame = tk.Frame(top_frame)
        entry_frame.pack(fill='x', padx=8, pady=6)

        self.func_entry = tk.Entry(entry_frame, font=("Helvetica", 12))
        self.func_entry.pack(side='left', fill='x', expand=True)
        self.func_entry.insert(0, "(A.B)+(B.A)+C")

        tk.Button(entry_frame, text="Generate", command=self.on_generate).pack(side='left', padx=6)

        # Scrollable area for results inside a frame so root isn't fully taken
        container = tk.Frame(self)
        container.pack(fill='both', expand=True, padx=8, pady=6)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
        self.results_frame = tk.Frame(canvas)

        self.results_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.results_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def clear_results(self):
        for child in self.results_frame.winfo_children():
            child.destroy()

    def on_generate(self):
        func_text = self.func_entry.get().strip()
        if not func_text:
            return
        # call the calculation function
        try:
            result = calculate_function(func_text)
            # print(result)
            if result is None:
                tk.messagebox.showerror("Error", "Could not interpret the function. Make sure variables are letters and operator syntax is correct.")
                return
            variables, columns_data, simplified_expr, is_minterm, indexes = result

            # normalized simplified expression (sympy may return an Expr or None)
            if isinstance(simplified_expr, set):
                # if function returned as a set (old behaviour), take an item
                simplified_expr = next(iter(simplified_expr)) if len(simplified_expr) > 0 else None
            if simplified_expr is not None:
                simplified_str = str(simplified_expr)
            else:
                simplified_str = 'N/A'

            # columns_data is list of variable lists with final_function appended as last element
            # ensure last element is function output
            func_values = columns_data[-1]
            var_columns = columns_data[:-1]

            # Now build UI pieces
            self.clear_results()

            tt = build_truth_table_frame(self.results_frame, variables, columns_data)
            tt.pack(pady=6, fill='x')

            desc = minsop_description_frame(self.results_frame, is_minterm)
            desc.pack(pady=6, fill='x')

            km = build_kmap_frame(self.results_frame, indexes, is_minterm, len(variables))
            km.pack(pady=6, fill='x')

            se = simplified_equation_frame(self.results_frame, simplified_str)
            se.pack(pady=6, fill='x')

        except Exception as e:
            tkinter.messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == '__main__':
    app = LogicApp()
    app.mainloop()
