import time
print("STARTING SCRIPT")
t = time.time(); import torch;    print(f"torch:   {time.time()-t:.1f}s")
t = time.time(); import cv2;      print(f"cv2:     {time.time()-t:.1f}s")
t = time.time(); import viser;    print(f"viser:   {time.time()-t:.1f}s")
t = time.time(); import trimesh;  print(f"trimesh: {time.time()-t:.1f}s")
t = time.time(); import vggt; print(f"vggt:    {time.time()-t:.1f}s")