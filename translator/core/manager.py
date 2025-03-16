"""Translation manager module to coordinate translation components."""
import os
import torch
import gc
from pathlib import Path
from typing import Optional, Union
from translator.models.nllb import NLLBTranslationModel
from translator.models.m2m100 import M2M100TranslationModel
from translator.models.base import BaseTranslationModel
from translator.core.processor import FileProcessor
from translator.config.languages import SUPPORTED_LANGUAGES
from translator.config.models import TRANSLATION_MODELS

class TranslationManager:
    def __init__(self, device: Optional[str] = None, use_large_model: bool = False):
        """Initialize translation manager with optional device and model size specification."""
        # Handle symlinks warning
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        
        # Set PyTorch memory management settings
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        torch.backends.cudnn.benchmark = True
        
        # Enhanced GPU detection logging
        print("\n🔍 Checking GPU availability:")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU device: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   Available GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            print("\n🚀 Using GPU for translation")
            
            # Check if we have enough GPU memory for the selected model
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            required_memory = 12 if use_large_model else 6  # Large model needs more memory
            if total_memory < required_memory:
                print(f"\n⚠️  Warning: GPU memory may be insufficient for the selected model (needs {required_memory}GB)")
                print("   Will attempt to use model with reduced memory usage")
                print("   If translation fails, will automatically fall back to CPU")
        else:
            print("   ⚠️  CUDA not available. Using CPU (translations will be slower)")
            print("   To enable GPU support:")
            print("   1. Make sure you have NVIDIA GPU drivers installed")
            print("   2. Install PyTorch with CUDA support using:")
            print("      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
            
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.nllb_model = None
        self.m2m_model = None
        self.use_large_model = use_large_model
        
    def _cleanup_gpu_memory(self):
        """Clean up GPU memory."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

    def _fallback_to_cpu(self):
        """Fall back to CPU if GPU memory is insufficient."""
        print("\n⚠️  Falling back to CPU due to GPU memory constraints")
        print("   This will be slower but more reliable")
        self.device = "cpu"
        self._cleanup_gpu_memory()

    def _is_model_downloaded(self, model_name: str) -> bool:
        """Check if a model is already downloaded."""
        try:
            from huggingface_hub import scan_cache_dir
            
            cache_dir = os.path.expanduser('~/.cache/huggingface/hub')
            if not os.path.exists(cache_dir):
                return False
                
            cache = scan_cache_dir()
            for repo in cache.repos:
                if model_name in repo.repo_id:
                    return True
            return False
            
        except Exception:
            return False  # If we can't check, assume not downloaded

    def _check_disk_space(self, required_gb: float, model_name: str) -> bool:
        """Check if there's enough disk space for model download."""
        try:
            import shutil
            
            # Get the cache directory where models are downloaded
            cache_dir = os.path.expanduser('~/.cache/huggingface/hub')
            
            # Get available disk space in GB
            _, _, free = shutil.disk_usage(cache_dir)
            free_gb = free / (1024**3)  # Convert to GB
            
            if not self._is_model_downloaded(model_name):
                print(f"\n💾 Checking disk space for model download:")
                print(f"   Required space: {required_gb:.1f} GB")
                print(f"   Available space: {free_gb:.1f} GB")
                print(f"   Download location: {cache_dir}")
                
                if free_gb < required_gb:
                    print(f"\n⚠️  Warning: Not enough disk space to download model")
                    print(f"   Please free up at least {required_gb:.1f} GB")
                    print("\n💡 To free up space:")
                    print(f"   1. Go to: {cache_dir}")
                    print("   2. Delete any unused model folders")
                    return False
            else:
                print("\n💡 Model already downloaded, skipping download step")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Warning: Could not check disk space: {e}")
            return True  # Proceed anyway if we can't check

    def _load_nllb_model(self) -> Optional[BaseTranslationModel]:
        """Load the NLLB translation model."""
        try:
            # Determine which model to use
            model_name = TRANSLATION_MODELS['nllb']['model_large' if self.use_large_model else 'model']
            model_size = "3.3B" if self.use_large_model else "1.3B"
            
            print(f"\n📦 Using NLLB-200 {model_size} model for translation")
            
            # Check disk space (20GB for large model, 8GB for normal)
            required_space = 20.0 if self.use_large_model else 8.0
            if not self._check_disk_space(required_space, model_name):
                return None
                
            print("   Attempting to load model with GPU optimizations...")
            self.nllb_model = NLLBTranslationModel(device=self.device)
            self.nllb_model.load_model(model_name)
            return self.nllb_model
            
        except Exception as e:
            print(f"\n❌ Failed to load NLLB model: {str(e)}")
            return None

    def _get_translation_model(self, source_lang: str, target_lang: str) -> BaseTranslationModel:
        """Get the appropriate translation model for the language pair."""
        # Try NLLB first (best quality)
        if self.nllb_model is None:
            self.nllb_model = self._load_nllb_model()
            
        if self.nllb_model:
            return self.nllb_model
            
        # Fall back to M2M-100 if NLLB fails
        if self.m2m_model is None:
            print("\n📦 Falling back to M2M-100 model")
            self.m2m_model = M2M100TranslationModel(device=self.device)
            self.m2m_model.load_model(TRANSLATION_MODELS['m2m100']['model'])
            
        return self.m2m_model

    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text to target language."""
        if not text.strip():
            return ""
            
        model = self._get_translation_model("en", target_lang)
        return model.translate(text, target_lang)

    def translate_file(self, input_path: Path, target_lang: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """Translate a file to the target language."""
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Get translation model
        model = self._get_translation_model("en", target_lang)
        
        # Set up file processor
        processor = FileProcessor(model)
        
        # Determine output path if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_{target_lang}{input_path.suffix}"
            
        # Process file based on type
        try:
            if input_path.suffix.lower() == '.srt':
                processor.process_srt(input_path, target_lang, output_path)
            elif input_path.suffix.lower() == '.vtt':
                processor.process_vtt(input_path, target_lang, output_path)
            elif input_path.suffix.lower() == '.json':
                processor.process_json(input_path, target_lang, output_path)
            elif input_path.suffix.lower() == '.txt':
                processor.process_txt(input_path, target_lang, output_path)
            else:
                raise ValueError(f"Unsupported file type: {input_path.suffix}")
                
            return output_path
            
        except Exception as e:
            print(f"\n❌ Error translating file: {str(e)}")
            if "CUDA out of memory" in str(e):
                self._fallback_to_cpu()
                return self.translate_file(input_path, target_lang, output_path)
            raise 