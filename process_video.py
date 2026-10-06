import numpy as np
import cv2
import imageio.v2 as imageio

SRC_VIDEO = "original_video.mp4"
OUT_VIDEO = "processed_video.mp4"

CROP_FRAC = 0.08          # сколько % убрать с каждого края при обрезке
STRETCH_AMPLITUDE = 0.35  # амплитуда сжатия/растяжения (0.35 -> от x0.65 до x1.35)
STRETCH_CYCLES = 3        # сколько циклов сжатия/растяжения за всё видео
ROTATIONS = 1             # сколько полных оборотов за всё видео
GAMMA_CYCLES = 2          # сколько циклов изменения гаммы за всё видео
GAMMA_MIN, GAMMA_MAX = 0.3, 2.5


def gamma_correction(frame, gamma):
    inv_gamma = 1.0 / max(gamma, 1e-3)
    table = (np.linspace(0, 1, 256) ** inv_gamma * 255).astype(np.uint8)
    return cv2.LUT(frame, table)


def place_centered(canvas, src):
    dh, dw = canvas.shape[:2]
    sh, sw = src.shape[:2]

    y_off = (dh - sh) // 2
    x_off = (dw - sw) // 2

    dst_y0, dst_y1 = max(0, y_off), min(dh, y_off + sh)
    dst_x0, dst_x1 = max(0, x_off), min(dw, x_off + sw)

    src_y0 = max(0, -y_off)
    src_x0 = max(0, -x_off)
    src_y1 = src_y0 + (dst_y1 - dst_y0)
    src_x1 = src_x0 + (dst_x1 - dst_x0)

    canvas[dst_y0:dst_y1, dst_x0:dst_x1] = src[src_y0:src_y1, src_x0:src_x1]
    return canvas


reader = imageio.get_reader(SRC_VIDEO)
fps = reader.get_meta_data().get("fps", 15)
frames = [f[..., :3] for f in reader]
reader.close()

n = len(frames)
h, w = frames[0].shape[:2]

y0, y1 = int(h * CROP_FRAC), int(h * (1 - CROP_FRAC))
x0, x1 = int(w * CROP_FRAC), int(w * (1 - CROP_FRAC))

writer = imageio.get_writer(OUT_VIDEO, fps=fps, codec="libx264", quality=8)

for i, frame in enumerate(frames):
    t = i / n  # фаза проигрывания: от 0 до 1 за всё видео

    # 1) Обрезка
    cropped = frame[y0:y1, x0:x1]

    # 2) Сжатие/растяжение по горизонтали и вертикали (в противофазе)
    scale_x = 1.0 + STRETCH_AMPLITUDE * np.sin(2 * np.pi * t * STRETCH_CYCLES)
    scale_y = 1.0 + STRETCH_AMPLITUDE * np.sin(2 * np.pi * t * STRETCH_CYCLES + np.pi / 2)
    ch, cw = cropped.shape[:2]
    new_w = max(1, int(cw * scale_x))
    new_h = max(1, int(ch * scale_y))
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    canvas = place_centered(canvas, resized)

    # 3) Поворот
    angle = t * 360 * ROTATIONS
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    rotated = cv2.warpAffine(canvas, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    # 4) Гамма-коррекция (колеблется между тёмным и светлым)
    gamma_phase = np.sin(2 * np.pi * t * GAMMA_CYCLES)  # -1..1
    gamma = GAMMA_MIN + (gamma_phase + 1) / 2 * (GAMMA_MAX - GAMMA_MIN)
    final = gamma_correction(rotated, gamma)

    writer.append_data(final)

writer.close()
print(f"Сохранено: {OUT_VIDEO}")
print(f"Кадров: {n}, FPS: {fps}")
