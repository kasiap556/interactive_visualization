import tkinter as tk
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import json
from datetime import datetime
import os

API_KEY = "fa8affeb2df4221f0806768ba77b95ec"

kraje_miasta = {
    "Polska": [("Warszawa", 1_800_000, 52.2297, 21.0122), ("Kraków", 780_000, 50.0647, 19.9450),
               ("Łódź", 670_000, 51.7592, 19.4560), ("Wrocław", 640_000, 51.1079, 17.0385),
               ("Poznań", 540_000, 52.4064, 16.9252)],
    "Niemcy": [("Dortmund", 1_900_000, 51.5136, 7.4653), ("Essen", 1_900_000, 51.4556, 7.0116),
                ("Lipsk", 1_200_000, 51.3397, 12.3731), ("Kolonia", 1_100_000, 50.9375, 6.9603),
                ("Frankfurt", 750_000, 50.1109, 8.6821)],
    "Francja": [("Marsylia", 860_000, 43.2965, 5.3698), ("Lyon", 520_000, 45.7640, 4.8357),
               ("Tuluza", 480_000, 43.6047, 1.4442), ("Nicea", 340_000, 43.7102, 7.2620),
               ("Nantes", 1_000_000, 47.2184, -1.5536)],
    "Hiszpania": [("Barcelona", 1_600_000, 41.3851, 2.1734), ("Walencja", 800_000, 39.4699, -0.3763),
              ("Sewilla", 700_000, 37.3891, -5.9845), ("Saragossa", 675_000, 41.6488, -0.8891),
              ("Bilbao", 1_000_000, 43.2630, -2.9350)],
    "Włochy": [("Mediolan", 1_350_000, 45.4642, 9.1900), ("Neapol", 970_000, 40.8518, 14.2681),
              ("Turyn", 870_000, 45.0703, 7.6869), ("Palermo", 660_000, 38.1157, 13.3615),
              ("Florencja", 380_000, 43.7696, 11.2558)]
}

def pobierz_temperature(lat, lon):
    return requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}"
        f"&appid={API_KEY}&units=metric"
    ).json()["main"]["temp"]

def pobierz_pm25(lat, lon):
    return requests.get(
        f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}"
        f"&appid={API_KEY}"
    ).json()["list"][0]["components"]["pm2_5"]

root = tk.Tk()
root.title("Wpływ populacji i temperatury na PM2.5")

frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.TOP, fill=tk.X)

fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

country_plots = {}
alpha_values = {}
text_labels = {}
hover_annotation = None

colors = sns.color_palette("hls", len(kraje_miasta))

################################
use_api = True


def plot():
    ax.clear()
    ax.xaxis.set_major_locator(ticker.MultipleLocator(100_000))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.grid(True, alpha=0.1)

    country_plots.clear()
    alpha_values.clear()
    text_labels.clear()

    all_data_to_save = []

    if use_api:
        for idx, (country, cities) in enumerate(kraje_miasta.items()):
            color = colors[idx]
            populations = []
            temps = []
            pm25s = []
            names = []

            for city, population, lat, lon in cities:
                t = pobierz_temperature(lat, lon)
                p = pobierz_pm25(lat, lon)
                populations.append(population)
                temps.append(t)
                pm25s.append(p)
                names.append(city)

                all_data_to_save.append({
                    "country": country,
                    "city": city,
                    "population": population,
                    "temperature": t,
                    "pm2_5": p,
                    "lat": lat,
                    "lon": lon
                })

            alpha_values[country] = 0.6

            scatter = ax.scatter(
                populations, temps,
                s=[p * 15 for p in pm25s],
                label=country,
                alpha=0.7,
                color=color,
                edgecolor='black',
                linewidth=0.5
            )

            labels = []
            for i, city in enumerate(cities):
                txt = ax.text(populations[i], temps[i] + 0.35, city[0], fontsize=8, ha='center', alpha=0.7)
                labels.append(txt)

            country_plots[country] = {"scatter": scatter, "data": list(zip(populations, temps, names, pm25s)), "color": color}
            text_labels[country] = labels

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"all_cities_data_{now}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_data_to_save, f, indent=2, ensure_ascii=False)

    else:
        filename = "all_cities_data.json"
        if not os.path.exists(filename):
            print(f"Plik {filename} nie istnieje! Najpierw wygeneruj dane z API.")
            return

        with open(filename, "r", encoding="utf-8") as f:
            all_data_to_save = json.load(f)

        data_by_country = {}
        for d in all_data_to_save:
            country = d["country"]
            if country not in data_by_country:
                data_by_country[country] = []
            data_by_country[country].append(d)

        for idx, (country, data_list) in enumerate(data_by_country.items()):
            color = colors[idx]
            populations = [d["population"] for d in data_list]
            temps = [d["temperature"] for d in data_list]
            pm25s = [d["pm2_5"] for d in data_list]
            names = [d["city"] for d in data_list]

            alpha_values[country] = 0.6

            scatter = ax.scatter(
                populations, temps,
                s=[p * 15 for p in pm25s],
                label=country,
                alpha=0.7,
                color=color,
                edgecolor='black',
                linewidth=0.5
            )

            labels = []
            for i, name in enumerate(names):
                txt = ax.text(populations[i], temps[i], name, fontsize=8, ha='center', alpha=0.7)
                labels.append(txt)

            country_plots[country] = {"scatter": scatter, "data": list(zip(populations, temps, names, pm25s)), "color": color}
            text_labels[country] = labels

    ax.set_xlabel("Liczba mieszkańców")
    ax.set_ylabel("Temperatura (°C)")
    ax.set_title("Wpływ populacji i temperatury na PM2.5")
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                  label=country, markerfacecolor=country_plots[country]["color"],
                                  markersize=10) for country in alpha_values]
    ax.legend(handles=legend_elements, title="Kraj", fontsize=8)
    fig.tight_layout()
    canvas.draw()


def toggle_alpha(kraj):
    scatter_obj = country_plots[kraj]["scatter"]
    new_alpha = 0.1 if alpha_values[kraj] == 0.6 else 0.6
    scatter_obj.set_alpha(new_alpha)
    for txt in text_labels[kraj]:
        txt.set_alpha(new_alpha)
    alpha_values[kraj] = new_alpha
    canvas.draw()

for kraj in kraje_miasta.keys():
    btn = tk.Button(frame_buttons, text=kraj, command=lambda c=kraj: toggle_alpha(c))
    btn.pack(side=tk.LEFT, padx=5, pady=5)

def motion(event):
    global hover_annotation
    if event.inaxes != ax:
        if hover_annotation:
            hover_annotation.remove()
            hover_annotation = None
            canvas.draw()
        return

    for kraj, obj in country_plots.items():
        scatter = obj["scatter"]
        data = obj["data"]
        contains, info = scatter.contains(event)
        if contains:
            ind = info["ind"][0]
            pop, temp, name, pm = data[ind]

            if hover_annotation:
                hover_annotation.remove()

            x_display, y_display = ax.transData.transform((pop, temp))
            ax_width, ax_height = fig.get_size_inches() * fig.dpi

            margin = 10
            offset_x, offset_y = 10, 10

            approx_width = 150
            approx_height = 60

            if x_display + approx_width + offset_x > ax_width:
                offset_x = -approx_width - margin
            if y_display + approx_height + offset_y > ax_height:
                offset_y = -approx_height - margin

            hover_annotation = ax.annotate(
                f"{name}\nPopulacja: {pop:,}\nTemperatura: {temp:.1f}°C\nPM2.5: {pm:.1f}",
                xy=(pop, temp), xycoords='data',
                xytext=(offset_x, offset_y), textcoords='offset points',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.6),
                fontsize=8
            )
            canvas.draw()
            return

    if hover_annotation:
        hover_annotation.remove()
        hover_annotation = None
        canvas.draw()


canvas.mpl_connect("motion_notify_event", motion)
plot()
root.mainloop()
