//initialize
float R = 150.0; //dome radius
float r = 33.0;  // spherical mirror radius

float dx = 0.0;// dome coordinate
float dy = 0.0;
float dz = R;

float mx = 0.0;
float my = -18*cos( 70*PI/180 - atan(8.3/13.8) );
float mz = -18*sin( 70*PI/180 - atan(8.3/13.8) );

float px = 0.0;
float py = -20.0; 
float pz = 75.0;

// projection center
float cx = 0.0;
float cy = 0.0;
float cz = 0.0;

Sphere dome, mirror, p, c; 
PVector mirVect;

PVector projector;
PVector projCenter;
PVector projectingVect;
float projectorThrow = 2.2;
float aspect = 4.0/3.0;
float projectionDepth;

PVector imgCenter;
PImage img, imgWarped;
int ix = 499;
int iy = 499;
PVector x0, x1,x2,x3,x4,x5, distorted; 

float leftRight ;
float upDown ;
float zoom = 6;

int maxX = -1;
int maxY = -1;
int minX = 10000;
int minY = 10000;
int[] mapX ;
int[] mapY ;

PVector onDome, onMirror;
void setup() {
  img = loadImage("CircularMesh.jpg");
  img.loadPixels();
  dome = new Sphere(dx, dy, dz, R);
  mirror = new Sphere(mx, my, mz, r);
  mirVect = new PVector(mx,my,mz);
  imgWarped = createImage(img.width,img.height,RGB);
  imgWarped.loadPixels();
  
  projCenter = new PVector(cx, cy, cz);
  projector = new PVector(px, py, pz);
  projectingVect = PVector.sub(projCenter, projector);
  projectionDepth = img.width * projectorThrow;
  
  mapX = new int[img.width*img.height];
  mapY = new int[img.width*img.height];
  
   
  //for (int i = 0; i < img.width; i++) for(int j = 0; j < img.height; j++){
  //  onMirror = imagePlaneToMirror(pixelToImagePlane(i,j));
  //  if(onMirror.z < mirVect.z) println("mirror method failed");
  //  onDome = mirrorToDome(onMirror);
  //  if(onDome.y > 0) {
  //    distorted = circleToPixel(domeToCircle(onDome));
  //    distorted.sub(imgCenter);
  //    distorted.mult(2);
    
  //    mapX[j*img.width+i] = i;
  //    mapY[j*img.width+i] = j;
    
  //  int disx = int(distorted.x + img.width/2);
  //  int disy = int(distorted.z + img.height/2);
    
  //  if(disy*img.width+disx < img.width*img.height &&disy*img.width+disx>=0) imgWarped.pixels[j*img.width+i] = img.pixels[disy*img.width+disx]; 
  //  }
  //} 
  
  //imgWarped.updatePixels();
  //imgWarped.save("outputImage.jpg");
  size(640, 640, P3D);
}

void draw() {
  pushMatrix(); background(0); strokeWeight(1);
  camera(R*zoom, dy, R, 0.0, 0.0, R, 0, -1, 0);
  perspective(PI/2.0, 1.0, -1.0, 150.0);// face the mirror
  translate(0,0,150);
  rotateY(PI/180*leftRight);
  rotateZ(PI/180*upDown);
  rotateX(PI/6);
  if (keyPressed && key == 's') upDown++;
  if (keyPressed && key == 'w') upDown--;
  if (keyPressed && key == 'a') leftRight++;
  if (keyPressed && key == 'd') leftRight--;
  if (keyPressed && key == 'z') upDown=0;
  if (keyPressed && key == 'y') leftRight=90;
  if (keyPressed && key == '=') zoom -=0.1;
  if (keyPressed && key == '-') zoom +=0.1;
  translate(0,0,-150);
  mirror.display();
  //dome.display();
  
  // upside line
  line(0, 0, R, 0, R, R);
  
  //image 2D
  beginShape();
  //texture(img);
  stroke(0,255,255);
  fill(255,200);
  vertex(-img.width/2, 0, -img.height/2, 0, 0);
  vertex( -img.width/2, 0, img.height/2,500,0);
  vertex( img.width/2,  0, img.height/2,500,500);
  vertex(img.width/2, 0 , -img.height/2 ,0, 500);
  endShape(CLOSE);
   
   
  ////projection plane
  //textureMode(IMAGE);
  //translate(px,py,pz);
  //PVector nZ = new PVector(0,0,-1);
  //rotateX(+(PVector.angleBetween(nZ,projectingVect)));
  
  //beginShape();
  ////imgWarped.updatePixels();
  ////texture(imgWarped);
  //vertex( img.width/2, img.height/2, -projectionDepth,0,0 );
  //vertex( -img.width/2, img.height/2, -projectionDepth,500,0);
  //vertex( -img.width/2,  -img.height/2, -projectionDepth,500,500);
  //vertex( img.width/2,  -img.height/2, -projectionDepth,0,500);
  //endShape(CLOSE);
  //// projection Center Cross
  //stroke(0, 0, 255);
  //strokeWeight(4);
  //line(img.width/2, 0.0, -projectionDepth, -img.width/2, 0.0, -projectionDepth);
  //line(0.0, img.height/2,   -projectionDepth,0.0 , -img.height/2,  -projectionDepth);
  //translate(-px,-py,-pz);
  //rotateX(-(PVector.angleBetween(nZ,projectingVect)));
  

  
  
 
 
 
  int[] bounds = {img.width*3/4, img.height*3/4, 0,0,  img.width,0,  0,img.height,  img.width,img.height , img.width/2,img.height/2};
  for (int i = 0 ; i < bounds.length-1; i = i+2 ){
    x1 = pixelToImagePlane(bounds[i],bounds[i+1]);
    stroke(0, 250, 0);
    strokeWeight(8);
    point(x1.x, x1.y, x1.z);
    
    x2 = imagePlaneToDome(x1);
    stroke(255, 0, 0);
    strokeWeight(8);
    point(x2.x, x2.y, x2.z); // imagePlaneToMirror
  
    x3 = domeToMirror(x2);
    stroke(0, 0, 255);
    //strokeWeight(3);  
    //line(x2.x, x2.y, x2.z, x3.x, x3.y, x3.z);
    //strokeWeight(3);
    point(x3.x, x3.y, x3.z);
  
    //x4 = domeToCircle(x3);
    //stroke(255, 0, 255);
    //strokeWeight(3);
    //line(x4.x, x4.y, x4.z, x3.x, x3.y, x3.z);
    //strokeWeight(13);
    //point(x4.x, x4.y, x4.z); // Mirror To Dome
  
    //  x5 = circleToPixel(x4);
    
    //  //stroke(255, 255, 0);
    //  //strokeWeight(13);
    //  //point(x5.x, 0, x5.y);
  }

  
  //noLoop();
  popMatrix();
}

PVector pixelToImagePlane(int i, int j){
  PVector v = new PVector(img.width/2-i,0,-img.height/2+j);
  v.mult(2*R/sqrt(sq(img.width)+sq(img.height)));
  v.z += R;
  return v;
}

PVector imagePlaneToDome(PVector u){
  PVector v = u.copy();
  v.z -= R;
  float theta = atan2(v.z,v.x);
  float phi = PI*sqrt(v.x*v.x + v.z*v.z)/(2*R);
  v.y = abs(R*cos(phi));
  v.z = R*sin(phi)*sin(theta)+R;
  v.x = R*sin(phi)*cos(theta);
  return v;
}

PVector domeToMirror(PVector u){
  PVector i = PVector.sub(projector, mirVect);
  PVector o = PVector.sub(u, mirVect).setMag(i.mag());
  PVector n = PVector.add(i,o);
  n.setMag(r);
  //n.add(mirVect);
  
  PVector fi =  PVector.sub(projector,n);
  PVector fo =  PVector.sub(u,n);
  println(degrees(PVector.angleBetween(n,fi)),degrees(PVector.angleBetween(n,fo)));
  
  return n;
}

PVector domeToCircle(PVector u){
  // shift to origin
  PVector v = u.copy();
  v.z = v.z - R;
  PVector posY = new PVector(0,1,0);
  float phi = PVector.angleBetween(v, posY);
  v.y = 0;
  v.setMag(2*R*phi/PI);
  v.z = v.z + R;
  return v;
}

PVector circleToPixel(PVector u){
  // shift to origin
  PVector v = u.copy();
  v.z = v.z - R;
  // rotate about y-axis
  PVector l = v.copy();
  // x y coords are now becoming pixel i, v 
  v.x = l.x*cos(-PI/2) - l.z*sin(-PI/2);
  v.z = l.x*sin(-PI/2) + l.z*cos(-PI/2);
  //v.y = v.x;
  //v.x = v.z;
  //v.z = 0; 
  v.mult(img.height/(2*R));
  return v;
}
