class Sphere {
  //parent class of Object and PlayerBall
  PVector position;
  float radius = 10;
  
  Sphere(float x, float y, float z, float r){
    position = new PVector(x,y,z);
    radius = r;
  }
  
  void display() {
      pushMatrix();
      translate(position.x, position.y, position.z);
      noFill();
      stroke(255);
      sphere(radius);  
      popMatrix();
  }
  
  boolean onSphere(PVector v) {
    return (abs(sq(position.x-v.x)+sq(position.y-v.y)+sq(position.z-v.z) - sq(radius)) < 0.01);
  }
}
