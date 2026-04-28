# backend/data/optimizer_config.py
"""
Static platform knowledge base for the optimizer.
Can be replaced by DB-driven config later.
"""

# General platform peak times (UTC) – day_of_week: 0=Mon, 6=Sun
PLATFORM_PEAK_TIMES: dict = {
    "youtube": {
        "default": [
            {"day": 4, "hours": [15, 16, 17]},  # Friday 15-17 UTC
            {"day": 5, "hours": [10, 11, 14, 15]},  # Saturday
            {"day": 6, "hours": [10, 11, 14, 15]},  # Sunday
            {"day": 1, "hours": [14, 15, 16]},  # Tuesday
        ],
        "gaming": [
            {"day": 4, "hours": [16, 17, 18, 19]},
            {"day": 5, "hours": [14, 15, 16, 17, 18]},
            {"day": 6, "hours": [14, 15, 16, 17]},
        ],
        "education": [
            {"day": 0, "hours": [9, 10, 11]},
            {"day": 1, "hours": [9, 10, 11]},
            {"day": 2, "hours": [9, 10, 11]},
        ],
        "music": [
            {"day": 4, "hours": [14, 15, 16]},
            {"day": 5, "hours": [11, 12, 13]},
        ],
    },
    "tiktok": {
        "default": [
            {"day": 1, "hours": [6, 9, 12]},
            {"day": 2, "hours": [6, 9]},
            {"day": 4, "hours": [9, 12, 19]},
            {"day": 5, "hours": [9, 11]},
        ],
        "gaming": [
            {"day": 4, "hours": [16, 17, 20, 21]},
            {"day": 5, "hours": [11, 14, 15, 20]},
            {"day": 6, "hours": [11, 14, 20]},
        ],
        "entertainment": [
            {"day": 1, "hours": [12, 13, 19, 20]},
            {"day": 2, "hours": [12, 13]},
            {"day": 4, "hours": [12, 19, 20]},
        ],
    },
    "instagram": {
        "default": [
            {"day": 0, "hours": [8, 9, 11]},
            {"day": 1, "hours": [8, 9, 11]},
            {"day": 2, "hours": [8, 9, 11, 17]},
            {"day": 3, "hours": [8, 9, 11]},
            {"day": 4, "hours": [8, 9, 11, 17]},
        ],
        "lifestyle": [
            {"day": 0, "hours": [8, 11, 17]},
            {"day": 2, "hours": [8, 11, 17]},
            {"day": 4, "hours": [11, 14, 17]},
        ],
    },
}

# Platform-specific constraints for text optimization
PLATFORM_CONSTRAINTS: dict = {
    "youtube": {
        "title_max_chars": 100,
        "description_max_chars": 5000,
        "tags_max_count": 30,
        "tags_max_total_chars": 500,
        "description_note": "Use timestamps, chapters, and links. First 2 lines are shown without expanding.",
    },
    "tiktok": {
        "title_max_chars": 150,  # Caption
        "description_max_chars": 2200,
        "tags_max_count": 20,
        "tags_max_total_chars": 300,
        "description_note": "Caption with hashtags. Hooks in first 3 seconds are critical.",
    },
    "instagram": {
        "title_max_chars": 2200,  # Caption (Reels)
        "description_max_chars": 2200,
        "tags_max_count": 30,
        "tags_max_total_chars": 400,
        "description_note": "First 125 chars visible without 'more'. Hashtags at end or first comment.",
    },
}

# Trending hashtag seeds per category/platform (static fallback)
HASHTAG_SEEDS: dict = {
    "youtube": {
        "gaming": ["gaming", "gameplay", "gamer", "pcgaming", "consolegaming", "letsplay",
                   "gamingcommunity", "videogames", "streamer", "gamingsetup"],
        "education": ["education", "learning", "tutorial", "howto", "tips", "knowledge",
                      "study", "edtech", "explainer", "learnontiktok"],
        "music": ["music", "newsong", "musician", "originalmusic", "indiemusic",
                  "musicvideo", "singer", "producer", "hiphop", "rnb"],
        "default": ["viral", "trending", "youtube", "content", "creator",
                    "subscribe", "youtuber", "video", "watch", "new"],
    },
    "tiktok": {
        "gaming": ["gaming", "gamer", "fyp", "foryou", "tiktokgaming", "gameplay",
                   "gaminglife", "pcgamer", "consolegaming", "esports"],
        "entertainment": ["fyp", "foryoupage", "viral", "trending", "entertainment",
                          "funny", "comedy", "tiktok", "foryou", "explore"],
        "default": ["fyp", "foryoupage", "viral", "trending", "tiktok",
                    "foryou", "explore", "content", "creator", "new"],
    },
    "instagram": {
        "gaming": ["gaming", "gamer", "instagaming", "gamingcommunity", "reels",
                   "instareels", "gameplay", "gamersofinstagram", "videogames", "esports"],
        "lifestyle": ["lifestyle", "reels", "instareels", "explore", "instagood",
                      "viral", "trending", "reelsinstagram", "reelsviral", "instadaily"],
        "default": ["reels", "instareels", "explore", "viral", "trending",
                    "instagood", "instagram", "content", "reelsviral", "creator"],
    },
}
