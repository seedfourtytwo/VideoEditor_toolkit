"""Translation validator module using high-quality translation models."""
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from translator.config.models import TRANSLATION_MODELS

class TranslationValidator:
    def __init__(self):
        """Initialize the translation validator."""
        self.model = None
        self.tokenizer = None
        self.src_lang = "eng_Latn"
        self.tgt_lang = None

    def validate_translation(self, translated_text: str, source_text: str, target_lang: str) -> list:
        """Validate a translation using back-translation comparison."""
        issues = []
        
        # Initialize model if needed
        if self.model is None:
            print("\n🔍 Initializing validation...")
            self.tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-3.3B")
            self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-3.3B")
            self.tgt_lang = TRANSLATION_MODELS['nllb']['languages'][target_lang]
        
        # Split texts into sentences for better comparison
        source_sentences = [s.strip() for s in source_text.split('.') if s.strip()]
        translated_sentences = [s.strip() for s in translated_text.split('.') if s.strip()]
        
        # Check overall length ratio
        source_len = len(source_text.split())
        translated_len = len(translated_text.split())
        ratio = translated_len / source_len
        if ratio < 0.5 or ratio > 2.0:
            issues.append(f"Unusual translation length ratio: {ratio:.2f}")
        
        # Check sentence count ratio
        sent_ratio = len(translated_sentences) / len(source_sentences)
        if sent_ratio < 0.7 or sent_ratio > 1.3:
            issues.append(f"Unusual sentence count ratio: {sent_ratio:.2f}")
        
        # Validate each sentence through back-translation
        print("   Performing back-translation check...")
        for i, (trans_sent, src_sent) in enumerate(zip(translated_sentences, source_sentences), 1):
            if not trans_sent or not src_sent:
                continue
                
            # Back-translate to English
            inputs = self.tokenizer(trans_sent, return_tensors="pt", padding=True, truncation=True, max_length=512)
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(self.src_lang),
                max_length=512,
                num_beams=4,
                length_penalty=1.0,
                do_sample=False
            )
            back_translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Compare back-translation with source
            # Calculate similarity using word overlap
            src_words = set(src_sent.lower().split())
            back_words = set(back_translation.lower().split())
            shared_words = src_words & back_words
            similarity = len(shared_words) / len(src_words | back_words) if src_words or back_words else 0
            
            if similarity < 0.5:  # Threshold for flagging potential issues
                issues.append(f"Low similarity in sentence {i}: {similarity:.2f}")
                issues.append(f"   Original: {src_sent}")
                issues.append(f"   Back-translated: {back_translation}")
        
        # Check for common French patterns if target is French
        if target_lang == 'fr':
            patterns = [
                "n'", "l'", "d'", "qu'",  # Common elisions
                "ne", "pas", "plus",      # Negation
                "le", "la", "les",        # Articles
                "un", "une", "des"        # Indefinite articles
            ]
            
            missing_patterns = []
            for pattern in patterns:
                if pattern not in translated_text.lower():
                    missing_patterns.append(pattern)
                    
            if missing_patterns:
                issues.append(f"Missing common French patterns: {', '.join(missing_patterns)}")
        
        return issues 