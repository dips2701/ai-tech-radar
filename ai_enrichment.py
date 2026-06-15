import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def enrich_update(title, summary):
    prompt = f"""
You are an AI industry analyst.

Title:
{title}

Content:
{summary}

Return ONLY in this format:

SUMMARY:
...

WHY_IT_MATTERS:
...

ACTION:
...

IMPACT:
1-10
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def parse_enrichment(text):
    data = {
        "SUMMARY": "",
        "WHY_IT_MATTERS": "",
        "ACTION": "",   
        "IMPACT": ""
    }

    current = None

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("SUMMARY:"):
            current = "SUMMARY"
            data[current] = line.replace("SUMMARY:", "").strip()

        elif line.startswith("WHY_IT_MATTERS:"):
            current = "WHY_IT_MATTERS"
            data[current] = line.replace("WHY_IT_MATTERS:", "").strip()

        elif line.startswith("ACTION:"):
            current = "ACTION"
            data[current] = line.replace("ACTION:", "").strip()

        elif line.startswith("IMPACT:"):
            current = "IMPACT"
            impact_text = line.replace("IMPACT:", "").strip()
            data[current] = impact_text.split()[0] if impact_text else ""

        elif current and line:
            data[current] += " " + line

    return data