import random
from datetime import datetime
from typing import Dict, Any

class StreetCamVision:
    # ok so this is the "fake it till you make it" cam vision guy
    def __init__(self) -> None:
        self.vibes = ["light", "chill", "medium", "kinda busy", "heavy"]

    def fetch_nearby_cams(self, lat: float, lng: float) -> Dict[str, Any]:
        # pretend we looked up traffic cams near the coordinates
        return {
            "cams": [
                {
                    "id": "demo_cam_1",
                    "name": "Main & 1st",
                    "lat": lat + 0.003,
                    "lng": lng - 0.002,
                    "frame_url": "https://placehold.co/640x360?text=Street+Cam"
                }
            ],
            "source": "pretend-directory",
        }

    def analyze_frame(self, frame_url: str) -> Dict[str, Any]:
        # roll some dice to act like we did computer vision
        level = random.choice(self.vibes)
        score = random.randint(45, 92)
        cars_est = random.randint(3, 28)
        return {
            "traffic_level": level,
            "confidence": score,
            "estimated_cars": cars_est,
            "frame": frame_url,
        }

    def get_insight(self, lat: float, lng: float) -> Dict[str, Any]:
        cams = self.fetch_nearby_cams(lat, lng)
        pick = cams["cams"][0]
        analysis = self.analyze_frame(pick["frame_url"])
        return {
            "cam": pick,
            "analysis": analysis,
            "note": "beta demo – talking point for hackathon, not real yet",
            "timestamp": datetime.now().isoformat(),
        }
