# Autonomiczny Agent Badawczy AI

Autonomiczny agent AI zbudowany przy użyciu **LangGraph**, który samodzielnie przeszukuje internet, analizuje źródła i generuje ustrukturyzowane raporty.

## Funkcje
- **Architektura Grafowa**: Wykorzystanie grafów stanowych do cyklicznego procesu pracy (Researcher -> Writer -> Critic).
- **Autokorekta**: Agent-krytyk weryfikuje raport pod kątem faktów. Jeśli dane są niewystarczające, agent automatycznie zmienia strategię wyszukiwania i próbuje ponownie.
- **Web Search**: Integracja z **Tavily API** w celu uzyskania aktualnych danych w czasie rzeczywistym.
- **Interfejs UI**: Przejrzysty dashboard zbudowany w **Streamlit**.

## 🛠 Technologie
- **Python**
- **LangGraph** (Zarządzanie stanem i logiką)
- **LangChain** (Framework LLM)
- **OpenAI GPT-4o-mini** (Mózg systemu)
- **Tavily** (Wyszukiwarka dla AI)
- **Streamlit** (Interfejs użytkownika)

## Instalacja i uruchomienie

1. Sklonuj repozytorium:
```bash
git clone [https://github.com/TWOJA_NAZWA/ai-research-agent-langgraph.git](https://github.com/TWOJA_NAZWA/ai-research-agent-langgraph.git)