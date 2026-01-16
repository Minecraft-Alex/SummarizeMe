from transformers import pipeline

def summarize_text(text, max_length=200, min_length=60):
    """
    Summarizes long text into a more compact form using a HuggingFace transformer model.
    Default model: facebook/bart-large-cnn
    """
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", tokenizer="facebook/bart-large-cnn")
    
    # Truncate or chunk if text is too long
    if len(text) > 1024:
        text = text[:1024]

    # Generate summary
    summary = summarizer(
        text,
        max_length=max_length,
        min_length=min_length,
        do_sample=False
    )
    
    return summary[0]["summary_text"]
