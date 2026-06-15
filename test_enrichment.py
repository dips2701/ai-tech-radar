from ai_enrichment import enrich_update, parse_enrichment

if __name__ == "__main__":
    title = "OpenAI launches GPT-Rosalind"
    summary = "New model focused on biology and chemistry."
    
    print("=" * 60)
    print("RAW OUTPUT:")
    print("=" * 60)
    
    raw = enrich_update(title, summary)
    print(raw)
    
    print("\n" + "=" * 60)
    print("PARSED OUTPUT:")
    print("=" * 60)
    
    parsed = parse_enrichment(raw)
    for key, value in parsed.items():
        print(f"\n{key}:")
        print(value)
