import pygame
import polars as pl
import time
from dataclasses import dataclass
import numpy as np
from theme import onehalfdark, themes
from widgits import Widget, Window, Block, Paragraph, List


def theme_generator():
    while True:
        for theme in themes.values():
            yield theme


theme = onehalfdark


@dataclass
class ViewBox:
    left: float
    right: float
    bottom: float
    top: float

    def width(self):
        return self.right - self.left

    def height(self):
        return self.top - self.bottom

    def move_horizontally(self, shift: float):
        self.left += shift
        self.right += shift

    def zoom_horizontally(self, zoom: float):
        center = (self.left + self.right) / 2
        range_half = self.width() / 2 * zoom
        self.left = center - range_half
        self.right = center + range_half


def compute_grid_lines(view_box: ViewBox):
    """Compute nice grid line intervals for the x and y axes."""

    def nice_interval(range_value):
        """Find a good interval for grid lines based on the range."""
        raw_interval = range_value / 10  # Start with roughly 10 grid lines
        exponent = np.floor(np.log10(raw_interval))
        base_interval = 10**exponent

        # Choose a "nice" factor (1, 2, 5, 10, etc.)
        for factor in [1, 2, 5, 10]:
            if raw_interval <= base_interval * factor:
                return base_interval * factor

    # Compute the intervals for x and y axes
    x_range = view_box.right - view_box.left
    y_range = view_box.top - view_box.bottom

    x_interval = nice_interval(x_range)
    y_interval = nice_interval(y_range)

    # Generate grid lines for x-axis
    x_lines = np.arange(
        np.floor(view_box.left / x_interval) * x_interval,
        view_box.right + x_interval,
        x_interval,
    )

    # Generate grid lines for y-axis
    y_lines = np.arange(
        np.floor(view_box.bottom / y_interval) * y_interval,
        view_box.top + y_interval,
        y_interval,
    )

    return x_lines[1:], y_lines[1:]


class LinePlot(Widget):
    def __init__(
        self, df: pl.DataFrame, x_axis="time", y_columns=None, grid=True, legend=True
    ):
        self.df = df
        self.x_axis = x_axis
        self.y_columns = y_columns or list(set(df.columns) - {x_axis})
        self.grid = grid
        self.legend = legend
        self.font = pygame.font.SysFont("firacodenerdfont", 10)

        self.view_box = ViewBox(
            df[self.x_axis].min(),
            df[self.x_axis].max(),
            df.select([pl.col(col) for col in self.y_columns])
            .min()
            .min_horizontal()
            .item(),
            df.select([pl.col(col) for col in self.y_columns])
            .max()
            .max_horizontal()
            .item(),
        )
        self._block = None

    def with_view(self, view_box: ViewBox):
        self.view_box = view_box
        return self

    def lerp(self, x0, x1, y0, y1, x):
        return (x - x0) / (x1 - x0) * (y1 - y0) + y0

    def map_x_to_pixel(self, x, width):
        x = self.lerp(self.view_box.left, self.view_box.right, 0, width, x)
        if isinstance(x, pl.Expr):
            return x.cast(pl.Int32)
        return int(x)

    def map_y_to_pixel(self, y, height):
        y = self.lerp(self.view_box.top, self.view_box.bottom, 0, height, y)
        if isinstance(y, pl.Expr):
            return y.cast(pl.Int32)
        return int(y)

    def map_to_pixel(self, width, height):
        df = self.df.filter(
            pl.col(self.x_axis).is_between(self.view_box.left, self.view_box.right)
        )

        df = df.with_columns(
            (self.map_x_to_pixel(pl.col(self.x_axis), width)).alias(self.x_axis)
        )
        df = df.group_by(self.x_axis).mean().sort(self.x_axis)

        for y_col in self.y_columns:
            df = df.with_columns(
                (self.map_y_to_pixel(pl.col(y_col), height)).cast(pl.Int32).alias(y_col)
            )

        return df

    def render_legend(self, surface: pygame.Surface):
        rect = surface.get_rect()
        for i, col in enumerate(self.y_columns):
            left = rect.right - 50
            top = 30 + i * 15
            color = theme.accents[i]
            pygame.draw.rect(surface, color.rgb(), pygame.Rect(left, top, 10, 10))
            surface.blit(self.font.render(col, True, theme.fg0.rgb()), (left + 15, top))

    def block(self, block: Block):
        self._block = block
        return self

    def render(self, area: pygame.Rect, surface: pygame.Surface):
        width, height = area.width, area.height
        margin = 50
        pygame.draw.rect(surface, theme.bg0.rgb(), area)
        inner_area = area.inflate(-2 * margin, -2 * margin)
        if self._block:
            self._block.render(inner_area, surface)
            inner_area = self._block.inner(inner_area)
        pygame.draw.rect(surface, theme.bg1.rgb(), inner_area)

        inner_surface = pygame.Surface(inner_area.size)
        inner_surface.fill(theme.bg1.rgb())

        if self.grid:
            v_lines, h_lines = compute_grid_lines(self.view_box)

            for x in v_lines:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x / 1e6))
                x_pixel = self.map_x_to_pixel(x, width)
                pygame.draw.line(
                    inner_surface, theme.fg1.rgb(), (x_pixel, 0), (x_pixel, height)
                )
                text_width_px, text_height_px = self.font.size(timestamp)
                text_surface = self.font.render(
                    timestamp, True, theme.fg0.rgb(), theme.bg0.rgb()
                )
                pos = (
                    margin + x_pixel + text_height_px,
                    margin + inner_surface.get_height(),
                )
                surface.blit(text_surface, pos)

            for y in h_lines:
                value = f"{y}"
                y_pixel = self.map_y_to_pixel(y, height)
                pygame.draw.line(
                    inner_surface, theme.fg1.rgb(), (0, y_pixel), (width, y_pixel)
                )
                text_width_px, text_height_px = self.font.size(value)
                text_surface = self.font.render(
                    value, True, theme.fg0.rgb(), theme.bg0.rgb()
                )
                pos = (margin - text_width_px, margin + y_pixel)
                surface.blit(text_surface, pos)

        pixel_df = self.map_to_pixel(*inner_surface.get_size())

        for i, col in enumerate(self.y_columns):
            color = theme.accents[i]
            data = pixel_df.select([self.x_axis, col]).to_numpy()
            if len(data) < 2:
                continue
            pygame.draw.aalines(inner_surface, color.rgb(), False, data)

        if self.legend:
            self.render_legend(inner_surface)

        surface.blit(inner_surface, inner_area.topleft)


class App:
    def __init__(self, df: pl.DataFrame, x_axis="time"):
        self.running = True
        self.df = df
        self.x_axis = x_axis
        self.theme_popup = False

        self.view_box = ViewBox(
            df[self.x_axis].min(),
            df[self.x_axis].max(),
            df.select([pl.col(col) for col in df.columns if col != x_axis])
            .min()
            .min_horizontal()
            .item(),
            df.select([pl.col(col) for col in df.columns if col != x_axis])
            .max()
            .max_horizontal()
            .item(),
        )

        self.line_plot = LinePlot(df, x_axis=x_axis)
        self.line_plot.with_view(self.view_box)

        self.select = 0

        self.state = "normal"

    def run(self, window: Window):
        cycle_times = []
        x = 5000  # Number of cycles to average over
        clock = pygame.time.Clock()
        clock.tick(100)

        while self.running:
            self.loop_once(window)
            cycle_time = clock.tick(100)
            cycle_times.append(cycle_time)
            if sum(cycle_times) > x:
                avg_cycle_time = sum(cycle_times) / len(cycle_times)
                cycle_times.pop(0)
                print(
                    f"Avg loop time: {avg_cycle_time:.2f}ms, FPS: {1000 / avg_cycle_time:.2f}"
                )
                cycle_times = []

    def loop_once(self, window: Window):
        window.draw(self.draw)
        self.handle_events()

    def draw(self, surface: pygame.Surface):
        area = surface.get_rect()
        self.line_plot.block(Block(1, theme.bg0, theme.fg1))
        self.line_plot.render(area, surface)
        if self.theme_popup:
            width = 300
            height = 200
            left = (surface.get_width() - width) // 2
            top = (surface.get_height() - height) // 2
            popup_area = pygame.Rect(left, top, width, height)
            List(
                list(themes.keys()), pygame.font.SysFont("firacodenerdfont", 20)
            ).with_fg(theme.fg0).with_bg(theme.bg0).block(
                Block(2, theme.bg0, theme.fg1)
            ).select(self.select).render(popup_area, surface)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.TEXTINPUT:
                if event.text == "h":  # Pan left
                    self.view_box.move_horizontally(-self.view_box.width() * 0.5)
                elif event.text == "l":  # Pan right
                    self.view_box.move_horizontally(self.view_box.width() * 0.5)
                elif event.text == "j":  # Zoom in
                    if self.theme_popup:
                        self.select += 1
                    else:
                        self.view_box.zoom_horizontally(0.5)
                elif event.text == "k":  # Zoom out
                    if self.theme_popup:
                        self.select -= 1
                    else:
                        self.view_box.zoom_horizontally(2.0)
                elif event.text == "t":
                    self.theme_popup = not self.theme_popup
                elif event.text == "q":
                    self.running = False
                elif event.text == " ":
                    if self.theme_popup:
                        self.theme_popup = False
                        global theme
                        theme = themes[list(themes.keys())[self.select]]
                self.line_plot.with_view(self.view_box)


def main():
    import os

    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    df = pl.read_parquet("data.parquet")
    print("df size mb:", df.estimated_size("mb"))
    window = Window(2000, 1000)
    window.init()
    app = App(df)
    app.run(window)
    window.quit()


if __name__ == "__main__":
    main()
