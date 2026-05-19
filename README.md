# EndoSLAM 3D Reconstruction Pipeline

A modular, memory-efficient 3D computer vision and spatial registration pipeline designed to process sequential RGB-D frames from the EndoSLAM dataset. This system accurately stitches localized frame data into a cohesive, global 3D point cloud model using pose-based rigid body transformations.

---

## 🛠️ Software Architecture & Modules

To maintain a clean separation of concerns and high modularity, the codebase is split into specialized engineering modules:

### 1. Preprocessing Stack (`src/preprocessing/`)
* **`camera_model.py`**: Establishes optical foundations. Uses the pinhole camera intrinsic matrix ($K$) to calculate the trajectory of visual rays. It handles critical sensor coordinate system alignment, mapping pixel configurations cleanly into metric space.

### 2. Reconstruction Stack (`src/reconstruction/`)
* **`point_cloud.py`**: Handles individual frame generation. It transforms raw 16-bit depth values into real-world metric distances (meters), back-projects pixels into structured 3D coordinates, and runs a localized **voxel downsampling** pass to prevent downstream memory bottlenecks.
* **`stitching.py`**: The spatial registration engine. It parses 6DoF camera tracking trajectory coordinates, handles a critical similarity reflection matrix to correct left/right-handed coordinate system mismatches, and applies a $4 \times 4$ homogeneous rigid body transformation matrix ($SE(3)$ mapping) to lock local frames into a unified global map.

### 3. Orchestration Layer (`scripts/`)
* **`batch_reconstruct.py`**: The master pipeline executive. It manages the sequential data ingestion loops, streams image indices smoothly through the perception modules, coordinates the multi-frame accumulation array, and exports the finalized global `.ply` model to disk.

---

## 🚀 Key Technical Challenges Resolved

### 1. The "Shuriken" Alignment Artifact (Coordinate Space Resolution)
* **Challenge**: Initial stitching passes resulted in a chaotic star-like geometric explosion (the "shuriken" artifact) due to a fundamental mismatch between the left-handed tracking frame of the synthetic simulation environment and Open3D's right-handed Cartesian system.
* **Resolution**: Implemented a mathematical basis change via a similarity transformation matrix ($T_{open3d} = M \cdot T_{unity} \cdot M$), smoothly mirroring the translation vectors and orientation quaternions to align tracking steps with the 3D point generation.

### 2. Specular & Featureless Tracking Stabilization
* **Challenge**: Endoscopic frames suffer from severe specular reflections (wet tissue glare) and a lack of rigid, sharp geometric features, causing traditional data-driven SLAM algorithms (like ICP or ORB-SLAM) to slip, drift, or lock into catastrophic local minima.
* **Resolution**: Engineered a deterministic pose-based rigid transformation algorithm utilizing synchronized tracking logs to guarantee perfect architectural structure without tracking drift.

---

## 📦 Prerequisites & Setup
* Python 3.8+
* Open3D, NumPy, SciPy

```bash
# Execute the pipeline execution loop
python -m scripts.batch_reconstruct