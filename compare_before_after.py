import numpy as np
import cv2
import imageio.v2 as imageio

ORIG_VIDEO = "original_video.mp4"
PROC_VIDEO = "processed_video.mp4"
OUT_VIDEO = "comparison_before_after.mp4"

orig_reader = imageio.get_reader(ORIG_VIDEO)
proc_reader = imageio.get_reader(PROC_VIDEO)
fps = orig_reader.get_meta_data().get("fps", 15)

orig_frames = [f[..., :3] for f in orig_reader]
proc_frames = [f[..., :3] for f in proc_reader]
orig_reader.close()
proc_reader.close()

n = min(len(orig_frames), len(proc_frames))
h, w = orig_frames[0].shape[:2]
sep_width = 4

writer = imageio.get_writer(OUT_VIDEO, fps=fps, codec="libx264", quality=8)

for i in range(n):
    left = orig_frames[i].copy()
    right = proc_frames[i].copy()

    cv2.putText(left, "BEFORE", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(right, "AFTER", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    separator = np.full((h, sep_width, 3), 255, dtype=np.uint8)
    combined = np.hstack([left, separator, right])
    writer.append_data(combined)

writer.close()
print(f"Сохранено: {OUT_VIDEO}")
print(f"Кадров: {n}, FPS: {fps}, размер кадра: {w * 2 + sep_width}x{h}")
