import pygame


class Button:
    def __init__(self, canvas, text, position, toggle, function, *args, **kwargs):
        self.canvas = canvas
        self.colours = ((128, 128, 128), (0, 0, 0))
        self.colours_hovering = ((255, 0, 0), (128, 0, 0))
        self.text = text
        font = pygame.font.Font(None, 30)
        self.text_drawn = font.render(text, True, (0, 0, 255))


        self.position = position
        x, y = position
        self.text_pos = (x+20, y+10)
        self.size = (100, 50)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.clicking = False
        self.toggleable = toggle

        self.top_rect = pygame.Rect(*position, *self.size)
        self.bottom_rect = pygame.Rect(x, y + 10, *self.size)

    def hovering(self):
        x, y = pygame.mouse.get_pos()
        x1, y1 = self.position
        xs, ys = self.size
        return x1 <= x <= x1+xs and y1 <= y <= y1+ys


    def update_click(self, status):
        if self.hovering() and status:
            if self.toggleable:
                self.clicking = not self.clicking
            else:
                self.clicking = True
            self.function(*self.args, **self.kwargs)
        elif not self.toggleable:
            self.clicking = False

    def draw(self):
        top_colour, bottom_colour = self.colours_hovering if self.hovering() else self.colours
        if self.clicking:
            pygame.draw.rect(self.canvas, top_colour, self.bottom_rect, 0, border_radius=10)
            self.canvas.blit(self.text_drawn, (self.text_pos[0], self.text_pos[1] + 10))
        else:
            pygame.draw.rect(self.canvas, bottom_colour, self.bottom_rect, 0, border_radius=10)
            pygame.draw.rect(self.canvas, top_colour, self.top_rect, 0, border_radius=10)
            self.canvas.blit(self.text_drawn, self.text_pos)




if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption('Gui Menu')
    clock = pygame.time.Clock()
    gui_font = pygame.font.Font(None, 30)

    button = Button(screen, "Test", (100, 100), lambda x:print(x), 1)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    button.update_click(False)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    button.update_click(True)
        screen.fill('#DCDDD8')
        button.draw()

        pygame.display.update()
        clock.tick(60)