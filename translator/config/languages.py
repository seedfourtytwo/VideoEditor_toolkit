"""Language configuration and mappings."""

# Supported target languages
SUPPORTED_LANGUAGES = {
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'ru': 'Russian'
}

# MarianMT model names for specific language pairs
MARIAN_LANGUAGE_PAIRS = {
    'en-fr': 'Helsinki-NLP/opus-mt-en-fr',  # English to French
    'en-es': 'Helsinki-NLP/opus-mt-en-es',  # English to Spanish
    'en-de': 'Helsinki-NLP/opus-mt-en-de',  # English to German
    'en-it': 'Helsinki-NLP/opus-mt-en-it',  # English to Italian
    'en-pt': 'Helsinki-NLP/opus-mt-en-pt',  # English to Portuguese
    'en-nl': 'Helsinki-NLP/opus-mt-en-nl',  # English to Dutch
    'en-pl': 'Helsinki-NLP/opus-mt-en-pl',  # English to Polish
    'en-ru': 'Helsinki-NLP/opus-mt-en-ru',  # English to Russian
}

# Language model mapping for spaCy
SPACY_MODELS = {
    'fr': 'fr_core_news_sm',  # French
    'es': 'es_core_news_sm',  # Spanish
    'de': 'de_core_news_sm',  # German
    'it': 'it_core_news_sm',  # Italian
    'pt': 'pt_core_news_sm',  # Portuguese
    'nl': 'nl_core_news_sm',  # Dutch
    'pl': 'pl_core_news_sm',  # Polish
    'ru': 'ru_core_news_sm',  # Russian
}

# File format settings
SUPPORTED_FORMATS = {'.srt', '.vtt', '.json', '.txt'}

# Translation settings
TRANSLATION_SETTINGS = {
    'max_chunk_length': 450,  # Maximum tokens per chunk
    'text_chunk_size': 1000,  # Characters per chunk for text files
    'context_chars': 100,     # Characters of context to show
} 