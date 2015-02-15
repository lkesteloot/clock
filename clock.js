
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

// Simulate the motion of the escapement.
var escapedTime = function (time) {
    var integer = Math.floor(time);
    var fraction = time - integer;

    // Move for the last 1/16 of a second because of the escapement.
    fraction = Math.max(0, fraction*16 - 15);

    return integer + fraction;
};

var keydown = function (event) {
    // Minute hand goes around in one minute instead of one hour.
    if (event.keyCode === 49) { // "1"
        g_sim_speed = 60;
    } else if (event.keyCode === 50) { // "2"
        g_sim_speed = 60*12;
    }
    window.removeEventListener("keydown", keydown);
};

var keyup = function (event) {
    g_sim_speed = 1;
    window.addEventListener("keydown", keydown, false);
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

var startRendering = function (data) {
    var pieces = data.pieces;

    var scene = new THREE.Scene();

    var renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    window.addEventListener("keydown", keydown, false);
    window.addEventListener("keyup", keyup, false);

    // Each object has two keys:
    //    object3d: the THREE.Object3D object.
    //    piece: the piece (gear, axle, etc.).
    var objects = [];

    // List of holes we've seen. Each item is an object with keys:
    //    x, y: center of holes.
    //    r: smallest radius we've seen.
    //    type: "axle".
    //    attachedTo: piece we're stuck to.
    //    speed: speed of gear with a matching radius.
    // Duplicate (x,y) are removed.
    var holes = [];

    // Lowest and highest plane.
    var maxPlane = -100000;
    var minPlane = 100000;

    // Draw each gear.
    for (var gear_index in pieces) {
        var gear = pieces[gear_index];
        var points = gear.points;
        var cx = gear.cx;
        var cy = -gear.cy;
        var plane = gear.plane*data.material_thickness;

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

            minPlane = Math.min(minPlane, plane);
            maxPlane = Math.max(maxPlane, plane);
        }

        if (gear.bind) {
            for (var i = 0; i < gear.bind.centers.length; i++) {
                var center = gear.bind.centers[i];
                addCylinder(center[0], center[1], 0, data.material_thickness,
                            gear.bind.hole_radius, 20, material, gearObject);
            }
        }

        // Make a parent gear object for all three.
        gearObject.position.x = cx;
        gearObject.position.y = cy;
        gearObject.position.z = plane;

        scene.add(gearObject);
        objects.push({
            object3d: gearObject,
            piece: gear
        });
    }

    // Create axles.
    var material = new THREE.LineBasicMaterial({ color: "#222222" });
    for (var i = 0; i < holes.length; i++) {
        var hole = holes[i];

        var axle = new THREE.Object3D();
        addCylinder(0, 0, minPlane - 60, maxPlane + 80, hole.r, 20, material, axle);
        axle.position.x = hole.x;
        axle.position.y = hole.y;
        axle.position.z = 0;
        scene.add(axle);
        objects.push({
            object3d: axle,
            piece: hole
        });
    }

    // Create our camera.
    var centerOfScene = new THREE.Vector3(1100, -400, 0);
    var camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 10, 10000);
    camera.position.x = centerOfScene.x + 1300;
    camera.position.y = centerOfScene.y + 1300;
    camera.position.z = centerOfScene.z + 1300;
    camera.lookAt(centerOfScene);

    // Create the trackball controller.
    var controls = new THREE.TrackballControls(camera);

    controls.rotateSpeed = 1.0;
    controls.zoomSpeed = 1.2;
    controls.panSpeed = 0.8;
    controls.noZoom = false;
    controls.noPan = false;
    controls.staticMoving = true;
    controls.dynamicDampingFactor = 0.3;
    controls.keys = [ 65, 83, 68 ];

    controls.setTarget(centerOfScene);

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
        for (var object_index in objects) {
            var object = objects[object_index];
            var piece = object.piece;
            var object3d = object.object3d;
            var theta;

            // Turn with the piece we're attached to.
            if (piece.type === "axle") {
                piece = piece.attachedTo;
            }

            if (piece.type === "verge") {
                // Map two seconds to TAU (one cycle), then Sine that, map to 0 to 1.
                var span = Math.sin(g_time/2*TAU)/2 + 0.5;
                span /= 2;
                var left_full_in_angle = piece.left_full_in_angle*TAU/360;
                var right_full_in_angle = piece.right_full_in_angle*TAU/360;
                theta = span*(left_full_in_angle - right_full_in_angle) + right_full_in_angle;
            } else {
                // 43200 = 12 hours' worth of seconds.
                theta = escapedTime(g_time) * TAU / 43200 * piece.speed;
            }

            // Negate theta because our Y is upside down.
            object3d.rotation.z = -theta;
        }

        // Update camera position.
        controls.update();

        // Keep camera pointing up so we don't get disoriented.
        camera.up = new THREE.Vector3(0, 1, 0);

        // Render the scene.
        renderer.render(scene, camera);
    };

    var onWindowResize = function () {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        controls.handleResize();
    };
    window.addEventListener("resize", onWindowResize, false);

    render();
};

$(function () {
    $.getJSON("clock.json", function (data) {
        startRendering(data);
    });
});

})();
