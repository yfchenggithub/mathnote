"""UID-local encoding repair after frozen exporter preview; no shared tools changed."""
from pathlib import Path
import sys,subprocess,json,os,uuid
ROOT=Path(__file__).resolve().parents[3]
uid=Path(__file__).resolve().parents[1].name[:4]
mp4=Path(sys.argv[1]).resolve();target=Path(sys.argv[2]).resolve()
assert ROOT in mp4.parents and ROOT in target.parents
assert target.parent==Path(__file__).resolve().parents[1]/"images"
if target.exists():raise FileExistsError("Never overwrite an existing asset")
staged=mp4.parent/("fullframes_"+uuid.uuid4().hex+".gif")
subprocess.run(["ffmpeg","-y","-i",str(mp4),"-filter_complex","fps=12,scale=576:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=full[p];[b][p]paletteuse=dither=bayer:bayer_scale=3","-gifflags","-transdiff","-loop","0",str(staged),"-loglevel","error"],check=True)
subprocess.run([str(ROOT/".venv-manim/Scripts/python.exe"),str(ROOT/"scripts/manim/verify_gif.py"),str(staged)],check=True)
os.link(staged,target)
print("Created new reviewed GIF",target)
