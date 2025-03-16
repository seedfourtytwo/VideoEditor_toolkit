"""File processor module for handling different file formats."""
import json
from pathlib import Path
from typing import Optional, Union
import pysrt
import webvtt
from tqdm import tqdm
from ..config.languages import TRANSLATION_SETTINGS
from ..models.base import BaseTranslationModel
import time

class FileProcessor:
    def __init__(self, model: BaseTranslationModel):
        self.model = model

    def process_srt(self, input_file: Path, target_lang: str, output_file: Path) -> None:
        """Process and translate SRT subtitle file."""
        subs = pysrt.open(str(input_file))
        total_subs = len(subs)
        
        print(f"\n🎬 Found {total_subs} subtitles in {input_file.name}")
        
        # Ensure model is ready before starting translation
        # This will trigger any pending downloads
        self.model.prepare_for_translation(target_lang)
        
        print(f"\n📝 Starting translation to {target_lang.upper()}...")
        
        # Start translation with progress bar
        with tqdm(total=total_subs, desc=f"Translating", unit="subs",
                 bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            
            # Process in smaller batches for visible progress
            batch_size = 5
            for i in range(0, total_subs, batch_size):
                batch = [sub.text for sub in subs[i:i + batch_size]]
                translated_batch = self.model.translate_batch(batch, target_lang)
                
                # Update subtitles with translations
                for j, translated_text in enumerate(translated_batch):
                    if i + j < total_subs:  # Safety check
                        subs[i + j].text = translated_text
                
                pbar.update(len(batch))
                pbar.refresh()  # Force refresh the display
        
        subs.save(str(output_file), encoding='utf-8')
        print(f"\n✨ Translation completed! Output saved to: {output_file}")
        print("\n💡 Quality Note: Using NLLB-200 model which provides high-quality translations")
        print("   Validation step skipped to optimize performance")

    def process_vtt(self, input_file: Path, target_lang: str, output_file: Path) -> None:
        """Process and translate WebVTT subtitle file."""
        vtt = webvtt.read(str(input_file))
        total_captions = len(vtt.captions)
        translated_captions = []
        
        print(f"\n🎬 Translating {total_captions} captions from {input_file.name}")
        
        # Process in smaller batches
        batch_size = 5
        with tqdm(total=total_captions, desc=f"📝 Translating to {target_lang.upper()}", unit="captions",
                 bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            
            for i in range(0, total_captions, batch_size):
                batch = [caption.text for caption in vtt.captions[i:i + batch_size]]
                translated_batch = self.model.translate_batch(batch, target_lang)
                
                for j, translated_text in enumerate(translated_batch):
                    if i + j < total_captions:  # Safety check
                        caption = vtt.captions[i + j]
                        caption.text = translated_text
                        translated_captions.append(caption)
                
                pbar.update(len(batch))
                pbar.refresh()  # Force refresh the display
        
        # Create new VTT file with translations
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('WEBVTT\n\n')
            for caption in translated_captions:
                f.write(f"{caption.start} --> {caption.end}\n")
                f.write(f"{caption.text}\n\n")
        
        print(f"\n✨ Translation completed! Output saved to: {output_file}")
        print("\n💡 Quality Note: Using NLLB-200 model which provides high-quality translations")
        print("   Validation step skipped to optimize performance")

    def process_json(self, input_file: Path, target_lang: str, output_file: Path) -> None:
        """Process and translate JSON file with timestamps."""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # Handle array of segments
            segments = [s for s in data if 'text' in s]
            total_segments = len(segments)
            
            print(f"\n🎬 Found {total_segments} segments in {input_file.name}")
            
            # Ensure model is ready before starting translation
            self.model.prepare_for_translation(target_lang)
            
            print(f"\n📝 Starting translation to {target_lang.upper()}...")
            
            with tqdm(total=total_segments, desc=f"Translating", unit="segments",
                     bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
                
                # Process in smaller batches
                batch_size = 5
                for i in range(0, total_segments, batch_size):
                    batch_segments = segments[i:i + batch_size]
                    texts = [s['text'] for s in batch_segments]
                    translated_batch = self.model.translate_batch(texts, target_lang)
                    
                    # Update segments with translations
                    for segment, translated_text in zip(batch_segments, translated_batch):
                        segment['text'] = translated_text
                        
                        # Find and update the corresponding segment in the original data
                        for d in data:
                            if 'text' in d and d['text'] == segment.get('text', ''):
                                d['text'] = translated_text
                                break
                    
                    pbar.update(len(batch_segments))
                    pbar.refresh()
                    
        elif isinstance(data, dict):
            # Handle dictionary format
            print(f"\n🎬 Processing JSON dictionary from {input_file.name}")
            
            # First, count total number of text fields
            def count_text_fields(d):
                count = 0
                if isinstance(d, dict):
                    for key, value in d.items():
                        if key == 'text' and isinstance(value, str):
                            count += 1
                        elif isinstance(value, (dict, list)):
                            count += count_text_fields(value)
                elif isinstance(d, list):
                    for item in d:
                        count += count_text_fields(item)
                return count
            
            total_fields = count_text_fields(data)
            print(f"   Found {total_fields} text fields to translate")
            
            # Ensure model is ready before starting translation
            self.model.prepare_for_translation(target_lang)
            
            print(f"\n📝 Starting translation to {target_lang.upper()}...")
            
            # Create progress bar
            pbar = tqdm(total=total_fields, desc="Translating", unit="fields",
                       bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            
            def translate_dict(d):
                """Recursively translate text fields in dictionary."""
                if isinstance(d, dict):
                    for key, value in d.items():
                        if key == 'text' and isinstance(value, str):
                            d[key] = self.model.translate(value, target_lang)
                            pbar.update(1)
                            pbar.refresh()
                        elif isinstance(value, (dict, list)):
                            translate_dict(value)
                elif isinstance(d, list):
                    for item in d:
                        translate_dict(item)
            
            try:
                translate_dict(data)
            finally:
                pbar.close()
        
        # Save translated data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✨ Translation completed! Output saved to: {output_file}")
        print("\n💡 Quality Note: Using NLLB-200 model which provides high-quality translations")
        print("   Validation step skipped to optimize performance")

    def process_txt(self, input_source: Union[str, Path], target_lang: str, output_file: Optional[Path] = None) -> Optional[str]:
        """Process text for translation."""
        try:
            # Determine if input is a file path or text string
            if isinstance(input_source, Path):
                with open(input_source, 'r', encoding='utf-8') as f:
                    text = f.read()
                print(f"\n🎬 Translating text file {input_source.name}")
            else:
                text = input_source
                print("\n🎬 Translating text")
            
            # Split text into manageable chunks
            chunks = self._split_into_chunks(text)
            total_chunks = len(chunks)
            
            print(f"   Original text length: {len(text)} characters")
            print(f"   Split into {total_chunks} chunks for translation")
            
            translated_chunks = []
            with tqdm(total=total_chunks, desc=f"📝 Translating to {target_lang.upper()}",
                     bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} chunks [{elapsed}<{remaining}]') as pbar:
                
                # Process in smaller batches
                batch_size = 3  # Smaller batch size for text chunks as they're larger
                for i in range(0, total_chunks, batch_size):
                    batch = chunks[i:i + batch_size]
                    try:
                        translated_batch = self.model.translate_batch(batch, target_lang)
                        translated_chunks.extend(translated_batch)
                        pbar.update(len(batch))
                        pbar.refresh()  # Force refresh the display
                        
                    except Exception as batch_error:
                        print(f"\n⚠️  Error translating batch {i//batch_size + 1}: {str(batch_error)}")
                        print("   Retrying chunks individually...")
                        
                        # Fall back to translating chunks one by one
                        for chunk in batch:
                            try:
                                translated_chunk = self.model.translate(chunk, target_lang)
                                translated_chunks.append(translated_chunk)
                                pbar.update(1)
                                pbar.refresh()
                            except Exception as chunk_error:
                                print(f"❌ Failed to translate chunk: {str(chunk_error)}")
                                translated_chunks.append(chunk)  # Keep original if translation fails
                                pbar.update(1)
                                pbar.refresh()
            
            # Join all translated chunks
            translated_text = ' '.join(translated_chunks)
            
            # Save to file if output path provided
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(translated_text)
                print(f"\n✨ Translation completed! Output saved to: {output_file}")
                print("\n💡 Quality Note: Using NLLB-200 model which provides high-quality translations")
                print("   Validation step skipped to optimize performance")
                return None
            
            return translated_text
            
        except Exception as e:
            print(f"\n❌ Error processing text: {str(e)}")
            raise

    def _split_into_chunks(self, text: str, max_length: int = 500) -> list:
        """Split text string into chunks of specified maximum length."""
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Find the end of the current chunk
            chunk_end = min(current_pos + max_length, len(text))
            
            # Try to find a sentence boundary
            if chunk_end < len(text):
                # Look for the last sentence boundary within this chunk
                for marker in ['. ', '! ', '? ', '\n']:
                    last_boundary = text.rfind(marker, current_pos, chunk_end + 50)
                    if last_boundary != -1:
                        chunk_end = last_boundary + 1
                        break
            
            # Extract the chunk
            chunk = text[current_pos:chunk_end].strip()
            if chunk:
                chunks.append(chunk)
            current_pos = chunk_end
        
        return chunks 