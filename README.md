# Resume Strength Matrix

A lightweight Flask web app that evaluates resumes with the OpenAI API and visualizes the candidate's strengths, weaknesses, and recommendations in a matrix layout inspired by hiring dashboards.

## Features

- Paste a resume (and optional job description) to get instant insights.
- Uses OpenAI's GPT models to extract skills, highlight strengths & weaknesses, and assign tag scores.
- Presents results in an interactive matrix with color-coded status tags.
- Simple Flask backend with a single `/api/parse_resume` endpoint.

## Requirements

- Python 3.10+
- An OpenAI API key with access to GPT-4o class models.

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key**

   ```bash
   export OPENAI_API_KEY="sk-your-key"
   ```

   You can optionally create a `.env` file and load it with a tool such as `python-dotenv` if desired.

3. **Run the development server**

   ```bash
   flask --app app.py run --debug
   ```

   The application will be available at <http://127.0.0.1:5000>.

## How it works

- The frontend collects resume text and an optional job description, sending both to the Flask API.
- The backend forwards the text to the OpenAI `gpt-4o-mini` model with a structured prompt requesting JSON.
- The response is parsed and rendered as a matrix showing skill categories, strengths, weaknesses, scores, and hiring recommendations.

## Notes

- The OpenAI API call happens server-side to avoid exposing your API key in the browser.
- If the OpenAI package is missing or the API key is not configured, the API returns a helpful error message.
- Styling is handled with vanilla CSS and requires no build step.
