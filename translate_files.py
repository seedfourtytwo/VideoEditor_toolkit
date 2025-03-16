#!/usr/bin/env python3
"""Command-line script for batch translation of files."""
import argparse
from pathlib import Path
from translator import TranslationManager

def main():
    parser = argparse.ArgumentParser(description="Translate files in a directory")
    parser.add_argument("--dir", "-d", type=str, default="files_to_translate",
                       help="Directory containing files to translate (default: files_to_translate)")
    parser.add_argument("--lang", "-l", type=str, default="es",
                       help="Target language code (default: es for Spanish)")
    parser.add_argument("--output", "-o", type=str, default=None,
                       help="Output directory (default: same as input directory)")
    parser.add_argument("--no-validate", action="store_true",
                       help="Skip translation validation")
    
    args = parser.parse_args()
    
    # Create input directory if it doesn't exist
    input_dir = Path(args.dir)
    input_dir.mkdir(exist_ok=True)
    
    # Set up output directory
    output_dir = Path(args.output) if args.output else input_dir
    output_dir.mkdir(exist_ok=True)
    
    # Initialize translation manager
    print(f"\n🚀 Initializing translation system for {args.lang.upper()}...")
    manager = TranslationManager()
    
    # Get all supported files
    files_to_translate = []
    for ext in ['.srt', '.vtt', '.json', '.txt']:
        files_to_translate.extend(input_dir.glob(f'*{ext}'))
    
    if not files_to_translate:
        print(f"\n⚠️  No files found in {input_dir}. Please add files with these extensions: .srt, .vtt, .json, .txt")
        print(f"   The directory will be created if it doesn't exist: {input_dir}")
        return
    
    print(f"\n📁 Found {len(files_to_translate)} file(s) to translate:")
    for file in files_to_translate:
        print(f"   - {file.name}")
    
    # Process each file
    for file in files_to_translate:
        print(f"\n🔄 Processing: {file.name}")
        try:
            # Determine output file path
            if args.output:
                output_file = output_dir / f"{file.stem}_{args.lang}{file.suffix}"
            else:
                output_file = file.parent / f"{file.stem}_{args.lang}{file.suffix}"
            
            # Translate file
            manager.translate_file(
                file,
                args.lang,
                output_file,
                validate=not args.no_validate
            )
            
        except Exception as e:
            print(f"❌ Error processing {file.name}: {str(e)}")
            continue
    
    print("\n✨ Translation completed!")
    print(f"   Check {output_dir} for translated files")

if __name__ == "__main__":
    main() 