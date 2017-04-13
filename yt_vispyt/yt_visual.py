# -*- coding: utf-8 -*-

import numpy as np
from vispy import gloo, visuals
import os

class YTVisual(visuals.Visual):
    data_vbo = None
    dtype = ()
    visual_name = None
    draw_type = None

    def __init__(self):
        super(YTVisual, self).__init__()
        self.shaders = {}
        curpath = os.path.dirname(os.path.abspath(__file__))
        for shader in ["vertex", "fragment"]:
            with open(os.path.join(curpath, "shaders",
                "{}.{}.glsl".format(self.visual_name, shader))) as f:
                self.shaders[shader] = f.read()
        self.program = visuals.shaders.ModularProgram(self.shaders["vertex"],
                                                      self.shaders["fragment"])
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

    def reset_data(self, *args):
        if len(self.dtype) == 0:
            raise RuntimeError
        ## shader data
        data = np.zeros(args[0].shape[0], dtype = list(self.dtype))
        for (field, dt, c), val in zip(self.dtype, args):
            data[field] = val
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
        self.program.draw(self.draw_type)
