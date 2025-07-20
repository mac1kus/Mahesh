import os
import subprocess
from scipy.optimize import linprog
from pathlib import Path

def solve_lp(c, A, b):
    # Convert max to min
    neg_c = [-x for x in c]

    # Solve using SciPy to get basic results
    res = linprog(
        c=neg_c,
        A_ub=A,
        b_ub=b,
        bounds=[(0, None) for _ in c],
        method="highs",
        options={"disp": False}
    )

    result = {
        'status': res.message,
        'max_profit': round(-res.fun, 2) if res.success else None,
        'variables': {f'x{i+1}': round(val, 2) for i, val in enumerate(res.x)} if res.success else {},
        'reduced_costs': {},
        'range_report': '',
        'problem_statement': ''
    }

    # Prepare LP file
    Path("output").mkdir(exist_ok=True)
    lp_path = "output/problem.lp"
    with open(lp_path, "w") as f:
        f.write("Maximize\n")
        f.write(" obj: " + " + ".join(f"{c[i]} x{i+1}" for i in range(len(c))) + "\n")
        f.write("Subject To\n")
        for i, row in enumerate(A):
            f.write(f" c{i+1}: " + " + ".join(f"{row[j]} x{j+1}" for j in range(len(c))) + f" <= {b[i]}\n")
        f.write("Bounds\n")
        for i in range(len(c)):
            f.write(f" x{i+1} >= 0\n")
        f.write("End\n")

    # Call glpsol
    try:
        subprocess.run([
            "glpsol",                 # only command name, assuming it's in PATH
            "--lp", lp_path,
            "--output", "output/result.txt",
            "--ranges", "output/ranges.txt"
        ], check=True)
    except FileNotFoundError:
        result['range_report'] = "Error: glpsol not found. Make sure GLPK is installed and glpsol is in PATH."
        return result
    except subprocess.CalledProcessError as e:
        result['range_report'] = f"glpsol failed with error: {e}"
        return result

    # Read range report
    try:
        with open("output/ranges.txt", "r") as f:
            full_range_report = f.read()
            result['range_report'] = full_range_report
    except FileNotFoundError:
        result['range_report'] = "Range report not generated."

    # Append summary of sensitivity section to result file
    try:
        lines = full_range_report.splitlines()
        capture = False
        extracted = []

        for line in lines:
            if "No. Row name" in line:
                capture = True
                extracted.append(line)
            elif capture:
                if line.strip() == "":
                    break
                extracted.append(line)

        with open("output/result.txt", "a") as fout:
            fout.write("\n\n--- Constraint Sensitivity Report ---\n")
            fout.write("\n".join(extracted))
            fout.write("\n")

    except Exception as e:
        with open("output/result.txt", "a") as fout:
            fout.write(f"\nCould not extract sensitivity data: {e}\n")

    return result





