attribute float a_kernel;
attribute float a_density;
attribute float a_radius;
attribute vec3 a_position;
attribute vec4 a_color;

uniform float u_radius_scale;
varying vec4 color;
varying float kernel;
void main(void){
    vec4 visual_pos = vec4(a_position, 1);
    vec4 doc_pos    = $visual_to_doc(visual_pos);
    gl_Position     = $doc_to_render(doc_pos);
    // To compute the pointsize, we figure out what corresponds to the right
    // radius from the visual frame, in the render frame.  To do that, we first
    // offset by some value in the visual coordinates, then work that through
    // to the end, and then get the distance between the two points.
    vec4 extend_direction = $itrans(vec4(1.0, 1.0, 0.0, 0.0));
    vec4 edge = visual_pos + normalize(extend_direction)*a_radius*u_radius_scale;
    vec4 ren_edge = $visual_to_doc(edge);
    gl_PointSize    = distance(ren_edge.xy, doc_pos.xy) / doc_pos.w;
    color           = a_color;
    kernel          = a_kernel;
}
