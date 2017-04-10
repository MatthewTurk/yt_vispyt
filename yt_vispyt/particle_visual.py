# -*- coding: utf-8 -*-

import numpy as np
from vispy import gloo, visuals
from .yt_visual import YTVisual
import os

class ParticleVisual(YTVisual):
    data_vbo = None
    dtype = (('a_position',     np.float32, 3),
             ('a_color',        np.float32, 4),
             ('a_radius',       np.float32, 1),
             ('a_kernel',       np.float32, 1))
    visual_name = "sph_particle"

    def __init__(self, pos, radius, radius_scale, color, alpha, kernel):
        
        ## set particle colors
        if isinstance(color, (tuple, list)):
            color = tuple(color)
            if len(color) == 3:
                color += (1.0,)
            color = np.ones((pos.shape[0], 4), dtype="float32") * color
        elif isinstance(color, np.ndarray):
            assert(color.shape[0] == pos.shape[0])
            if color.shape[-1] == 3:
                color = np.concatenate([color, np.zeros((pos.shape[0], 1))],
                                       axis=-1)
            elif color.ndim == 1:
                color = np.tile(color, (4, 1)).T
            else:
                assert(color.shape == (pos.shape[0], 4))
        else:
            raise NotImplementedError

        color[:,3] = alpha # Should work as long for scalar and array
        self.reset_data(pos, color, radius, kernel)

        super(ParticleVisual, self).__init__()

        self.program['u_radius_scale'] = radius_scale
