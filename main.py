import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import json
from weather_utils import WeatherFetcher
from email_utils import EmailSender
from weather_agent import WeatherAgent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Weather Agent API",
    description="An AI-powered weather forecasting and email notification system",
    version="1.0.0"
)

# Initialize components
weather_fetcher = WeatherFetcher()
email_sender = EmailSender()

try:
    weather_agent = WeatherAgent()
    agent_available = True
except Exception as e:
    print(f"Warning: Weather agent not available: {e}")
    agent_available = False


# Pydantic models
class WeatherRequest(BaseModel):
    city: str
    email: str


class WeatherResponse(BaseModel):
    success: bool
    message: str
    city: str
    email: str
    weather_data: dict = None
    analysis: str = None


# Routes

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the main HTML page"""
    return r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather Agent - Tomorrow's Forecast</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 500px;
                width: 100%;
            }

            .header {
                text-align: center;
                margin-bottom: 40px;
            }

            .header h1 {
                color: #333;
                font-size: 32px;
                margin-bottom: 10px;
            }

            .header p {
                color: #666;
                font-size: 16px;
            }

            .weather-icon {
                font-size: 48px;
                margin: 10px 0;
            }

            .form-group {
                margin-bottom: 25px;
            }

            label {
                display: block;
                color: #333;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
            }

            input[type="text"],
            input[type="email"] {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }

            input[type="text"]:focus,
            input[type="email"]:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .btn-submit {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .btn-submit:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }

            .btn-submit:active {
                transform: translateY(0);
            }

            .btn-submit:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }

            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }

            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .result {
                display: none;
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }

            .result.success {
                border-left-color: #28a745;
                background: #d4edda;
            }

            .result.error {
                display: block;
                border-left-color: #dc3545;
                background: #f8d7da;
            }

            .result h3 {
                color: #333;
                margin-bottom: 10px;
            }

            .result p {
                color: #555;
                line-height: 1.6;
            }

            .info-box {
                background: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin-bottom: 25px;
                border-radius: 4px;
                color: #0c5460;
                font-size: 13px;
                line-height: 1.5;
            }

            .weather-report h3 {
                color: #333;
                margin-bottom: 12px;
            }

            .weather-report .sent-note {
                font-size: 13px;
                color: #2e7d32;
                margin-bottom: 15px;
            }

            .weather-report .analysis-box {
                background: #fff8e1;
                border-left: 4px solid #ffb300;
                padding: 12px 15px;
                border-radius: 4px;
                margin-bottom: 15px;
                line-height: 1.5;
                color: #5d4037;
                white-space: pre-wrap;
            }

            .weather-report .source-block {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 12px;
            }

            .weather-report .source-block h4 {
                color: #667eea;
                font-size: 15px;
                margin-bottom: 8px;
                border-bottom: 1px solid #eee;
                padding-bottom: 6px;
            }

            .weather-report .forecast-row {
                display: flex;
                justify-content: space-between;
                padding: 6px 0;
                border-bottom: 1px dashed #eee;
                font-size: 13px;
                color: #444;
            }

            .weather-report .forecast-row:last-child {
                border-bottom: none;
            }

            .weather-report .temp-badge {
                font-weight: 700;
                color: #e74c3c;
            }

            .weather-report dl {
                display: grid;
                grid-template-columns: auto 1fr;
                gap: 4px 10px;
                font-size: 13px;
                color: #444;
            }

            .weather-report dt {
                font-weight: 600;
                color: #555;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="weather-icon">🌤️</div>
                <h1>Weather Agent</h1>
                <p>Get tomorrow's weather forecast delivered to your email</p>
            </div>

            <div class="info-box">
                ℹ️ Enter your city name and email to receive a detailed weather forecast powered by AI analysis.
            </div>

            <form id="weatherForm">
                <div class="form-group">
                    <label for="city">City Name</label>
                    <input 
                        type="text" 
                        id="city" 
                        name="city" 
                        placeholder="e.g., London, New York, Tokyo"
                        required
                    >
                </div>

                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input 
                        type="email" 
                        id="email" 
                        name="email" 
                        placeholder="your.email@example.com"
                        required
                    >
                </div>

                <button type="submit" class="btn-submit">Get Weather Forecast</button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="color: #666; margin-top: 10px;">Fetching weather data...</p>
            </div>

            <div class="result" id="result"></div>
        </div>

        <script>
            function escapeHtml(str) {
                if (str === null || str === undefined) return '';
                return String(str)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;');
            }

            function renderWeatherHtml(data) {
                const wd = data.weather_data || {};
                const ow = wd.openweather;
                const an = wd.api_ninjas;

                let html = `<div class="weather-report">`;
                html += `<h3>🌤️ Weather Report for ${escapeHtml(data.city)}</h3>`;
                html += `<p class="sent-note">✅ Also emailed to <strong>${escapeHtml(data.email)}</strong></p>`;

                if (data.analysis) {
                    const analysisText = typeof data.analysis === 'string' ? data.analysis : JSON.stringify(data.analysis);
                    html += `<div class="analysis-box"><strong>🤖 AI Analysis:</strong><br>${escapeHtml(analysisText)}</div>`;
                }

                if (ow && ow.forecasts && ow.forecasts.length) {
                    html += `<div class="source-block">`;
                    html += `<h4>OpenWeatherMap — ${escapeHtml(ow.city)}, ${escapeHtml(ow.country)}</h4>`;
                    ow.forecasts.forEach(f => {
                        html += `
                            <div class="forecast-row">
                                <span>${escapeHtml(f.time)} — ${escapeHtml(f.description)}</span>
                                <span class="temp-badge">${escapeHtml(f.temperature)}°C</span>
                            </div>`;
                    });
                    html += `</div>`;
                }

                if (an) {
                    html += `<div class="source-block">`;
                    html += `<h4>API Ninjas — ${escapeHtml(an.city)}, ${escapeHtml(an.country)}</h4>`;
                    html += `<dl>
                        <dt>Temperature</dt><dd>${escapeHtml(an.temperature)}°C</dd>
                        <dt>Feels Like</dt><dd>${escapeHtml(an.feels_like)}°C</dd>
                        <dt>Min/Max</dt><dd>${escapeHtml(an.min_temp)}°C / ${escapeHtml(an.max_temp)}°C</dd>
                        <dt>Humidity</dt><dd>${escapeHtml(an.humidity)}%</dd>
                        <dt>Wind Speed</dt><dd>${escapeHtml(an.wind_speed)} m/s</dd>
                        <dt>Cloud Coverage</dt><dd>${escapeHtml(an.cloudiness)}%</dd>
                        <dt>Sunrise</dt><dd>${escapeHtml(an.sunrise)}</dd>
                        <dt>Sunset</dt><dd>${escapeHtml(an.sunset)}</dd>
                    </dl>`;
                    html += `</div>`;
                }

                html += `</div>`;
                return html;
            }

            const form = document.getElementById('weatherForm');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const city = document.getElementById('city').value;
                const email = document.getElementById('email').value;

                loading.style.display = 'block';
                result.style.display = 'none';

                try {
                    const formData = new FormData();
                    formData.append('city', city);
                    formData.append('email', email);

                    const response = await fetch('/api/weather', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();
                    loading.style.display = 'none';

                    if (data.success) {
                        result.className = 'result success';
                        result.innerHTML = renderWeatherHtml(data);
                    } else {
                        result.className = 'result error';
                        result.innerHTML = `
                            <h3>❌ Error</h3>
                            <p>${escapeHtml(data.message)}</p>
                        `;
                    }
                    result.style.display = 'block';

                } catch (error) {
                    loading.style.display = 'none';
                    result.className = 'result error';
                    result.innerHTML = `
                        <h3>❌ Error</h3>
                        <p>Failed to process request: ${error.message}</p>
                    `;
                    result.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """


@app.post("/api/weather")
async def get_weather(city: str = Form(...), email: str = Form(...)):
    """
    Get weather forecast and send email with AI analysis

    Args:
        city: City name
        email: Recipient email address

    Returns:
        JSON response with success status and message
    """
    try:
        # Validate inputs
        if not city or not city.strip():
            raise HTTPException(status_code=400, detail="City name is required")

        if not email or not email.strip():
            raise HTTPException(status_code=400, detail="Email address is required")

        # Fetch weather data
        print(f"Fetching weather for {city}...")
        weather_data = weather_fetcher.get_combined_weather(city)
        print(weather_data)
        if not weather_data or (not weather_data.get("openweather") and not weather_data.get("api_ninjas")):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"Could not find weather data for '{city}'. Please check the city name and try again.",
                    "city": city,
                    "email": email,
                    "analysis": ""
                }
            )

        # Get AI analysis if agent is available
        analysis = ""
        if agent_available:
            try:
                print("Analyzing weather with AI agent...")
                analysis = weather_agent.get_simple_analysis(city, weather_data)
                # Ensure analysis is a string
                if not isinstance(analysis, str):
                    analysis = str(analysis) if analysis else ""
                print(f"Analysis received: {analysis[:100]}...")
            except Exception as e:
                print(f"Warning: Could not get AI analysis: {e}")
                analysis = ""

        # Send email WITH ANALYSIS
        print(f"Sending email to {email}...")
        email_result = email_sender.send_email(email, city, weather_data, analysis)
        print(f"Email result: {email_result}")

        # Ensure email_result is a dict
        if not isinstance(email_result, dict):
            print(f"ERROR: email_result is not a dict! Type: {type(email_result)}")
            email_result = {"success": False,
                            "error": f"Unexpected return type from email sender: {type(email_result)}"}

        if not email_result.get("success", False):
            return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "message": f"Weather data was fetched, but the email could not be sent: {email_result.get('error', 'Unknown error')}",
                    "city": city,
                    "email": email,
                    "weather_data": weather_data,
                    "analysis": analysis
                }
            )

        return {
            "success": True,
            "message": f"Weather forecast for {city} has been sent to {email} with AI analysis",
            "city": city,
            "email": email,
            "weather_data": weather_data,
            "analysis": analysis
        }

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"An error occurred: {str(e)}",
                "city": "",
                "email": "",
                "analysis": ""
            }
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_available": agent_available,
        "services": {
            "weather_fetcher": "ready",
            "email_sender": "ready",
            "gemini_agent": "ready" if agent_available else "unavailable"
        }
    }


@app.get("/api/weather/{city}")
async def get_weather_data(city: str):
    """Get weather data for a city (no email sending)"""
    try:
        weather_data = weather_fetcher.get_combined_weather(city)

        if not weather_data or (not weather_data.get("openweather") and not weather_data.get("api_ninjas")):
            raise HTTPException(status_code=404, detail=f"Weather data not found for {city}")

        return {
            "success": True,
            "city": city,
            "data": weather_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Weather Agent API Starting...")
    print(f"🤖 AI Agent Available: {agent_available}")
    print(f"📧 Email Service: {'Configured' if email_sender.sender_email else 'Not Configured'}")
    print("✅ All systems ready!")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False") == "True"

    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
