"""
Factory for creating content filter instances.
"""
from .filter import AdvancedContentFilter


def create_advanced_content_filter() -> AdvancedContentFilter:
    """
    Factory function to create and return a new instance of the 
    AdvancedContentFilter.
    """
    return AdvancedContentFilter()
