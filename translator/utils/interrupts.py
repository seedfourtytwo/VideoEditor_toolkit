"""Interrupt handling utilities."""
import signal
import sys

# Global flag for interrupt handling
interrupted = False

def signal_handler(sig, frame):
    """Handle CTRL+C gracefully"""
    global interrupted
    interrupted = True
    print("\n\nInterrupted by user. Cleaning up...")
    print("Cleanup complete. Exiting...")
    sys.exit(0)

def progress_callback(current, total):
    """Custom progress callback that checks for interrupts."""
    global interrupted
    if interrupted:
        raise KeyboardInterrupt("Model loading interrupted by user")
    return True

# Set up signal handler
signal.signal(signal.SIGINT, signal_handler) 