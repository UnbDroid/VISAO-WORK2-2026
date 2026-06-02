class CubeDetector:
    def __init__(self, color_detector):
        self.color_detector = color_detector

    def detect_cubes(self, frame, tags):
        h, w = frame.shape[:2]

        cubes = []

        for tag in tags:

            cx = int(tag["center"][0])
            cy = int(tag["center"][1])

            size = 40

            x1 = max(cx - size, 0)
            x2 = min(cx + size, w)

            y1 = max(cy - size, 0)
            y2 = min(cy + size, h)

            roi = frame[y1:y2, x1:x2] # região da imagem ao redor da tag

            color = self.color_detector.detect_color(roi)

            # posição na mesa
            if cx < w * 0.33:
                position = "left"

            elif cx > w * 0.66:
                position = "right"

            else:
                position = "center"

            cube = {
                "tag": tag["id"],
                "color": color,
                "position": position,
                "x": cx
            }

            cubes.append(cube)

        return cubes