import yt
import yt.extensions.vispyt as vp
import numpy as np

ds = yt.load("snapshot_033/snap_033.0.hdf5")
dd = ds.r[:]

pr = vp.ParticleRendering()

# stars
pr.add_particles(dd["PartType4", "particle_position"],
        np.ones(dd["PartType4","particle_position"].shape[0]),
        color=(1.0, 0.0, 1.0), alpha=0.5,
        radius_scale = 0.01)

# Now for dm
pr.add_particles(dd["PartType1", "particle_position"],
        np.ones(dd["PartType1","particle_position"].shape[0]),
        color=(0.0, 1.0, 0.0), alpha=0.5,
        radius_scale = 0.01)

# Now for gas
pr.add_particles(dd["PartType0", "particle_position"],
        dd["PartType0", "SmoothingLength"].in_units("code_length"),
        color=(0.0, 0.0, 1.0), alpha=0.5,
        radius_scale = 0.1)


pr.distance = 0.5
pr.render()

pr.view.camera.center = ds.domain_center
