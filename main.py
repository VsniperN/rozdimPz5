import random
import json
import os
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import tkinter as tk
from tkinter import messagebox

app = Flask(__name__)

M1 = 8
M2 = 32
N1 = 24.1
N2 = 25.0
CONFIG_FILE = "config.json"

temperature = random.uniform(M1, M2)
heating_on = False
temperature_data = []

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config['lower_threshold'], config['upper_threshold']
    else:
        config = {
            'lower_threshold': N1,
            'upper_threshold': N2
        }
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file)
        return N1, N2

lower_threshold, upper_threshold = load_config()

def update_temperature():
    global temperature, heating_on, temperature_data
    temperature = random.uniform(M1, M2)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temperature_data.append({'timestamp': timestamp, 'temperature': temperature})
    if temperature < lower_threshold:
        heating_on = True
    elif temperature > upper_threshold:
        heating_on = False
    # Ограничиваем количество записей температур
    if len(temperature_data) > 50:
        temperature_data.pop(0)

@app.route('/')
def index():
    update_temperature()
    return render_template('index.html',
                           temperature=temperature,
                           lower_threshold=lower_threshold,
                           upper_threshold=upper_threshold,
                           heating_on=heating_on,
                           temperature_data=temperature_data)

@app.route('/temperature')
def get_temperature():
    update_temperature()
    return jsonify({
        'temperature': temperature,
        'heating_on': heating_on,
        'lower_threshold': lower_threshold,
        'upper_threshold': upper_threshold,
        'temperature_data': temperature_data
    })

@app.route('/update_thresholds', methods=['POST'])
def update_thresholds():
    global lower_threshold, upper_threshold
    data = request.get_json()
    new_lower_threshold = data.get('lower_threshold')
    new_upper_threshold = data.get('upper_threshold')
    if new_lower_threshold is not None and new_upper_threshold is not None:
        lower_threshold = float(new_lower_threshold)
        upper_threshold = float(new_upper_threshold)
        save_config()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid thresholds'})

def save_config():
    config = {
        'lower_threshold': lower_threshold,
        'upper_threshold': upper_threshold
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Abdukarimov Ruslan ITSHIi-21-2.")
        self.geometry("800x600")  # Змінено розміри вікна графічного інтерфейсу
        self.create_widgets()
        self.update_gui()

    def create_widgets(self):
        self.temperature_label = tk.Label(self, text=f"Поточна температура: {temperature:.2f} °C", font=("Arial", 14))
        self.temperature_label.pack(pady=10)
        self.heating_status_label = tk.Label(self, text=f"Стан системи опалення: {'УВІМКНЕНО' if heating_on else 'ВИМКНЕНО'}", font=("Arial", 14))
        self.heating_status_label.pack(pady=10)
        self.lower_threshold_label = tk.Label(self, text=f"Нижній поріг (N1): {lower_threshold} °C", font=("Arial", 14))
        self.lower_threshold_label.pack(pady=10)
        self.lower_threshold_entry = tk.Entry(self)
        self.lower_threshold_entry.pack(pady=10)
        self.upper_threshold_label = tk.Label(self, text=f"Верхній поріг (N2): {upper_threshold} °C", font=("Arial", 14))
        self.upper_threshold_label.pack(pady=10)
        self.upper_threshold_entry = tk.Entry(self)
        self.upper_threshold_entry.pack(pady=10)
        self.update_button = tk.Button(self, text="Оновити пороги", command=self.update_thresholds)
        self.update_button.pack(pady=10)

    def update_thresholds(self):
        global lower_threshold, upper_threshold
        try:
            new_lower_threshold = float(self.lower_threshold_entry.get())
            new_upper_threshold = float(self.upper_threshold_entry.get())
            lower_threshold = new_lower_threshold
            upper_threshold = new_upper_threshold
            self.lower_threshold_label.config(text=f"Нижній поріг (N1): {lower_threshold} °C")
            self.upper_threshold_label.config(text=f"Верхній поріг (N2): {upper_threshold} °C")
            save_config()
            messagebox.showinfo("Успіх", "Пороги успішно оновлено!")
        except ValueError:
            messagebox.showerror("Помилка", "Будь ласка, введіть коректні значення порогів")

    def update_gui(self):
        self.temperature_label.config(text=f"Поточна температура: {temperature:.2f} °C")
        self.heating_status_label.config(text=f"Стан системи опалення: {'УВІМКНЕНО' if heating_on else 'ВИМКНЕНО'}")
        self.lower_threshold_label.config(text=f"Нижній поріг (N1): {lower_threshold} °C")
        self.upper_threshold_label.config(text=f"Верхній поріг (N2): {upper_threshold} °C")
        self.after(2000, self.update_gui)

def run_flask():
    app.run(debug=True, use_reloader=False)

def run_tkinter():
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    run_tkinter()
