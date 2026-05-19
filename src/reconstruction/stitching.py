import open3d as o3d
import numpy as np
import pandas as pd
import os
from tqdm import tqdm

def stitch_movement_sequence(csv_path, ply_dir, start_idx=16000, num_frames=500, step=10):
    df = pd.read_csv(csv_path)
    master_pcd = o3d.geometry.PointCloud()
    
    # Use the first frame of OUR sequence as the origin
    t0 = np.array([df.iloc[start_idx]['tX'], df.iloc[start_idx]['tY'], df.iloc[start_idx]['tZ']])
    
    print(f"Stitching movement sequence...")
    
    for i in tqdm(range(start_idx, start_idx + num_frames, step)):
        ply_path = os.path.join(ply_dir, f"frame_{i:04d}.ply")
        if not os.path.exists(ply_path): continue
            
        pcd = o3d.io.read_point_cloud(ply_path)
        
        # 1. Coordinate alignment: Unity (Y-up) to Open3D (Y-down)
        # We must invert the Y and Z axes of the LOCAL points to match the world logic
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

        row = df.iloc[i]
        t = np.array([row['tX'], row['tY'], row['tZ']]) - t0
        
        # Open3D Quaternion: [W, X, Y, Z]
        q = np.array([row['rW'], row['rX'], row['rY'], row['rZ']])
        R = pcd.get_rotation_matrix_from_quaternion(q)
        
        # 2. Build the transformation
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t
        
        pcd.transform(T)
        master_pcd += pcd
        master_pcd = master_pcd.voxel_down_sample(voxel_size=0.01) # 1cm voxels
        
    return master_pcd

if __name__ == "__main__":
    csv_file = "data/raw/UnityCam/Colon/Poses/colon_position_rotation.csv"
    ply_folder = "results/point_clouds/colon_seq_1"
    
    # POLISH SETTINGS:
    # 1. We use a step of 1 or 2 to get high density (closes the gaps).
    # 2. We'll process 1000 frames to see a significant segment of the colon.
    full_model = stitch_movement_sequence(
        csv_file, 
        ply_folder, 
        start_idx=12000, 
        num_frames=1000, 
        step=2 
    )
    
    # Save this as "Final Result" 
    os.makedirs("results/final", exist_ok=True)
    o3d.io.write_point_cloud("results/final/colon_tunnel_high_res.ply", full_model)
    
    print("\n--- Map Finalized ---")
    print("PRO TIP: Press '+' on your keyboard in the window to make points larger!")
    o3d.visualization.draw_geometries([full_model])