# ===================================================================
# 🧸 AI Teddy Bear - DDD File Classification Strategies
# Enterprise DDD File Classification Strategy Implementations
# Architect: Your Name
# Date: January 2025
# ===================================================================

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List


class FileClassificationStrategy(ABC):
    """
    Abstract base class for a file classification strategy.
    It defines a common interface for different classification rules
    based on Domain-Driven Design (DDD) principles.
    """

    def __init__(self, keywords: List[str], target_layer: str):
        self.keywords = keywords
        self.target_layer = target_layer

    @abstractmethod
    def classify(self, file_path: Path, file_content: str) -> Optional[str]:
        """
        Classifies the file based on its path and content.

        Args:
            file_path: The Path object of the file.
            file_content: The lowercased file name for simple matching.

        Returns:
            The target DDD layer string if it matches, otherwise None.
        """
        pass


class NameBasedClassificationStrategy(FileClassificationStrategy):
    """
    A concrete strategy that classifies files based on keywords in their names.
    """

    def classify(self, file_path: Path, file_content: str) -> Optional[str]:
        if any(keyword in file_content for keyword in self.keywords):
            return self.target_layer
        return None


class DomainServiceClassificationStrategy(FileClassificationStrategy):
    """
    A concrete strategy to classify domain services, which requires checking
    both the name and the path.
    """

    def classify(self, file_path: Path, file_content: str) -> Optional[str]:
        if "service" in file_content and "domain" in str(file_path):
            return self.target_layer
        return None


class ApplicationLayerClassificationStrategy(FileClassificationStrategy):
    """
    A more complex strategy for the application layer that directs files
    to different sub-directories (commands, queries, handlers).
    """

    def classify(self, file_path: Path, file_content: str) -> Optional[str]:
        if any(keyword in file_content for keyword in self.keywords):
            if "command" in file_content:
                return "src/application/commands"
            elif "query" in file_content:
                return "src/application/queries"
            else:
                return "src/application/handlers"
        return None
