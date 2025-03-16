"""Test script for the translation system."""
from translator import TranslationManager

def main():
    # Initialize the translation manager
    print("🚀 Initializing translation manager...")
    manager = TranslationManager()
    
    # Test text translation
    text = "Hello, this is a test translation."
    target_lang = "es"  # Spanish
    
    print(f"\n📝 Translating text to {target_lang.upper()}:")
    print(f"Original: {text}")
    
    try:
        translated = manager.translate_text(text, target_lang)
        print(f"Translated: {translated}")
        print("\n✅ Translation successful!")
    except Exception as e:
        print(f"\n❌ Translation failed: {str(e)}")

if __name__ == "__main__":
    main() 