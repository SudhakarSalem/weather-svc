import os
import json
from typing import Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool


# --- Tools -------------------------------------------------------------
# In LangChain 1.x, tools are plain functions decorated with @tool.
# The docstring becomes the tool description shown to the model.

@tool
def analyze_weather(weather_data_json: str) -> str:
    """Analyze raw weather data (as a JSON string) and return insights:
    overview, what-to-wear advice, activity suggestions, and any health
    warnings (heat, cold, UV, etc.)."""
    try:
        data = json.loads(weather_data_json)
    except json.JSONDecodeError:
        return "Error: Invalid weather data format"
    return f"Parsed weather data with {len(data)} top-level fields ready for analysis."


@tool
def generate_summary(weather_data_json: str) -> str:
    """Generate a short, friendly 2-3 sentence summary of the given
    weather data (as a JSON string)."""
    try:
        json.loads(weather_data_json)
    except json.JSONDecodeError:
        return "Error: Invalid weather data format"
    return "Summary generated from the provided weather data."


class WeatherAgent:
    """LangChain 1.x agent for weather analysis using Gemini."""

    def __init__(self, model_name: str = "gemini-3.5-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
        )

        # create_agent replaces the deprecated initialize_agent/AgentType API.
        # It returns a LangGraph-backed runnable agent.
        self.agent = create_agent(
            model=self.llm,
            tools=[analyze_weather, generate_summary],
            system_prompt=(
                "You are a helpful weather assistant. Use the provided tools "
                "when useful, then give clear, practical recommendations."
            ),
        )

    def _run_agent(self, query: str) -> str:
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        # The final AI message is the last one in the returned message list.
        return result["messages"][-1].content

    def process_weather(self, city: str, weather_data: Dict) -> Dict:
        """Process weather data through the full agent (tools + reasoning)."""
        try:
            weather_json = json.dumps(weather_data, indent=2)

            query = f"""
            Please analyze the weather data for {city} and provide:
            1. A summary of the weather conditions
            2. Recommendations for tomorrow's activities
            3. Any important warnings or considerations

            Here's the weather data:
            {weather_json}
            """

            response = self._run_agent(query)

            return {
                "success": True,
                "city": city,
                "analysis": response,
                "raw_data": weather_data,
            }

        except Exception as e:
            return {
                "success": False,
                "city": city,
                "error": str(e),
                "raw_data": weather_data,
            }

    def get_simple_analysis(self, city: str, weather_data: Dict) -> str:
        """Get a brief weather analysis directly from the model (no tool
        calls) - cheaper and faster than the full agent loop."""
        try:
            prompt = f"""
              Provide a brief weather analysis for {city} based on this data:

              {json.dumps(weather_data, indent=2)}

              Include: temperature range, conditions, and one key recommendation.
              Keep it under 100 words.
              """

            response = self.llm.invoke(prompt)
            text = self._extract_text_from_response(response)
            return text

        except Exception as e:
            return f"Unable to generate analysis: {str(e)}"

    def _extract_text_from_response(self, response) -> str:
        """Extract plain text from LLM response, handling various formats."""
        if isinstance(response, str):
            return response

        if hasattr(response, 'content'):
            content = response.content

            # If content is a string, return it
            if isinstance(content, str):
                return content

            # If content is a list of message objects with 'text' field
            if isinstance(content, list) and len(content) > 0:
                if isinstance(content[0], dict) and 'text' in content[0]:
                    return content[0]['text']
                # Try to extract text from first item if it has content
                if hasattr(content[0], 'text'):
                    return content[0].text

            # If content is a dict with 'text' field
            if isinstance(content, dict) and 'text' in content:
                return content['text']

            # Fallback: convert to string
            return str(content)

        return str(response)
