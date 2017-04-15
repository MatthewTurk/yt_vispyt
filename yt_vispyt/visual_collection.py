# -*- coding: utf-8 -*-

import numpy as np
from vispy import app, visuals, scene
from .particle_visual import ParticleVisual

def delegate_view(name, convert_to_unitary = True):
    def getter(self):
        return getattr(self, "_{}".format(name), None)
    def setter(self, value):
        if convert_to_unitary:
            value = self._in_unitary(value)
         setattr(self, "_{}".format(name), value)
         if hasattr(self, "view"):
            setattr(self.view.camera, name, value)
    return property(getter, setter)

class YTVispyScene(object):
    _fov = 60.0
    _distance = 1.0
    _center = (0.0,0.0,0.0)

    def __init__(self, ds):
        self.ds = ds
        self.nodes = []

        self.particle_node = scene.visuals.create_visual_node(ParticleVisual)

    def _in_unitary(self, value):
        if isinstance(value, tuple) and len(value) == 2 \
                and isinstance(value[1], str):
            value = self.ds.quan(value[0], value[1])
        if hasattr(value, "in_units"):
            return value.in_units("unitary")
        else:
            return self.ds.quan(value[0], "unitary")

    distance = delegate_view("distance")
    fov = delegate_view("fov", False)
    focal_point = delegate_view("center")
    
    def add_particles(self, particle_position, radius,
                      radius_scale=1.0,
                      color=(1,1,1), color_by='', 
                      alpha=1.0, alpha_by='', kernel=1.0):
        
        if len(color_by) == len(particle_position):
            if np.max(color_by) > 1.0:
                color_by /= np.max(color_by)
            import matplotlib.cm as cm
            #color = cm.winter_r(color_by) 
            color = cm.GnBu(color_by)
            color = color[:,0:3]
        
        if len(alpha_by) == len(particle_position):
            if np.max(alpha_by) > 1.0:
                alpha_by /= np.max(alpha_by)
            alpha = alpha_by

        self.particles.append({
            'pos':particle_position,
            'color':color,
            'alpha':alpha,
            'radius':radius,
            'radius_scale':radius_scale,
            'kernel':kernel
        })
        
    def draw_cube(self, cube_size=(1.0,1.0,1.0),
                        cube_color=(0,0,0,0),
                        edge_color=(1,1,1,1)):
        self.cube_settings = {
            'cube_size':cube_size,
            'cube_color':cube_color,
            'edge_color':edge_color
        }

    def _render_particles(self):                
        for v in self.particles:
            p = self.particle_node(v['pos'],v['radius'],
                                   v['radius_scale'],
                                   color=v['color'],alpha=v['alpha'],
                                   kernel=v['kernel'],
                                   parent=self.view.scene)
            p.transform = visuals.transforms.AffineTransform()
            self.particle_items.append(p)
        self.particles = []
        
    def render(self, bgcolor='k', border_color='k', 
               camera='arcball',center=_focal_point):

        self.canvas = scene.SceneCanvas(keys='interactive',show=True)
        grid   = self.canvas.central_widget.add_grid(bgcolor=bgcolor,
                                        border_color=border_color)
        self.view   = grid.add_view()
        self.view.camera = camera
        self.view.camera.fov = self.fov
        self.view.camera.distance = self.distance
        self.focal_point = center

        # random console stuff
        #console = grid.add_widget(
        #    scene.Console(text_color='g',font_size=12.,border_color='g'))
        #console.write('lkjasdfkljasf')

        self._render_particles()
        scene.visuals.XYZAxis(parent=self.view.scene)

        if hasattr(self,'cube_settings'):
            self.cube = scene.visuals.Box(self.cube_settings['cube_size'][0],
                                          self.cube_settings['cube_size'][1],
                                          self.cube_settings['cube_size'][2],
                                          color= self.cube_settings['cube_color'],
                                          edge_color = self.cube_settings['edge_color'],
                                          parent = self.view.scene)
            self.cube.color = self.cube_settings['cube_color']
        self.canvas.connect(self.on_key_press)
        app.run()


    def __iter__(self):
        for p in self.particle_items:
            yield p
        self.canvas.update()

    def on_key_press(self, event):
        if event.text.upper() == '+':
            print ("Increasing scale")
            for p in self:
                p['u_radius_scale'] *= 2
        elif event.text.upper() == '-':
            print ("Decreasing scale")
            for p in self:
                p['u_radius_scale'] /= 2
