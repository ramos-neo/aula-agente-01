from google.adk import Agent

root_agent = Agent(
    name="meu_agente_2",
    instruction=("Você é um especialista em python e agentes de IA"),
    model="gemini-3.5-flash-lite"
    )
