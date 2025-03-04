import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import joblib
import numpy as np
import datetime
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load the trained model
model = joblib.load('finial_prediction.pkl')

# City Encoding Dictionary
city_mapping = {'Ahmedabad':0 , 'Aizawl':1, 'Amaravati':2, 'Amritsar':3, 
                'Bengaluru':4, 'Bhopal':5, 'Brajrajnagar':6,'Chandigarh':7, 
                'Chennai':8, 'Coimbatore':9,'Delhi':10, 'Ernakulam':11, 
                'Gurugram':12, 'Guwahati':13, 'Hyderabad':14, 'Jaipur':15, 
                'Jorapokhar':16, 'Kochi':17, 'Kolkata':18, 'Lucknow':19, 
                'Mumbai':20, 'Patna':21, 'Shillong':22, 'Talcher':23, 
                'Thiruvananthapuram':24, 'Visakhapatnam':25}

# Email Credentials (Use App Password)
SENDER_EMAIL = "datahackathon64@gmail.com"
SENDER_PASSWORD = "Muruga@1234"  # Use App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# Function to get AQI category
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif 51 < aqi <= 100:
        return "Moderate"
    elif 101 < aqi <= 200:
        return "Moderate"
    elif 201 < aqi <= 300:
        return "Poor"
    elif 301 < aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

# Function to predict AQI
def predict_aqi():
    try:
        # Get input values
        pm25 = float(entry_pm25.get())
        pm10 = float(entry_pm10.get())
        no = float(entry_no.get())
        no2 = float(entry_no2.get())
        nox = float(entry_nox.get())
        nh3 = float(entry_nh3.get())
        co = float(entry_co.get())
        so2 = float(entry_so2.get())
        toluene = float(entry_toluene.get())

        # Get city encoding
        city_name = city_var.get()
        if city_name not in city_mapping:
            messagebox.showerror("Input Error", "Invalid City Selected")
            return
        
        city_encoded = city_mapping[city_name]

        date_input = entry_date.get()
        if not date_input:
            messagebox.showerror("Input Error", "Please enter a date in YYYY-MM-DD format")
            return
        try:
            year = datetime.datetime.strptime(date_input, "%Y-%m-%d").year
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD")
            return

        # Arrange input values as numpy array
        input_data = np.array([[year, pm25, pm10, no, no2, nox, nh3, co, so2, toluene, city_encoded]])

        # Predict AQI
        prediction = model.predict(input_data)
        prediction = round(prediction[0], 2)

        # Get AQI category
        category = get_aqi_category(prediction)

        # Display results
        result_label.config(text=f"Predicted AQI: {prediction}")
        category_label.config(text=f"AQI Category: {category}")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers")

# Function to send AQI alert emails
def send_aqi_alert():
    try:
        aqi_value = result_label.cget("text").split(": ")[1]  # Get AQI value
        category = category_label.cget("text").split(": ")[1]  # Get AQI category
        city_name = city_var.get()

        if not aqi_value or aqi_value == "Predicted AQI: ":
            messagebox.showerror("Error", "Predict AQI first before sending email!")
            return

        # Load recipient data from CSV
        df = pd.read_csv("recipients.csv")

        for _, row in df.iterrows():
            email = row.iloc[1]
            name = row.iloc[0]
            location = row.iloc[2]

            subject = f"AQI Alert for {location} - {category}"
            body = f"""
            Dear {name},

            This is an important Air Quality Index (AQI) alert for your area.

            📍 Location: {location}
            🌫️ AQI Level: {aqi_value} ({category})

            Please take necessary precautions:
            - Keep children and patients indoors.
            - Use air purifiers if available.
            - Avoid outdoor activities.

            Stay safe,
            AQI Monitoring Team
            """

            # Email setup
            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, msg.as_string())

        messagebox.showinfo("Success", "AQI alert emails sent successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email\nError: {str(e)}")

# Tkinter GUI
root = tk.Tk()
root.title("AQI Prediction & Alerts")

# Load Background Image
bg_image = Image.open("image.jpg")
bg_image = bg_image.resize((800, 600), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Background Label
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Center Frame
frame = tk.Frame(root, bg="white", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Labels and Entry Widgets
tk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
entry_date = tk.Entry(frame)
entry_date.grid(row=0, column=1)

tk.Label(frame, text="PM2.5:").grid(row=1, column=0)
entry_pm25 = tk.Entry(frame)
entry_pm25.grid(row=1, column=1)

tk.Label(frame, text="PM10:").grid(row=2, column=0)
entry_pm10 = tk.Entry(frame)
entry_pm10.grid(row=2, column=1)

tk.Label(frame, text="NO:").grid(row=3, column=0)
entry_no = tk.Entry(frame)
entry_no.grid(row=3, column=1)

tk.Label(frame, text="NO2:").grid(row=4, column=0)
entry_no2 = tk.Entry(frame)
entry_no2.grid(row=4, column=1)

tk.Label(frame, text="NOx:").grid(row=5, column=0)
entry_nox = tk.Entry(frame)
entry_nox.grid(row=5, column=1)

tk.Label(frame, text="NH3:").grid(row=6, column=0)
entry_nh3 = tk.Entry(frame)
entry_nh3.grid(row=6, column=1)

tk.Label(frame, text="CO:").grid(row=7, column=0)
entry_co = tk.Entry(frame)
entry_co.grid(row=7, column=1)

tk.Label(frame, text="SO2:").grid(row=8, column=0)
entry_so2 = tk.Entry(frame)
entry_so2.grid(row=8, column=1)

tk.Label(frame, text="Toluene:").grid(row=9, column=0)
entry_toluene = tk.Entry(frame)
entry_toluene.grid(row=9, column=1)

tk.Label(frame, text="City:").grid(row=10, column=0)
city_var = tk.StringVar(root)
city_var.set("Select City")
city_dropdown = tk.OptionMenu(frame, city_var, *city_mapping.keys())
city_dropdown.grid(row=10, column=1)

# Buttons
predict_button = tk.Button(frame, text="Predict AQI", command=predict_aqi)
predict_button.grid(row=11, column=0, columnspan=2)

send_email_button = tk.Button(frame, text="Send AQI Alerts", command=send_aqi_alert, bg="green", fg="white")
send_email_button.grid(row=15, column=0, columnspan=2)

# Labels for output
result_label = tk.Label(frame, text="Predicted AQI: ", font=('Arial', 12, 'bold'), bg="white")
result_label.grid(row=13, column=0, columnspan=2)

category_label = tk.Label(frame, text="AQI Category: ", font=('Arial', 12, 'bold'), bg="white")
category_label.grid(row=12, column=0, columnspan=2)

# Run GUI
root.geometry("800x600")
root.mainloop()
