import math
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def calculate_motor_specs(weight_kg, slope_deg, terrain, wheel_radius_mm, speed_kmh):
    g = 9.81
    wheel_radius_m = wheel_radius_mm / 1000
    speed_ms = speed_kmh / 3.6
    terrain_coeff = {
        "Flat Ground": 0.05,
        "Soft Soil": 0.15,
        "Rocky": 0.25
    }
    Cr = terrain_coeff[terrain]
    slope_rad = math.radians(slope_deg)
    F_slope = weight_kg * g * math.sin(slope_rad)
    F_rolling = Cr * weight_kg * g * math.cos(slope_rad)
    F_total = F_slope + F_rolling
    torque_nm = F_total * wheel_radius_m
    rpm = (speed_ms / (2 * math.pi * wheel_radius_m)) * 60
    power_w = F_total * speed_ms
    power_w_with_efficiency = power_w / 0.85
    motor_rpm = 540
    gear_ratio = motor_rpm / rpm
    return {
        "F_slope": round(F_slope, 2),
        "F_rolling": round(F_rolling, 2),
        "F_total": round(F_total, 2),
        "torque_nm": round(torque_nm, 2),
        "rpm": round(rpm, 2),
        "power_w": round(power_w_with_efficiency, 2),
        "gear_ratio": round(gear_ratio, 2)
    }

def generate_pdf(inputs, results):
    filename = f"motor_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("<b>Farm Robot Motor Sizing Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    subtitle = Paragraph(f"Generated: {datetime.datetime.now().strftime('%d %B %Y, %H:%M')}", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # Input table
    elements.append(Paragraph("<b>Input Parameters</b>", styles['Heading2']))
    elements.append(Spacer(1, 8))
    input_data = [
        ["Parameter", "Value", "Unit"],
        ["Robot Weight", str(inputs["weight"]), "kg"],
        ["Slope Angle", str(inputs["slope"]), "degrees"],
        ["Terrain Type", inputs["terrain"], "-"],
        ["Wheel Radius", str(inputs["radius"]), "mm"],
        ["Desired Speed", str(inputs["speed"]), "km/h"],
    ]
    input_table = Table(input_data, colWidths=[200, 150, 100])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 20))

    # Results table
    elements.append(Paragraph("<b>Calculated Motor Specifications</b>", styles['Heading2']))
    elements.append(Spacer(1, 8))
    results_data = [
        ["Parameter", "Value", "Unit"],
        ["Slope Force", str(results["F_slope"]), "N"],
        ["Rolling Resistance Force", str(results["F_rolling"]), "N"],
        ["Total Drive Force Required", str(results["F_total"]), "N"],
        ["Required Wheel Torque", str(results["torque_nm"]), "Nm"],
        ["Required Wheel RPM", str(results["rpm"]), "RPM"],
        ["Required Motor Power", str(results["power_w"]), "W"],
        ["Recommended Gear Ratio", str(results["gear_ratio"]), ":1"],
    ]
    results_table = Table(results_data, colWidths=[200, 150, 100])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
    ]))
    elements.append(results_table)
    elements.append(Spacer(1, 20))

    # Notes
    elements.append(Paragraph("<b>Design Notes</b>", styles['Heading2']))
    notes = f"""
    • Motor efficiency assumed at 85%<br/>
    • Base motor speed assumed at 540 RPM<br/>
    • Gear ratio of {results['gear_ratio']}:1 required to achieve {results['rpm']} RPM at wheel<br/>
    • Add 20% safety margin to motor power selection: <b>{round(results['power_w']*1.2, 1)} W minimum</b><br/>
    • Recommended motor: BLDC {round(results['power_w']*1.2/100)*100}W with planetary gearbox
    """
    elements.append(Paragraph(notes, styles['Normal']))

    doc.build(elements)
    return filename

def calculate():
    try:
        weight = float(entry_weight.get())
        slope = float(entry_slope.get())
        terrain = combo_terrain.get()
        radius = float(entry_radius.get())
        speed = float(entry_speed.get())

        results = calculate_motor_specs(weight, slope, terrain, radius, speed)

        # Update result labels
        lbl_fslope.config(text=f"{results['F_slope']} N")
        lbl_frolling.config(text=f"{results['F_rolling']} N")
        lbl_ftotal.config(text=f"{results['F_total']} N")
        lbl_torque.config(text=f"{results['torque_nm']} Nm")
        lbl_rpm.config(text=f"{results['rpm']} RPM")
        lbl_power.config(text=f"{results['power_w']} W")
        lbl_ratio.config(text=f"{results['gear_ratio']} : 1")

        # Store for PDF
        global last_inputs, last_results
        last_inputs = {"weight": weight, "slope": slope, "terrain": terrain, "radius": radius, "speed": speed}
        last_results = results

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers in all fields")

def export_pdf():
    try:
        filename = generate_pdf(last_inputs, last_results)
        messagebox.showinfo("PDF Exported", f"Report saved as:\n{filename}")
    except:
        messagebox.showerror("Error", "Please calculate first before exporting")

# ── GUI ──────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Farm Robot Motor Sizing Calculator")
root.geometry("600x650")
root.configure(bg="#1a1a2e")
root.resizable(False, False)

# Fonts and colors
BG = "#1a1a2e"
CARD = "#16213e"
ACCENT = "#2E86AB"
TEXT = "white"
font_title = ("Helvetica", 16, "bold")
font_label = ("Helvetica", 10)
font_result = ("Helvetica", 10, "bold")

# Title
tk.Label(root, text="🚜 Farm Robot Motor Sizing Calculator",
         font=font_title, bg=BG, fg=ACCENT).pack(pady=15)

# Input frame
frame_in = tk.Frame(root, bg=CARD, bd=0, relief="flat")
frame_in.pack(padx=20, pady=5, fill="x")
tk.Label(frame_in, text="INPUT PARAMETERS", font=("Helvetica", 9, "bold"),
         bg=CARD, fg=ACCENT).grid(row=0, column=0, columnspan=3, pady=8)

inputs = [
    ("Robot Weight (kg):", "25"),
    ("Slope Angle (°):", "10"),
    ("Wheel Radius (mm):", "100"),
    ("Desired Speed (km/h):", "3"),
]

entries = []
for i, (label, default) in enumerate(inputs):
    tk.Label(frame_in, text=label, font=font_label, bg=CARD, fg=TEXT,
             width=22, anchor="w").grid(row=i+1, column=0, padx=15, pady=6)
    e = tk.Entry(frame_in, font=font_label, width=12, bg="#0f3460", fg=TEXT,
                 insertbackground=TEXT, relief="flat", bd=5)
    e.insert(0, default)
    e.grid(row=i+1, column=1, padx=10, pady=6)
    entries.append(e)

entry_weight, entry_slope, entry_radius, entry_speed = entries

# Terrain dropdown
tk.Label(frame_in, text="Terrain Type:", font=font_label, bg=CARD, fg=TEXT,
         width=22, anchor="w").grid(row=5, column=0, padx=15, pady=6)
combo_terrain = ttk.Combobox(frame_in, values=["Flat Ground", "Soft Soil", "Rocky"],
                              width=14, state="readonly")
combo_terrain.set("Soft Soil")
combo_terrain.grid(row=5, column=1, padx=10, pady=6)

# Buttons
frame_btn = tk.Frame(root, bg=BG)
frame_btn.pack(pady=12)
tk.Button(frame_btn, text="  CALCULATE  ", font=("Helvetica", 11, "bold"),
          bg=ACCENT, fg="white", relief="flat", padx=10, pady=6,
          command=calculate).grid(row=0, column=0, padx=10)
tk.Button(frame_btn, text="  EXPORT PDF  ", font=("Helvetica", 11, "bold"),
          bg="#A23B72", fg="white", relief="flat", padx=10, pady=6,
          command=export_pdf).grid(row=0, column=1, padx=10)

# Results frame
frame_out = tk.Frame(root, bg=CARD)
frame_out.pack(padx=20, pady=5, fill="x")
tk.Label(frame_out, text="CALCULATED MOTOR SPECIFICATIONS", font=("Helvetica", 9, "bold"),
         bg=CARD, fg="#A23B72").grid(row=0, column=0, columnspan=3, pady=8)

result_rows = [
    ("Slope Force:", "lbl_fslope"),
    ("Rolling Resistance:", "lbl_frolling"),
    ("Total Drive Force:", "lbl_ftotal"),
    ("Required Torque:", "lbl_torque"),
    ("Required RPM:", "lbl_rpm"),
    ("Motor Power Needed:", "lbl_power"),
    ("Gear Ratio Required:", "lbl_ratio"),
]

result_labels = {}
for i, (label, var) in enumerate(result_rows):
    tk.Label(frame_out, text=label, font=font_label, bg=CARD, fg=TEXT,
             width=25, anchor="w").grid(row=i+1, column=0, padx=15, pady=5)
    lbl = tk.Label(frame_out, text="—", font=font_result, bg=CARD, fg=ACCENT,
                   width=15, anchor="w")
    lbl.grid(row=i+1, column=1, padx=10, pady=5)
    result_labels[var] = lbl

lbl_fslope = result_labels["lbl_fslope"]
lbl_frolling = result_labels["lbl_frolling"]
lbl_ftotal = result_labels["lbl_ftotal"]
lbl_torque = result_labels["lbl_torque"]
lbl_rpm = result_labels["lbl_rpm"]
lbl_power = result_labels["lbl_power"]
lbl_ratio = result_labels["lbl_ratio"]

last_inputs, last_results = {}, {}

root.mainloop()