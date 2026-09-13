import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import asyncio

class EmailSender:
    """Handle email sending for weather updates"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
    
    def create_weather_email_body(self, city: str, weather_data: Dict) -> str:
        """Create HTML email body with weather information"""
        
        openweather = weather_data.get("openweather", {})
        api_ninjas = weather_data.get("api_ninjas", {})
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }}
                    h1 {{ color: #2c3e50; text-align: center; }}
                    h2 {{ color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                    .weather-item {{ background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                    .temp {{ font-size: 24px; font-weight: bold; color: #e74c3c; }}
                    .description {{ font-style: italic; color: #7f8c8d; }}
                    .forecast {{ background-color: #e8f4f8; padding: 10px; margin: 5px 0; border-left: 4px solid #3498db; }}
                    .footer {{ text-align: center; color: #95a5a6; margin-top: 20px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🌤️ Weather Forecast for {city}</h1>
                    <p>Here's your tomorrow's weather update from multiple sources:</p>
        """
        
        # OpenWeatherMap Section
        if openweather and openweather.get("forecasts"):
            html_body += f"""
                    <h2>OpenWeatherMap Forecast</h2>
                    <p><strong>Location:</strong> {openweather.get('city')}, {openweather.get('country')}</p>
            """
            
            for forecast in openweather.get("forecasts", []):
                html_body += f"""
                    <div class="forecast">
                        <strong>{forecast['time']}</strong><br>
                        <span class="temp">{forecast['temperature']}°C</span><br>
                        <span class="description">{forecast['description']}</span><br>
                        Feels like: {forecast['feels_like']}°C<br>
                        Humidity: {forecast['humidity']}%<br>
                        Wind Speed: {forecast['wind_speed']} m/s
                    </div>
                """
        
        # API Ninjas Section
        if api_ninjas:
            html_body += f"""
                    <h2>API Ninjas Weather Data</h2>
                    <div class="weather-item">
                        <p><strong>Location:</strong> {api_ninjas.get('city')}, {api_ninjas.get('country')}</p>
                        <p class="temp">Current: {api_ninjas.get('temperature')}°C</p>
                        <ul>
                            <li>Feels Like: {api_ninjas.get('feels_like')}°C</li>
                            <li>Min / Max: {api_ninjas.get('min_temp')}°C / {api_ninjas.get('max_temp')}°C</li>
                            <li>Humidity: {api_ninjas.get('humidity')}%</li>
                            <li>Wind Speed: {api_ninjas.get('wind_speed')} m/s</li>
                            <li>Wind Direction: {api_ninjas.get('wind_direction')}°</li>
                            <li>Cloud Coverage: {api_ninjas.get('cloudiness')}%</li>
                            <li>Sunrise: {api_ninjas.get('sunrise')}</li>
                            <li>Sunset: {api_ninjas.get('sunset')}</li>
                        </ul>
                    </div>
            """
        
        html_body += """
                    <div class="footer">
                        <p>Weather information provided by OpenWeatherMap and API Ninjas</p>
                        <p>This is an automated weather update. Please check the weather services directly for critical decisions.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html_body
    
    def send_email(self, recipient_email: str, city: str, weather_data: Dict) -> bool:
        """Send weather email to recipient"""
        try:
            if not all([self.sender_email, self.sender_password]):
                print("Error: Email credentials not configured")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🌤️ Tomorrow's Weather Forecast for {city}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Create HTML content
            html_content = self.create_weather_email_body(city, weather_data)
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"Email sent successfully to {recipient_email}")
            return True
            
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {e}")
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
