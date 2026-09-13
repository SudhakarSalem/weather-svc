# 🌤️ Weather Agent - AI-Powered Weather Forecast System

An intelligent weather forecasting application built with FastAPI, LangChain, and Google's Gemini AI that fetches weather data from multiple sources and delivers personalized weather reports via email.

## Features

✨ **Core Features:**
- 🤖 **AI-Powered Analysis** - Uses Google Gemini 3.5-Flash for intelligent weather insights
- 📊 **Multi-Source Data** - Fetches from OpenWeatherMap and API Ninjas for comprehensive coverage
- 📧 **Email Delivery** - Sends formatted weather reports directly to your inbox
- 🌐 **Web Interface** - Beautiful, responsive HTML interface for easy access
- 🔄 **REST API** - Full API endpoints for programmatic access
- ⚡ **FastAPI** - Modern, fast Python web framework

## Project Structure

```
weather-agent/
├── main.py                 # FastAPI application and routes
├── weather_utils.py        # Weather data fetching from APIs
├── email_utils.py          # Email sending functionality
├── weather_agent.py        # LangChain agent with Gemini
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Prerequisites

- **Python 3.14.5** or higher
- **API Keys** (required):
  - Google Gemini API Key: https://aistudio.google.com/app/apikey
  - OpenWeatherMap API Key: https://openweathermap.org/api
  - API Ninjas API Key: https://api-ninjas.com/api/weather
  - Gmail App Password (for email sending)

## Installation

### 1. Clone or Download Project

```bash
cd weather-agent
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Google Gemini API
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Weather APIs
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
API_NINJAS_API_KEY=your_api_ninjas_api_key_here

# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here

# FastAPI Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Getting API Keys

#### Google Gemini API
1. Visit https://aistudio.google.com/app/apikey
2. Create a new API key
3. Copy and paste into `.env`

#### OpenWeatherMap API
1. Sign up at https://openweathermap.org/api
2. Go to your API keys section
3. Copy your API key

#### API Ninjas
1. Visit https://api-ninjas.com/
2. Sign up and navigate to API keys
3. Copy your API key

#### Gmail App Password
1. Enable 2-Step Verification on your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for Gmail
4. Use this password in `.env` (not your regular Gmail password)

## Running the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: **http://localhost:8000**

## API Endpoints

### 1. Get Homepage
```
GET /
```
Returns the main HTML interface.

### 2. Get Weather & Send Email
```
POST /api/weather
Content-Type: application/x-www-form-urlencoded

city=London&email=user@example.com
```

**Response:**
```json
{
  "success": true,
  "message": "Weather forecast for London has been sent to user@example.com",
  "city": "London",
  "email": "user@example.com",
  "weather_data": {...},
  "analysis": "AI weather analysis..."
}
```

### 3. Get Weather Data Only
```
GET /api/weather/{city}
```

**Response:**
```json
{
  "success": true,
  "city": "London",
  "data": {
    "openweather": {...},
    "api_ninjas": {...}
  }
}
```

### 4. Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_available": true,
  "services": {
    "weather_fetcher": "ready",
    "email_sender": "ready",
    "gemini_agent": "ready"
  }
}
```

## Usage Examples

### Web Interface
1. Open http://localhost:8000 in your browser
2. Enter a city name (e.g., "London")
3. Enter your email address
4. Click "Get Weather Forecast"
5. Check your email for the weather report

### Python Script
```python
from weather_utils import WeatherFetcher
from email_utils import EmailSender
from weather_agent import WeatherAgent

# Fetch weather
fetcher = WeatherFetcher()
weather = fetcher.get_combined_weather("London")

# Send email
sender = EmailSender()
sender.send_email("user@example.com", "London", weather)

# Analyze with AI
agent = WeatherAgent()
analysis = agent.get_simple_analysis("London", weather)
print(analysis)
```

### cURL Command
```bash
curl -X POST http://localhost:8000/api/weather \
  -d "city=London&email=user@example.com"
```

## Features Breakdown

### 🌍 Weather Data Sources

**OpenWeatherMap:**
- 5-day forecast data
- Detailed hourly information
- Temperature, humidity, pressure
- Wind speed and direction
- Weather conditions

**API Ninjas:**
- Current weather conditions
- Temperature and "feels like" temperature
- Cloud coverage percentage
- Sunrise/sunset times
- Wind information

### 🤖 AI Analysis Features

The Gemini 3.5-Flash model provides:
- Weather summary and overview
- Activity recommendations
- Clothing suggestions
- Health warnings (heat, cold, UV index concerns)
- Best times for outdoor activities
- Practical lifestyle advice

### 📧 Email Features

- HTML-formatted emails
- Data from both weather sources
- Professional styling
- Responsive design for all devices
- Clear weather information presentation

## Troubleshooting

### "GOOGLE_API_KEY not set" Error
- Ensure `.env` file exists in the project root
- Check that `GOOGLE_API_KEY` is properly set
- Verify the API key is valid

### "Email credentials not configured" Error
- Check `SENDER_EMAIL` and `SENDER_PASSWORD` in `.env`
- For Gmail, use an App Password, not your regular password
- Enable 2-Step Verification if using Gmail

### "Could not find weather data" Error
- Verify API keys for weather services are valid
- Check that the city name is spelled correctly
- Ensure your API keys have remaining quota

### Email Not Received
- Check spam folder
- Verify recipient email is correct
- Check SMTP configuration (Gmail uses port 587)
- Ensure "Less secure app access" is enabled (if not using App Password)

## Performance Tips

- The agent analysis step may take a few seconds
- Weather data is not cached; each request fetches fresh data
- For production, consider adding caching or request queuing

## Development

### Adding New Weather Sources
Edit `weather_utils.py` and add a new method to the `WeatherFetcher` class.

### Customizing Email Templates
Edit the `create_weather_email_body` method in `email_utils.py`.

### Modifying AI Analysis
Edit the prompts in `weather_agent.py` to change analysis style.

## Security Notes

⚠️ **Important:**
- Never commit `.env` file with real API keys
- Use environment variables in production
- Keep API keys secret and rotate regularly
- For Gmail, always use App Passwords, never regular passwords

## Requirements Versions

- Python 3.14.5+
- FastAPI 0.115+
- Uvicorn 0.32+
- LangChain 1.3.1+ (uses the new `create_agent` API — `initialize_agent`/`AgentType` are deprecated)
- langchain-google-genai 4.0.0+
- Requests 2.32+

> **Note on LangChain 1.x:** The agent construction API changed significantly from 0.x. This project uses `create_agent` from `langchain.agents` (LangGraph-backed) instead of the deprecated `initialize_agent` + `AgentType` pattern. Tools are defined with the `@tool` decorator, and the agent is invoked with a `{"messages": [...]}` payload rather than `.run(...)`.

## License

This project is open source. Feel free to modify and use as needed.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all API keys are correct
3. Ensure all dependencies are installed
4. Check that Python version is 3.14.5+

## Future Enhancements

- ✅ Multi-language support
- ✅ Weather alerts and warnings
- ✅ Weekly/monthly forecasts
- ✅ Historical weather analysis
- ✅ Weather trend predictions
- ✅ User preferences and subscriptions
- ✅ Mobile app integration
- ✅ Database for storing forecasts