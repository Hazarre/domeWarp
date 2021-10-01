  
PImage tex;
PShader deform;

void setup() {
  size(640, 360, P2D);
  tex = loadImage("CircularMesh.jpg");
  deform = loadShader("texvert.glsl","texfrag.glsl");
  deform.set("resolution", float(width), float(height));
}

void draw() {
  shader(deform);
  image(tex, 0, 0, width, height);
}
