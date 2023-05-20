import pygame
import time
import sys
import math
import structure
import button
import draw
import physics

SELECTOR = 0
POINT = 1
FIXED = 2
BEAM = 3


class App:
    def __init__(self, window_size):
        self.locked_fixed = True  # for now to stop fixed nodes being placed at
        # different heights so that the calculations are easier

        self.resolved = False  # used so that the arrows can be drawn at the correct times

        self.nodes = []
        self.beams = []
        self.fixed = []

        self.selected = SELECTOR  # this is the selected mode chosen from the buttons
        self.selection_box_start = None  # the selections box requires a start position
        self.time_of_selection = 0  # initialising the variable used to determine whether it is a click or drag
        self.selected_structures = []  # the selection tool can select multiple objects
        self.dragging_selected = False  # this is so that the objects selected can be moved
        self.selected_node = None  # this is used for the beam so that it can latch onto points

        self.grid_snapping = False  # for grid snapping
        self.dragging = False  # this will be true when right click is held down (moving canvas)
        self.last_mouse_position = (0, 0)  # used for figuring out how much the mouse has moved
        self.screen_offset = (0, 0)  # the current offset of the centre of the grid to the centre of the screen 
        self.scale = 50  # pixels per distance 

        pygame.init()

        self._window_size = window_size
        self.canvas = pygame.display.set_mode(window_size)
        self.clock = pygame.time.Clock()

        self.bg_colour = (255, 255, 255)
        select = button.Button(self.canvas, "Select", (10, 10), False, self.change_selection, SELECTOR)
        point = button.Button(self.canvas, "Point", (160, 10), False, self.change_selection, POINT)
        fixed = button.Button(self.canvas, "Fixed", (310, 10), False, self.change_selection, FIXED)
        beam = button.Button(self.canvas, "Beam", (460, 10), False, self.change_selection, BEAM)
        resolve = button.Button(self.canvas, "Resolve", (610, 10), False, self.resolve)
        def snap():
            self.grid_snapping = not self.grid_snapping
        snapping = button.Button(self.canvas, "Grid", (800, 10), True, snap)
        self.buttons = [select, point, fixed, beam, resolve, snapping]
        self.top_bar_height = 80
        self.top_bar = pygame.Rect(0, 0, window_size[0], self.top_bar_height)

    def change_selection(self, selection):
        """Function for changing what is currently selected - used by the buttons."""
        if self.selected_node is not None:
            self.selected_node = None  # unselecting the node from the beam
        self.selected = selection

    def draw(self):
        """Draws anything that needs to be drawn to the screen"""
        self.canvas.fill(self.bg_colour)
        self.draw_grid()
        self.draw_structures()

        # draw any force arrows
        if self.resolved:
            for i in self.fixed:
                draw.force_arrow(self.canvas, self.coords_to_pos(i.position), math.pi/2, i.vertical_force, self.scale)

        # draw the top bar
        pygame.draw.rect(self.canvas, (200, 200, 200), self.top_bar)
        # draw the buttons
        for button in self.buttons:
            button.draw()
        # draw the item being held
        if self.selected == POINT:
            draw.node(self.canvas, pygame.mouse.get_pos())
        elif self.selected == FIXED:
            draw.fixed(self.canvas, pygame.mouse.get_pos())
        elif self.selected == BEAM:
            if self.selected_node is None:
                draw.beam_selector(self.canvas, pygame.mouse.get_pos())
            else:
                draw.beam(self.canvas, self.coords_to_pos(self.selected_node.position),
                          pygame.mouse.get_pos())
        elif self.selected == SELECTOR and self.selection_box_start is not None:
            draw.selector_box(self.canvas, self.selection_box_start, pygame.mouse.get_pos())



    def resolve(self):
        """Resolves the forces"""
        if physics.check_complete(self.nodes, self.fixed, self.beams):
            physics.calculate_fixed(self.nodes, self.fixed, self.beams)
            self.resolved = True
            print([i.vertical_force for i in self.fixed])

    def pos_to_coords(self, pos: tuple) -> tuple:
        """Returns the coordinates of a point given its position on the screen"""
        cx, cy = [i/2 for i in self._window_size]  # finding the centre x and y 
        x, y = pos
        x = (x - cx - self.screen_offset[0])/self.scale  # working out the x position  
        y = (cy + self.screen_offset[1] - y)/self.scale  # y position works differently as y is flipped
        return x, y

    def coords_to_pos(self, coords: tuple) -> tuple:
        """Returns the position on the screen of a point given its coordinates"""
        cx, cy = [i/2 for i in self._window_size]  # finding the centre x and y 
        x, y = coords
        x = x*self.scale + cx + self.screen_offset[0]  # working out the x position 
        y = cy + self.screen_offset[1] - y*self.scale  # y position works differently as y is flipped
        return x, y

    def nearest_node(self, coords: tuple):
        """Returns the nearst nde or fixed node to a given point 
        (using its coordinates not its position on the screen)"""
        x, y = coords
        closest = None
        distance = math.inf
        for i in self.nodes + self.fixed:
            x1, y1 = i.position  # extract the coordinates of the node
            temp_distance = ((x1-x)**2 + (y1-y)**2)**(1/2)  # use pythagoras to find the distance
            if temp_distance < distance:  # if this is closer than the previous closest
                closest = i  # then put this as the closest
                distance = temp_distance
        return closest


    def place(self):
        """Create an instance of the selected item and add it to the corresponding place"""
        coords = self.pos_to_coords(pygame.mouse.get_pos())
        
        if self.selected == POINT:
            if self.grid_snapping:
                x, y = coords
                coords = round(x), round(y)
            self.nodes.append(structure.Node(coords))

        elif self.selected == FIXED:
            if self.grid_snapping:
                x, y = coords
                coords = round(x), round(y)
            if len(self.fixed) < 2 or not self.locked_fixed:  # only allow 2 fixed nodes
                self.fixed.append(structure.FixedNode(coords if not self.locked_fixed else (coords[0], 0)))

        elif self.selected == BEAM:
            nearest = self.nearest_node(coords)
            if self.selected_node is None:
                # if there is no selected node, then the beam has not latched onto any node yey
                # and so an instance should not be created but it should be latched
                self.selected_node = nearest

            elif self.selected_node != nearest:
                # adding the beam joining the 2 nodes
                beam = structure.Beam(self.selected_node, nearest)
                if not any([beam == i for i in self.beams]):  # disallowing duplicate beams
                    self.beams.append(beam)
                self.selected_node = None  # unselecting the first node

    def draw_structures(self):
        """Draws the currently placed structures onto the screen"""
        # drawing the nodes
        for i in self.nodes:
            if i in self.selected_structures:
                draw.node_selected(self.canvas, self.coords_to_pos(i.position))
            else:
                draw.node(self.canvas, self.coords_to_pos(i.position))
        # drawing all the fixed nodes
        for i in self.fixed:
            if i in self.selected_structures:
                draw.fixed_selected(self.canvas, self.coords_to_pos(i.position))
            else:
                draw.fixed(self.canvas, self.coords_to_pos(i.position))
        # drawing the beams
        for i in self.beams:
            if i in self.selected_structures:
                draw.beam_selected(self.canvas, *map(self.coords_to_pos, i.ends))
            else:
                draw.beam(self.canvas, *map(self.coords_to_pos, i.ends))

    def draw_grid(self):
        """Draws the grid of coordinates on the screen"""
        # check for out of range if so make the lines shorter
        xlen, ylen = self._window_size
        
        # finding the closest coordinate to the corner
        start = [int(math.ceil(i)) for i in self.pos_to_coords((0, 0))]
        #turning that coordinate into a position on the screen
        start = self.coords_to_pos(start)

        # draw the lines
        colour = (200, 200, 200)
        pos = start[0]
        # drawing the vertical lines
        for i in range(self._window_size[0] // self.scale + 1):
            pygame.draw.line(self.canvas, colour, (pos, 0), (pos, ylen))
            pos += self.scale

        pos = start[1]
        # drawing the horizontal lines
        for i in range(self._window_size[1] // self.scale + 1):
            pygame.draw.line(self.canvas, colour, (0, pos), (xlen, pos))
            pos += self.scale

    def selector_released(self):
        """Handles what to do when the selection tool is released"""

        if self.selected == SELECTOR:
            if time.time() - self.time_of_selection < 0.1:

                # look for anything close enough if it was only a click
                mouse = self.pos_to_coords(pygame.mouse.get_pos())
                nearest = structure.nearest_structure(self.nodes + self.fixed + self.beams, mouse)

                if nearest is not None:  # nearest is none when there are no structures on the screen
                    if structure.distance_from(nearest, mouse) * self.scale < 50:
                        self.selected_structures = [nearest]
                    else:  # not clicked close enough, reset selected 
                        self.selected_structures = []


            # The click was slower so assuming it was a box select
            else:
                # setting up the box coordinated for easy access
                x1, y1 = self.pos_to_coords(self.selection_box_start)
                x2, y2 = self.pos_to_coords(pygame.mouse.get_pos())
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)

                # looping over the structures and checking if they are in the box
                for i in self.nodes + self.fixed:
                    x, y = i.position
                    if x1 < x < x2 and y1 < y < y2:
                        self.selected_structures.append(i)
                for i in self.beams:
                    x, y = i.centre
                    if x1 < x < x2 and y1 < y < y2:
                        self.selected_structures.append(i)


        # reset selection box
        if self.selection_box_start is not None:
            self.selection_box_start = None





    def handle_events(self):
        """Deals with any events such as keys or clicks"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # delete all of the selected items
                if event.key == pygame.K_DELETE:
                    for i in self.selected_structures:
                        # remove any connected beams
                        if isinstance(i, structure.Node):
                            for beam in self.beams:
                                if i is beam.node1 or i is beam.node2:
                                    self.beams.remove(beam)
                        # remove the selected object
                        if i in self.fixed:
                            self.fixed.remove(i)
                        elif i in self.nodes:
                            self.nodes.remove(i)
                        elif i in self.beams:
                            self.beams.remove(i)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # left mouse button
                    # tell the buttons that a click has occured
                    for button in self.buttons:
                        button.update_click(False)
                    
                    # make sure selection is only dealt with if not on top bar
                    if self.selected == SELECTOR:
                        # stop moving the selected structures if dragging them
                        if self.dragging_selected:
                            self.dragging_selected = False
                        # select the things that need to be selected
                        elif pygame.mouse.get_pos()[1] > self.top_bar_height:
                            self.selector_released()
                        # button released on menu bar so stop the box without selecting
                        else:
                            self.selection_box_start = None

                if event.button == 3:  # right mouse button
                    self.dragging = False  # stop panning

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left mouse button
                    # check that cursor is not hovering over the topbar so that items
                    # are not placed underneath
                    if pygame.mouse.get_pos()[1] > self.top_bar_height:
                        self.place()
                        if self.selected == SELECTOR:
                            if self.selected_structures == []:
                                self.time_of_selection = time.time()
                                self.selection_box_start = pygame.mouse.get_pos()
                            else:
                                dist_from_mouse = lambda x: structure.distance_from(x, self.pos_to_coords(pygame.mouse.get_pos()))
                                distance = min(map(dist_from_mouse, self.selected_structures))
                                if distance * self.scale < 100:
                                    self.dragging_selected = True
                                    self.last_mouse_position = pygame.mouse.get_pos()
                                else:
                                    self.selected_structures = []
                                    self.time_of_selection = time.time()
                                    self.selection_box_start = pygame.mouse.get_pos()

                    # tell the buttons that a click has occured
                    for button in self.buttons:
                        button.update_click(True)

                if event.button == 3:  # right mouse button
                    self.dragging = True  # start panning the screen
                    self.last_mouse_position = pygame.mouse.get_pos()
            
            if event.type == pygame.MOUSEWHEEL:
                # change the scale by the movement of the mouse wheel to allow zooming
                if self.scale + event.y > 0:  # stops having a negative scale
                    self.scale += event.y

        if self.dragging:
            # extract required x and ys for ease of use
            x, y = pygame.mouse.get_pos()
            x1, y1 = self.last_mouse_position
            xoff, yoff = self.screen_offset
            # add the mouse movement to the offset
            self.screen_offset = xoff + (x-x1), yoff + (y-y1)
            # reset the last mouse position
            self.last_mouse_position = pygame.mouse.get_pos()

        if self.dragging_selected:
            # extract required x and ys for ease of use
            x, y = pygame.mouse.get_pos()
            x1, y1 = self.last_mouse_position
            xoff, yoff = (x - x1)/self.scale , (y1 - y)/self.scale

            # add the mouse movement to the offset
            for i in self.selected_structures:
                if isinstance(i, structure.Beam):
                    continue  # do not move if it is a beam
                xpos, ypos = i.position
                if i in self.fixed and self.locked_fixed:  # don't change the y of the fixed nodes if locked
                    i.position = xpos + xoff, 0
                else:
                    i.position = xpos + xoff, ypos + yoff
            # reset the last mouse position
            self.last_mouse_position = pygame.mouse.get_pos()

    def mainloop(self):
        """Mainloop of the program"""
        while True:
            self.handle_events()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)

    def main_menu(self):
        """Runs the main menu of the program - the text is in an image as that is the easiest solution"""
        start = button.Button(self.canvas, "Start", (10, 10), False, self.mainloop)
        description = """Statics construction simulation:
        In this program, you construct a structure constructed of 2 fixed nodes, weightless nodes and 1d beams.
        Each beam has a weight which acts on the centre of the beam. 
        Buttons:
        select - enables the selection mode where you can select items on the screen and move or delete them.
        point - adds a weightless point that the beams can connect to.
        fixed - adds a point that is fixed e.g. the ends of the bridge. There has to be exactly 2 of these.
        beam - adds a beam between the 2 closest nodes to the clicks.
        resolve - resolves the vertical forces of the fixed nodes and displays them on the screen.
        grid - enables grid snapping for the points and fixed points."""
        image = pygame.image.load("Description.png")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        start.update_click(True)

            self.canvas.fill((255, 255, 255))
            start.draw()
            self.canvas.blit(image, (0, 70))
            pygame.display.update()
            self.clock.tick(60)




