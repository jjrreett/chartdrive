from abc import ABC, abstractmethod
import pygame


class Widget(ABC):
    @abstractmethod
    def render(self, surface: pygame.Surface):
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

    def render(self, surface: pygame.Surface):
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, (0, 0))


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
