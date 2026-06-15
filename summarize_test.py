from summarizer import summarize_update

if __name__ == "__main__":
    result = summarize_update(
        "OpenAI releases new model",
        "OpenAI announced..."
    )

    print(result)
