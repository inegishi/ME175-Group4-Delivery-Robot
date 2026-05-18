import pygame
import math
import networkx as nx
import random


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "MOVE_FORWARD"
        self.velocity = 0
        self.max_speed = 2.2
        self.acceleration = 0.03
        self.path = []
        self.target_index = 0
        self.theta = math.pi / 2

        self.sensor_length = 80
        self.sensor_offsets = [0, math.radians(30), math.radians(-30)]

        self.image_original = pygame.image.load("assets/mouse.png").convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, (40, 40))
        self.image_original = pygame.transform.rotate(self.image_original, -90)

    def update(self, obstacle_rects):
        sensor_hits = [False, False, False]

        for rect in obstacle_rects:
            hits = self.detect_sensors(rect)
            if any(hits):
                sensor_hits = hits
                break

        if self.state == "MOVE_FORWARD":
            if any(sensor_hits):
                self.velocity = 0
                self.state = "ALERT"
            else:
                self.follow_path()

        elif self.state == "ALERT":
            self.apply_throttle(0)

            if not any(sensor_hits):
                self.state = "MOVE_FORWARD"

        elif self.state == "IDLE":
            self.apply_throttle(0)

    def apply_throttle(self, throttle):
        self.velocity += throttle * self.acceleration
        self.velocity = clamp(self.velocity, -self.max_speed, self.max_speed)

        self.x += self.velocity * math.cos(self.theta)
        self.y += self.velocity * math.sin(self.theta)

    def follow_path(self):
        if self.target_index >= len(self.path):
            self.state = "IDLE"
            return

        LOOKAHEAD_PX = 30
        WP_SWITCH_PX = 40
        MAX_TURN_RATE = 0.05
        ANGLE_SLOWDOWN = 4

        tx, ty = self.path[self.target_index]
        distance = math.hypot(tx - self.x, ty - self.y)

        if self.target_index == len(self.path) - 1:
            if distance < WP_SWITCH_PX:
                self.velocity = 0
                self.state = "IDLE"
                return

        if distance < WP_SWITCH_PX:
            self.target_index += 1

            if self.target_index >= len(self.path):
                self.state = "IDLE"
                return

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
        self.apply_throttle(turn_factor)

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
        self.theta = -math.pi / 2
        self.detected = False
        self.escape_timer = 0
        self.escape_duration = 60   # 60 frames = about 1 second
        self.image_original = pygame.image.load("assets/cat.png").convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, (60, 60))
        self.image_original = pygame.transform.rotate(self.image_original, -90)

    def update(self, robot):
        if self.detected:
            self.escape_timer = self.escape_duration

        if self.escape_timer > 0:
            dx = self.x - robot.x
            dy = self.y - robot.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                speed = 2
                self.x += speed * dx / dist
                self.y += speed * dy / dist

            self.escape_timer -= 1

    def draw(self, screen):
        rotated = pygame.transform.rotate(
            self.image_original,
            -math.degrees(self.theta)
        )
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)

        if self.detected:
            pygame.draw.rect(screen, (255, 0, 0), rect, 3)
        else:
            pygame.draw.rect(screen, (120, 120, 120), rect, 2)

    def get_rect(self):
        rotated = pygame.transform.rotate(
            self.image_original,
            -math.degrees(self.theta)
        )
        return rotated.get_rect(center=(self.x, self.y))


def graph_to_coord(x, y):
    screen_x = (x - min_x) * SCALE + MARGIN // 2
    screen_y = (max_y - y) * SCALE + MARGIN // 2
    return screen_x, screen_y


def normalize_angle(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def generate_maze(cols, rows, spacing):
    positions = {}
    node_id = 1

    for y in range(rows):
        for x in range(cols):
            positions[node_id] = (x * spacing, -y * spacing)
            node_id += 1

    def node(x, y):
        return y * cols + x + 1

    visited = set()
    edges = []

    def dfs(x, y):
        visited.add((x, y))

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx_ = x + dx
            ny_ = y + dy

            if 0 <= nx_ < cols and 0 <= ny_ < rows and (nx_, ny_) not in visited:
                edges.append((node(x, y), node(nx_, ny_)))
                dfs(nx_, ny_)

    dfs(0, 0)

    extra_edges = 35

    for _ in range(extra_edges):
        x = random.randint(0, cols - 1)
        y = random.randint(0, rows - 1)

        possible = []

        if x + 1 < cols:
            possible.append((node(x, y), node(x + 1, y)))
        if y + 1 < rows:
            possible.append((node(x, y), node(x, y + 1)))

        if possible:
            e = random.choice(possible)

            if e not in edges and (e[1], e[0]) not in edges:
                edges.append(e)

    return positions, edges


pygame.init()
pygame.font.init()

font = pygame.font.Font(None, 30)

G = nx.Graph()

positions, edges = generate_maze(cols=14, rows=10, spacing=2)

G.add_nodes_from(positions.keys())
nx.set_node_attributes(G, positions, "pos")
G.add_edges_from(edges)

for u, v in G.edges():
    x1, y1 = positions[u]
    x2, y2 = positions[v]
    dist = math.hypot(x2 - x1, y2 - y1)
    G[u][v]["weight"] = dist

start = 1
goal = max(positions.keys())

path = nx.dijkstra_path(G, start, goal)
path_edges = list(zip(path, path[1:]))

SCALE = 45
MARGIN = 150

xs = [p[0] for p in positions.values()]
ys = [p[1] for p in positions.values()]

min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)

height = int((max_y - min_y) * SCALE + MARGIN)
width = int((max_x - min_x) * SCALE + MARGIN)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Big Maze Robot Simulation With Independent Cats")

clock = pygame.time.Clock()

start_graph = positions[start]
start_x, start_y = graph_to_coord(*start_graph)

robot = Robot(start_x, start_y)
robot.path = [graph_to_coord(*positions[n]) for n in path]

NUM_CATS = 10
cats = []

valid_nodes = list(positions.values())

while len(cats) < NUM_CATS:
    node_pos = random.choice(valid_nodes)
    x, y = graph_to_coord(*node_pos)

    if math.hypot(x - start_x, y - start_y) > 180:
        cats.append(Obstacle(x, y))


running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    # reset every cat's detected state
    for cat in cats:
        cat.detected = False

    obstacle_rects = []

    # detect each cat separately
    for cat in cats:
        rect = cat.get_rect()
        obstacle_rects.append(rect)

        hits = robot.detect_sensors(rect)
        if any(hits):
            cat.detected = True

    robot.update(obstacle_rects)

    # only detected cats move
    for cat in cats:
        cat.update(robot)

    for u, v in G.edges():
        x1, y1 = graph_to_coord(*positions[u])
        x2, y2 = graph_to_coord(*positions[v])
        pygame.draw.line(screen, (200, 200, 200), (x1, y1), (x2, y2), 2)

    for u, v in path_edges:
        x1, y1 = graph_to_coord(*positions[u])
        x2, y2 = graph_to_coord(*positions[v])
        pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 5)

    for n, p in positions.items():
        x, y = graph_to_coord(*p)
        pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 4)

    if robot.target_index < len(robot.path):
        tx, ty = robot.path[robot.target_index]
        pygame.draw.circle(screen, (0, 0, 255), (int(tx), int(ty)), 12)

    for start_ray, end_ray in robot.get_sensor_rays():
        pygame.draw.line(screen, (0, 255, 0), start_ray, end_ray, 2)

    for cat in cats:
        cat.draw(screen)

    robot.draw(screen)

    state_text = font.render(f"State: {robot.state}", True, (0, 0, 0))
    screen.blit(state_text, (10, 20))

    velocity_text = font.render(f"Velocity: {round(robot.velocity, 2)}", True, (0, 0, 0))
    screen.blit(velocity_text, (250, 20))

    node_text = font.render(f"Next Node: {robot.target_index}", True, (0, 0, 0))
    screen.blit(node_text, (470, 20))

    path_text = font.render(f"Path Length: {len(path)} nodes", True, (0, 0, 0))
    screen.blit(path_text, (680, 20))

    cat_text = font.render(f"Cats: {len(cats)}", True, (0, 0, 0))
    screen.blit(cat_text, (930, 20))

    pygame.display.flip()

pygame.quit()