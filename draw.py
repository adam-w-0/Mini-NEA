import pygame
import math


def node(canvas: pygame.Surface, position: tuple) -> None:
    """Draws a node onto the screen at the given position on the screen"""
    pygame.draw.circle(canvas, (50, 50, 50), position, 10)


def node_selected(canvas: pygame.Surface, position: tuple) -> None:
    """Draws a node onto the screen at the given position on the screen 
    with a blue background behind to indicate it has been selected"""
    pygame.draw.circle(canvas, (0, 0, 255), position, 12)
    pygame.draw.circle(canvas, (50, 50, 50), position, 10)


def fixed(canvas: pygame.Surface, position: tuple) -> None:
    """Draws a fixed node onto the screen at the given position on the screen"""
    pygame.draw.circle(canvas, (50, 50, 50), position, 10)
    pygame.draw.circle(canvas, (255, 255, 255), position, 5)


def fixed_selected(canvas: pygame.Surface, position: tuple) -> None:
    """Draws a fixed node onto the screen at the given position on the screen 
    with a blue background behind to indicate it has been selected"""
    pygame.draw.circle(canvas, (0, 0, 255), position, 12)
    pygame.draw.circle(canvas, (50, 50, 50), position, 10)
    pygame.draw.circle(canvas, (255, 255, 255), position, 5)


def beam(canvas: pygame.Surface, pos1: tuple, pos2: tuple) -> None:
    """Draws a line representing a beam between the 2 given points 
    onto the screen at the given position"""
    colour = (255, 0, 0)
    pygame.draw.line(canvas, colour, pos1, pos2, 3)

def beam_selected(canvas: pygame.Surface, pos1: tuple, pos2: tuple) -> None:
    """Draws a line representing a beam between the 2 given points
    onto the screen at the given position with a blue background
    behind to indicate it has been selected"""
    selected_colour = (0, 0, 255)
    colour = (255, 0, 0)
    pygame.draw.line(canvas, selected_colour, pos1, pos2, 5)
    pygame.draw.line(canvas, colour, pos1, pos2, 3)

def beam_selector(canvas: pygame.Surface, position: tuple) -> None:
    """Draws the icon to show that the beam is currently selected at the 
    given position"""
    colour = (255, 0, 0)
    pygame.draw.circle(canvas, colour, position, 4)


def selector_box(canvas: pygame.Surface, pos1: tuple, pos2: tuple):
    """Draws the blue box that appears while dragging the selector"""
    x1, y1 = pos1
    x2, y2 = pos2
    surf = pygame.Surface((abs(x1 - x2), abs(y1 - y2)))
    surf.set_alpha(64)
    surf.fill((0, 0, 255))
    canvas.blit(surf, (min(x1, x2), min(y1, y2)))


def force_arrow(canvas: pygame.Surface, position: tuple, angle: float, force: float, scale: int):
    """Draws a force arrow at the given point - angle given in radians and position as position on the screen"""
    x, y = position  # unpack the position for ease of use
    arrowscale = 50  # scale o the arrow
    ahs = 25  # arrow head size
    # the offset of the arrowhead
    endoffx, endoffy = (math.cos(angle) * force * scale)/arrowscale, -(math.sin(angle) * force * scale)/arrowscale
    end = endoffx + x, endoffy + y
    tx, ty = endoffx*0.8 + x, endoffy*0.8 + y
    t1 = (-math.sin(angle) * scale * ahs)/arrowscale + tx,\
          - (math.cos(angle) * scale * ahs)/arrowscale + ty
    t2 = - (- math.sin(angle) * scale * ahs) / arrowscale + tx, \
         (math.cos(angle) * scale * ahs) / arrowscale + ty
    pygame.draw.line(canvas, (0, 255, 0), position, end, 5)
    pygame.draw.polygon(canvas, (0, 255, 0), (end, t1, t2))