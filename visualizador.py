import math
import time

import glfw
import numpy as np
from OpenGL.GL import *


def carregar_obj(caminho):
    vertices = []
    indices = []

    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            if linha.startswith("v "):
                _, x, y, z = linha.strip().split()
                vertices.append([float(x), float(y), float(z)])
            elif linha.startswith("f "):
                partes = linha.strip().split()[1:]
                tri = []
                for p in partes:
                    idx = p.split("/")[0]
                    tri.append(int(idx) - 1)
                if len(tri) == 3:
                    indices.extend(tri)

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)
    return vertices, indices


def carregar_particulas_xyz(caminho):
    pontos = []
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split()
            if len(partes) < 3:
                continue
            x, y, z = map(float, partes[:3])
            pontos.append([x, y, z])
    if not pontos:
        return np.zeros((0, 3), dtype=np.float32)
    return np.array(pontos, dtype=np.float32)


vertex_shader_src = """
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 u_mvp;
uniform float u_point_size;

void main()
{
    gl_Position = u_mvp * vec4(aPos, 1.0);
    gl_PointSize = u_point_size;
}
"""


fragment_shader_src = """
#version 330 core
out vec4 FragColor;

uniform vec3 u_color;

void main()
{
    FragColor = vec4(u_color, 1.0);
}
"""


def compilar_shader(tipo, src):
    shader = glCreateShader(tipo)
    glShaderSource(shader, src)
    glCompileShader(shader)
    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not status:
        log = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"erro ao compilar shader: {log}")
    return shader


def criar_programa(vertex_src, fragment_src):
    vs = compilar_shader(GL_VERTEX_SHADER, vertex_src)
    fs = compilar_shader(GL_FRAGMENT_SHADER, fragment_src)
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    status = glGetProgramiv(prog, GL_LINK_STATUS)
    if not status:
        log = glGetProgramInfoLog(prog).decode()
        raise RuntimeError(f"erro ao linkar programa: {log}")
    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog


def look_at(eye, center, up):
    eye = np.array(eye, dtype=np.float32)
    center = np.array(center, dtype=np.float32)
    up = np.array(up, dtype=np.float32)

    f = center - eye
    f = f / np.linalg.norm(f)
    u = up / np.linalg.norm(up)
    s = np.cross(f, u)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)

    m = np.identity(4, dtype=np.float32)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)
    return m


def perspective(fov_deg, aspect, near, far):
    fov_rad = math.radians(fov_deg)
    f = 1.0 / math.tan(fov_rad / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def criar_vao_malha(vertices, indices):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, None)

    glBindVertexArray(0)
    return vao, vbo, ebo, indices.size


def criar_vao_pontos(vertices):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, None)

    glBindVertexArray(0)
    return vao, vbo, vertices.shape[0]


def main():
    if not glfw.init():
        print("falha ao inicializar glfw")
        return

    largura, altura = 1280, 720
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    janela = glfw.create_window(largura, altura, "visualizador cfd", None, None)
    if not janela:
        glfw.terminate()
        print("falha ao criar janela")
        return

    glfw.make_context_current(janela)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_PROGRAM_POINT_SIZE)

    programa = criar_programa(vertex_shader_src, fragment_shader_src)
    glUseProgram(programa)

    vertices_malha, indices_malha = carregar_obj("tubo_com_tampas.obj")
    vao_malha, vbo_malha, ebo_malha, num_indices = criar_vao_malha(vertices_malha, indices_malha)

    vertices_particulas = carregar_particulas_xyz("particulas.xyz")
    vao_part, vbo_part, num_pontos = criar_vao_pontos(vertices_particulas)

    loc_u_mvp = glGetUniformLocation(programa, "u_mvp")
    loc_u_color = glGetUniformLocation(programa, "u_color")
    loc_u_point_size = glGetUniformLocation(programa, "u_point_size")

    inicio = time.time()

    while not glfw.window_should_close(janela):
        glfw.poll_events()

        t = time.time() - inicio

        glViewport(0, 0, largura, altura)
        glClearColor(0.05, 0.05, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        raio = 8.0
        ang = 0.3 * t
        eye = (raio * math.cos(ang), raio * math.sin(ang), 4.0)
        center = (0.0, 0.0, 2.5)
        up = (0.0, 0.0, 1.0)

        view = look_at(eye, center, up)
        proj = perspective(45.0, largura / altura, 0.1, 100.0)
        mvp = proj @ view

        glUseProgram(programa)
        glUniformMatrix4fv(loc_u_mvp, 1, GL_FALSE, mvp.astype(np.float32))

        glUniform3f(loc_u_color, 0.7, 0.7, 0.9)
        glUniform1f(loc_u_point_size, 1.0)
        glBindVertexArray(vao_malha)
        glDrawElements(GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, None)

        if num_pontos > 0:
            glUniform3f(loc_u_color, 1.0, 0.4, 0.1)
            glUniform1f(loc_u_point_size, 5.0)
            glBindVertexArray(vao_part)
            glDrawArrays(GL_POINTS, 0, num_pontos)

        glBindVertexArray(0)
        glfw.swap_buffers(janela)

    glDeleteProgram(programa)
    glDeleteVertexArrays(1, [vao_malha])
    glDeleteBuffers(1, [vbo_malha])
    glDeleteBuffers(1, [ebo_malha])

    glDeleteVertexArrays(1, [vao_part])
    glDeleteBuffers(1, [vbo_part])

    glfw.terminate()


if __name__ == "__main__":
    main()

