
//   Copyright 2015 Lawrence Kesteloot
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.

(function () {

var TAU = 2*Math.PI;

// For keeping track of simulation time.
var g_time = 0.0;
var g_sim_speed = 1.0;
var g_previous_date = null;

// Globals for the scene.
var g_scene = null;
var g_objects = [];

// Simulate the motion of the escapement.
var escapedTime = function (time) {
    var integer = Math.floor(time);
    var fraction = time - integer;

    // Move for the last 1/16 of a second because of the escapement.
    fraction = Math.max(0, fraction*16 - 15);

    return integer + fraction;
};

var onKeyDown = function (event) {
    // Minute hand goes around in one minute instead of one hour.
    if (event.keyCode === 48) { // "0"
        g_sim_speed = 0;
    } else if (event.keyCode === 49) { // "1"
        g_sim_speed = 1;
    } else if (event.keyCode === 50) { // "2"
        g_sim_speed = 60;
    } else if (event.keyCode === 51) { // "3"
        g_sim_speed = 60*12;
    } else if (event.keyCode === 82) { // "r"
        // Reload.
        console.log("Reloading");
        fetchData();
    } else {
        /// console.log(event.keyCode);
    }
    window.removeEventListener("keydown", onKeyDown);
};

var onKeyUp = function (event) {
    window.addEventListener("keydown", onKeyDown, false);
};

var closeEnough = function (a, b) {
    return Math.abs(a - b) < 0.0001;
};

var addCylinder = function (cx, cy, z1, z2, r, facets, material, parent) {
    var geometry1 = new THREE.Geometry();
    var geometry2 = new THREE.Geometry();
    var geometry3 = new THREE.Geometry();

    for (var i = 0; i <= facets; i++) {
        var t = i/facets*TAU;
        var x = cx + Math.sin(t)*r;
        var y = cy + Math.cos(t)*r;
        geometry1.vertices.push(new THREE.Vector3(x, y, z1));
        geometry2.vertices.push(new THREE.Vector3(x, y, z2));
        geometry3.vertices.push(new THREE.Vector3(x, y, z1));
        geometry3.vertices.push(new THREE.Vector3(x, y, z2));
    }

    parent.add(new THREE.Line(geometry1, material, THREE.LineStrip));
    parent.add(new THREE.Line(geometry2, material, THREE.LineStrip));
    parent.add(new THREE.Line(geometry3, material, THREE.LinePieces));
};

var findHole = function (holes, x, y) {
    for (var i = 0; i < holes.length; i++) {
        var hole = holes[i];
        if (closeEnough(hole.x, x) && closeEnough(hole.y, y)) {
            return hole;
        }
    }

    return null;
}

var initializeThree = function () {
    var renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    g_scene = new THREE.Scene();

    window.addEventListener("keydown", onKeyDown, false);
    window.addEventListener("keyup", onKeyUp, false);

    // Create our camera.
    var centerOfScene = new THREE.Vector3(1100, -400, 0);
    var camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 10, 10000);
    camera.position.x = centerOfScene.x + 1300;
    camera.position.y = centerOfScene.y + 1300;
    camera.position.z = centerOfScene.z + 1300;
    camera.lookAt(centerOfScene);

    // Create the trackball controller.
    var controls = new THREE.Trackball(camera);
    controls.setTarget(centerOfScene);

    var onWindowResize = function () {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        controls.handleResize();
    };
    window.addEventListener("resize", onWindowResize, false);

    var render = function () {
        requestAnimationFrame(render);

        // Advance time.
        var now = new Date();
        if (g_previous_date !== null) {
            var millis = now - g_previous_date;
            g_time += millis * g_sim_speed / 1000;
        }
        g_previous_date = now;

        // Rotate the gears.
        for (var object_index in g_objects) {
            var object = g_objects[object_index];
            var piece = object.piece;
            var object3d = object.object3d;
            var theta;

            if (piece.type === "verge" || piece.type === "pendulum") {
                // Map two seconds to TAU (one cycle), then Sine that, map to 0 to 1.
                var span = Math.sin(g_time/2*TAU + 0.6)/2 + 0.5;
                var left_full_in_angle = piece.left_full_in_angle*TAU/360;
                var right_full_in_angle = piece.right_full_in_angle*TAU/360;
                theta = span*(left_full_in_angle - right_full_in_angle) + right_full_in_angle;
            } else if (piece.type === "axle") {
                // Axles don't turn.
                theta = 0;
            } else {
                // 43200 = 12 hours' worth of seconds. The 0.4 adjustment is so
                // that the verge matches up with the escapement wheel.
                theta = (escapedTime(g_time) - 0.4) * TAU / 43200 * piece.speed;
            }

            // Negate theta because our Y is upside down.
            object3d.rotation.z = -theta;
        }

        // Update camera position.
        controls.update();

        // Render the scene.
        renderer.render(g_scene, camera);
    };

    render();
};

var startRendering = function (data) {
    var pieces = data.pieces;

    // New scene.
    g_scene = new THREE.Scene();

    // Each object has two keys:
    //    object3d: the THREE.Object3D object.
    //    piece: the piece (gear, axle, etc.).
    g_objects = [];

    // List of holes we've seen. Each item is an object with keys:
    //    x, y: center of holes.
    //    r: smallest radius we've seen.
    //    type: "axle".
    //    attachedTo: piece we're stuck to.
    //    speed: speed of gear with a matching radius.
    // Duplicate (x,y) are removed.
    var holes = [];

    // Lowest and highest Z value.
    var maxZ = -100000;
    var minZ = 100000;

    // Draw each gear.
    for (var gear_index in pieces) {
        var gear = pieces[gear_index];
        var points = gear.points;
        var cx = gear.cx;
        var cy = -gear.cy;
        var cz = gear.cz*data.material_thickness;

        // Create geometry.
        var material = new THREE.LineBasicMaterial({ color: gear.color });
        var gearObject = new THREE.Object3D();

        var geometry1 = new THREE.Geometry();
        var geometry2 = new THREE.Geometry();
        var geometry3 = new THREE.Geometry();
        for (var i = 0; i < points.length; i++) {
            var x = points[i][0];
            var y = points[i][1];
            geometry1.vertices.push(new THREE.Vector3(x, -y, 0));
            geometry2.vertices.push(new THREE.Vector3(x, -y, data.material_thickness));
            geometry3.vertices.push(new THREE.Vector3(x, -y, 0));
            geometry3.vertices.push(new THREE.Vector3(x, -y, data.material_thickness));
        }
        gearObject.add(new THREE.Line(geometry1, material, THREE.LineStrip));
        gearObject.add(new THREE.Line(geometry2, material, THREE.LineStrip));
        gearObject.add(new THREE.Line(geometry3, material, THREE.LinePieces));

        if (gear.hole_radius) {
            addCylinder(0, 0, 0, data.material_thickness, gear.hole_radius, 20, material, gearObject);

            // Find a hole with this center.
            var hole = findHole(holes, cx, cy);
            if (hole === null) {
                // Not found.
                holes.push({
                    x: cx,
                    y: cy,
                    r: gear.hole_radius,
                    type: "axle",
                    attachedTo: gear,
                    speed: gear.speed
                });
            } else if (gear.hole_radius < hole.r) {
                // Keep track of smallest hole -- that's the axle radius.
                hole.r = gear.hole_radius;
                hole.speed = gear.speed;
                hole.attachedTo = gear;
            }

            minZ = Math.min(minZ, cz);
            maxZ = Math.max(maxZ, cz);
        }

        if (gear.bind) {
            for (var i = 0; i < gear.bind.centers.length; i++) {
                var center = gear.bind.centers[i];
                addCylinder(center[0], center[1], 0, data.material_thickness,
                            gear.bind.hole_radius, 20, material, gearObject);
            }
        }
        if (gear.holes) {
            for (var i = 0; i < gear.holes.length; i++) {
                var hole = gear.holes[i];
                addCylinder(hole.cx, -hole.cy, 0, data.material_thickness,
                            hole.r, 20, material, gearObject);
            }
        }

        // Make a parent gear object for all three.
        gearObject.position.x = cx;
        gearObject.position.y = cy;
        gearObject.position.z = cz;

        g_scene.add(gearObject);
        g_objects.push({
            object3d: gearObject,
            piece: gear
        });
    }

    // Create axles.
    var material = new THREE.LineBasicMaterial({ color: "#222222" });
    for (var i = 0; i < holes.length; i++) {
        var hole = holes[i];

        var axle = new THREE.Object3D();
        addCylinder(0, 0, minZ - 60, maxZ + 80, data.large_bolt_radius, 20, material, axle);
        axle.position.x = hole.x;
        axle.position.y = hole.y;
        axle.position.z = 0;
        g_scene.add(axle);
        g_objects.push({
            object3d: axle,
            piece: hole
        });
    }
};

// Fetch the JSON data from the net and display it.
var fetchData = function () {
    $.getJSON("clock.json", function (data) {
        startRendering(data);
    });
};

$(function () {
    initializeThree();
    fetchData();
});

})();
