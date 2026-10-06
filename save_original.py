import imageio.v2 as imageio

SRC_GIF = "../КТ2/wave_animation.gif"
OUT_VIDEO = "original_video.mp4"
LOOPS = 4     # сколько раз повторить анимацию подряд
FPS = 15

reader = imageio.get_reader(SRC_GIF)
frames = [frame[..., :3] for frame in reader]  # отбрасываем альфа-канал GIF
reader.close()

all_frames = frames * LOOPS

writer = imageio.get_writer(OUT_VIDEO, fps=FPS, codec="libx264", quality=8)
for frame in all_frames:
    writer.append_data(frame)
writer.close()

duration = len(all_frames) / FPS
print(f"Сохранено: {OUT_VIDEO}")
print(f"Кадров: {len(all_frames)}, FPS: {FPS}, длительность: {duration:.1f} сек")
