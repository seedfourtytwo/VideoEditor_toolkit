"""Translation settings and configurations."""

TRANSLATION_SETTINGS = {
    'max_chunk_length': 512,  # Maximum number of tokens per chunk
    'text_chunk_size': 1000,  # Characters per chunk for text files
    'batch_size': 8,         # Number of segments to translate at once
    'max_length': 200,       # Maximum length for generated translations
}

# Default paths
DEFAULT_PATHS = {
    'corrections': 'translation_corrections.json',
    'cache': '.translation_cache'
} 