var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

var renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);


const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 5, 0);
controls.update();

var MAX_LEN = 25;
var cubes = [];
var x, y, z;
var geometry = new THREE.BoxGeometry(0.001, 0.001, 0.001);
var geometry1 = new THREE.BoxGeometry(0.05, 0.05, 0.05);
var geometry2 = new THREE.BoxGeometry(0.1, 0.1, 0.1);

var geometry_arr = [geometry, geometry1, geometry2];

var material = new THREE.MeshBasicMaterial({
  color: 0x0022aa
});

var LAYERS = 50;

camera.position.x = MAX_LEN / 2;
camera.position.y = MAX_LEN / 2;
camera.position.z = 75;
for (z = 0; z < LAYERS; z++) {
  var layer_distance = Math.random();
  for (x = 0; x < MAX_LEN; x++) {
    for (y = 0; y < MAX_LEN; y++) {
      number = (z * (x * MAX_LEN) + y); 
      cube = new THREE.Mesh(geometry, material);
      cubes.push(cube);
      scene.add(cubes[number]);
      cubes[number].position.x = x; 
      cubes[number].position.y = y; 
      cubes[number].position.z = z + (z * layer_distance);
      }
    }
  }

  var change = 0.1;
  camera.lookAt(MAX_LEN / 2, 0, 0);



  var animate = function() {
    requestAnimationFrame(animate);
    for (z = 0; z < LAYERS; z++) {
      for (x = 0; x < MAX_LEN; x++) {
        g = Math.floor(Math.random() * 3);
        for (y = 0; y < MAX_LEN; y++) {
          number = z * (x * MAX_LEN) + y;
          cubes[number].geometry = geometry_arr[g];
 //         cubes[number].rotation.x += 0.01;
 //         cubes[number].rotation.y += 0.01;
          //    cubes[number].position.z = Math.floor(Math.random() * 4);

        }
      }
    }
    if (camera.position.x > 10) change = -0.1;
    if (camera.position.x < -10) change = 0.1;
    camera.position.x = camera.position.x + change;




    renderer.render(scene, camera);
  };

  animate();