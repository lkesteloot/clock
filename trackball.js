/**
 * Adds trackball controls to Three.js.
 *
 * Originally based on TrackballControls by Eberhard Graether and Mark Lundin.
 */

(function () {

var STATE = {
    NONE: -1,
    ROTATE: 0,
    ZOOM: 1,
    PAN: 2,
    TOUCH_ROTATE: 3,
    TOUCH_ZOOM_PAN: 4
};

var EPS = 0.000001;

// Events.
var CHANGE_EVENT = { type: 'change' };
var START_EVENT = { type: 'start'};
var END_EVENT = { type: 'end'};

// Constructor. The domElement is optional.
THREE.Trackball = function (camera, domElement) {
    this._camera = camera;
    this._domElement = (domElement !== undefined) ? domElement : document;

    // Public API.

    this.enabled = true;

    this.screen = {
        left: 0,
        top: 0,
        width: 0,
        height: 0
    };

    this.rotateSpeed = 2.5;
    this.zoomSpeed = 1.2;
    this.panSpeed = 0.8;

    this.allowRotate = true;
    this.allowZoom = true;
    this.allowPan = true;

    this.minDistance = 0;
    this.maxDistance = Infinity;

    // Private.
    this._target = new THREE.Vector3();

    this._lastPosition = new THREE.Vector3();

    this._state = STATE.NONE;

    // Which keys are pressed, by key code.
    this._keyPressed = {};

    this._eye = new THREE.Vector3();

    this._rotateStart = new THREE.Vector2();
    this._rotateEnd = new THREE.Vector2();

    this._zoomStart = new THREE.Vector2();
    this._zoomEnd = new THREE.Vector2();

    this._touchZoomDistanceStart = 0;
    this._touchZoomDistanceEnd = 0;

    this._panStart = new THREE.Vector2();
    this._panEnd = new THREE.Vector2();

    // For reset.

    this._target0 = this._target.clone();
    this._position0 = this._camera.position.clone();
    this._up0 = this._camera.up.clone();

    // Disable right-click menu so we can use it to move the camera.
    this._domElement.addEventListener('contextmenu', function (event) {
        event.preventDefault();
    }, false);

    // Capture mouse clicks.
    this._domElement.addEventListener('mousedown', this._onMouseDown.bind(this), false);
    this._onMouseMoveFunc = this._onMouseMove.bind(this);
    this._onMouseUpFunc = this._onMouseUp.bind(this);

    // Capture mouse wheel moves.
    this._domElement.addEventListener('mousewheel', this._onMouseWheel.bind(this), false);
    this._domElement.addEventListener('DOMMouseScroll', this._onMouseWheel.bind(this), false); // Firefox

    // Capture touch screen taps.
    this._domElement.addEventListener('touchstart', this._onTouchStart.bind(this), false);
    this._domElement.addEventListener('touchend', this._onTouchEnd.bind(this), false);
    this._domElement.addEventListener('touchmove', this._onTouchMove.bind(this), false);

    // Capture keyboard presses.
    this._onKeyDownFunc = this._onKeyDown.bind(this);
    window.addEventListener('keydown', this._onKeyDownFunc, false);
    window.addEventListener('keyup', this._onKeyUp.bind(this), false);

    // Figure our the size of our window.
    this.handleResize();

    // Force an update at start.
    this.update();
};

THREE.Trackball.prototype = Object.create(THREE.EventDispatcher.prototype);

THREE.Trackball.prototype._getKeyboardState = function () {
    var state;

    // Space bar to pan, like Photoshop.
    if (this._keyPressed[32] && this.allowPan) {
        state = STATE.PAN;
    } else {
        state = STATE.NONE;
    }

    return state;
};

// Client must call this when the window is resized.
THREE.Trackball.prototype.handleResize = function () {
    if (this._domElement === document) {
        this.screen.left = 0;
        this.screen.top = 0;
        this.screen.width = window.innerWidth;
        this.screen.height = window.innerHeight;
    } else {
        var box = this._domElement.getBoundingClientRect();
        // adjustments come from similar code in the jquery offset() function
        var d = this._domElement.ownerDocument.documentElement;
        this.screen.left = box.left + window.pageXOffset - d.clientLeft;
        this.screen.top = box.top + window.pageYOffset - d.clientTop;
        this.screen.width = box.width;
        this.screen.height = box.height;
    }
};

THREE.Trackball.prototype.handleEvent = function (event) {
    if (typeof this[event.type] == 'function') {
        this[event.type](event);
    }
};

THREE.Trackball.prototype._getMouseOnScreen = function (pageX, pageY) {
    var vector = new THREE.Vector2();

    vector.set(
        (pageX - this.screen.left) / this.screen.width,
        (pageY - this.screen.top) / this.screen.height
    );

    return vector;
};

THREE.Trackball.prototype._rotateCamera = function () {
    var angleX = this._rotateEnd.x - this._rotateStart.x;
    var angleY = this._rotateEnd.y - this._rotateStart.y;

    if (angleX !== 0 || angleY !== 0) {
        var up = new THREE.Vector3(),
            right = new THREE.Vector3(),
            quaternion = new THREE.Quaternion();

        up.set(0, 1, 0);

        angleX *= this.rotateSpeed;
        quaternion.setFromAxisAngle(up, -angleX);
        this._eye.applyQuaternion(quaternion);
        this._camera.up.applyQuaternion(quaternion);

        angleY *= this.rotateSpeed;
        right.copy(this._eye).cross(up).normalize();
        quaternion.setFromAxisAngle(right, angleY);
        this._eye.applyQuaternion(quaternion);
        this._camera.up.applyQuaternion(quaternion);

        this._rotateStart.copy(this._rotateEnd);
    }
};

THREE.Trackball.prototype._zoomCamera = function () {
    if (this._state === STATE.TOUCH_ZOOM_PAN) {
        var factor = this._touchZoomDistanceStart / this._touchZoomDistanceEnd;
        this._touchZoomDistanceStart = this._touchZoomDistanceEnd;
        this._eye.multiplyScalar(factor);
    } else {
        var factor = 1.0 + (this._zoomEnd.y - this._zoomStart.y) * this.zoomSpeed;

        if (factor !== 1.0 && factor > 0.0) {
            this._eye.multiplyScalar(factor);

            this._zoomStart.copy(this._zoomEnd);
        }
    }
};

THREE.Trackball.prototype._panCamera = function() {
    var mouseChange = new THREE.Vector2(),
        objectUp = new THREE.Vector3(),
        pan = new THREE.Vector3();

    mouseChange.copy(this._panEnd).sub(this._panStart);

    if (mouseChange.lengthSq()) {
        mouseChange.multiplyScalar(this._eye.length() * this.panSpeed);

        pan.copy(this._eye).cross(this._camera.up).setLength(mouseChange.x);
        pan.add(objectUp.copy(this._camera.up).setLength(mouseChange.y));

        this._camera.position.add(pan);
        this._target.add(pan);

        this._panStart.copy(this._panEnd);
    }
};

/**
 * Make sure the distance to the point of interest is within permitted bounds.
 */
THREE.Trackball.prototype._checkDistances = function () {
    if (this.allowZoom || this.allowPan) {
        if (this._eye.lengthSq() > this.maxDistance * this.maxDistance) {
            this._camera.position.addVectors(this._target, this._eye.setLength(this.maxDistance));
        }

        if (this._eye.lengthSq() < this.minDistance * this.minDistance) {
            this._camera.position.addVectors(this._target, this._eye.setLength(this.minDistance));
        }
    }
};

/**
 * Update the position of the camera based on input.
 */
THREE.Trackball.prototype.update = function () {
    this._eye.subVectors(this._camera.position, this._target);

    if (this.allowRotate) {
        this._rotateCamera();
    }

    if (this.allowZoom) {
        this._zoomCamera();
    }

    if (this.allowPan) {
        this._panCamera();
    }

    this._camera.position.addVectors(this._target, this._eye);
    this._checkDistances();
    this._camera.lookAt(this._target);

    // Dispatch change event if we've moved.
    if (this._lastPosition.distanceToSquared(this._camera.position) > EPS) {
        this.dispatchEvent(CHANGE_EVENT);

        this._lastPosition.copy(this._camera.position);
    }
};

/**
 * Reset all values to their original values.
 */
THREE.Trackball.prototype.reset = function () {
    this._state = STATE.NONE;
    this._keyPressed = {};

    this._target.copy(this._target0);
    this._camera.position.copy(this._position0);
    this._camera.up.copy(this._up0);

    this._eye.subVectors(this._camera.position, this._target);

    this._camera.lookAt(this._target);

    this.dispatchEvent(CHANGE_EVENT);

    this._lastPosition.copy(this._camera.position);
};

/**
 * Set the point where we're looking.
 */
THREE.Trackball.prototype.setTarget = function (newTarget) {
    this._target0.copy(newTarget);
    this.reset();
};

// Listeners.

THREE.Trackball.prototype._onKeyDown = function (event) {
    if (this.enabled) {
        // Avoid listening to key repeats.
        window.removeEventListener('keydown', this._onKeyDownFunc);

        this._keyPressed[event.keyCode] = true;
    }
};

THREE.Trackball.prototype._onKeyUp = function (event) {
    if (this.enabled) {
        this._keyPressed[event.keyCode] = false;

        window.addEventListener('keydown', this._onKeyDownFunc, false);
    }
};

THREE.Trackball.prototype._onMouseDown = function (event) {
    if (this.enabled) {
        event.preventDefault();
        event.stopPropagation();

        var keyboardState = this._getKeyboardState();
        if (keyboardState === STATE.NONE) {
            this._state = event.button;
        } else {
            this._state = keyboardState;
        }

        if (this._state === STATE.ROTATE && this.allowRotate) {
            this._rotateStart.copy(this._getMouseOnScreen(event.pageX, event.pageY));
            this._rotateEnd.copy(this._rotateStart);
        } else if (this._state === STATE.ZOOM && this.allowZoom) {
            this._zoomStart.copy(this._getMouseOnScreen(event.pageX, event.pageY));
            this._zoomEnd.copy(this._zoomStart);
        } else if (this._state === STATE.PAN && this.allowPan) {
            this._panStart.copy(this._getMouseOnScreen(event.pageX, event.pageY));
            this._panEnd.copy(this._panStart)
        }

        document.addEventListener('mousemove', this._onMouseMoveFunc, false);
        document.addEventListener('mouseup', this._onMouseUpFunc, false);

        this.dispatchEvent(START_EVENT);
    }
};

THREE.Trackball.prototype._onMouseMove = function (event) {
    if (this.enabled) {
        event.preventDefault();
        event.stopPropagation();

        if (this._state === STATE.ROTATE && this.allowRotate) {
            this._rotateEnd.copy(this._getMouseOnScreen(event.pageX, event.pageY));
        } else if (this._state === STATE.ZOOM && this.allowZoom) {
            this._zoomEnd.copy(this._getMouseOnScreen(event.pageX, event.pageY));
        } else if (this._state === STATE.PAN && this.allowPan) {
            this._panEnd.copy(this._getMouseOnScreen(event.pageX, event.pageY));
        }
    }
};

THREE.Trackball.prototype._onMouseUp = function (event) {
    if (this.enabled) {
        event.preventDefault();
        event.stopPropagation();

        this._state = STATE.NONE;

        document.removeEventListener('mousemove', this._onMouseMoveFunc);
        document.removeEventListener('mouseup', this._onMouseUpFunc);
        this.dispatchEvent(END_EVENT);
    }
};

THREE.Trackball.prototype._onMouseWheel = function (event) {
    if (this.enabled) {
        event.preventDefault();
        event.stopPropagation();

        var delta = 0;

        if (event.wheelDelta) { // WebKit / Opera / Explorer 9
            delta = event.wheelDelta / 40;
        } else if (event.detail) { // Firefox
            delta = -event.detail / 3;
        }

        this._zoomStart.y += delta * 0.01;
        this.dispatchEvent(START_EVENT);
        this.dispatchEvent(END_EVENT);
    }
};

THREE.Trackball.prototype._onTouchStart = function (event) {
    if (this.enabled) {
        switch (event.touches.length) {
            case 1:
                this._state = STATE.TOUCH_ROTATE;
                this._rotateStart.copy(this._getMouseOnScreen(event.touches[0].pageX, event.touches[0].pageY));
                this._rotateEnd.copy(this._rotateStart);
                break;

            case 2:
                this._state = STATE.TOUCH_ZOOM_PAN;
                var dx = event.touches[0].pageX - event.touches[1].pageX;
                var dy = event.touches[0].pageY - event.touches[1].pageY;
                this._touchZoomDistanceEnd = this._touchZoomDistanceStart = Math.sqrt(dx*dx + dy*dy);

                var x = (event.touches[0].pageX + event.touches[1].pageX) / 2;
                var y = (event.touches[0].pageY + event.touches[1].pageY) / 2;
                this._panStart.copy(this._getMouseOnScreen(x, y));
                this._panEnd.copy(this._panStart);
                break;

            default:
                this._state = STATE.NONE;
        }

        this.dispatchEvent(START_EVENT);
    }
};

THREE.Trackball.prototype._onTouchMove = function (event) {
    if (this.enabled) {
        event.preventDefault();
        event.stopPropagation();

        switch (event.touches.length) {
            case 1:
                this._rotateEnd.copy(this._getMouseOnScreen(event.touches[0].pageX, event.touches[0].pageY));
                break;

            case 2:
                var dx = event.touches[0].pageX - event.touches[1].pageX;
                var dy = event.touches[0].pageY - event.touches[1].pageY;
                this._touchZoomDistanceEnd = Math.sqrt(dx * dx + dy * dy);

                var x = (event.touches[0].pageX + event.touches[1].pageX) / 2;
                var y = (event.touches[0].pageY + event.touches[1].pageY) / 2;
                this._panEnd.copy(this._getMouseOnScreen(x, y));
                break;

            default:
                this._state = STATE.NONE;
        }
    }
};

THREE.Trackball.prototype._onTouchEnd = function (event) {
    if (this.enabled) {
        switch (event.touches.length) {
            case 1:
                this._rotateEnd.copy(this._getMouseOnScreen(event.touches[0].pageX, event.touches[0].pageY));
                this._rotateStart.copy(this._rotateEnd);
                break;

            case 2:
                this._touchZoomDistanceStart = this._touchZoomDistanceEnd = 0;

                var x = (event.touches[0].pageX + event.touches[1].pageX) / 2;
                var y = (event.touches[0].pageY + event.touches[1].pageY) / 2;
                this._panEnd.copy(this._getMouseOnScreen(x, y));
                this._panStart.copy(this._panEnd);
                break;
        }

        this._state = STATE.NONE;
        this.dispatchEvent(END_EVENT);
    }
};

})();
