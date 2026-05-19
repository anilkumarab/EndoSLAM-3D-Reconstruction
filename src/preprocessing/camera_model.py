import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

class EndoscopeCamera:
    """
    Handles camera intrinsics, distortion coefficients, and image rectification
    for the EndoSLAM dataset.
    """
    def __init__(self, intrinsic_matrix: np.ndarray, dist_coeffs: np.ndarray):
        """
        Args:
            intrinsic_matrix: 3x3 numpy array of camera intrinsics (fx, fy, cx, cy)
            dist_coeffs: numpy array of distortion coefficients (k1, k2, p1, p2, k3...)
        """
        self.K = intrinsic_matrix
        self.D = dist_coeffs
        self.new_camera_matrix = None
        self.roi = None

    def undistort(self, image: np.ndarray) -> np.ndarray:
        """
        Removes radial and tangential distortion from an endoscopic image.
        """
        h, w = image.shape[:2]
        
        # Calculate optimal new camera matrix only once for efficiency
        if self.new_camera_matrix is None:
            self.new_camera_matrix, self.roi = cv2.getOptimalNewCameraMatrix(
                self.K, self.D, (w, h), 1, (w, h)
            )
            
        # Apply the undistortion
        undistorted_img = cv2.undistort(image, self.K, self.D, None, self.new_camera_matrix)
        
        return undistorted_img

    @classmethod
    def from_calibration_file(cls, filepath: str | Path):
        """
        Parses the EndoSLAM UnityCam/OlympusCam calibration string.
        Assumes a comma-separated list of 9 values representing a 3x3 matrix.
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
                
            # Convert the comma-separated string into a list of floats
            values = [float(x) for x in content.split(',')]
            
            if len(values) != 9:
                raise ValueError(f"Expected 9 values, got {len(values)}")
            
            # Reshape into a 3x3 intrinsic matrix
            intrinsic_matrix = np.array(values).reshape((3, 3))
            
            # Synthetic data (UnityCam) usually has zero distortion (k1, k2, p1, p2, k3)
            # If the file had 14 values, the remaining 5 would be distortion.
            dist_coeffs = np.zeros((5, 1)) 
            
            return cls(intrinsic_matrix, dist_coeffs)
            
        except Exception as e:
            print(f"Error parsing calibration file: {e}")
            return None
            
if __name__ == "__main__":
    print("Camera Preprocessing Module Loaded Successfully.")