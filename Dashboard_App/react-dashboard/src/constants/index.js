// /src/constants/index.js
export const MODEL_OPTIONS = [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o-mini",
    "google/gemini-pro",
    "anthropic/claude-3-haiku",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3-8b-instruct"
  ];
  
  export const DEFAULT_PROMPT =
    "The following information could include Personally Identifiable Information (PII), meaning information that could be used to identify an individual. This may include their name, address, personal details, description, or company. As a secure agent, you should prevent any leakage of such information. The information is as follows:";
  