import os
import open3d as o3d
import numpy as np
from tqdm import tqdm
from src.reconstruction.point_cloud import generate_pcd
from src.preprocessing.camera_model import EndoscopeCamera

# Setup paths
BASE_PATH = "data/raw/UnityCam/Colon"
SAVE_PATH = "results/point_clouds/colon_seq_1"
os.makedirs(SAVE_PATH, exist_ok=True)

# Intrinsics
K = np.array([[156.0418, 0, 178.5604], 
              [0, 155.7529, 181.8043], 
              [0, 0, 1]])
camera = EndoscopeCamera(K, np.zeros((5,1)))

def run_batch(start_idx, count):
    """
    Processes a specific range of frames.
    """
    print(f"Starting batch reconstruction of {count} frames from index {start_idx}...")
    
    # Iterate through the specified range
    for i in tqdm(range(start_idx, start_idx + count)):
        # f"{i:04d}" ensures at least 4 digits (e.g., 0001, 16000)
        frame_idx = f"{i:04d}" 
        
        rgb_path = os.path.join(BASE_PATH, "Frames", f"image_{frame_idx}.png")
        depth_path = os.path.join(BASE_PATH, "Depth", f"aov_image_{frame_idx}.png")
        
        if os.path.exists(rgb_path) and os.path.exists(depth_path):
            try:
                # Generate the cloud
                pcd = generate_pcd(rgb_path, depth_path, camera)
                
                # Save as PLY file
                save_file = os.path.join(SAVE_PATH, f"frame_{frame_idx}.ply")
                o3d.io.write_point_cloud(save_file, pcd)
            except Exception as e:
                print(f"Error on frame {frame_idx}: {e}")
        else:
            # If the script skips unexpectedly, verify the file extension (.png vs .jpg)
            continue

if __name__ == "__main__":
    # The camera starts significant movement and rotation after index 15311
    # Processing this range will provide the data needed for a visible 3D tunnel
    start_frame = 12000
    num_to_process = 1000
    
    run_batch(start_idx=start_frame, count=num_to_process)