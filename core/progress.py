"""Progress indicator utilities"""
from typing import Optional
import sys


class ProgressBar:
    """Simple progress bar for long operations"""
    
    def __init__(self, total: int, description: str = "Progress"):
        """Initialize progress bar
        
        Args:
            total: Total number of items to process
            description: Description text to display
        """
        self.total = total
        self.current = 0
        self.description = description
        self.bar_length = 50
    
    def update(self, increment: int = 1):
        """Update progress
        
        Args:
            increment: Number of items completed
        """
        self.current = min(self.current + increment, self.total)
        self._display()
    
    def _display(self):
        """Display progress bar"""
        if self.total == 0:
            percent = 100.0
        else:
            percent = (self.current / self.total) * 100
        filled = int(self.bar_length * self.current / self.total)
        bar = '=' * filled + '-' * (self.bar_length - filled)
        sys.stdout.write(f'\r{self.description}: [{bar}] {percent:.1f}% ({self.current}/{self.total})')
        sys.stdout.flush()
    
    def finish(self):
        """Finish progress bar"""
        self.current = self.total
        self._display()
        print()  # New line after completion

