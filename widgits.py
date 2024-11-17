from abc import ABC, abstractmethod
import pygame
import theme


class Widget(ABC):
    @abstractmethod
    def render(self, area: pygame.Rect, surface: pygame.Surface):
        pass


class Text(Widget):
    def __init__(self, text: str):
        self.text = text
        self.font = pygame.font.Font(None, 25)
        self.color = (255, 255, 255)

    def with_font(self, font: pygame.font.Font):
        self.font = font
        return self

    def with_color(self, color: tuple):
        self.color = color
        return self

    def render(self, area: pygame.Rect, surface: pygame.Surface):
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, area.topleft)


class Block(Widget):
    def __init__(
        self,
        thickness: int = 1,
        inner_color: theme.Color = theme.BLACK,
        outer_color: theme.Color = theme.WHITE,
    ):
        self.thickness = thickness
        self.inner_color = inner_color
        self.outer_color = outer_color

    def render(self, area: pygame.Rect, surface: pygame.Surface):
        inner_area = self.inner(area)
        pygame.draw.rect(surface, self.outer_color.rgb(), area, border_radius=1)
        pygame.draw.rect(surface, self.inner_color.rgb(), inner_area, border_radius=3)

    def inner(self, area: pygame.Rect):
        inner_area = area.inflate(-2 * self.thickness, -2 * self.thickness)
        return inner_area


class Paragraph(Widget):
    def __init__(
        self, text: str, font: pygame.font.Font, color: theme.Color = theme.WHITE
    ):
        self.text = text
        self.font = font
        self.color = color
        self._block = None

    def render(self, area: pygame.Rect, surface: pygame.Surface):
        if self._block:
            self._block.render(area, surface)
            area = self._block.inner(area)
        text_surface = self.font.render(self.text, True, self.color.rgb())

        surface.blit(text_surface, area.topleft)

    def block(self, block: Block):
        self._block = block
        return self

class List(Widget):
    def __init__(self, items: list, font: pygame.font.Font, color: theme.Color = theme.WHITE):
        self.items = items
        self.font = font
        self.fg = color
        self.bg = theme.BLACK
        self._block = None
        self.selected = None
    
    def with_fg(self, color: theme.Color):
        self.fg = color
        return self
    
    def with_bg(self, color: theme.Color):
        self.bg = color
        return self
    
    def select(self, index: int):
        self.selected = index
        return self

    def render(self, area: pygame.Rect, surface: pygame.Surface):
        if self._block:
            self._block.render(area, surface)
            area = self._block.inner(area)
        y = area.y
        for i, item in enumerate(self.items):
            # TODO force the text surface to have the width of the area
            if i == self.selected:
                text_surface = self.font.render(item, True, self.bg.rgb(), self.fg.rgb())
            else:
                text_surface = self.font.render(item, True, self.fg.rgb(), self.bg.rgb())
            surface.blit(text_surface, (area.x, y))
            y += text_surface.get_height()

    def block(self, block: Block):
        self._block = block
        return self

class Window:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def init(self):
        pygame.init()
        self.surface = pygame.display.set_mode((self.width, self.height))

    def draw(self, closure):
        closure(self.surface)
        pygame.display.flip()

    def quit(self):
        pygame.quit()


if __name__ == "__main__":

    def main():
        window = Window(800, 600)
        window.init()
        run(window)
        window.quit()

    def run(window: Window):
        while True:
            window.draw(lambda surface: Text("Hello, World!").render(surface))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            pygame.time.wait(10)

    main()
