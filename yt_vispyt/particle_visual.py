# -*- coding: utf-8 -*-

import numpy as np
from vispy import gloo, visuals
import os

class ParticleVisual(visuals.Visual):
    data_vbo = None
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

        visuals.Visual.__init__(self)
        shaders = {}
        curpath = os.path.dirname(os.path.abspath(__file__))
        for shader in ["vertex", "fragment"]:
            with open(os.path.join(curpath, "shaders",
                "sph_particle.{}.glsl".format(shader))) as f:
                shaders[shader] = f.read()
        self.program = visuals.shaders.ModularProgram(shaders["vertex"],
                                                      shaders["fragment"])
        self.program['u_radius_scale'] = radius_scale
        self.data_vbo = gloo.VertexBuffer(self.data)
        self.program.bind(self.data_vbo)

    def __setitem__(self, field, vals):
        if field in (n for _, _, n in self.program.variables):
            self.program[field] = vals
            return
        fields = self.data.dtype.fields
        if field not in fields and ("a_%s" % field) in fields:
            field = "a_%s" % field
        self.data[field] = vals
        self.data_vbo.set_data(self.data)

    def __getitem__(self, field):
        if field in (n for _, _, n in self.program.variables):
            return self.program[field]
        fields = self.data.dtype.fields
        if field not in fields and ("a_%s" % field) in fields:
            field = "a_%s" % field
        return self.data[field]

    def reset_data(self, pos, color, radius, kernel):
        ## shader data
        data = np.zeros(pos.shape[0],
                        dtype=[('a_position',     np.float32, 3),
                               ('a_color',        np.float32, 4),
                               ('a_radius',       np.float32, 1),
                               ('a_kernel',       np.float32, 1)])
        data['a_position']     = pos
        data['a_color']        = color
        data['a_radius']       = radius
        data['a_kernel']       = kernel
        self.data = data
        if self.data_vbo is not None:
            self.data_vbo.set_data(self.data)

    def draw(self,transforms):
        gloo.set_state('additive', cull_face=False)

        self.program.vert['visual_to_doc'] = transforms.visual_to_document
        imap = transforms.visual_to_document.inverse
        self.program.vert['doc_to_render'] = (
            transforms.framebuffer_to_render *
            transforms.document_to_framebuffer)
        #self.program.vert['transform'] = transforms.get_full_transform()
        self.program.vert['itrans'] = transforms.get_full_transform().inverse
        self.program.draw('points')

