# Research: Google Antigravity Authentication & API Keys

Research into whether an API key can be obtained programmatically through the Google Antigravity (AGY) SDK or if manual setup is required.

## Key Findings

### 1. Programmatic SDK Auth vs. CLI Auth
The Antigravity ecosystem handles authentication differently depending on whether you are using the CLI tool or the SDK library:

*   **Antigravity CLI (`agy`)**: Natively supports **system-level OAuth**. Running the TUI prompts the user to log in with their Google account via browser OAuth, eliminating the need for manual API key setup for CLI sessions.
*   **Antigravity SDK (`google-antigravity`)**: Does **not** natively support OAuth automatic retrieval. Programmatic integrations of the SDK rely strictly on manual **Gemini API Keys** (configured via the `GEMINI_API_KEY` environment variable or passed in code using `LocalAgentConfig(api_key="...")`).

### 2. Recommended Setup Method for the SDK
Since programmatic agents using the SDK cannot automatically fetch credentials, the standard workflow is:
1.  Generate a free Gemini API key manually from the **[Google AI Studio API Keys Panel](https://aistudio.google.com/app/api-keys)**.
2.  Store this key in a local `.env` file in the project directory:
    ```env
    GEMINI_API_KEY=AIzaSy...
    ```
3.  Load it in your Python runtime using `python-dotenv`:
    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

---

## Sources
*   [Google AI Studio Documentation](https://ai.google.dev/gemini-api/docs/models/gemini)
*   [Google Antigravity SDK Configuration references/agent_configuration.md](file:///Users/znglyvlad/.gemini/config/plugins/google-antigravity-sdk/skills/google-antigravity-sdk/references/agent_configuration.md)
*   [Google Antigravity CLI documentation and online help resources]
