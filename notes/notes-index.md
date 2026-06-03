# Notes Index

## cowork-notes.md
Documents Xander's hands-on learning with Claude's Cowork mode, capturing experiments with the Figma design plugin (specifically a Formula One website mockup) and insights about tool selection. Contains a decision matrix for when to use Cowork versus Chat, emphasizing that Cowork is best for batch file operations and persistent outputs, while Chat suits quick questions and explanations. Includes a newly added personal ground rules section for managing computer use and file access.

## prompting-notes.md
Records an exercise comparing two prompts to the same task, demonstrating how vague instructions produce generic, unhelpful responses while detailed prompts with specific context and constraints yield comprehensive, actionable outputs. Uses the Open-Meteo API as the example task, illustrating a core lesson: prompt quality directly impacts answer quality and usefulness.

## tool-guide.md
Claude Chat is best for quick explanations and simple tasks, while Cowork gives Claude access to your files and computer to make autonomous changes and build things directly in your workspace. The key difference is that Chat advises you, but Cowork actually does the work for you while keeping everything saved where it belongs.

## weather.py
A production-quality Python script that fetches and displays current weather data for multiple cities using the wttr.in API. Demonstrates best practices including robust input validation, string sanitization to prevent URL injection, comprehensive error handling for timeout and HTTP errors, and graceful degradation with informative error messages for each failure mode.
