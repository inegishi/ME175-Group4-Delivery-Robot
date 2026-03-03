import pygame
import math
import networkx as nx
import matplotlib.pyplot as plt


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "MOVE_FORWARD"
        self.velocity = 0
        self.max_speed = 2.0
        self.acceleration = 0.04
        self.path = []
        self.target_index = 0
        self.theta = -math.pi / 2
        self.rot_angle = 5
        self.sensor_length = 80
        self.sensor_offsets = [0, math.radians(30), math.radians(-30)]

        self.image_original = pygame.image.load("assets/mouse.png").convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, (40, 40))
        self.image_original = pygame.transform.rotate(self.image_original, -90)

    def update(self,obstacle_rect):
        sensor_hits = self.detect_sensors(obstacle_rect)
        if self.state == "MOVE_FORWARD":
            if any(sensor_hits): 
                self.velocity = 0
                self.state = "ALERT"
            else:
                self.follow_path()

        elif self.state == "ALERT":
            self.apply_throttle(0)
            if not all(sensor_hits):
                self.state = "MOVE_FORWARD" 

        elif self.state == "IDLE":
            self.apply_throttle(0)

    
    #movement
    def apply_throttle(self, throttle):
        # throttle between -1 and 1

        self.velocity += throttle * self.acceleration

        self.velocity = clamp(self.velocity, -self.max_speed, self.max_speed)

        self.x += self.velocity * math.cos(self.theta)
        self.y += self.velocity * math.sin(self.theta)

    def follow_path(self):
        if self.target_index >= len(self.path):
            self.state="IDLE"
            return

        # --- tuning knobs ---
        LOOKAHEAD_PX = 50          # bigger = smoother / wider turns
        WP_SWITCH_PX = 40         # distance needed to advance waypoint
        MAX_TURN_RATE = 0.03       # rad per frame-ish (controls steering smoothness)
        ANGLE_SLOWDOWN = 2       # higher = slow down more on sharp turns

        tx, ty = self.path[self.target_index]
        distance = math.hypot(tx - self.x, ty - self.y)

        if self.target_index == len(self.path) - 1:
            if distance < WP_SWITCH_PX:
                self.velocity = 0
                self.state = "IDLE"
                return

        if distance < WP_SWITCH_PX:
            self.target_index += 1

        look_i = self.target_index
        while look_i < len(self.path) - 1:
            lx, ly = self.path[look_i]
            if math.hypot(lx - self.x, ly - self.y) >= LOOKAHEAD_PX:
                break
            look_i += 1

        lx, ly = self.path[look_i]

        desired = math.atan2(ly - self.y, lx - self.x)
        err = normalize_angle(desired - self.theta)

        turn = clamp(err, -MAX_TURN_RATE, MAX_TURN_RATE)
        self.theta += turn

        turn_factor = clamp(1.0 - (abs(err) / ANGLE_SLOWDOWN), 0.2, 1.0)
        self.apply_throttle(1 * turn_factor)

    def rotate(self):
        self.theta += math.radians(self.rot_angle)

    #render in pygame
    def draw(self, screen):
        rotated = pygame.transform.rotate(
            self.image_original,
            -math.degrees(self.theta)
        )
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)

    def get_sensor_rays(self):
        rays = []
        for offset in self.sensor_offsets:
            angle = self.theta + offset
            end_x = self.x + self.sensor_length * math.cos(angle)
            end_y = self.y + self.sensor_length * math.sin(angle)
            rays.append(((self.x, self.y), (end_x, end_y)))
        return rays

    def detect_sensors(self, obstacle_rect):
        hits = []

        for start, end in self.get_sensor_rays():
            hit = obstacle_rect.clipline(start, end)
            hits.append(bool(hit))

        return hits  


class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "IDLE"
        self.speed = 2
        self.path = []
        self.target_index = 0
        self.theta = -math.pi / 2
        self.rot_angle = 5
        self.sensor_length = 80
        self.sensor_offsets = [0, math.radians(30), math.radians(-30)]

        self.image_original = pygame.image.load("assets/cat.png").convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, (60, 60))
        self.image_original = pygame.transform.rotate(self.image_original, -90)

    def update(self, robot):
        if robot.state == "ALERT":
            self.y += 2
        

    #render in pygame
    def draw(self, screen):
        rotated = pygame.transform.rotate(
            self.image_original,
            -math.degrees(self.theta)
        )
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)
        pygame.draw.rect(screen, (255, 0, 0), rect, 2)
    
    def get_rect(self):
        rotated = pygame.transform.rotate(
            self.image_original,
            -math.degrees(self.theta)
        )
        return rotated.get_rect(center=(self.x, self.y))

#helper functions
def graph_to_coord(x,y):
    screen_x = (x - min_x) * SCALE + MARGIN // 2
    screen_y = (max_y - y) * SCALE + MARGIN // 2
    return screen_x, screen_y   

def normalize_angle(a):
    return (a + math.pi) % (2 * math.pi) - math.pi

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

#xnetwork
G = nx.Graph()

positions = {
    1: (0,0),
    2: (0,4),
    3: (-2,4),
    4: (-2,0),
    5: (-2,3),
    6: (-5,3),
    7: (-5,5),
    8: (-5,1),
    9: (-7,3),
    10: (-7,1),
    11: (-7,5)
}

G.add_nodes_from(positions.keys())
nx.set_node_attributes(G, positions, 'pos')
pos = nx.get_node_attributes(G, 'pos')

#map generation
edges = [(1,2),(1,4),(2,3),(4,5),(3,5),(5,6),(6,7),(6,8),(6,9),(9,10),(9,11)]
G.add_edges_from(edges)
for u, v in G.edges():
    x1, y1 = positions[u]
    x2, y2 = positions[v]
    dist = math.hypot(x2 - x1, y2 - y1)
    G[u][v]['weight'] = dist
    
#define start/goal node
start =1 
goal = 11
path = nx.dijkstra_path(G, start, goal)
path_edges = list(zip(path, path[1:]))

#display self.state
pygame.font.init()   
font = pygame.font.Font(None, 30)

#pygame setup
pygame.init()

#determine size of screen based on map
SCALE = 100
MARGIN = 150

xs = [p[0] for p in positions.values()]
ys = [p[1] for p in positions.values()]
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
height = int((max_y-min_y)* SCALE + MARGIN)
width = int((max_x-min_x)* SCALE + MARGIN)
screen = pygame.display.set_mode((width, height))

#determine starting coord
start_graph = positions[start]
start_x, start_y = graph_to_coord(start_graph[0], start_graph[1])
clock = pygame.time.Clock()

robot = Robot(start_x,start_y)
path_points = [graph_to_coord(*positions[n]) for n in path]
robot.path = path_points
print(robot.path)
cat = Obstacle(*graph_to_coord(-4,3))

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    robot.update(cat.get_rect())
    cat.update(robot)
    robot.draw(screen)

    cat.draw(screen)

    #display info as text
    state_text = font.render(f"State: {robot.state}", True, (0, 0, 0))
    screen.blit(state_text, (10, 20))
    state_text = font.render(f"Velocity: {round(robot.velocity,2)}", True, (0, 0, 0))
    screen.blit(state_text, (300, 20))
    state_text = font.render(f"Next Node: {robot.target_index}", True, (0, 0, 0))
    screen.blit(state_text, (500, 20))

    # Draw sensors
    for start, end in robot.get_sensor_rays():
        pygame.draw.line(screen, (0, 255, 0), start, end, 2)

    for u,v in path_edges:
        x1, y1 = graph_to_coord(*positions[u])
        x2, y2 = graph_to_coord(*positions[v])
        pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 5)
    for u, v in G.edges():
        x1, y1 = graph_to_coord(*positions[u])
        x2, y2 = graph_to_coord(*positions[v])
        pygame.draw.line(screen, (200, 200, 200), (x1, y1), (x2, y2), 2)
    if robot.target_index < len(robot.path):
        tx, ty = robot.path[robot.target_index]
        pygame.draw.circle(screen, (0, 0, 255), (int(tx), int(ty)), 12)
    pygame.display.flip()

pygame.quit()

