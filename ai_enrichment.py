import ollama

def enrich_update(title, summary):
    """Generate AI insights for a news update.
    
    Returns a formatted string with SUMMARY, WHY_IT_MATTERS, ACTION, and IMPACT.
    """
    prompt = f"""You are an AI industry analyst.

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

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]


def parse_enrichment(raw_output):
    """Parse enrichment output into a dict."""
    sections = {"SUMMARY": "", "WHY_IT_MATTERS": "", "ACTION": "", "IMPACT": ""}
    current = None

    for line in raw_output.splitlines():
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
