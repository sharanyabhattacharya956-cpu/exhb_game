"""EARTH//25: a five-stage pixel arcade adventure. Run: python earth_rescue.py"""
import json
import math
import os
import random
import textwrap
from pathlib import Path
import pygame

W, H = 480, 270
BG = (14, 17, 34)
INK = (238, 239, 213)
MUTED = (117, 131, 154)
GREEN = (174, 230, 91)
BLUE = (101, 180, 219)
RED = (236, 111, 93)
GOLD = (255, 204, 105)
PANEL = (29, 37, 56)
PURPLE = (178, 120, 220)
CREW = [('NOVA', BLUE), ('RUST', RED), ('MOSS', GREEN)]
CREW_BLURB = [
    'NOVA: optimistic pilot. Later: Moon Hop, Slalom, Last Shot.',
    'RUST: gruff engineer. Later: Engine, Reactor, Calibration.',
    'MOSS: gentle botanist. Later: Greenhouse, Radar, Decode.']
# Levels 1-2 are shared; after the lights come back on, each crew member flies their own missions.
TRACKS = [
    ['lift', 'wires', 'hop', 'slalom', 'shot'],
    ['lift', 'wires', 'engine', 'reactor', 'calib'],
    ['lift', 'wires', 'greenhouse', 'radar', 'decode']]
MISSIONS = {
    'lift': ('LIFT OFF', 'PILOT', 'ARROWS / WASD: move. Grab 5 green fuel cells.', 'Orange meteors cost time. Collect the fuel to finish.',
             'Thrust pushes a rocket opposite to its exhaust.'),
    'wires': ('LIGHT THE STATION', 'SPARK', 'ARROWS: select tile. SPACE: rotate. ENTER: test.', 'Join IN to OUT on a 3x3 board. Green = live wire.',
              'Current flows through a closed conducting path.'),
    'hop': ('MOON HOP', 'MOONWALKER', 'SPACE / UP: jump. Clear five rocks.', 'Rocks vary in size and speed. Hit one and it is game over!',
            'Moon gravity is about one-sixth of Earth gravity.'),
    'slalom': ('DEBRIS SLALOM', 'NAVIGATOR', 'UP / DOWN (W / S): fly through the gaps.', 'Each clean gate scores. Hit debris and that gate is lost.',
               'With no air to push on, a ship drifts until thrusters fire.'),
    'shot': ('LAST SHOT', 'DEFENDER', 'SPACE: fire when the marker is inside the green zone.', 'Five shots. Your mission needs 20 total points.',
             'An impact transfers momentum and changes motion.'),
    'engine': ('ENGINE REPAIR', 'MECHANIC', 'HOLD SPACE to charge. RELEASE inside the green zone.', 'Five bolts. The zone shrinks. Overcharge strips the thread!',
               'Torque is the turning force a wrench puts on a bolt.'),
    'reactor': ('REACTOR BALANCE', 'ENGINEER', 'LEFT / RIGHT (A / D): vent the matching gauge.', 'Keep BOTH in the green. 1 point per 7 safe seconds.',
                'Heat flows from hot places to cooler ones until they balance.'),
    'calib': ('CANNON CALIBRATION', 'TECHNICIAN', 'LEFT / RIGHT: 1 degree. UP / DOWN: 10 degrees.', 'ENTER locks. Land within 2 degrees of the target. One try!',
              'A tiny angle error grows into a huge miss over distance.'),
    'greenhouse': ('GREENHOUSE RESCUE', 'GARDENER', 'UP: spore bin. DOWN: seed tray.', 'Sort 3 per batch. All 3 right = 1 point. Five batches.',
                   'Plants use light, water and air to make their own food.'),
    'radar': ('ASTEROID RADAR', 'DECODER', 'Match the TARGET silhouette. Press 1, 2, 3 or 4.', 'The target stays visible. One pick per scan - wrong is final!',
              'Comparing observations helps identify objects in space.'),
    'decode': ('SIGNAL DECODE', 'LISTENER', 'Watch the lights, then repeat them with ARROWS / WASD.', 'One mistake ends the round. Signals get longer.',
               'A pattern is an order that repeats, so it can be predicted.')}
CONTROL_BRIEF = {
    'lift': 'Kepler-9 is on a collision course with Earth. Reach the station and grab fuel. The meteor belt is thick today.',
    'wires': 'You made it. The station lost power in the storm. Bring all five power banks online or we are flying blind.',
    'hop': 'Lights are on! Next, our launch parts are stranded on the Moon. Low gravity, loose rocks. Watch your step.',
    'slalom': 'Kepler-9 left a debris field across your path. Thread the gates. No scratches on the ship, please.',
    'shot': 'This is it. Kepler-9 is in range. Five shots to nudge it off course. Make every one count.',
    'engine': 'The main engine is cold. Five bolts need exact torque. Too loose and it rattles, too tight and it strips.',
    'reactor': 'The reactor is running hot on both sides. Keep both gauges in the green. Vent one side and the other climbs.',
    'calib': 'Final calibration. The cannon needs exact angles, and Kepler-9 will not wait. Read the numbers and set them.',
    'greenhouse': 'Spores crept into the greenhouse seed trays. Sort seeds from spores before they spread to everything.',
    'radar': 'Kepler-9 is hiding among the echoes. Match its outline on the scanner. You get one look per scan.',
    'decode': 'Kepler-9 is... sending a pattern. Watch the lights, then repeat the signal back exactly.'}
CREW_BRIEF = [
    ['Wheels up! Hold on to your helmets, Haven. We got this!',
     'Dark station? Perfect, I love a dramatic entrance. Lights on!',
     'Moon hops! My favourite. I will be gentle with the rocks. Mostly.',
     'A debris slalom? Honestly, that is just a Tuesday for me.',
     'One clean shot. I have been practising my aim all week!'],
    ['Fine. Fuel cells and meteors. I have fixed worse with a spanner.',
     'Who wired this? Not me. Nobody touch anything. I will sort it.',
     'Cold engine, loose bolts. Typical. Hand me the wrench.',
     'Two gauges, one pair of hands. Nobody breathe on the reactor.',
     'Measure twice, fire once. Give me the numbers.'],
    ['Please be careful with the fuel... oh, and Fern is strapped in too.',
     'It is so dark in here... Fern does not like the dark. Let us fix it.',
     'Oh no, spores near the seeds! Do not worry Fern, we will sort them.',
     'There... that echo. I think I can see its shape. I will be careful.',
     'It sounds like it is... singing? Okay. I will listen very closely.']]
CONTROL_TIER = {
    'great': ['Flawless! The whole control room is cheering.', 'Textbook! Kepler-9 never saw that coming.', 'Five for five. Remarkable work, crew.'],
    'ok': ['Good work. Not perfect, but we will take it.', 'Solid. Earth is still in the game.', 'That will do. Onward.'],
    'bad': ['Rough one. Breathe. You can retry it.', 'We needed more than that. Try again, crew.', 'Not our best. I know you have more in you.']}
CREW_TIER = [
    {'great': ['Told you! Easy! Who wants a high-five?', 'Did you see that? I surprised even myself!'],
     'ok': ['Not bad! A little polish and we shine.', 'Good enough for me. On to the next one!'],
     'bad': ['Okay, okay. Round two will be better, promise!', 'Even astronauts bounce a few times. Again!']},
    {'great': ['Hm. Acceptable. Do not let it go to your head.', 'Clean. No notes. Well, one note: more coffee.'],
     'ok': ['Held together. Barely. Like most good machines.', 'I have seen worse. Do not tell anyone I said so.'],
     'bad': ['That is broken. I will fix it. Again.', 'Bah. Failure is just data. Annoying data.']},
    {'great': ['We did it... Fern is waving a leaf, I swear.', 'Oh, that went so well! I think I am crying.'],
     'ok': ['It was close... I think we are going to be okay.', 'Good. Okay. Deep breath. Next one.'],
     'bad': ['Oh dear... that was scary. Please, let us try again.', 'It is alright. Everyone wilts sometimes. Again.']}]
CONTROL_END = {
    True: ['Kepler-9 has changed course! Earth is safe. Welcome home, crew!'],
    False: ['We missed it, but there is still time for one more try.']}
CREW_END = [
    {True: ['Told you we had this! Drinks are on me!'], False: ['One more go! I never lose twice in a row.']},
    {True: ['Not bad. Fine, it was a bit good.'], False: ['It will hold. Back to the workshop.']},
    {True: ['Fern says thank you. And so do I.'], False: ['We are so close... I know we can do it.']}]
SPRITE = ['0001111000', '0012222100', '0123333210', '0123333210', '0122222210', '0014444100', '0144444410', '0144444410', '0014444100', '0011001100', '0011001100', '0111001110']

class Game:
    def __init__(self):
        pygame.init()
        self.fullscreen = True
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        pygame.display.set_caption('EARTH // 25 - Pixel Rescue')
        self.screen = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        face = 'couriernew,consolas,lucidaconsole,dejavusansmono,monospace'
        self.font = pygame.font.SysFont(face, 12, bold=True)
        self.big = pygame.font.SysFont(face, 28, bold=True)
        self.small = pygame.font.SysFont(face, 10, bold=True)
        self.board_path = Path(__file__).with_name('earth_scores.json')
        self.board = self.load_board()
        self.scene = 'title'
        self.crew = 0
        self.scores = [None] * 5
        self.name = ''
        self.t = 0
        self.running = True
        self.stars = [(random.randrange(W), random.randrange(H), random.choice([1, 1, 2])) for _ in range(65)]
        self.message = ''
        self.particles = []
        self.paused = False
        self.crashed = False
        self.from_ending = False
        self.level = 0
        self.points = 0
        self.remaining = 60.
        self.brief_t = 0.
        self.marks = []
        self.warned = False
        self.res_lines = ('', '')
        self.end_lines = ('', '')

    @property
    def mission(self):
        return TRACKS[self.crew][self.level]

    @property
    def info(self):
        return MISSIONS[self.mission]

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((960, 540), pygame.RESIZABLE)
        pygame.mouse.set_visible(not self.fullscreen)

    def load_board(self):
        try:
            rows = json.loads(self.board_path.read_text())
            return sorted([r for r in rows if isinstance(r, dict) and isinstance(r.get('score'), int) and isinstance(r.get('name'), str)], key=lambda r: r['score'], reverse=True)[:8]
        except (OSError, ValueError, TypeError):
            return []

    def text(self, value, x, y, color=INK, size='normal', center=False, right=False):
        font = self.big if size == 'big' else self.small if size == 'small' else self.font
        surface = font.render(str(value), False, color)
        self.screen.blit(surface, (x - surface.get_width() // 2 if center else x - surface.get_width() if right else x, y))

    def box(self, rect, color=PANEL, border=MUTED):
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, border, rect, 1)

    def astronaut(self, x, y, scale=2, color=None, walk=False):
        color = color or CREW[self.crew][1]
        palette = {'1': (44, 52, 69), '2': INK, '3': BLUE, '4': color}
        for row, line in enumerate(SPRITE):
            for col, cell in enumerate(line):
                if cell != '0':
                    offset = (int(self.t * 8) % 2) if walk and row > 8 and col < 5 else 0
                    pygame.draw.rect(self.screen, palette[cell], (x + col * scale, y + (row + offset) * scale, scale, scale))

    def earth(self, x, y, radius=35):
        pygame.draw.circle(self.screen,(31,57,85),(x,y),radius+2,2)
        for yy in range(-radius,radius+1,2):
            for xx in range(-radius,radius+1,2):
                if xx*xx+yy*yy > radius*radius:
                    continue
                u,v=xx/radius,yy/radius
                land = ((-.8<u<-.1 and -.6<v<-.1) or (-.4<u<-.05 and -.2<v<.7) or (.2<u<.8 and -.3<v<.35))
                base = GREEN if land else BLUE
                shade = .58 if u>.4 or v>.65 else (1.1 if u<-.25 and v<-.2 else .85)
                tone = tuple(min(255,int(c*shade)) for c in base)
                pygame.draw.rect(self.screen,tone,(x+xx,y+yy,2,2))
        pygame.draw.rect(self.screen,INK,(x-radius//2,y-radius//2,radius//2,2))

    def total(self):
        return sum(v or 0 for v in self.scores)

    def brief(self, level):
        self.level = level
        self.message = ''
        self.brief_t = 0.
        self.scene = 'brief'

    def start(self):
        self.scene = 'play'
        self.particles = []
        self.points = 0
        self.remaining = 60.
        self.elapsed = 0.
        self.message = ''
        self.flash = 0.
        self.x, self.y = 230., 205.
        self.objects = []
        self.spawn = .8
        self.jump, self.vy = 0., 0.
        self.crossed = 0
        self.round = 0
        self.cursor = 0
        self.phase = random.uniform(0, math.tau)
        self.shots = 0
        self.paused = False
        self.crashed = False
        self.over = 0.
        self.next_v = 105.
        self.marks = []
        self.warned = False
        self.setup_puzzle()
        setup = getattr(self, 'setup_' + self.mission, None)
        if setup:
            setup()

    def setup_puzzle(self):
        # Ports are N/E/S/W; each solved board is generated from a real path.
        paths = [
            [0, 1, 2, 5, 8], [0, 3, 4, 5, 8],
            [0, 1, 4, 3, 6, 7, 8], [0, 3, 6, 7, 4, 5, 8],
            [0, 1, 2, 5, 4, 3, 6, 7, 8]]
        path = paths[self.round]
        self.wires = [random.choice([5, 10, 3, 6, 12, 9]) for _ in range(9)]
        self.solution = {}
        for i, tile in enumerate(path):
            mask = 0
            for neighbor in ([path[i-1]] if i else [-1]) + ([path[i+1]] if i+1 < len(path) else [9]):
                if neighbor == -1:
                    mask |= 8
                elif neighbor == 9:
                    mask |= 2
                else:
                    dr, dc = neighbor // 3 - tile // 3, neighbor % 3 - tile % 3
                    mask |= {(0, 1): 2, (0, -1): 8, (1, 0): 4, (-1, 0): 1}[(dr, dc)]
            self.wires[tile] = mask
            self.solution[tile] = mask
        for i in range(9):
            for _ in range(random.randrange(4)):
                self.wires[i] = self.rotate_mask(self.wires[i])
        if self.circuit()[1]:
            self.wires[0] = self.rotate_mask(self.wires[0])
        self.cursor = 0
        self.radar_shapes = [
            ['01100','11110','11111','01110','00100'],
            ['00100','01110','11111','01110','00100'],
            ['01110','11111','11110','01100','00100'],
            ['00110','01111','11111','11110','01100'],
            ['01100','11110','11011','01111','00110'],
            ['00100','01110','11110','11111','01100']]
        picks = random.sample(range(len(self.radar_shapes)), 4)
        self.radar_options = [self.radar_shapes[n] for n in picks]
        self.radar_correct = random.randrange(4)
        self.radar_target = self.radar_options[self.radar_correct]

    @staticmethod
    def rotate_mask(mask):
        return ((mask << 1) & 15) | (mask >> 3)

    def circuit(self):
        live = set()
        if not self.wires[0] & 8:
            return live, False
        todo = [0]
        directions = [(-1, 0, 1, 4), (0, 1, 2, 8), (1, 0, 4, 1), (0, -1, 8, 2)]
        while todo:
            tile = todo.pop()
            if tile in live:
                continue
            live.add(tile)
            r, c = divmod(tile, 3)
            for dr, dc, port, opposite in directions:
                rr, cc = r + dr, c + dc
                if 0 <= rr < 3 and 0 <= cc < 3:
                    neighbor = rr * 3 + cc
                    if self.wires[tile] & port and self.wires[neighbor] & opposite:
                        todo.append(neighbor)
        return live, 8 in live and bool(self.wires[8] & 2)

    def burst(self, x, y, color):
        for _ in range(14):
            self.particles.append([x, y, random.uniform(-60, 60), random.uniform(-70, 15), .7, color])

    def finish(self):
        self.scores[self.level] = max(self.scores[self.level] or 0, self.points)
        tier = 'bad' if self.crashed else 'great' if self.points == 5 else 'ok' if self.points >= 3 else 'bad'
        self.res_lines = self.voice(tier)
        self.scene = 'result'

    def hit(self, key):
        if self.scene == 'name':
            if key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif key == pygame.K_RETURN and self.name.strip():
                self.board.append({'name': self.name.strip().upper(), 'score': self.total(), 'crew': CREW[self.crew][0]})
                self.board = sorted(self.board, key=lambda r: r['score'], reverse=True)[:8]
                try:
                    tmp = self.board_path.with_suffix('.tmp')
                    tmp.write_text(json.dumps(self.board, indent=2))
                    os.replace(tmp, self.board_path)
                    self.message = ''
                except OSError:
                    self.message = 'Scores kept for this session (file unavailable).'
                self.scene = 'board'
            return
        if key == pygame.K_ESCAPE:
            self.scene = 'title'
            self.message = ''
            self.paused = False
            return
        if self.scene == 'play' and key == pygame.K_p:
            self.paused = not self.paused
            return
        if self.scene == 'play' and self.paused:
            return
        if self.scene == 'title':
            if key == pygame.K_RETURN:
                self.scene = 'crew'
            elif key == pygame.K_b:
                self.message = ''
                self.scene = 'board'
        elif self.scene == 'crew':
            if key in (pygame.K_LEFT, pygame.K_a):
                self.crew = (self.crew - 1) % 3
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.crew = (self.crew + 1) % 3
            elif key == pygame.K_RETURN:
                self.scores = [None] * 5
                self.from_ending = False
                self.brief(0)
        elif self.scene == 'brief' and key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.brief_t * 45 < len(CONTROL_BRIEF[self.mission]) + len(CREW_BRIEF[self.crew][self.level]) + 12:
                self.brief_t = 99.
            else:
                self.start()
        elif self.scene == 'result':
            if key == pygame.K_r:
                self.brief(self.level)
            elif key == pygame.K_RETURN:
                if self.level < 4 and not self.from_ending:
                    self.brief(self.level + 1)
                else:
                    self.go_ending()
        elif self.scene == 'ending':
            if key == pygame.K_RETURN:
                self.name = ''
                self.from_ending = False
                self.scene = 'name'
            elif pygame.K_1 <= key <= pygame.K_5:
                self.from_ending = True
                self.brief(key - pygame.K_1)
        elif self.scene == 'board' and key == pygame.K_RETURN:
            self.scene = 'title'
        elif self.scene == 'play':
            if self.mission == 'wires':
                r, c = divmod(self.cursor, 3)
                if key in (pygame.K_LEFT, pygame.K_a):
                    self.cursor = r * 3 + (c - 1) % 3
                elif key in (pygame.K_RIGHT, pygame.K_d):
                    self.cursor = r * 3 + (c + 1) % 3
                elif key in (pygame.K_UP, pygame.K_w):
                    self.cursor = ((r - 1) % 3) * 3 + c
                elif key in (pygame.K_DOWN, pygame.K_s):
                    self.cursor = ((r + 1) % 3) * 3 + c
                elif key == pygame.K_SPACE:
                    self.wires[self.cursor] = self.rotate_mask(self.wires[self.cursor])
                elif key == pygame.K_RETURN:
                    if not self.circuit()[1]:
                        self.message = 'No power at OUT. Follow the green path from IN.'
                    else:
                        self.points += 1
                        self.round += 1
                        self.burst(340, 180, GREEN)
                        self.message = 'POWER BANK ONLINE! +1'
                        if self.round == 5:
                            self.finish()
                        else:
                            self.setup_puzzle()
            elif self.mission == 'hop' and key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w) and self.jump == 0 and not self.crashed:
                self.vy = 190.
            elif self.mission == 'radar' and pygame.K_1 <= key <= pygame.K_4:
                pick = key - pygame.K_1
                if pick == self.radar_correct:
                    self.points += 1
                    self.round += 1
                    self.burst(240, 145, BLUE)
                    self.message = 'TARGET IDENTIFIED! +1'
                    if self.round == 5:
                        self.finish()
                    else:
                        self.setup_puzzle()
                else:
                    self.round += 1
                    self.burst(240, 145, RED)
                    self.message = f'WRONG! It was echo {self.radar_correct + 1}. No point.'
                    if self.round == 5:
                        self.finish()
                    else:
                        self.setup_puzzle()
            elif self.mission == 'shot' and key == pygame.K_SPACE and self.flash <= 0:
                success = abs(math.sin(self.phase) * 150) < 29
                self.points += int(success)
                self.shots += 1
                self.burst(400, 105, GREEN if success else RED)
                self.flash = .6
                self.message = 'DIRECT HIT! +1' if success else 'MISSED! Watch the green launch window.'
                if self.shots == 5:
                    self.finish()
            elif getattr(self, 'key_' + self.mission, None):
                getattr(self, 'key_' + self.mission)(key)

    def update(self, dt):
        self.t += dt
        for particle in self.particles[:]:
            particle[0] += particle[2] * dt
            particle[1] += particle[3] * dt
            particle[3] += 80 * dt
            particle[4] -= dt
            if particle[4] <= 0:
                self.particles.remove(particle)
        if self.scene == 'brief':
            self.brief_t += dt
        if self.scene != 'play' or self.paused:
            return
        if self.crashed:
            self.over -= dt
            if self.over <= 0:
                self.finish()
            return
        self.remaining -= dt
        self.elapsed += dt
        self.flash = max(0., self.flash - dt)
        if self.remaining <= 0:
            self.finish()
            return
        if self.remaining < 10 and not self.warned:
            self.warned = True
            self.message = f'HAVEN: Ten seconds, {CREW[self.crew][0]}!'
        keys = pygame.key.get_pressed()
        if self.mission == 'lift':
            if self.flash <= 0:
                self.x += ((keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])) * 170 * dt
                self.y += ((keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])) * 150 * dt
            self.x = max(25, min(435, self.x))
            self.y = max(70, min(219, self.y))
            self.spawn -= dt
            if self.spawn <= 0:
                self.spawn = .65
                self.objects.append({'x': random.randrange(30, 440), 'y': 48., 'fuel': random.random() < .6})
            player = pygame.Rect(self.x + 3, self.y, 15, 24)
            for obj in self.objects[:]:
                obj['y'] += 85 * dt
                if player.colliderect(pygame.Rect(obj['x'], obj['y'], 14, 14)):
                    self.objects.remove(obj)
                    if obj['fuel']:
                        self.points += 1
                        self.message = 'FUEL COLLECTED! +1'
                        self.burst(self.x + 10, self.y + 12, GREEN)
                        if self.points == 5:
                            self.finish()
                            return
                    elif self.flash <= 0:
                        self.remaining = max(0, self.remaining - 2)
                        self.flash = .65
                        self.message = 'METEOR HIT! -2 seconds'
                elif obj['y'] > 245:
                    self.objects.remove(obj)
        elif self.mission == 'hop':
            self.vy -= 320 * dt
            self.jump = max(0., self.jump + self.vy * dt)
            if self.jump == 0:
                self.vy = 0.
            self.spawn -= dt
            if self.spawn <= 0:
                # Pick this rock and the next one's speed together, so the next spawn
                # is timed to arrive at least 1.5s after this one (always jumpable).
                w, h = random.randint(14, 24), random.randint(13, 24)
                self.objects.append({'x': 490., 'w': w, 'h': h, 'v': self.next_v, 'counted': False})
                base = 105 + 6 * self.crossed
                self.next_v = base * random.uniform(.9, 1.15)
                arrive_now, arrive_next = 407 / self.objects[-1]['v'], 407 / self.next_v
                self.spawn = max(.3, arrive_now + random.uniform(1.5, 2.8) - arrive_next)
            for obj in self.objects[:]:
                obj['x'] -= obj['v'] * dt
                if pygame.Rect(85, 204 - self.jump, 10, 22).colliderect(pygame.Rect(obj['x'] + 2, 226 - obj['h'] + 2, obj['w'] - 4, obj['h'] - 2)):
                    self.crashed = True
                    self.over = 1.3
                    self.flash = 1.3
                    self.burst(90, 210 - self.jump, RED)
                    self.message = 'CRASH! GAME OVER'
                    return
                if obj['x'] + obj['w'] < 83 and not obj['counted']:
                    obj['counted'] = True
                    self.crossed += 1
                    self.points += 1
                    self.message = 'CLEAN JUMP! +1'
                    if self.crossed == 5:
                        self.finish()
                        return
                if obj['x'] < -30:
                    self.objects.remove(obj)
        elif self.mission == 'shot':
            self.phase += dt * 2.5
        else:
            tick = getattr(self, 'tick_' + self.mission, None)
            if tick:
                tick(dt, keys)

    # ---- crew missions: setup_* / tick_* / key_* / draw_* are looked up by mission name ----

    def settle(self, ok, good, bad):
        """Score one finished round; five rounds end the mission."""
        self.round += 1
        self.points += int(ok)
        self.message = good if ok else bad
        self.marks.append(ok)

    # DEBRIS SLALOM (NOVA)
    def setup_slalom(self):
        self.x, self.y = 90., 150.
        self.gap_prev = 150
        self.spawn = .6

    def tick_slalom(self, dt, keys):
        self.y += ((keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])) * 150 * dt
        self.y = max(52, min(212, self.y))
        self.spawn -= dt
        if self.spawn <= 0 and self.round < 5:
            self.round += 1
            self.spawn = 1.9
            gh = 66 - 4 * self.round
            top = random.randint(max(50, self.gap_prev - 100), min(246 - gh, self.gap_prev + 100))
            self.gap_prev = top
            self.objects.append({'x': 490., 'top': top, 'gh': gh, 'hit': False, 'counted': False, 'v': 125 + 10 * self.round})
        ship = pygame.Rect(int(self.x) + 4, int(self.y) + 5, 28, 16)
        for obj in self.objects[:]:
            obj['x'] -= obj['v'] * dt
            walls = (pygame.Rect(int(obj['x']), 46, 20, obj['top'] - 46), pygame.Rect(int(obj['x']), obj['top'] + obj['gh'], 20, 246 - obj['top'] - obj['gh']))
            if not obj['hit'] and any(ship.colliderect(w) for w in walls):
                obj['hit'] = True
                self.flash = .5
                self.burst(self.x + 30, self.y + 12, RED)
                self.message = 'DEBRIS HIT! No point for this gate.'
            if obj['x'] + 20 < self.x and not obj['counted']:
                obj['counted'] = True
                self.crossed += 1
                if not obj['hit']:
                    self.points += 1
                    self.message = 'CLEAN GATE! +1'
                if self.crossed == 5:
                    self.finish()
                    return
            if obj['x'] < -30:
                self.objects.remove(obj)

    def draw_slalom(self):
        self.text(f'GATE {min(self.crossed + 1, 5)}/5  /  UP + DOWN TO STEER', 240, 52, GOLD, 'small', True)
        for obj in self.objects:
            x = int(obj['x'])
            tone = (140, 74, 62) if obj['hit'] else (92, 76, 64)
            for y0, y1 in ((46, obj['top']), (obj['top'] + obj['gh'], 246)):
                pygame.draw.rect(self.screen, tone, (x, y0, 20, y1 - y0))
                pygame.draw.rect(self.screen, (60, 50, 44), (x, y0, 20, y1 - y0), 2)
                for k in range(y0 + 6, y1 - 4, 14):
                    pygame.draw.rect(self.screen, (120, 102, 84), (x + 4 + (k % 3) * 4, k, 5, 3))
            pygame.draw.rect(self.screen, GREEN, (x + 8, obj['top'] + 2, 4, obj['gh'] - 4), 1)
        if self.flash <= 0 or int(self.t * 15) % 2:
            self.rocket(int(self.x) - 2, int(self.y) - 4, 90)

    # ENGINE REPAIR (RUST)
    def setup_engine(self):
        self.charge, self.charging, self.armed, self.last_val = 0., False, False, None
        self.new_bolt()

    def new_bolt(self):
        self.zw = 26 - 3 * self.round
        self.zc = random.randint(45, 80)

    def tick_engine(self, dt, keys):
        down = keys[pygame.K_SPACE]
        if not down:
            self.armed = True
        if self.flash > 0:
            return
        if down and self.armed:
            self.charging = True
            self.charge = min(100., self.charge + 75 * dt)
            if self.charge >= 100:
                self.torque(100.)
        elif self.charging:
            self.torque(self.charge)

    def torque(self, value):
        ok = abs(value - self.zc) <= self.zw / 2 and value < 100
        self.last_val = value
        self.charging, self.charge, self.armed, self.flash = False, 0., False, .7
        self.burst(240, 112, GREEN if ok else RED)
        self.settle(ok, 'BOLT SECURED! +1', 'STRIPPED THREAD!' if value >= 100 else 'WRONG TORQUE! No point.')
        if self.round == 5:
            self.finish()
        else:
            self.new_bolt()

    def draw_engine(self):
        self.text(f'BOLT {min(self.round + 1, 5)}/5', 240, 52, GOLD, 'small', True)
        pygame.draw.circle(self.screen, (60, 70, 88), (240, 112), 42)
        pygame.draw.circle(self.screen, (31, 38, 56), (240, 112), 30)
        for i in range(5):
            a = i / 5 * math.tau - math.pi / 2
            bx, by = int(240 + math.cos(a) * 36), int(112 + math.sin(a) * 36)
            if i < len(self.marks):
                tone = GREEN if self.marks[i] else RED
            else:
                tone = GOLD if i == self.round else MUTED
            pygame.draw.circle(self.screen, tone, (bx, by), 6)
            pygame.draw.circle(self.screen, BG, (bx, by), 2)
        left, width = 95, 290
        self.box((left, 176, width, 22))
        zx = left + int((self.zc - self.zw / 2) / 100 * width)
        pygame.draw.rect(self.screen, GREEN, (zx, 177, int(self.zw / 100 * width), 20))
        pygame.draw.rect(self.screen, GOLD if self.charge < 95 else RED, (left + 1, 190, int(self.charge / 100 * (width - 2)), 7))
        shown = self.charge if self.charging else self.last_val if self.flash > 0 else None
        if shown is not None:
            pygame.draw.rect(self.screen, INK, (left + int(shown / 100 * width) - 1, 170, 3, 34))
        self.text('HOLD SPACE TO CHARGE - RELEASE IN THE GREEN', 240, 212, INK, 'small', True)

    # REACTOR BALANCE (RUST)
    def setup_reactor(self):
        self.gl = self.gr = 50.
        self.safe = 0.

    def tick_reactor(self, dt, keys):
        t = self.elapsed
        rise_l = 18 + 9 * math.sin(t * .9) + 4 * math.sin(t * 2.3 + 1)
        rise_r = 20 + 9 * math.sin(t * .7 + 2) + 4 * math.sin(t * 2.9)
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.gl = max(0., self.gl + (rise_l - (50 if left else 0)) * dt)
        self.gr = max(0., self.gr + (rise_r - (50 if right else 0)) * dt)
        if self.gl >= 100 or self.gr >= 100:
            self.gl, self.gr = (70. if self.gl >= 100 else self.gl), (70. if self.gr >= 100 else self.gr)
            self.safe = max(0., self.safe - 3)
            self.flash = .5
            self.message = 'OVERHEAT! -3 safe seconds'
        if 30 <= self.gl <= 70 and 30 <= self.gr <= 70:
            self.safe += dt
        earned = min(5, int(self.safe / 7))
        if earned > self.points:
            self.points = earned
            self.burst(240, 150, GREEN)
            self.message = 'REACTOR STABLE! +1'
            if self.points == 5:
                self.finish()

    def draw_reactor(self):
        self.text(f'STABLE {self.safe:4.1f}s / NEXT POINT AT {7 * (self.points + 1)}s', 240, 52, GOLD, 'small', True)
        for x, val, label in ((150, self.gl, 'LEFT / A'), (290, self.gr, 'RIGHT / D')):
            self.box((x, 70, 40, 150), (12, 20, 32))
            y_of = lambda v: 219 - int(min(v, 100) / 100 * 148)
            pygame.draw.rect(self.screen, (30, 70, 50), (x + 1, y_of(70), 38, y_of(30) - y_of(70)))
            safe = 30 <= val <= 70
            pygame.draw.rect(self.screen, GREEN if safe else RED, (x + 6, y_of(val), 28, 219 - y_of(val)))
            self.text(label, x + 20, 224, MUTED, 'small', True)
            self.text(f'{int(val)}', x + 20, 74, INK, 'small', True)
        self.text('HOLD KEY', 240, 108, BLUE, 'small', True)
        self.text('TO VENT', 240, 120, BLUE, 'small', True)
        self.text('KEEP BOTH', 240, 142, GREEN, 'small', True)
        self.text('IN GREEN', 240, 154, GREEN, 'small', True)

    # CANNON CALIBRATION (RUST)
    def setup_calib(self):
        self.angle = 45.
        self.hold_t = 0.
        self.new_target()

    def new_target(self):
        self.target = random.randint(15, 80)
        while abs(self.target - self.angle) < 12:
            self.target = random.randint(15, 80)

    def key_calib(self, key):
        step = {pygame.K_LEFT: -1, pygame.K_a: -1, pygame.K_RIGHT: 1, pygame.K_d: 1,
                pygame.K_DOWN: -10, pygame.K_s: -10, pygame.K_UP: 10, pygame.K_w: 10}
        if key in step:
            self.angle = max(0, min(90, round(self.angle) + step[key]))
            self.hold_t = 0.
        elif key == pygame.K_RETURN:
            ok = abs(round(self.angle) - self.target) <= 2
            self.burst(150, 190, GREEN if ok else RED)
            self.settle(ok, 'ON TARGET! +1', f'OFF TARGET! You set {round(self.angle)}, needed {self.target}. No point.')
            if self.round == 5:
                self.finish()
            else:
                self.new_target()

    def tick_calib(self, dt, keys):
        direction = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        if direction:
            self.hold_t += dt
            if self.hold_t > .3:
                self.angle = max(0., min(90., self.angle + direction * 30 * dt))
        else:
            self.hold_t = 0.

    def draw_calib(self):
        self.text(f'SHOT {min(self.round + 1, 5)}/5', 240, 52, GOLD, 'small', True)
        px, py = 120, 215
        pygame.draw.line(self.screen, MUTED, (px - 20, py), (px + 130, py), 2)
        for deg in range(0, 91, 10):
            a = math.radians(deg)
            pygame.draw.line(self.screen, MUTED, (px + math.cos(a) * 92, py - math.sin(a) * 92), (px + math.cos(a) * 102, py - math.sin(a) * 102), 2)
            self.text(str(deg), int(px + math.cos(a) * 118), int(py - math.sin(a) * 118) - 5, MUTED, 'small', True)
        a = math.radians(self.angle)
        pygame.draw.line(self.screen, CREW[self.crew][1], (px, py), (px + math.cos(a) * 85, py - math.sin(a) * 85), 7)
        pygame.draw.circle(self.screen, INK, (px, py), 9)
        self.box((290, 70, 170, 110))
        self.text('TARGET', 375, 80, MUTED, 'small', True)
        self.text(f'{self.target} DEG', 375, 94, GOLD, 'big', True)
        self.text('YOUR ANGLE', 375, 132, MUTED, 'small', True)
        close = abs(round(self.angle) - self.target) <= 2
        self.text(f'{round(self.angle)} DEG', 375, 146, GREEN if close else INK, center=True)
        self.text('ARROWS TURN / ENTER LOCKS', 375, 200, GREEN, 'small', True)

    # GREENHOUSE RESCUE (MOSS)
    def setup_greenhouse(self):
        self.queue = [random.choice(['seed', 'spore']) for _ in range(15)]
        self.spawned = self.sorted_n = 0
        self.batch_ok = True
        self.spawn = .5

    def tick_greenhouse(self, dt, keys):
        speed = 95 + 10 * (self.sorted_n // 3)
        self.spawn -= dt
        if self.spawn <= 0 and self.spawned < 15:
            self.objects.append({'x': 480., 'kind': self.queue[self.spawned]})
            self.spawned += 1
            self.spawn = 1.3
        for obj in self.objects[:]:
            obj['x'] -= speed * dt
            if obj['x'] < 96:
                self.objects.remove(obj)
                self.sort_item(obj, None)
                if self.scene != 'play':
                    return

    def key_greenhouse(self, key):
        choice = 'spore' if key in (pygame.K_UP, pygame.K_w) else 'seed' if key in (pygame.K_DOWN, pygame.K_s) else None
        ready = [o for o in self.objects if o['x'] <= 430]
        if choice and ready:
            front = min(ready, key=lambda o: o['x'])
            self.objects.remove(front)
            self.sort_item(front, choice)

    def sort_item(self, obj, choice):
        ok = choice == obj['kind']
        self.marks.append(ok)
        self.batch_ok = self.batch_ok and ok
        self.sorted_n += 1
        self.burst(70, 120 if choice == 'spore' else 200, GREEN if ok else RED)
        self.message = 'SORTED!' if ok else ('MISSED ONE! Batch ruined.' if choice is None else 'WRONG BIN! Batch ruined.')
        if self.sorted_n % 3 == 0:
            if self.batch_ok:
                self.points += 1
                self.message = 'BATCH CLEAN! +1'
            else:
                self.message = 'BATCH CONTAMINATED. No point.'
            self.batch_ok = True
            self.marks = []
        if self.sorted_n == 15:
            self.finish()

    def draw_greenhouse(self):
        batch = min(self.sorted_n // 3 + 1, 5)
        self.text(f'BATCH {batch}/5', 240, 52, GOLD, 'small', True)
        for i in range(3):
            tone = (54, 65, 78) if i >= len(self.marks) else GREEN if self.marks[i] else RED
            pygame.draw.rect(self.screen, tone, (228 + i * 14, 66, 10, 8))
        pygame.draw.rect(self.screen, (22, 29, 44), (0, 150, W, 22))
        for x in range(0, W + 20, 20):
            pygame.draw.rect(self.screen, (44, 54, 74), ((x - int(self.t * 60)) % (W + 20) - 10, 160, 10, 2))
        pygame.draw.rect(self.screen, (120, 40, 40), (0, 150, 92, 22))
        for x in range(4, 92, 12):
            pygame.draw.polygon(self.screen, RED, [(x, 150), (x + 6, 150), (x + 3, 158)])
        self.box((14, 92, 78, 44), (36, 20, 44), PURPLE)
        self.text('SPORES', 53, 100, PURPLE, 'small', True)
        self.text('[UP]', 53, 116, INK, 'small', True)
        self.box((14, 186, 78, 44), (18, 40, 30), GREEN)
        self.text('SEEDS', 53, 194, GREEN, 'small', True)
        self.text('[DOWN]', 53, 210, INK, 'small', True)
        ready = [o for o in self.objects if o['x'] <= 430]
        front = min(ready, key=lambda o: o['x']) if ready else None
        for obj in self.objects:
            x, cy = int(obj['x']), 140
            if obj['kind'] == 'seed':
                pygame.draw.ellipse(self.screen, GREEN, (x, cy - 7, 18, 14))
                pygame.draw.line(self.screen, (80, 120, 40), (x + 3, cy), (x + 15, cy), 2)
            else:
                for dx, dy in ((-3, 0), (21, 0), (9, -10), (9, 10), (0, -7), (18, 7), (0, 7), (18, -7)):
                    pygame.draw.rect(self.screen, PURPLE, (x + dx - 1, cy + dy - 1, 4, 4))
                pygame.draw.circle(self.screen, PURPLE, (x + 9, cy), 8)
                pygame.draw.circle(self.screen, BG, (x + 9, cy), 3)
            if obj is front:
                pygame.draw.polygon(self.screen, GOLD, [(x + 9, 118), (x + 3, 110), (x + 15, 110)])
        self.text('UP = SPORE BIN    DOWN = SEED TRAY', 300, 200, GREEN, 'small', True)
        self.text('Spore: spiky + dark core. Seed: smooth + stripe.', 300, 218, MUTED, 'small', True)

    # SIGNAL DECODE (MOSS)
    PAD_COLORS = [BLUE, GOLD, GREEN, RED]

    def setup_decode(self):
        self.lengths = [3, 4, 4, 5, 6]
        self.seq, self.inp, self.show_t, self.lit, self.lit_t = [], 0, 0., None, 0.
        self.dstate, self.pause_t = 'pause', 1.0

    def new_signal(self):
        self.seq = [random.randrange(4) for _ in range(self.lengths[self.round])]
        self.dstate, self.show_t, self.inp = 'show', 0., 0
        self.message = 'WATCH THE SIGNAL...'

    def tick_decode(self, dt, keys):
        self.lit_t = max(0., self.lit_t - dt)
        if self.dstate == 'pause':
            self.pause_t -= dt
            if self.pause_t <= 0:
                if self.round >= 5:
                    self.finish()
                else:
                    self.new_signal()
        elif self.dstate == 'show':
            self.show_t += dt
            if int(self.show_t / .75) >= len(self.seq):
                self.dstate = 'input'
                self.message = 'YOUR TURN: repeat the signal'

    def key_decode(self, key):
        pads = {pygame.K_UP: 0, pygame.K_w: 0, pygame.K_RIGHT: 1, pygame.K_d: 1, pygame.K_DOWN: 2, pygame.K_s: 2, pygame.K_LEFT: 3, pygame.K_a: 3}
        if self.dstate != 'input' or key not in pads:
            return
        pad = pads[key]
        self.lit, self.lit_t = pad, .25
        if pad == self.seq[self.inp]:
            self.inp += 1
            if self.inp == len(self.seq):
                self.round += 1
                self.points += 1
                self.burst(240, 148, GREEN)
                self.message = 'SIGNAL LOCKED! +1'
                self.dstate, self.pause_t = 'pause', 1.0
        else:
            self.round += 1
            self.burst(240, 148, RED)
            self.message = 'WRONG SIGNAL! Round lost. No point.'
            self.dstate, self.pause_t = 'pause', 1.2

    def draw_decode(self):
        n = self.lengths[min(self.round, 4)]
        self.text(f'SIGNAL {min(self.round + 1, 5)}/5  -  {n} SYMBOLS', 240, 52, GOLD, 'small', True)
        lit = None
        if self.dstate == 'show' and (self.show_t % .75) < .5 and int(self.show_t / .75) < len(self.seq):
            lit = self.seq[int(self.show_t / .75)]
        elif self.lit_t > 0:
            lit = self.lit
        spots = [(240, 100), (294, 148), (240, 196), (186, 148)]
        tips = [[(0, -14), (-12, 10), (12, 10)], [(14, 0), (-10, -12), (-10, 12)], [(0, 14), (-12, -10), (12, -10)], [(-14, 0), (10, -12), (10, 12)]]
        for i, (cx, cy) in enumerate(spots):
            color = self.PAD_COLORS[i]
            tone = color if lit == i else tuple(c // 4 for c in color)
            self.box((cx - 22, cy - 22, 44, 44), tone, color if lit == i else MUTED)
            pygame.draw.polygon(self.screen, INK if lit == i else MUTED, [(cx + dx, cy + dy) for dx, dy in tips[i]])
        label = 'WATCH' if self.dstate == 'show' else 'YOUR TURN' if self.dstate == 'input' else '...'
        self.text(label, 240, 140, GOLD, 'small', True)
        for k in range(len(self.seq)):
            tone = GREEN if k < self.inp else (54, 65, 78)
            pygame.draw.rect(self.screen, tone, (240 - len(self.seq) * 5 + k * 10, 154, 7, 5))

    def voice(self, tier):
        control = random.choice(CONTROL_TIER[tier])
        crew = random.choice(CREW_TIER[self.crew][tier])
        return f'HAVEN: {control}', f'{CREW[self.crew][0]}: {crew}'

    def go_ending(self):
        won = self.total() >= 20
        self.end_lines = (f'HAVEN: {random.choice(CONTROL_END[won])}', f'{CREW[self.crew][0]}: {random.choice(CREW_END[self.crew][won])}')
        self.scene = 'ending'

    def rock(self, x, y, scale=3, shape=None, color=GOLD):
        shape = shape or ['01100','11110','11111','01110','00100']
        shade = tuple(max(0, c - 55) for c in color)
        for r, line in enumerate(shape):
            for c, bit in enumerate(line):
                if bit == '1':
                    tone = shade if r > 2 or c > 2 else color
                    pygame.draw.rect(self.screen, tone, (x+c*scale, y+r*scale, scale, scale))
        pygame.draw.rect(self.screen, shade, (x+scale, y+scale, scale, scale))

    def rocket(self, x, y, angle=0):
        color = CREW[self.crew][1]
        target, ox, oy = self.screen, x, y
        if angle:
            target = pygame.Surface((26, 36), pygame.SRCALPHA)
            x = y = 0
        sprite = ['00011000','00122100','01233210','01233210','01444410','01444410','11444411','11011011','00055000','00055000']
        palette = {'1':MUTED,'2':INK,'3':BLUE,'4':color,'5':GOLD}
        for r, line in enumerate(sprite):
            for c, bit in enumerate(line):
                if bit != '0':
                    pygame.draw.rect(target, palette[bit], (x+c*3, y+r*3, 3, 3))
        pygame.draw.rect(target, RED, (x+9, y+30, 6, 3+int(self.t*12)%4))
        if angle:
            self.screen.blit(pygame.transform.rotate(target, -angle), (ox, oy))

    def station(self):
        pygame.draw.rect(self.screen, (21, 28, 45), (8, 48, 464, 197))
        for x in (18, 398):
            self.box((x, 80, 62, 92), (11, 25, 39), (56, 72, 86))
            for y in range(89, 163, 14):
                pygame.draw.rect(self.screen, BLUE, (x+8, y, 30, 3))
                pygame.draw.rect(self.screen, GREEN if int(self.t*3+y)%3 else GOLD, (x+44, y, 5, 3))
        for x in range(14, 469, 22):
            pygame.draw.rect(self.screen, GOLD if x%44 else MUTED, (x, 244, 10, 3))
        for x, y in [(14,54),(463,54),(14,229),(463,229)]:
            pygame.draw.rect(self.screen, MUTED, (x,y,3,3))

    def background(self):
        for y in range(0, H, 3):
            pygame.draw.rect(self.screen, (12+y//40, 16+y//35, 33+y//19), (0,y,W,3))
        for i, (x, y, size) in enumerate(self.stars):
            xx = int((x - self.t * (2 if size == 1 else 5)) % W)
            shade = INK if size == 2 and int(self.t*2+i)%4 else MUTED
            pygame.draw.rect(self.screen, shade, (xx,y,size,size))
        if self.scene == 'play' and self.mission in ('wires', 'radar', 'engine', 'reactor'):
            self.station()

    def hud(self):
        pygame.draw.rect(self.screen, PANEL, (0, 0, W, 44))
        self.text(f'0{self.level + 1} {self.info[0]}', 12, 8, GREEN)
        self.text(f'{CREW[self.crew][0]}  {self.total():02}/25', 12, 25, MUTED, 'small')
        self.text(f'{self.points}/5 PTS', 280, 12, GOLD)
        self.text(f'{max(0, math.ceil(self.remaining)):02}s', 430, 12, RED if self.remaining < 10 else INK)
        pygame.draw.rect(self.screen, MUTED, (0, 43, W, 1))
        for i in range(5):
            pygame.draw.rect(self.screen, GOLD if i < self.points else (54,65,78), (346+i*12, 26, 8, 6))

    def draw(self):
        self.background()
        if self.scene == 'title':
            self.text('A FIVE MINUTE PLANET RESCUE', 240, 25, GREEN, 'small', True)
            self.text('EARTH // 25', 240, 55, INK, 'big', True)
            self.earth(240, 132)
            self.astronaut(155, 125, 2)
            self.text('5 MISSIONS. 25 POINTS. ONE EARTH.', 240, 185, GOLD, center=True)
            if int(self.t * 2) % 2 == 0:
                self.text('PRESS ENTER TO START', 240, 214, GREEN, center=True)
            self.text('[B] SCORES  [ESC] TITLE  [F11] WINDOW', 240, 248, MUTED, 'small', True)
        elif self.scene == 'crew':
            self.text('CHOOSE YOUR CREW', 240, 26, INK, 'big', True)
            self.text('Everyone shares missions 1-2. Then your crew takes its own path.', 240, 65, MUTED, 'small', True)
            for i, (name, color) in enumerate(CREW):
                x = 70 + i * 120
                self.box((x, 92, 100, 111), border=color if i == self.crew else MUTED)
                self.astronaut(x + 35, 108, 3, color)
                self.text(name, x + 50, 164, color, center=True)
                if i == self.crew:
                    self.text('> READY <', x + 50, 184, GOLD, 'small', True)
            self.text(CREW_BLURB[self.crew], 240, 214, CREW[self.crew][1], 'small', True)
            self.text('LEFT / RIGHT TO CHOOSE   ENTER TO LAUNCH', 240, 240, GREEN, 'small', True)
        elif self.scene == 'brief':
            days = 5 - self.level
            self.text(f'LEVEL {self.level + 1} / 5', 14, 12, GREEN, 'small')
            self.text(f'IMPACT IN {days} DAY' + ('S' if days > 1 else ''), 466, 12, RED if days <= 2 else GOLD, 'small', right=True)
            self.text(self.info[0], 240, 26, INK, 'big', True)
            self.box((15, 66, 450, 94))
            control = textwrap.wrap(CONTROL_BRIEF[self.mission], 68)
            crew = textwrap.wrap(f'{CREW[self.crew][0]}: {CREW_BRIEF[self.crew][self.level]}', 68)
            budget = int(self.brief_t * 45)
            blink = int(self.t * 3) % 2 and budget < sum(map(len, control + crew))
            self.text('HAVEN CONTROL' + (' ...' if blink else ''), 24, 71, GOLD, 'small')
            y = 86
            for lines, color in ((control, INK), (crew, CREW[self.crew][1])):
                for line in lines:
                    self.text(line[:max(0, budget)], 24, y, color, 'small')
                    budget -= len(line)
                    y += 12
                y += 6
            self.box((15, 166, 450, 40), (21, 28, 45))
            self.text(self.info[2], 240, 172, INK, 'small', True)
            self.text(self.info[3], 240, 188, GOLD, 'small', True)
            self.text('60 SECONDS / UP TO 5 POINTS', 240, 214, MUTED, 'small', True)
            self.text('PRESS ENTER', 240, 236, GREEN, center=True)
        elif self.scene == 'play':
            self.hud()
            if self.mission == 'lift':
                for obj in self.objects:
                    x, y = int(obj['x']), int(obj['y'])
                    if obj['fuel']:
                        self.box((x, y, 12, 14), GREEN, INK)
                        pygame.draw.rect(self.screen, BG, (x + 4, y + 4, 4, 6))
                    else:
                        self.rock(x, y, 3, color=RED)
                if self.flash <= 0 or int(self.t * 15) % 2:
                    self.rocket(int(self.x)-2, int(self.y)-4)
            elif self.mission == 'wires':
                self.text(f'POWER BANK {self.round + 1}/5', 240, 52, GOLD, 'small', True)
                live, connected = self.circuit()
                self.text('IN >', 127, 87, GREEN, 'small')
                self.text('> OUT', 307, 175, GREEN if connected else RED, 'small')
                for i, wire in enumerate(self.wires):
                    r, col = divmod(i, 3)
                    x, y = 166 + col*44, 68 + r*44
                    self.box((x,y,42,42), (24,35,49), GOLD if i == self.cursor else (60,76,92))
                    color = GREEN if i in live else BLUE
                    cx, cy = x+21, y+21
                    for bit, dx, dy in [(1,0,-20),(2,20,0),(4,0,20),(8,-20,0)]:
                        if wire & bit:
                            pygame.draw.line(self.screen, (8,14,22), (cx+1,cy+2), (cx+dx+1,cy+dy+2), 6)
                            pygame.draw.line(self.screen, color, (cx,cy), (cx+dx,cy+dy), 3)
                    pygame.draw.rect(self.screen, INK if i in live else MUTED, (cx-2,cy-2,5,5))
                self.text('ARROWS move / SPACE rotate / ENTER test', 240, 213, INK, 'small', True)
                self.text('Join IN to OUT. Green tiles carry power.', 240, 231, GREEN, 'small', True)
            elif self.mission == 'hop':
                self.earth(405, 95, 28)
                for layer, speed, color in [(0,8,(36,43,64)),(1,18,(56,63,83))]:
                    offset = int(self.elapsed*speed)%160
                    for x in range(-160,640,160):
                        pygame.draw.polygon(self.screen,color,[(x-offset,227),(x+60-offset,155+layer*28),(x+120-offset,188+layer*12),(x+170-offset,227)])
                pygame.draw.rect(self.screen, MUTED, (0, 227, 480, 17))
                pygame.draw.line(self.screen, INK, (0,227),(480,227))
                for x in range(20,480,90):
                    pygame.draw.ellipse(self.screen, (64,74,94), ((x-int(self.elapsed*45))%480,233,24,7))
                self.box((418,207,35,13), BLUE, INK)
                pygame.draw.rect(self.screen, GOLD, (431,197,12,10))
                for x in (423,445):
                    pygame.draw.rect(self.screen,BG,(x,220,7,7))
                for x in range(0, W, 28):
                    pygame.draw.rect(self.screen, PANEL, (int((x - self.elapsed * 105) % 480), 232, 8, 3))
                if not self.crashed or int(self.t * 15) % 2:
                    self.astronaut(80, int(202 - self.jump), 2, walk=self.jump == 0)
                for obj in self.objects:
                    ox, w, h = obj['x'], obj['w'], obj['h']
                    pygame.draw.polygon(self.screen, GOLD, [(ox, 226), (ox + 2, 226 - h * .6), (ox + w * .65, 226 - h), (ox + w, 226 - h * .3), (ox + w, 226)])
                self.text(f'ROCKS {self.crossed}/5  /  SPACE TO JUMP', 240, 60, GOLD, 'small', True)
            elif self.mission == 'radar':
                self.text(f'SCAN {self.round+1}/5: FIND THE SAME OUTLINE', 240, 54, GOLD, 'small', True)
                self.box((201,72,78,64), (12,29,40), BLUE)
                self.text('TARGET',240,76,GREEN,'small',True)
                self.rock(225,94,6,self.radar_target,BLUE)
                pygame.draw.line(self.screen, BLUE, (90,144),(390,144),1)
                for i, shape in enumerate(self.radar_options):
                    x = 84+i*82
                    self.box((x,151,66,70), (12,26,38), MUTED)
                    self.rock(x+18,159,6,shape,GOLD)
                    self.text(str(i+1), x+33,198,INK,center=True)
                self.text('PRESS 1 / 2 / 3 / 4 - TARGET STAYS VISIBLE',240,234,GREEN,'small',True)
            elif self.mission == 'shot':
                self.earth(70, 122, 25)
                self.rock(380,85,9)
                self.rocket(130,104)
                if self.flash > 0:
                    pygame.draw.line(self.screen,GREEN,(151,106),(398,105),2)
                pygame.draw.line(self.screen, MUTED, (100, 122), (368, 105), 1)
                self.box((75, 166, 330, 21))
                pygame.draw.rect(self.screen, GREEN, (211, 167, 58, 19))
                x = int(240 + math.sin(self.phase) * 150)
                pygame.draw.rect(self.screen, INK, (x - 2, 159, 4, 35))
                self.text(f'SHOTS LEFT {5 - self.shots} / SPACE TO FIRE', 240, 217, GOLD, 'small', True)
            else:
                getattr(self, 'draw_' + self.mission)()
            if self.paused:
                self.box((150, 100, 180, 60), border=GOLD)
                self.text('PAUSED', 240, 112, GOLD, center=True)
                self.text('P: RESUME   ESC: QUIT', 240, 136, MUTED, 'small', True)
            pygame.draw.rect(self.screen, BG, (0, 248, W, 22))
            self.text(self.message, 240, 253, GREEN, 'small', True)
        elif self.scene == 'result':
            earned = self.points >= 3 and not self.crashed
            self.text('GAME OVER' if self.crashed else 'PERFECT RUN!' if self.points == 5 else 'LEVEL COMPLETE' if earned else 'MISSION FAILED', 240, 22, GREEN if earned else RED, center=True)
            self.text(f'{self.points} / 5 POINTS', 240, 40, GOLD, 'big', True)
            self.astronaut(80, 88, 4, walk=True)
            self.box((155, 84, 255, 56), border=GREEN if earned else RED)
            if earned:
                self.text('* ' + self.info[1] + ' BADGE *', 282, 96, GREEN, center=True)
                self.text(f'PRIZE CHECKPOINT {self.level + 1} UNLOCKED', 282, 120, INK, 'small', True)
            else:
                self.text('NO BADGE YET', 282, 96, RED, center=True)
                self.text('YOU HIT A ROCK - PRESS R' if self.crashed else 'SCORE 3 POINTS TO EARN IT - PRESS R', 282, 120, INK, 'small', True)
            self.text(self.res_lines[0], 240, 150, GOLD, 'small', True)
            self.text(self.res_lines[1], 240, 164, CREW[self.crew][1], 'small', True)
            self.text(self.info[4], 240, 186, MUTED, 'small', True)
            self.text(f'TOTAL {self.total():02}/25  |  RESCUE TARGET 20', 240, 208, GOLD, center=True)
            self.text(('ENTER: BACK TO RESULTS' if self.from_ending else 'ENTER: CONTINUE') + '   R: RETRY (BEST SCORE KEPT)', 240, 242, GREEN, 'small', True)
        elif self.scene == 'ending':
            won = self.total() >= 20
            self.text('EARTH SAVED!' if won else 'ONE MORE CHANCE', 240, 23, GREEN if won else GOLD, 'big', True)
            self.earth(240, 96, 33)
            self.text(f'{self.total():02} / 25 POINTS', 240, 134, GOLD, 'big', True)
            self.text('PLANET PROTECTOR' if won else 'Reach 20 points to change the asteroid path.', 240, 170, INK, 'small', True)
            self.text(self.end_lines[0], 240, 192, GOLD, 'small', True)
            self.text(self.end_lines[1], 240, 207, CREW[self.crew][1], 'small', True)
            self.text('1-5: RETRY LEVEL   ENTER: SAVE SCORE', 240, 242, GREEN, 'small', True)
        elif self.scene == 'name':
            self.text('SIGN THE CREW LOG', 240, 43, INK, 'big', True)
            self.text('TYPE YOUR NAME / UP TO 10 CHARACTERS', 240, 100, MUTED, 'small', True)
            self.box((140, 125, 200, 40), border=GREEN)
            self.text(self.name + ('_' if int(self.t * 2) % 2 else ''), 240, 135, GOLD, center=True)
            self.text('ENTER: SAVE TO LOCAL SCOREBOARD', 240, 216, GREEN, 'small', True)
        elif self.scene == 'board':
            self.text('HALL OF HEROES', 240, 15, GOLD, 'big', True)
            self.text('RANK  CREW NAME     PILOT        POINTS', 240, 54, MUTED, 'small', True)
            if not self.board:
                self.text('No heroes yet. Your name could be first.', 240, 113, INK, 'small', True)
            for i, row in enumerate(self.board):
                y = 77 + i * 18
                if i % 2 == 0:
                    pygame.draw.rect(self.screen, PANEL, (50, y - 2, 380, 17))
                self.text(f'{i + 1:02}', 62, y, GOLD, 'small')
                self.text(row['name'][:10], 102, y, INK, 'small')
                self.text(row.get('crew', 'NOVA'), 247, y, dict(CREW).get(row.get('crew'), BLUE), 'small')
                self.text(f'{row["score"]:02}/25' + (' *' if row['score'] >= 20 else ''), 354, y, GREEN, 'small')
            self.text(self.message or 'ENTER: TITLE   * = EARTH SAVED', 240, 247, GREEN, 'small', True)
        for x,y,vx,vy,life,color in self.particles:
            pygame.draw.rect(self.screen,color,(int(x),int(y),2,2))
        size = self.window.get_size()
        scale = min(size[0] / W, size[1] / H)
        sw, sh = max(W, int(W * scale)), max(H, int(H * scale))
        scaled = pygame.transform.scale(self.screen, (sw, sh))
        self.window.fill((0, 0, 0))
        self.window.blit(scaled, ((size[0] - sw) // 2, (size[1] - sh) // 2))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000, .05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and (event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)):
                    self.toggle_fullscreen()
                elif event.type == pygame.KEYDOWN:
                    was_name = self.scene == 'name'
                    self.hit(event.key)
                    if was_name and self.scene == 'name' and event.key not in (pygame.K_RETURN, pygame.K_BACKSPACE) and event.unicode.isascii() and (event.unicode.isalnum() or event.unicode == ' ') and len(self.name) < 10 and not (event.unicode == ' ' and not self.name):
                        self.name += event.unicode.upper()
            self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == '__main__':
    Game().run()
