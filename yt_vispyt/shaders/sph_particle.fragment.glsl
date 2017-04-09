varying vec4 color;
varying float kernel;
void main(){
    gl_FragColor = color;

    //poor man's anti aliasing
    vec2 circCoord = 2.0 * gl_PointCoord - 1.0;
    float r = dot(circCoord, circCoord);
    
    if (r > 1.0) {
        discard;
    }

    //poor man's kernel smoothing
    if(kernel > 0){
        float c = 0.5;
        float a = 0.1;
        float b = 0.0;
        gl_FragColor.a *= a * exp( -1.0 * (r-b)*(r-b) / (2.0 * c*c));
    }
    //gl_FragColor.a = 1.0;
}
