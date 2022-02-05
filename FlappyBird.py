import pygame   # Instalar biblioteca do pygame
import os
import random
import neat     # Biblioteca da IA

ai_playing = True
generation = 0

# Definição de constantes
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
FLOOR_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
BIRD_IMAGES = [ 
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))) ]
pygame.font.init()
SCORE_FONT = pygame.font.SysFont('arial', 50)


# Criação das classes
class Bird:                   
    # Constantes do pássaro
    IMGS = BIRD_IMAGES
 
    MAX_ROTATION = 25           # Animações da rotação
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5
  
    # Função que cria o pássaro
    def __init__(self, x, y):
        self.x = x                # Parâmetros iniciais do pássaro
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
    
        self.time = 0             # Parâmetros auxiliares
        self.image_counter = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self): 
        # Calcular o deslocamento
        self.time += 1
        displacement = 1.5 * (self.time**2) + self.speed * self.time #S = So + Vo*t + (a*t^2)/2

        # Restringir o deslocamento
        if displacement > 16:
            displacement = 16
        elif displacement <0:
            displacement -= 2

        self.y += displacement

        # Ângulo do pássaro
        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw(self, window):
        # Definir imagem do pássaro a ser utilizada
        self.image_counter += 1
        if self.image_counter < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.image_counter < self.ANIMATION_TIME * 2:
            self.image = self.IMGS[1]
        elif self.image_counter < self.ANIMATION_TIME * 3:
            self.image = self.IMGS[2]
        elif self.image_counter < self.ANIMATION_TIME * 4:
            self.image = self.IMGS[1]
        elif self.image_counter >= self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMGS[0]
            self.image_counter = 0

        # Se o pássaro estiver caindo, não bater asas
        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.image_counter = self.ANIMATION_TIME*2

        # Desenhar a imagem
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        image_center_pos = self.image.get_rect(topleft = (self.x, self.y)).center
        rectangle = rotated_image.get_rect(center = image_center_pos)
        window.blit(rotated_image, rectangle.topleft)

    # Cria máscara para hitbox 
    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    # Definindo constantes
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_pos = 0
        self.base_pos = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BASE_PIPE = PIPE_IMAGE
        self.passed = False
        self.define_height()

    # Define posição dos canos de forma aleatória dentro de um range
    def define_height(self):
        self.height = random.randrange(50, 450)
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.base_pos = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, window):
        window.blit(self.TOP_PIPE, (self.x, self.top_pos))
        window.blit(self.BASE_PIPE, (self.x, self.base_pos))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        base_mask = pygame.mask.from_surface(self.BASE_PIPE)

        top_distance = (self.x - bird.x, self.top_pos - round(bird.y))
        base_distance = (self.x - bird.x, self.base_pos - round(bird.y))

        top_collision = bird_mask.overlap(top_mask, top_distance)
        base_collision = bird_mask.overlap(base_mask, base_distance)

        if top_collision or base_collision:
            return True
        else:
            return False
   
    
class Floor:
    # Constantes
    SPEED = 5
    WIDTH = FLOOR_IMAGE.get_width()
    IMAGE = FLOOR_IMAGE

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.WIDTH

    def move(self):
        self.x0 -= self.SPEED
        self.x1 -= self.SPEED

        if self.x0 + self.WIDTH < 0:   # Quando X0 sair da tela, colo ele atrás do x1
            self.x0 = self.x1 + self.WIDTH 
        if self.x1 + self.WIDTH < 0:   # (vice-versa)
            self.x1 = self.x0 + self.WIDTH

    def draw(self, window): 
        window.blit(self.IMAGE, (self.x0, self.y))
        window.blit(self.IMAGE, (self.x1, self.y))

def draw_window(window, birds, pipes, floor, score):
    window.blit(BACKGROUND_IMAGE, (0, 0))
    for bird in birds:
        bird.draw(window)
    for pipe in pipes:
        pipe.draw(window)

    text = SCORE_FONT.render(f"Score: {score}", 1, (255,255,255))
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    if ai_playing:
        text = SCORE_FONT.render(f"Generation: {generation}", 1, (255,255,255))
        window.blit(text, (10, 10))

    floor.draw(window)
    pygame.display.update()

def main(genomes, config):      # Fitness function
    global generation
    generation += 1
    
    if ai_playing:              # Criar vários pássaros
        neural_networks = []
        genome_list = []
        birds = []
        for _, genome in genomes:
            neural_network = neat.nn.FeedForwardNetwork.create(genome, config)
            neural_networks.append(neural_network)
            genome.fitness = 0
            genome_list.append(genome)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]

    floor = Floor(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    score = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(144)
        for event in pygame.event.get():
            # Interação com usuário
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()


        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
                pipe_index = 1
        else:
            running = False
            break

        # Mover as coisas
        for i, bird in enumerate(birds):
            bird.move()
            genome_list[i].fitness += 0.1                                                                                                       # Aumenta o fitness ao andar
            output = neural_networks[i].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].base_pos)))    # -1 e 1
            if output[0] > 0.5:
                bird.jump()
        
        floor.move()

        add_pipe = False
        remove_pipes = []

        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ai_playing:
                        genome_list[i].fitness -= 1
                        genome_list.pop(i)
                        neural_networks.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe) 

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
            for genome in genome_list:
                genome.fitness += 5

        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)
                if ai_playing:
                    genome_list.pop(i)
                    neural_networks.pop(i)

        draw_window(window, birds, pipes, floor, score)


def run(config_dir):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_dir)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    config_dir = os.path.join(dir, 'config.txt')
    run(config_dir)