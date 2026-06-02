import cv2
from pupil_apriltags import Detector

class AprilTagDetector:
    def __init__(self):

        self.detector = Detector(
            families="tag36h11"
        )

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        results = self.detector.detect(gray)
        tags = []

        for r in results:
            tag_data = {
                "id": r.tag_id,
                "center": r.center,
                "corners": r.corners
            }

            tags.append(tag_data)

        return tags 