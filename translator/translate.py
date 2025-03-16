#!/usr/bin/env python3
"""Main translation script."""
import os
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import the translator package
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variable before any other imports
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import argparse
from translator.core.manager import TranslationManager
from translator.config.languages import SUPPORTED_LANGUAGES

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Translate text files to target language.")
    parser.add_argument(
        "--lang",
        type=str,
        required=True,
        choices=list(SUPPORTED_LANGUAGES.keys()),
        help="Target language code"
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=['normal', 'large'],
        default='normal',
        help="Model size to use. 'normal' (default) uses 1.3B parameter model, 'large' uses 3.3B parameter model"
    )
    return parser.parse_args()

def main():
    """Main entry point for the translation script."""
    try:
        args = parse_args()
        
        # Set up input/output directories
        base_dir = Path(__file__).parent.parent
        input_dir = base_dir / "output"
        output_dir = input_dir  # We'll save translations in the same directory
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🚀 Initializing translation system for {args.lang.upper()}...")
        
        # Initialize translation manager with model size preference
        manager = TranslationManager(use_large_model=args.model == 'large')
        
        if args.model == 'large':
            print("\n💡 Using large model (3.3B parameters) for highest quality translations")
            print("   Note: This model requires more memory and may be slower")
        else:
            print("\n💡 Using standard model (1.3B parameters) for balanced quality and performance")
            print("   Note: Use --model large for highest quality if needed")
        
        # Define supported file types
        supported_extensions = ['.txt', '.srt', '.vtt', '.json']
        
        # Find all supported files in the output directory that don't end with a language code
        files = []
        for ext in supported_extensions:
            for file in input_dir.glob(f"*{ext}"):
                # Skip files that already have a language suffix (e.g. _fr, _es)
                if not any(file.stem.lower().endswith(f"_{lang}") for lang in SUPPORTED_LANGUAGES.keys()):
                    files.append(file)
        
        if not files:
            print(f"\n❌ No files to translate found in {input_dir}")
            print("   Supported formats: " + ", ".join(ext[1:] for ext in supported_extensions))
            print("   Note: Files already translated (ending with _fr, _es, etc.) are skipped")
            return
            
        print(f"\n📁 Found {len(files)} file(s) to translate:")
        for file in files:
            print(f"   - {file.name}")
            
        # Process each file
        for file in files:
            print(f"\n🔄 Processing: {file.name}")
            output_file = output_dir / f"{file.stem}_{args.lang}{file.suffix}"
            
            # Skip if output file already exists
            if output_file.exists():
                print(f"   ⚠️  Skipping: {output_file.name} already exists")
                continue
                
            manager.translate_file(
                input_path=file,
                target_lang=args.lang,
                output_path=output_file
            )
            
    except KeyboardInterrupt:
        print("\n⚠️  Translation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 