"""
File Service für sicheres File-Handling
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import uuid

logger = logging.getLogger(__name__)


class FileService:
    """Verwaltet temporäre Dateien sicher"""
    
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_temp_file(
        self, 
        upload_file: UploadFile, 
        custom_name: Optional[str] = None
    ) -> str:
        """
        Speichert eine hochgeladene Datei temporär
        
        Args:
            upload_file: FastAPI UploadFile Objekt
            custom_name: Optional eigener Dateiname
        
        Returns:
            str: Pfad zur gespeicherten Datei
        """
        try:
            # Eindeutigen Dateinamen generieren
            if custom_name:
                filename = custom_name
            else:
                # UUID + Originaldatei-Extension
                ext = Path(upload_file.filename).suffix
                filename = f"{uuid.uuid4()}{ext}"
            
            filepath = self.temp_dir / filename
            
            # Datei speichern
            with open(filepath, "wb") as f:
                content = await upload_file.read()
                f.write(content)
            
            logger.info(f"📁 Datei gespeichert: {filepath} ({len(content)} bytes)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern der Datei: {e}")
            raise
    
    def delete_file(self, filepath: str) -> bool:
        """
        Löscht eine Datei sicher
        
        Args:
            filepath: Pfad zur Datei
        
        Returns:
            bool: True wenn erfolgreich gelöscht
        """
        try:
            path = Path(filepath)
            if path.exists():
                path.unlink()
                logger.info(f"🗑️ Datei gelöscht: {filepath}")
                return True
            return False
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim Löschen: {filepath} - {e}")
            return False
    
    def cleanup_all_temp_files(self):
        """Löscht alle temporären Dateien"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(parents=True, exist_ok=True)
                logger.info("🧹 Alle temporären Dateien gelöscht")
        except Exception as e:
            logger.error(f"❌ Cleanup fehlgeschlagen: {e}")
    
    def get_file_size(self, filepath: str) -> int:
        """Gibt die Dateigröße in Bytes zurück"""
        return Path(filepath).stat().st_size if Path(filepath).exists() else 0