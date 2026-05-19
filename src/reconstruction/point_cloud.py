import os
import open3d as o3d
import numpy as np
import cv2
from src.preprocessing.camera_model import EndoscopeCamera

def generate_pcd(rgb_path, depth_path, camera):
    # 1. Load images
    color_raw = o3d.io.read_image(str(rgb_path))
    
    # Use OpenCV to read the depth map as-is to handle the 4-channel issue
    depth_cv = cv2.imread(str(depth_path), cv2.IMREAD_UNCHANGED)
    
    # If it has 4 channels (RGBA), take just the first channel (R) 
    # Usually, in these sims, R, G, and B are identical for grayscale depth
    if len(depth_cv.shape) == 3:
        depth_cv = depth_cv[:, :, 0]

    # Convert back to Open3D format
    depth_raw = o3d.geometry.Image(depth_cv.astype(np.float32))

    # 2. Create RGBD Image
    # Setting depth_scale to 1.0 because '45' is likely already in meters
    # or a unit much larger than millimeters.
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_raw, 
        depth_raw, 
        depth_scale=1.0,  # Trying 1.0 first
        depth_trunc=100.0, 
        convert_rgb_to_intensity=False
    )

    # 3. Define the Intrinsic Parameters
    intrinsics = o3d.camera.PinholeCameraIntrinsic(
        width=320, height=320,
        fx=camera.K[0,0], fy=camera.K[1,1],
        cx=camera.K[0,2], cy=camera.K[1,2]
    )

    # 4. Create the Point Cloud
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsics)
    
    # 5. Flip it for Open3D's coordinate system
    #pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    
    return pcd

if __name__ == "__main__":
    # 1. Define the base directories
    base_path = "data/raw/UnityCam/Colon"
    rgb_dir = os.path.join(base_path, "Frames")
    depth_dir = os.path.join(base_path, "Depth")
    
    # 2. Pick a frame index to test (e.g., the first one '0000')
    frame_idx = "0000"
    
    # 3. Construct paths using the specific naming formats from the dataset
    rgb_file = os.path.join(rgb_dir, f"image_{frame_idx}.png")
    depth_file = os.path.join(depth_dir, f"aov_image_{frame_idx}.png")
    
    # 4. Calibration Matrix (from our earlier session)
    K = np.array([[156.0418, 0, 178.5604], 
                  [0, 155.7529, 181.8043], 
                  [0, 0, 1]])
    
    camera = EndoscopeCamera(K, np.zeros((5,1)))
    
    # 5. Run the reconstruction
    print(f"Attempting to fuse:\n RGB: {rgb_file}\n Depth: {depth_file}")
    
    if os.path.exists(rgb_file) and os.path.exists(depth_file):
        try:
            point_cloud = generate_pcd(rgb_file, depth_file, camera)
            print("\n--- Success! ---")
            print("Visualizing 3D Reconstruction... (Close the window to exit)")
            o3d.visualization.draw_geometries([point_cloud])
        except Exception as e:
            print(f"Technical Error: {e}")
    else:
        print("\n--- Error: Files not found ---")
        print("Double-check that the file extensions are actually .png and not .jpg")