"""
Instagram Upload Service (Reels via Graph API - resumable binary upload)
"""
import requests
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.instagram.com/v21.0"
UPLOAD_URL = "https://rupload.facebook.com/ig-api-upload"


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

        logger.info("Instagram Reel-Upload startet (resumable binary)...")

        upload_id = _init_resumable_upload(
            ig_user_id=ig_user_id,
            access_token=access_token,
            video_file=video_file,
            caption=caption,
            share_to_feed=share_to_feed,
        )
        logger.info(f"Resumable Upload initialisiert (ID: {upload_id})")

        _upload_binary(upload_id, video_file)
        logger.info("Binary-Upload abgeschlossen")

        container_id = _create_reel_container_from_upload(
            ig_user_id=ig_user_id,
            access_token=access_token,
            upload_id=upload_id,
        )
        logger.info(f"Container erstellt (ID: {container_id})")

        _wait_for_container_ready(ig_user_id, access_token, container_id)

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


def _init_resumable_upload(
    ig_user_id: str,
    access_token: str,
    video_file: Path,
    caption: str,
    share_to_feed: bool,
) -> str:
    url = f"{GRAPH_BASE}/{ig_user_id}/media"
    params = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "share_to_feed": "true" if share_to_feed else "false",
        "access_token": access_token,
    }
    if caption:
        params["caption"] = caption

    response = requests.post(url, params=params, timeout=30)

    if not response.ok:
        logger.error(f"Init {response.status_code}: {response.text}")
        token_error = False
        try:
            err = response.json().get("error", {})
            if err.get("code") == 190:
                token_error = True
        except Exception:
            pass
        if token_error:
            raise ValueError(
                "Instagram-Token abgelaufen oder widerrufen. "
                "Bitte Instagram in den Plattform-Einstellungen trennen und neu verbinden."
            )
        response.raise_for_status()

    result = response.json()
    logger.info(f"Init Response: {result}")

    if "upload_id" not in result:
        raise ValueError(f"Ungueltige Init-Response: {result}")

    return result["upload_id"]


def _upload_binary(upload_id: str, video_file: Path) -> None:
    url = f"{UPLOAD_URL}/v21.0/{upload_id}"
    
    file_size = video_file.stat().st_size
    video_data = video_file.read_bytes()

    headers = {
        "Offset": "0",
        "Content-Length": str(file_size),
        "Content-Type": "application/octet-stream",
    }

    response = requests.post(url, data=video_data, headers=headers, timeout=120)

    if not response.ok:
        logger.error(f"Binary upload {response.status_code}: {response.text}")
        response.raise_for_status()


def _create_reel_container_from_upload(
    ig_user_id: str,
    access_token: str,
    upload_id: str,
) -> str:
    url = f"{GRAPH_BASE}/{ig_user_id}/media"
    params = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "upload_id": upload_id,
        "access_token": access_token,
    }

    response = requests.post(url, params=params, timeout=30)

    if not response.ok:
        logger.error(f"Container {response.status_code}: {response.text}")
        response.raise_for_status()

    result = response.json()
    logger.info(f"Container Response: {result}")

    if "id" not in result:
        raise ValueError(f"Ungueltige Container-Response: {result}")

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
    params = {
        "creation_id": creation_id,
        "access_token": access_token,
    }

    response = requests.post(url, params=params, timeout=30)
    response.raise_for_status()
    result = response.json()

    if "id" not in result:
        raise ValueError(f"Ungueltige Publish-Response: {result}")

    return result["id"]