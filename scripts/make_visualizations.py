import os
import numpy as np
import trimesh

import yourdfpy
from yourdfpy.viz import generate_joint_limit_trajectory, viewer_callback

import glob

urdf_files = glob.glob("*/**/*.urdf")
# urdf_files = ["franka_panda/urdf/franka_gripper.urdf"]
# urdf_files = ["fetch/urdf/fetch_gripper.urdf"]

urdf_files = sorted(urdf_files)

animations_per_row = 3
markdown = (
    "| ".join([""] * (animations_per_row + 1))
    + "|\n"
    + "|:---:".join([""] * (animations_per_row + 1))
    + "|\n"
)

for i, path in enumerate(urdf_files):
    # urdf_model = yourdfpy.URDF.load(path)
    gripper_name = os.path.splitext(os.path.basename(path))[0]

    markdown = (
        markdown
        + f'|<img width="200px" alt="{gripper_name}" src="https://github.com/clemense/gripper_descriptions/blob/main/images/animations/{gripper_name}.gif">'  # [{path}]({path})'
    )

    if (i + 1) % animations_per_row == 0 or (i + 1) == len(urdf_files):
        markdown = markdown + "|\n"

    continue
    loop_time = 0.1  # creates 10 frames
    trajectory = generate_joint_limit_trajectory(
        urdf_model=urdf_model, loop_time=loop_time
    )
    trajectory_length = len(list(trajectory.values())[0])

    camera_transform_z_up = np.array(
        [
            [0.71067966, 0.39438262, -0.58257769, -0.34651126],
            [-0.70260909, 0.4399133, -0.55930023, -0.32087581],
            [0.03570538, 0.80680769, 0.58973425, 0.40941472],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )

    tmp_png_fnames = []
    for t in range(trajectory_length):
        cfg = {k: trajectory[k][t] for k in trajectory}
        urdf_model.update_cfg(configuration=cfg)
        scene = trimesh.Scene(
            (
                urdf_model._scene,
                trimesh.creation.axis(
                    origin_size=0.005, axis_length=0.2, axis_radius=0.0025
                ),
            ),
            base_frame=urdf_model._scene.graph.base_frame,
        )
        scene.camera_transform = camera_transform_z_up

        fname = f"hallo{t:03}.png"
        with open(fname, "wb") as f:
            png = scene.save_image(resolution=(640, 480), visible=True)
            f.write(png)
            f.close()

            tmp_png_fnames.append(fname)

            # Make image square
            cmd = f"convert {fname} -shave 80x0 {fname}"
            os.system(cmd)

    cmd = f"convert -delay 10 -loop 0 {' '.join(tmp_png_fnames)} images/animations/{gripper_name}.gif"
    os.system(cmd)

print(markdown)
cmd = f"rm {' '.join(tmp_png_fnames)}"
os.system(cmd)
