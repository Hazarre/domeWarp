
#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

#define PROCESSING_TEXTURE_SHADER

attribute vec4 position;
uniform sampler2D texture;

void main(void) {
  vec3 col = texture2D(texture, position.xy).xyz;
  gl_FragColor = vec4(col, 1.0);
}
