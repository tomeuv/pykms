from __future__ import annotations

import ctypes
import math
import numpy as np
from OpenGL import GL as gl

def check_shader_compile(shader, shader_type):
    if gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
        error_log = gl.glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f'{shader_type} shader compilation failed:\n{error_log}')

def check_program_link(program):
    if gl.glGetProgramiv(program, gl.GL_LINK_STATUS) != gl.GL_TRUE:
        error_log = gl.glGetProgramInfoLog(program).decode()
        raise RuntimeError(f'Shader program linking failed:\n{error_log}')

def get_gl_string(name):
    s = gl.glGetString(name)
    if not s:
        return ''
    return s.decode()

class GlScene:
    def __init__(self):
        self.width = 0
        self.height = 0

        print(f'GL_VENDOR: {get_gl_string(gl.GL_VENDOR)}')
        print(f'GL_VERSION: {get_gl_string(gl.GL_VERSION)}')
        print(f'GL_RENDERER: {get_gl_string(gl.GL_RENDERER)}')

        self.program = self._create_program()
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)
        self.vbo = self._create_cube_buffer()

        self.rotation_x = gl.glGetUniformLocation(self.program, 'rotationX')
        self.rotation_y = gl.glGetUniformLocation(self.program, 'rotationY')
        self.rotation_z = gl.glGetUniformLocation(self.program, 'rotationZ')

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

    def cleanup(self):
        gl.glDeleteBuffers(1, [self.vbo])
        gl.glDeleteVertexArrays(1, [self.vao])
        gl.glDeleteProgram(self.program)

    def _create_cube_buffer(self) -> int:
        vertices = []

        corners = [
            (-1, -1, -1),  # 0: left  bottom back
            ( 1, -1, -1),  # 1: right bottom back
            (-1,  1, -1),  # 2: left  top    back
            ( 1,  1, -1),  # 3: right top    back
            (-1, -1,  1),  # 4: left  bottom front
            ( 1, -1,  1),  # 5: right bottom front
            (-1,  1,  1),  # 6: left  top    front
            ( 1,  1,  1),  # 7: right top    front
        ]

        colors = {
            'front':  (0.0, 0.0, 1.0),  # blue
            'back':   (1.0, 0.0, 0.0),  # red
            'right':  (1.0, 0.0, 1.0),  # magenta
            'left':   (0.0, 1.0, 0.0),  # green
            'top':    (0.0, 1.0, 1.0),  # cyan
            'bottom': (1.0, 1.0, 0.0),  # yellow
        }

        faces = [
            # face corner indices    color
            ((4, 5, 6, 7), colors['front']),  # front
            ((1, 0, 3, 2), colors['back']),   # back
            ((5, 1, 7, 3), colors['right']),  # right
            ((0, 4, 2, 6), colors['left']),   # left
            ((6, 7, 2, 3), colors['top']),    # top
            ((0, 1, 4, 5), colors['bottom']), # bottom
        ]

        # Generate vertices for each face
        for corner_indices, color in faces:
            # First triangle of face
            vertices.extend([*corners[corner_indices[0]], *color, 1.0])  # v0 pos + color
            vertices.extend([*corners[corner_indices[1]], *color, 1.0])  # v1 pos + color
            vertices.extend([*corners[corner_indices[2]], *color, 1.0])  # v2 pos + color

            # Second triangle of face
            vertices.extend([*corners[corner_indices[1]], *color, 1.0])  # v1 pos + color
            vertices.extend([*corners[corner_indices[3]], *color, 1.0])  # v3 pos + color
            vertices.extend([*corners[corner_indices[2]], *color, 1.0])  # v2 pos + color

        vertices = np.array(vertices, dtype=np.float32)

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        # Position attribute
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 7 * 4, None)
        gl.glEnableVertexAttribArray(0)

        # Color attribute
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, gl.GL_FALSE, 7 * 4, ctypes.c_void_p(3 * 4))
        gl.glEnableVertexAttribArray(1)

        return vbo

    def _create_program(self) -> int:
        vertex_shader = '''#version 100
        precision highp float;

        attribute vec3 position;
        attribute vec4 color;

        uniform mat4 projectionMatrix;
        uniform float rotationX;
        uniform float rotationY;
        uniform float rotationZ;

        varying vec4 vColor;

        // Rotation matrices
        mat4 rotateX(float angle) {
            float s = sin(angle);
            float c = cos(angle);
            return mat4(
                1.0, 0.0, 0.0, 0.0,
                0.0,   c,  -s, 0.0,
                0.0,   s,   c, 0.0,
                0.0, 0.0, 0.0, 1.0
            );
        }

        mat4 rotateY(float angle) {
            float s = sin(angle);
            float c = cos(angle);
            return mat4(
                  c, 0.0,   s, 0.0,
                0.0, 1.0, 0.0, 0.0,
                 -s, 0.0,   c, 0.0,
                0.0, 0.0, 0.0, 1.0
            );
        }

        mat4 rotateZ(float angle) {
            float s = sin(angle);
            float c = cos(angle);
            return mat4(
                  c,  -s, 0.0, 0.0,
                  s,   c, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0
            );
        }

        void main() {
            mat4 model = rotateZ(rotationZ) * rotateY(rotationY) * rotateX(rotationX);
            gl_Position = projectionMatrix * model * vec4(position, 1.0);
            vColor = color;
        }
        '''

        fragment_shader = '''#version 100
        precision mediump float;

        varying vec4 vColor;

        void main() {
            gl_FragColor = vColor;
        }
        '''

        # Compile vertex shader
        vs = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vs, vertex_shader)
        gl.glCompileShader(vs)
        check_shader_compile(vs, 'Vertex')

        # Compile fragment shader
        fs = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fs, fragment_shader)
        gl.glCompileShader(fs)
        check_shader_compile(fs, 'Fragment')

        # Create and link program
        program = gl.glCreateProgram()
        assert program
        gl.glAttachShader(program, vs)
        gl.glAttachShader(program, fs)
        gl.glLinkProgram(program)
        check_program_link(program)

        gl.glDeleteShader(vs)
        gl.glDeleteShader(fs)
        gl.glUseProgram(program)

        # Get uniform locations after linking
        self.rotation_x = gl.glGetUniformLocation(program, 'rotationX')
        self.rotation_y = gl.glGetUniformLocation(program, 'rotationY')
        self.rotation_z = gl.glGetUniformLocation(program, 'rotationZ')
        self.projection_matrix = gl.glGetUniformLocation(program, 'projectionMatrix')

        return program

    def set_viewport(self, width: int, height: int):
        self.width = width
        self.height = height
        gl.glViewport(0, 0, width, height)

        aspect = float(width) / float(height)

        # Manually create a perspective projection matrix
        fov = np.radians(45.0)  # 45-degree field of view
        near, far = 6.0, 10.0
        f = 1.0 / np.tan(fov / 2.0)

        projection = np.array([
            [f / aspect, 0,  0,  0],
            [0,  f,  0,  0],
            [0,  0, -(far + near) / (far - near), -1],
            [0,  0, -(2 * far * near) / (far - near),  0]
        ], dtype=np.float32)

        view_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, -8, 1]  # Move cube back by 8 units
        ], dtype=np.float32)

        vp_matrix = view_matrix @ projection

        gl.glUniformMatrix4fv(self.projection_matrix, 1, gl.GL_FALSE, vp_matrix)

    def draw(self, frame_num: int):
        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT) # type: ignore

        # Set rotation uniforms
        gl.glUniform1f(self.rotation_x, math.radians(45.0 + (0.75 * frame_num)))
        gl.glUniform1f(self.rotation_y, math.radians(45.0 - (0.5 * frame_num)))
        gl.glUniform1f(self.rotation_z, math.radians(10.0 + (0.45 * frame_num)))

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3*2*6)
