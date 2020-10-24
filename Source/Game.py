from packages import *
shader_program = None

display = [1280, 720]
# Creating a vertex shader
vertex_shader_code = """
#version 330

layout (location = 0) in vec3 pos;
layout (location = 1) in vec3 color;

out vec3 newColor;

void main()
{
    gl_Position = vec4(pos.x, pos.y, pos.z, 1.0);
    newColor = color;
}
"""
fragment_shader_code = """
#version 330

in vec3 newColor;
out vec4 outColor;

void main()
{
    outColor = vec4(newColor.x, newColor.y, newColor.z, 1.0);
}
"""


def shader_compile():
    global shader_program
    shader_program = compileProgram(compileShader(vertex_shader_code, GL_VERTEX_SHADER),
                                    compileShader(fragment_shader_code, GL_FRAGMENT_SHADER))


class Game:
    def __init__(self, name, icon=None):
        self.name = name
        self.icon = icon
        self.game_window = None
        self.timer = pygame.time.Clock()
        self.is_running = False

    def start(self):
        # PyGame Initialization
        pygame.init()
        while not pygame.get_init():
            print("PyGame Initialization Failed.")
        self.game_window = pygame.display.set_mode((display[0], display[1]), DOUBLEBUF | OPENGL | pygame.RESIZABLE)
        pygame.display.set_caption(self.name)
        self.is_running = True
        glViewport(0, 0, display[0], display[1])
        # pygame.display.set_icon(pygame.image.load(self.icon))
        shader_compile()

    def loop(self):
        player = Player(0, 0, 2)
        player.create_player()
        while self.is_running:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(1, 1, 1, 1)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.is_running = False
                if event.type == VIDEORESIZE:
                    glViewport(0, 0, event.w, event.h)
            mouse = pygame.mouse.get_pos()
            # print(mouse[0]-640, mouse[1]-360) # Print mouse position with OpenGL Oxy base (0, 0)
            player.jump_handling()
            glUseProgram(shader_program)
            player.render_player()
            glUseProgram(0)
            pygame.display.flip()
            self.timer.tick(60)
        pygame.quit()
        sys.exit()


class Player:
    # vao = glGenVertexArrays(1)
    def __init__(self, x, y, size=1):
        self.x = x
        self.y = y
        self.velocity = 10
        self.is_jump = False
        self.base_gravity = 10 + size
        self.jump_count = self.base_gravity
        self.size = size
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(2)

        mod_x = self.x*2/display[0]
        mod_y = self.y*2/display[1]

        self.pos_data = [
            -0.027+mod_x, -0.05+mod_y, 0,
            0.027+mod_x, -0.05+mod_y, 0,
            0.027+mod_x, 0.05+mod_y, 0,
            -0.027+mod_x, 0.05+mod_y, 0
        ]
        self.pos_data = np.array(self.pos_data, dtype=np.float32)
        self.pos_data = self.size * self.pos_data

        self.width = self.pos_data[3]*display[0]
        self.height = self.pos_data[7]*display[1]

        self.color_data = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            1.0, 0.0, 1.0
        ]
        self.color_data = np.array(self.color_data, dtype=np.float32)

    def create_player(self):
        glBindVertexArray(self.vao)

        # Position processing
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        glBufferData(GL_ARRAY_BUFFER, self.pos_data.nbytes, self.pos_data, GL_DYNAMIC_DRAW)

        player_pos = glGetAttribLocation(shader_program, 'pos')
        glVertexAttribPointer(player_pos, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        # Color processing
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[1])
        glBufferData(GL_ARRAY_BUFFER, self.color_data.nbytes, self.color_data, GL_STATIC_DRAW)

        player_color = glGetAttribLocation(shader_program, 'color')
        glVertexAttribPointer(player_color, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def render_player(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_QUADS, 0, 4)
        glBindVertexArray(0)

    def move(self, vel_x, vel_y):
        self.x += vel_x
        self.y += vel_y
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        vel_x = vel_x*2/display[0]
        vel_y = vel_y*2/display[1]
        self.pos_data[0] += vel_x
        self.pos_data[3] += vel_x
        self.pos_data[6] += vel_x
        self.pos_data[9] += vel_x
        self.pos_data[1] += vel_y
        self.pos_data[4] += vel_y
        self.pos_data[7] += vel_y
        self.pos_data[10] += vel_y
        glBufferData(GL_ARRAY_BUFFER, self.pos_data.nbytes, self.pos_data, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def jump_handling(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT] and self.x < (display[0] / 2) - self.width/2:
            self.move(self.velocity, 0)
        if keys[K_LEFT] and self.x > -((display[0] / 2) - self.width/2):
            self.move(-self.velocity, 0)
        if not self.is_jump:

            if keys[K_SPACE] or keys[K_UP]:
                self.is_jump = True
        else:
            if self.jump_count >= -self.base_gravity:
                neg = 1
                if self.jump_count < 0:
                    neg = -1
                self.move(0, (self.jump_count ** 2) * 0.5 * neg)
                self.jump_count -= 1
            else:
                self.is_jump = False
                self.jump_count = self.base_gravity


#class Block:
    #def __init__(self, x, y, size, width, height):