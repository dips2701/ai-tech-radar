import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_update(title, content):
    prompt = f"""
You are an AI industry analyst.

News Title:
{title}

News Content:
{content}

Respond in this format:

SUMMARY:
1-2 sentence summary.

WHY_IT_MATTERS:
Why should an AI Engineer care?

ACTION:
What should the engineer learn, try, or explore?

IMPACT:
Rate from 1-10.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def parse_summary_output(output):
    sections = {"SUMMARY": "", "WHY_IT_MATTERS": "", "ACTION": "", "IMPACT": ""}
    current = None

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        upper = stripped.upper()
        for key in sections:
            if upper.startswith(key + ":"):
                current = key
                sections[key] = stripped.split(":", 1)[1].strip()
                break
        else:
            if current:
                if sections[current]:
                    sections[current] += "\n" + stripped
                else:
                    sections[current] = stripped

    return sections