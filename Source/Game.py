import Shaders.load as shader
import random
import pygame
from OpenGL.GL import *
from pygame.locals import *
from Globals import *
from Player import Player
from Scene import Scene
from Pipe import Pipe
from Button import Button

class Game:
    def __init__(self, game_name, icon=None):
        self.game_name = game_name
        self.icon = icon
        self.timer = pygame.time.Clock()
        self.is_running = True
        # Game variables
        self.flying = False
        self.game_over = False
        self.score = 0
        self.pass_pipe = False
        # Sound
        pygame.mixer.init(buffer=256)
        self.theme = pygame.mixer.music.load(path_themesong)
        self.flap_sound = pygame.mixer.Sound(path_wingsound)
        self.hit_sound = pygame.mixer.Sound(path_hitsound)
        self.die_sound = pygame.mixer.Sound(path_diesound)
        self.hit_played = False
        self.score_sound = pygame.mixer.Sound(path_scoresound)
        # PyGame Initialization
        pygame.init()
        while not pygame.get_init():
            print("PyGame Initialization Failed.")

        self.game_window = pygame.display.set_mode((display[0], display[1]), DOUBLEBUF | OPENGL)
        pygame.display.set_caption(self.game_name)
        glViewport(0, 0, display[0], display[1])
        # pygame.display.set_icon(pygame.image.load(self.icon))
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(1, 1, 1, 1)
        shader.compile_shader()

    def loop(self):
        pygame.mixer.music.play(-1)

        while self.is_running:
            # HUD
            startButton = Button(0, 50, path_buttonStart)
            startText = Button(0, 100, path_textStart)
            endText = Button(0, 100, path_textEnd)

            # Playground
            player = Player(-150, 0, 51, 36)
            bg = Scene(path_bg, 0, 100, 864, 768)
            ground = Scene(path_ground, 0, -368, 900, 168)
            pipe_group = []
            last_pipe = pygame.time.get_ticks() - pipe_frequency

            restart = False
            self.game_over = False
            self.flying = False
            self.hit_played = False
            startButton.active = True
            startText.active = True
            endText.active = False

            #=======
            # Ingame
            while (not self.game_over or not restart) and self.is_running:
                #=======
                # Events
                isFlying = False
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.is_running = False

                    if event.type == KEYDOWN:
                        if self.game_over:
                            restart = True

                        isFlying = isFlying | event.key == K_UP

                    if event.type == MOUSEBUTTONDOWN:
                        if self.game_over:
                            restart = True

                        isFlying = isFlying | pygame.mouse.get_pressed(3)[0]
                        isFlying = isFlying & startButton.isHovered()

                if isFlying and not self.flying and not self.game_over:
                    self.flying = True
                    startButton.active = False
                    startText.active = False


                #=======================
                # Controller
                player.move_handling(self.flying, self.game_over, self.flap_sound)

                #==============
                # Pipes handing
                if self.flying is True and self.game_over is False:
                    # Pipe random generation
                    time_now = pygame.time.get_ticks()
                    if time_now - last_pipe > pipe_frequency:
                        pipe_height = random.randint(-150, 250)
                        btm_pipe = Pipe(display[0], pipe_height, 78, 568, False)
                        top_pipe = Pipe(display[0], pipe_height, 78, 568, True)
                        pipe_group.append(btm_pipe)
                        pipe_group.append(top_pipe)
                        last_pipe = time_now
                    # Delete out of screen pipes
                    if pipe_group[0].x < -350:
                        pipe_group.pop(0)
                    # Scrolling pipes
                    for i in range(0, len(pipe_group)):
                        pipe_group[i].scrolling()


                #================
                # Check collision
                for i in range(0, len(pipe_group)):
                    if check_collision(player, pipe_group[i]):
                        self.game_over = True
                if player.y >= 425:
                    self.game_over = True
                if player.y <= -270:
                    self.game_over = True
                    self.flying = False
                if self.game_over:
                    endText.active = True

                #============
                # Check score
                if len(pipe_group) > 0:
                    if player.x - player.width / 2 > pipe_group[0].x - pipe_group[0].width / 2 and \
                        player.x + player.width / 2 < pipe_group[0].x + pipe_group[0].width / 2 and\
                            self.pass_pipe is False:
                        self.pass_pipe = True
                    if self.pass_pipe is True:
                        if player.x - player.width / 2 > pipe_group[0].x + pipe_group[0].width / 2:
                            self.score += 1
                            self.score_sound.play()
                            self.pass_pipe = False

                #=====================
                # Scrolling the ground
                if not self.game_over:
                    ground.scrolling()

                #=======
                # Sounds
                if self.game_over is True:
                    if self.hit_played is False:
                        self.hit_sound.play()
                        self.die_sound.play()
                        self.hit_played = True


                #=======
                # Render
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glUseProgram(shader.program)
                bg.draw()
                for i in range(0, len(pipe_group)):
                    pipe_group[i].draw()
                ground.draw()
                player.draw()

                # Draw Menu
                startButton.draw()
                startText.draw()
                endText.draw()

                # Draw UI
                #drawText(0, 0.83, f'{self.score}')


                glUseProgram(0)
                pygame.display.flip()
                self.timer.tick(fps)


def check_collision(player, collided_object):
    collision_x = player.x + player.width / 2 >= collided_object.x + leeway - collided_object.width / 2 and \
                  collided_object.x - leeway + collided_object.width / 2 >= player.x - player.width / 2
    collision_y = player.y + player.height / 2 >= collided_object.y + leeway - collided_object.height / 2 and \
                  collided_object.y - leeway + collided_object.height / 2 >= player.y - player.height / 2
    return collision_x and collision_y


def drawText(x, y, textString):
    font = pygame.font.SysFont('Bauhaus 93', 50)
    textSurface = font.render(textString, True, (255, 255, 255, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(x, y, 0)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)


"""
class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(2)

        mod_x = self.x * 2 / display[0]
        mod_y = self.y * 2 / display[1]
        mod_width = self.width / display[0]
        mod_height = self.height / display[1]

        self.pos_data = [
            -mod_width + mod_x, -mod_height + mod_y, 0,
            mod_width + mod_x, -mod_height + mod_y, 0,
            mod_width + mod_x, mod_height + mod_y, 0,
            -mod_width + mod_x, mod_height + mod_y, 0
        ]
        self.pos_data = np.array(self.pos_data, dtype=np.float32)

        self.color_data = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            1.0, 0.0, 1.0
        ]
        self.color_data = np.array(self.color_data, dtype=np.float32)

        glBindVertexArray(self.vao)

        # Position processing
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        glBufferData(GL_ARRAY_BUFFER, self.pos_data.nbytes, self.pos_data, GL_DYNAMIC_DRAW)

        platform_pos = glGetAttribLocation(shader.program, 'aPos')
        glVertexAttribPointer(platform_pos, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # Color processing

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[1])
        glBufferData(GL_ARRAY_BUFFER, self.color_data.nbytes, self.color_data, GL_STATIC_DRAW)

        platform_color = glGetAttribLocation(shader.program, 'aColor')
        glVertexAttribPointer(platform_color, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def render_platform(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_QUADS, 0, 4)
        glBindVertexArray(0)

"""
