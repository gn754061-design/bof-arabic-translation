from PIL import Image
import sys
im = Image.open(sys.argv[1]).convert("RGB")
x1, y1, x2, y2, s, out = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
crop = im.crop((x1, y1, x2, y2))
crop = crop.resize((crop.width * s, crop.height * s), Image.LANCZOS)
crop.save(out)
print("saved", out, crop.size)
