"""
Instagram Upload Service (Reels via Graph API — resumable binary upload)
"""
import requests
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.instagram.com/v21.0"


def instagram_upload_video(
    ig_user_id: str,
    access_token: str,
    video_path: str,
    caption: str = "",
    share_to_feed: bool = True
) -> dict:
    try:
        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"Video nicht gefunden: {video_path}")

        if len(caption) > 2200:
            logger.warning("Caption zu lang, wird gekuerzt")
            caption = caption[:2197] + "..."

        logger.info("Instagram Reel-Upload startet...")

        from config import settings
        filename = video_file.name
        video_url = f"{settings.FRONTEND_URL}/temp/{filename}"
        logger.info(f"Video URL: {video_url}")

        # Step 1: create media container
        container_id = _create_reel_container(
            ig_user_id=ig_user_id,
            access_token=access_token,
            video_url=video_url,
            caption=caption,
            share_to_feed=share_to_feed,
        )
        logger.info(f"Container erstellt (ID: {container_id})")

        # Step 3: wait for processing
        _wait_for_container_ready(ig_user_id, access_token, container_id)

        # Step 4: publish
        media_id = _publish_reel_container(
            ig_user_id=ig_user_id,
            access_token=access_token,
            creation_id=container_id,
        )

        logger.info(f"Instagram Reel veroeffentlicht! Media-ID: {media_id}")

        return {
            "media_id": media_id,
            "container_id": container_id,
            "status": "published",
            "message": "Reel erfolgreich veroeffentlicht",
        }

    except requests.RequestException as e:
        logger.error(f"Instagram API Fehler: {e}")
        raise Exception(f"Instagram Upload fehlgeschlagen: {str(e)}")
    except Exception as e:
        logger.error(f"Instagram Upload fehlgeschlagen: {e}")
        raise


def _create_reel_container(
    ig_user_id: str,
    access_token: str,
    video_url: str,
    caption: str,
    share_to_feed: bool,
) -> str:
    url = f"{GRAPH_BASE}/{ig_user_id}/media"
    data = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token,
    }

    response = requests.post(url, data=data, timeout=30)

    if not response.ok:
        logger.error(f"Instagram container {response.status_code}: {response.text}")
        response.raise_for_status()

    result = response.json()
    logger.info(f"Container Response: {result}")

    if "id" not in result:
        raise ValueError(f"Ungueltige Instagram API Response: {result}")

    return result["id"]


def _wait_for_container_ready(
    ig_user_id: str,
    access_token: str,
    container_id: str,
    max_wait_time: int = 300,
) -> None:
    url = f"{GRAPH_BASE}/{container_id}"
    params = {
        "fields": "status_code,error_message",
        "access_token": access_token,
    }

    start_time = time.time()
    logger.info("Warte auf Container-Verarbeitung...")

    while True:
        if time.time() - start_time > max_wait_time:
            raise TimeoutError("Container-Verarbeitung dauert zu lange")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            status = result.get("status_code")
            logger.info(f"Container Status: {status}")

            if status == "FINISHED":
                logger.info("Container ist bereit")
                return
            elif status == "ERROR":
                error_msg = result.get("error_message") or "unknown error"
                logger.error(f"Instagram container error detail: {result}")
                raise Exception(f"Container-Verarbeitung fehlgeschlagen: {error_msg}")

            time.sleep(5)

        except requests.RequestException as e:
            logger.warning(f"Status-Abfrage fehlgeschlagen: {e}")
            time.sleep(5)


def _publish_reel_container(
    ig_user_id: str,
    access_token: str,
    creation_id: str,
) -> str:
    url = f"{GRAPH_BASE}/{ig_user_id}/media_publish"
    data = {
        "creation_id": creation_id,
        "access_token": access_token,
    }

    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()
    result = response.json()

    if "id" not in result:
        raise ValueError(f"Ungueltige Publish-Response: {result}")

    return result["id"]


def get_media_insights(media_id: str, access_token: str) -> dict:
    url = f"{GRAPH_BASE}/{media_id}/insights"
    params = {
        "metric": "plays,likes,comments,shares,saved",
        "access_token": access_token,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Insights-Abfrage fehlgeschlagen: {e}")
        raise
