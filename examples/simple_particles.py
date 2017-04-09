import yt
import yt.extensions.vispyt as vp
import numpy as np

ds = yt.load("IsolatedGalaxy/galaxy0030/galaxy0030")
dd = ds.r[:]

pr = vp.ParticleRendering()

pr.add_particles(dd["particle_position"], 
        np.ones(dd["particle_position"].shape[0]),
        color=(1.0, 0.0, 1.0), alpha=0.5, radius_scale = 0.01)

pr.distance = 0.5
pr.render()
pr.view.camera.center = ds.domain_center
