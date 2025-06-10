import tkinter as tk
from tkinter import ttk
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text
import json
from datetime import datetime


API_KEY = "fa8affeb2df4221f0806768ba77b95ec"

miasta_info = {
    "USA": [
        ("New York", 8_400_000, 40.7128, -74.0060),
        ("Los Angeles", 4_000_000, 34.0522, -118.2437),
        ("Chicago", 2_700_000, 41.8781, -87.6298),
        ("Houston", 2_300_000, 29.7604, -95.3698),
        ("Phoenix", 1_600_000, 33.4484, -112.0740)
    ],
    "Chiny": [
        ("Shanghai", 24_800_000, 31.2304, 121.4737),
        ("Beijing", 21_700_000, 39.9042, 116.4074),
        ("Chongqing", 15_800_000, 29.4316, 106.9123),
        ("Tianjin", 13_200_000, 39.3434, 117.3616),
        ("Hotan", 400_000, 37.1136, 79.9186)
    ],
    "Polska": [
        ("Warszawa", 1_800_000, 52.2297, 21.0122),
        ("Kraków", 780_000, 50.0647, 19.9450),
        ("Łódź", 670_000, 51.7592, 19.4560),
        ("Wrocław", 640_000, 51.1079, 17.0385),
        ("Poznań", 540_000, 52.4064, 16.9252)
    ],
    "Pakistan": [
        ("Lahore", 11_100_000, 31.5497, 74.3436),
        ("Karachi", 14_900_000, 24.8607, 67.0011),
        ("Islamabad", 1_000_000, 33.6844, 73.0479),
        ("Faisalabad", 3_800_000, 31.4504, 73.1350),
        ("Rawalpindi", 2_100_000, 33.5651, 73.0169)
    ],
    "Indie": [
        ("Delhi", 32_000_000, 28.6139, 77.2090),
        ("Mumbai", 20_400_000, 19.0760, 72.8777),
        ("Bangalore", 12_300_000, 12.9716, 77.5946),
        ("Kolkata", 14_800_000, 22.5726, 88.3639),
        ("Bhiwadi", 104_000, 28.2104, 76.8606)
    ],
    "Japonia": [
        ("Tokio", 13_900_000, 35.6895, 139.6917),
        ("Osaka", 2_700_000, 34.6937, 135.5023),
        ("Yokohama", 3_700_000, 35.4437, 139.6380),
        ("Nagoya", 2_300_000, 35.1815, 136.9066),
        ("Sapporo", 1_900_000, 43.0618, 141.3545)
    ]
}

def pobierz_temp(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    resp = requests.get(url).json()
    return resp["main"]["temp"]

def pobierz_pm25(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    resp = requests.get(url).json()
    return resp["list"][0]["components"]["pm2_5"]

sns.set_style("whitegrid")
sns.set_context("talk")

def rysuj_wykres(kraj):
    fig.clear()
    ax = fig.add_subplot(111)
    # ax.ticklabel_format(style='plain')
    sns.set_style("whitegrid")
    sns.set_context("talk")

    cities = miasta_info[kraj]
    populacje = [c[1] for c in cities]
    temps = [pobierz_temp(c[2], c[3]) for c in cities]
    pm25 = [pobierz_pm25(c[2], c[3]) for c in cities]

    scatter = ax.scatter(
        populacje, temps, s=[v * 15 for v in pm25],
        c=pm25, cmap='autumn_r', alpha=0.7, edgecolor='k', linewidth=0.7
    )

    ax.set_xlabel("Populacja miasta", fontsize=12)
    ax.set_ylabel("Temperatura (°C)", fontsize=12)
    ax.set_title(f"Populacja i temperatura stosunek - wielkość PM2.5 – {kraj}", fontsize=10, fontweight='bold')

    ax.tick_params(axis='both', labelsize=10)

    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("PM2.5 (μg/m³)", fontsize=10)
    cbar.ax.tick_params(labelsize=10)

    texts = []
    for pop, t, (name, *_), p in zip(populacje, temps, cities, pm25):
        ax.text(pop + 0.05, t + 0.05, name,
                fontsize=10,
                ha='center',
                va='bottom')

    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="->", color='gray', lw=0.5))

    fig.tight_layout()
    canvas.draw()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dane_do_zapisu = {
        "kraj": kraj,
        "czas_pobrania": timestamp,
        "miasta": []
    }

    for (name, *_), pop, temp, pm in zip(cities, populacje, temps, pm25):
        dane_do_zapisu["miasta"].append({
            "miasto": name,
            "populacja": pop,
            "temperatura": temp,
            "pm25": pm
        })

    plik_nazwa = f"{kraj.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(plik_nazwa, "w", encoding="utf-8") as plik:
        json.dump(dane_do_zapisu, plik, ensure_ascii=False, indent=4)

    def hover(event):
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                i = ind["ind"][0]
                text = f"{cities[i][0]}:\nPopulacja: {populacje[i]:,}\nTemp: {temps[i]:.1f}°C\nPM2.5: {pm25[i]:.2f}"
                tooltip.config(text=text)
                tooltip.place(x=event.guiEvent.x_root - root.winfo_rootx() + 10,
                              y=event.guiEvent.y_root - root.winfo_rooty() + 10)
                tooltip.lift()
            else:
                tooltip.place_forget()
        else:
            tooltip.place_forget()

    canvas.mpl_connect("motion_notify_event", hover)


def on_select(event):
    kraj = combo.get()
    rysuj_wykres(kraj)

root = tk.Tk()
root.title("Populacja i Temperatura stosunek")

style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox",
                fieldbackground="#ffffff",
                background="#e6f2ff",
                foreground="#000000",
                font=('Segoe UI', 11, 'bold'))
style.map("TCombobox",
          fieldbackground=[('readonly', '#ffffff')],
          background=[('readonly', '#cce0ff')],
          foreground=[('readonly', '#000000')])

ctrl = tk.Frame(root)
ctrl.pack(side=tk.TOP, fill=tk.X, pady=5)

tk.Label(ctrl, text="Wybierz kraj:").pack(side=tk.LEFT, padx=5)
combo = ttk.Combobox(ctrl, values=list(miasta_info.keys()), state="readonly")
combo.pack(side=tk.LEFT)
combo.bind("<<ComboboxSelected>>", on_select)

fig = plt.Figure(figsize=(8, 6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

tooltip = tk.Label(root, bg="lightyellow", relief="solid", borderwidth=1, font=("Segoe UI", 10), justify=tk.LEFT)
tooltip.place_forget()

combo.current(0)
rysuj_wykres(combo.get())

root.mainloop()