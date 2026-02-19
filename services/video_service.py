"""
Video Service — Generates safe YouTube search URLs for topics
Deterministic, no API quota usage, production-safe
"""

from urllib.parse import quote


async def get_video_link(topic_name: str) -> str:
    """
    Generate a YouTube search URL for a given topic.
    
    Args:
        topic_name: Name of the topic (e.g., "Arrays", "Machine Learning Basics")
    
    Returns:
        Safe YouTube search URL
    
    Example:
        >>> await get_video_link("Arrays and Lists")
        "https://www.youtube.com/results?search_query=Arrays+and+Lists+tutorial"
    """
    
    if not topic_name or not isinstance(topic_name, str) or not topic_name.strip():
        return "#"
    
    # Clean topic name
    clean_topic = topic_name.strip()
    
    # Build search query
    search_query = f"{clean_topic} tutorial"
    
    # Encode for URL
    encoded_query = quote(search_query)
    
    # Return YouTube search URL
    return f"https://www.youtube.com/results?search_query={encoded_query}"
