import os
import requests
import wikipedia
import pyjokes
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_coreimport os
import requests
import wikipedia
import pyjokes
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")

# --- Define the Tools for the Agent ---
# The @tool decorator automatically creates a function calling schema for the LLM.

@tool
def get_weather(city: str) -> str:
    """Useful for fetching the current weather for a specified city.
    Input should be a string representing the city name, e.g., 'London' or 'Tokyo'."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweathermap_api_key}&units=metric"
        response = requests.get(url).json()
        if response.get('main'):
            temp = response['main']['temp']
            weather_desc = response['weather'][0]['description']
            return f"The current temperature in {city.capitalize()} is {temp}°C with {weather_desc}."
        return "I couldn't find the weather information for that city."
    except requests.exceptions.RequestException:
        return "An error occurred while fetching weather data."

@tool
def get_joke() -> str:
    """Useful for telling a joke. This tool returns a humorous one-liner joke."""
    return pyjokes.get_joke()

@tool
def get_wikipedia_summary(query: str) -> str:
    """Useful for getting a summary from Wikipedia about a specific topic.
    Input should be a string representing the search query."""
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.PageError:
        return "I couldn't find any information on that topic."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Please be more specific. Your query could refer to: {', '.join(e.options[:5])}."

@tool
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Useful for calculating Body Mass Index (BMI).
    Input should be a person's weight in kilograms and height in meters.
    Example: use 'calculate_bmi(70.5, 1.75)' for a person weighing 70.5 kg and 1.75 m tall."""
    if height_m <= 0:
        return "Height cannot be zero or negative."
    bmi = weight_kg / (height_m ** 2)
    category = "Unknown"
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obesity"
    return f"Your BMI is {bmi:.2f}, which is classified as {category}."

@tool
def get_mental_wellness_tip() -> str:
    """Provides a general tip for mental well-being and stress relief.
    This tool is to be used when the user asks for advice on stress, anxiety, or mental health."""
    tips = [
        "Take a few deep breaths. Inhale for 4 seconds, hold for 4, and exhale for 6.",
        "Remember to stay hydrated. Water can significantly impact your energy levels and mood.",
        "Take a short walk. Even 15 minutes of movement can help clear your mind.",
        "Practice gratitude. Write down three things you are thankful for today.",
        "Reach out to a friend or loved one. A quick chat can make a big difference."
    ]
    import random
    return random.choice(tips)

# --- Set up the LangChain Agent ---
tools = [get_weather, get_joke, get_wikipedia_summary, calculate_bmi, get_mental_wellness_tip]

llm = ChatGroq(model="qwen/qwen3-32b", groq_api_key=groq_api_key, temperature=0.7)

# The agent prompt is now much simpler. The LLM handles tool selection via
# Groq's tool-calling API, not by parsing a string.
system_prompt = """
You are Maitri AI, a helpful and empathetic assistant focused on physiological and physical well-being.
Answer the user's questions to the best of your ability.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        # This placeholder will be filled with the chat history
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        # This placeholder will be filled with intermediate agent steps
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Create the agent executor
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Memory Management with RunnableWithMessageHistory ---
store = {}
def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Wrap the agent executor with history management
agent_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Function to get a response from the agent
def get_agent_response(query, session_id):
    """
    Invokes the agent with a user query and a session ID.
    The session ID is crucial for maintaining chat history.
    """
    return agent_with_history.invoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}}
    )['output'].prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")

# --- Define the Tools for the Agent ---
# The @tool decorator automatically creates a function calling schema for the LLM.

@tool
def get_weather(city: str) -> str:
    """Useful for fetching the current weather for a specified city.
    Input should be a string representing the city name, e.g., 'London' or 'Tokyo'."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweathermap_api_key}&units=metric"
        response = requests.get(url).json()
        if response.get('main'):
            temp = response['main']['temp']
            weather_desc = response['weather'][0]['description']
            return f"The current temperature in {city.capitalize()} is {temp}°C with {weather_desc}."
        return "I couldn't find the weather information for that city."
    except requests.exceptions.RequestException:
        return "An error occurred while fetching weather data."

@tool
def get_joke() -> str:
    """Useful for telling a joke. This tool returns a humorous one-liner joke."""
    return pyjokes.get_joke()

@tool
def get_wikipedia_summary(query: str) -> str:
    """Useful for getting a summary from Wikipedia about a specific topic.
    Input should be a string representing the search query."""
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.PageError:
        return "I couldn't find any information on that topic."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Please be more specific. Your query could refer to: {', '.join(e.options[:5])}."

@tool
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Useful for calculating Body Mass Index (BMI).
    Input should be a person's weight in kilograms and height in meters.
    Example: use 'calculate_bmi(70.5, 1.75)' for a person weighing 70.5 kg and 1.75 m tall."""
    if height_m <= 0:
        return "Height cannot be zero or negative."
    bmi = weight_kg / (height_m ** 2)
    category = "Unknown"
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obesity"
    return f"Your BMI is {bmi:.2f}, which is classified as {category}."

@tool
def get_mental_wellness_tip() -> str:
    """Provides a general tip for mental well-being and stress relief.
    This tool is to be used when the user asks for advice on stress, anxiety, or mental health."""
    tips = [
        "Take a few deep breaths. Inhale for 4 seconds, hold for 4, and exhale for 6.",
        "Remember to stay hydrated. Water can significantly impact your energy levels and mood.",
        "Take a short walk. Even 15 minutes of movement can help clear your mind.",
        "Practice gratitude. Write down three things you are thankful for today.",
        "Reach out to a friend or loved one. A quick chat can make a big difference."
    ]
    import random
    return random.choice(tips)

# --- Set up the LangChain Agent ---
tools = [get_weather, get_joke, get_wikipedia_summary, calculate_bmi, get_mental_wellness_tip]

llm = ChatGroq(model="qwen/qwen3-32b", groq_api_key=groq_api_key, temperature=0.7)

# The agent prompt is now much simpler. The LLM handles tool selection via
# Groq's tool-calling API, not by parsing a string.
system_prompt = """
You are Maitri AI, a helpful and empathetic assistant focused on physiological and physical well-being.
Answer the user's questions to the best of your ability.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        # This placeholder will be filled with the chat history
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        # This placeholder will be filled with intermediate agent steps
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Create the agent executor
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Memory Management with RunnableWithMessageHistory ---
store = {}
def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Wrap the agent executor with history management
agent_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Function to get a response from the agent
def get_agent_response(query, session_id):
    """
    Invokes the agent with a user query and a session ID.
    The session ID is crucial for maintaining chat history.
    """
    return agent_with_history.invoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}}
    )['output']