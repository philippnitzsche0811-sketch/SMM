"""
Utility-Funktionen
"""
from typing import List


def build_tiktok_caption(title: str, description: str, tags: List[str]) -> str:
    """
    Erstellt eine TikTok-Caption aus Titel, Beschreibung und Tags
    
    Args:
        title: Video-Titel
        description: Video-Beschreibung
        tags: Liste von Tags
    
    Returns:
        str: Formatierte Caption
    """
    caption_parts = []
    
    # Titel hinzufügen
    if title:
        caption_parts.append(title)
    
    # Beschreibung hinzufügen
    if description:
        caption_parts.append(description)
    
    # Tags als Hashtags hinzufügen
    if tags:
        hashtags = " ".join([f"#{tag.strip().replace(' ', '')}" for tag in tags if tag.strip()])
        if hashtags:
            caption_parts.append(hashtags)
    
    return "\n\n".join(caption_parts)


def sanitize_filename(filename: str) -> str:
    """
    Bereinigt einen Dateinamen von ungültigen Zeichen
    
    Args:
        filename: Original-Dateiname
    
    Returns:
        str: Bereinigter Dateiname
    """
    # Ungültige Zeichen entfernen
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Formatiert Dateigröße in lesbare Form
    
    Args:
        size_bytes: Größe in Bytes
    
    Returns:
        str: Formatierte Größe (z.B. "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
