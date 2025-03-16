"""Configuration for translation models."""

TRANSLATION_MODELS = {
    'nllb': {
        'name': 'NLLB-200 (Meta AI)',
        'description': 'High-quality translation model with good performance balance',
        'size': '~8GB (supports 200 languages)',
        'model': 'facebook/nllb-200-1.3B',  # Default model
        'model_large': 'facebook/nllb-200-3.3B',  # Optional larger model
        'languages': {
            'fr': 'fra_Latn',  # French
            'es': 'spa_Latn',  # Spanish
            'de': 'deu_Latn',  # German
            'it': 'ita_Latn',  # Italian
            'pt': 'por_Latn',  # Portuguese
            'nl': 'nld_Latn',  # Dutch
            'pl': 'pol_Latn',  # Polish
            'ru': 'rus_Cyrl',  # Russian
        }
    },
    'm2m100': {
        'name': 'M2M100 (Meta AI)',
        'description': 'High quality fallback model',
        'size': '~5GB (supports 100 languages)',
        'model': 'facebook/m2m100_1.2B',
        'languages': {
            'fr': 'fr',  # French
            'es': 'es',  # Spanish
            'de': 'de',  # German
            'it': 'it',  # Italian
            'pt': 'pt',  # Portuguese
            'nl': 'nl',  # Dutch
            'pl': 'pl',  # Polish
            'ru': 'ru',  # Russian
        }
    },
    'marian': {
        'name': 'MarianMT (Helsinki-NLP)',
        'description': 'Fast and efficient for specific language pairs (use only if memory constrained)',
        'size': '~300MB per language',
        'languages': {
            'fr': 'Helsinki-NLP/opus-mt-en-fr',  # English to French
            'es': 'Helsinki-NLP/opus-mt-en-es',  # English to Spanish
            'de': 'Helsinki-NLP/opus-mt-en-de',  # English to German
            'it': 'Helsinki-NLP/opus-mt-en-it',  # English to Italian
            'pt': 'Helsinki-NLP/opus-mt-en-pt',  # English to Portuguese
            'nl': 'Helsinki-NLP/opus-mt-en-nl',  # English to Dutch
            'pl': 'Helsinki-NLP/opus-mt-en-pl',  # English to Polish
            'ru': 'Helsinki-NLP/opus-mt-en-ru',  # English to Russian
        }
    }
} 