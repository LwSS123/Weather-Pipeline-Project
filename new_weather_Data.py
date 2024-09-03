import requests
import pandas as pd
import sqlite3
from datetime import datetime
import schedule
import time
import numpy as np
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ.get('API_KEY')  #Replace your API key
city_list = ['New York', 'Tokyo', 'Paris', 'Cairo', 'Sydney', 'Mumbai', 'London', 'Berlin', 'Moscow', 'Beijing', 'Seoul', 'Bangkok','Hong Kong','Rome','Los Angeles'] # List of cities for which weather data will be fetched

def format_table_name(city):
    return city.replace(" ", "_").lower()
    
"""
Formats the city name into a valid SQLite table name.
Removes spaces and converts to lowercase.

Args:
city (str): The name of the city to format.

Returns:
str: A string suitable for use as a table name.
"""

# Task 1. define a database and table

"""
Initializes the database and creates one table per city in the city_list.
Each table will store weather data including temperature, humidity, and description.

"""

def init_db():
    conn = sqlite3.connect('new_weather_data.db')
    c = conn.cursor()
    for city in city_list:
        table_name = format_table_name(city)
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                temperature REAL,
                humidity INTEGER,
                description TEXT
            )
        ''')
    conn.commit()
    conn.close()

# Task 2. add weather data into database

"""
Fetches weather data from OpenWeatherMap API for a given city and stores it in the local database.

Args:
city (str): Name of the city to fetch weather data for.
"""

# def fetch_weather_data(city):
#     base_url = "http://api.openweathermap.org/data/2.5/weather"
#     url = f"{base_url}?q={city}&appid={API_KEY}&units=metric"  # Construct API request URL
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json() # Parse the JSON response
#             weather_data = (
#                 datetime.now(),
#                 data['main']['temp'],
#                 data['main']['humidity'],
#                 data['weather'][0]['description'],
#             )
#             conn = sqlite3.connect('new_weather_data.db') 
#             c = conn.cursor()
#             table_name = format_table_name(city)
#             c.execute(f'''
#                 INSERT INTO {table_name} (timestamp, temperature, humidity, description)
#                 VALUES (?, ?, ?, ?)
#             ''', weather_data)
#             conn.commit()
#             conn.close()
#             print(f"Data inserted for {city}: {weather_data}")
#         else:
#             print(f"Failed to fetch data for {city}, HTTP Status: {response.status_code}")
#     except requests.RequestException as e:
#         print(f"Failed to fetch data for {city}: {e}") # Handle API errors

# """
# Continuously schedules and runs the fetch_weather_data function for all cities.
# """
# def scheduled_fetch():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# """
# Main function to initialize the database, schedule data fetching tasks, and start the scheduler.
# """
# def main():
#     init_db()
#     for city in city_list:
#         schedule.every(1).minutes.do(fetch_weather_data, city=city)
#     print("Scheduler started. Fetching weather data every 1 minute for each city.")
#     scheduled_fetch() # Start the scheduled fetching process

# if __name__ == "__main__":
#     main()

# Task 3. write functions to perform analysis - generate analysis based on weather data
"""
Fetch weather data for a specified city from a database.

Args:
city (str): Name of the city to retrieve data for.
db (str): Database file path.

Returns:
pandas.DataFrame: Weather data containing timestamps, temperatures, and humidity levels.
"""

def fetch_data(city, db='new_weather_data.db'):
    conn = sqlite3.connect(db)
    table_name = city.replace(" ", "_").lower()
    df = pd.read_sql_query(f"SELECT timestamp, temperature, humidity FROM {table_name}", conn, parse_dates=['timestamp'])
    conn.close()
    return df

# Analyze Max/Min Temperature for Each City
"""
Analyzes maximum and minimum temperatures for a given city.

Args:
city (str): City to analyze.

Returns:
tuple: Maximum and minimum temperatures.
"""

def analyze_temperature(city):
    df = fetch_data(city)
    max_temp = df['temperature'].max()
    min_temp = df['temperature'].min()
    return max_temp, min_temp


"""
Analyzes highest and lowest humidity levels for a given city.

Args:
city (str): City to analyze.

Returns:
tuple: Highest and lowest humidity levels.
"""

def analyze_humidity(city):
    df = fetch_data(city)
    highest_humidity = df['humidity'].max()
    lowest_humidity = df['humidity'].min()
    return highest_humidity, lowest_humidity

# Task 4. compare cities
"""
Compares maximum and minimum temperatures across multiple cities.

Args:
cities (list of str): List of city names to compare.

Returns:
tuple of lists: Lists containing maximum and minimum temperatures for each city.
"""

def compare_temperature(cities):
    max_temps = []
    min_temps = []
    for city in cities:
        max_temp, min_temp = analyze_temperature(city)
        max_temps.append(max_temp)
        min_temps.append(min_temp)
    return max_temps, min_temps

"""
Compares highest and lowest humidity levels across multiple cities.

Args:
cities (list of str): List of city names to compare.

Returns:
tuple of lists: Lists containing highest and lowest humidity levels for each city.
"""

def compare_humidity(cities):
    highest_humidities = []
    lowest_humidities = []
    for city in cities:
        highest_humidity, lowest_humidity = analyze_humidity(city)
        highest_humidities.append(highest_humidity)
        lowest_humidities.append(lowest_humidity)
    return highest_humidities, lowest_humidities

"""Plot comparison of maximum and minimum temperatures for a list of cities.

Args:
    cities (list): List of city names.
    ax (matplotlib.axes.Axes): Matplotlib Axes object where the plot is drawn.
"""

def plot_temperature_comparison(cities, ax):
    max_temps, min_temps = compare_temperature(cities)  
    indices = np.arange(len(cities))  
    bar_width = 0.35  

    ax.clear()  
    bars_max = ax.bar(indices - bar_width/2, max_temps, width=bar_width, color='red', label='Max Temperature (°C)')
    bars_min = ax.bar(indices + bar_width/2, min_temps, width=bar_width, color='yellow', label='Min Temperature (°C)', alpha=0.7)

    # Annotate each bar with its respective data value for max temperatures
    for bar in bars_max:
        height = bar.get_height()
        ax.annotate(f'{height}°C',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Annotate each bar with its respective data value for min temperatures
    for bar in bars_min:
        height = bar.get_height()
        ax.annotate(f'{height}°C',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    ax.set_xlabel('City')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Comparison of Max and Min Temperatures Across Cities')
    ax.set_xticks(indices)
    ax.set_xticklabels(cities, rotation=45)
    ax.legend()
    ax.figure.canvas.draw()

"""Plot comparison of highest and lowest humidity percentages for a list of cities.

Args:
    cities (list): List of city names.
    ax (matplotlib.axes.Axes): Matplotlib Axes object where the plot is drawn.
"""

def plot_humidity_comparison(cities, ax):
    highest_humidities, lowest_humidities = compare_humidity(cities)  
    indices = np.arange(len(cities))  
    bar_width = 0.35  

    ax.clear()  
    bars_high = ax.bar(indices - bar_width/2, highest_humidities, width=bar_width, color='darkblue', label='Highest Humidity (%)')
    bars_low = ax.bar(indices + bar_width/2, lowest_humidities, width=bar_width, color='lightblue', label='Lowest Humidity (%)', alpha=0.7)

    # Annotate each bar with its respective data value for highest humidity
    for bar in bars_high:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Annotate each bar with its respective data value for lowest humidity
    for bar in bars_low:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    ax.set_xlabel('City')
    ax.set_ylabel('Humidity (%)')
    ax.set_title('Comparison of Highest and Lowest Humidity Across Cities')
    ax.set_xticks(indices)
    ax.set_xticklabels(cities, rotation=45)
    ax.legend()
    ax.figure.canvas.draw()

# Task 5. Create interface to interact with data or get reports, use tkinter or terminal but remember to make it data centric and user frinedly
"""A simple GUI application for comparing weather data across cities.

 Attributes:
    master (tk.Tk): The main window of the application.
    selected_cities (list): List of currently selected cities for comparison.
    city_buttons (dict): Dictionary of city names to their corresponding buttons.
"""

class WeatherApp:
    def __init__(self, master):
        self.master = master
        self.selected_cities = []
        self.city_buttons = {}  
        
        self.master.title("Weather Comparison Tool")
        self.master.configure(bg='lightgray')
        
        self.create_city_buttons()
        self.create_control_buttons()
        self.create_canvas_area()

    def create_city_buttons(self):
        """Create buttons for each city in the city list."""
        row = 0
        col = 0
        for city in city_list:
            cmd = lambda c=city: self.handle_city_selection(c)
            btn = tk.Button(self.master, text=city, command=cmd, width=12, bg='white')  
            btn.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
            self.city_buttons[city] = btn  # Store the button with city as key
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def create_control_buttons(self):
        """Create control buttons for undo, clear, and comparison actions."""
        self.undo_button = tk.Button(self.master, text="Undo", command=self.undo, bg='lightgray')
        self.undo_button.grid(row=5, column=0, sticky='nsew', padx=5, pady=5)

        self.clear_button = tk.Button(self.master, text="Clear", command=self.clear, bg='lightgray')
        self.clear_button.grid(row=5, column=1, sticky='nsew', padx=5, pady=5)

        self.compare_temp_button = tk.Button(self.master, text="Compare Temp.", command=self.compare_temperature, bg='lightblue')
        self.compare_temp_button.grid(row=5, column=2, sticky='nsew', padx=5, pady=5)

        self.compare_humidity_button = tk.Button(self.master, text="Compare Humidity", command=self.compare_humidity, bg='pink')
        self.compare_humidity_button.grid(row=6, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)

    def create_canvas_area(self):
        """Create a canvas area in the GUI for displaying matplotlib plots."""
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=7, column=0, columnspan=4, pady=10)

    def handle_city_selection(self, city):
        """Toggle the selection of a city and update the UI accordingly."""
        if city not in self.selected_cities:
            self.selected_cities.append(city)
            self.city_buttons[city].configure(bg='darkgray')  # Change button color to dark gray
            messagebox.showinfo("City Added", f"Added {city}")
        else:
            self.selected_cities.remove(city)
            self.city_buttons[city].configure(bg='white')  # Change button color back to white
            messagebox.showinfo("City Removed", f"Removed {city}")

    def undo(self):
        """Undo the last city selection."""
        if self.selected_cities:
            removed_city = self.selected_cities.pop()
            self.city_buttons[removed_city].configure(bg='white')  # Revert color to white
            messagebox.showinfo("City Removed", f"Removed {removed_city}")

    def clear(self):
        """Clear all city selections and reset the plot area."""
        for city in self.selected_cities:
            self.city_buttons[city].configure(bg='white')  # Revert all city button colors to white
        self.selected_cities = []
        self.ax.clear()
        self.ax.figure.canvas.draw()
        messagebox.showinfo("Cleared", "All selections cleared.")

    def compare_temperature(self):
        """Compare temperatures of selected cities and display the results."""
        if self.selected_cities:
            plot_temperature_comparison(self.selected_cities, self.ax)
        else:
            messagebox.showinfo("No City Selected", "Please add cities to compare.")

    def compare_humidity(self):
        """Compare humidity levels of selected cities and display the results."""
        if self.selected_cities:
            plot_humidity_comparison(self.selected_cities, self.ax)
        else:
            messagebox.showinfo("No City Selected", "Please add cities to compare.")

root = tk.Tk()
app = WeatherApp(root)
root.mainloop()