# %%
import pygame
import polars as pl
import time
from dataclasses import dataclass
from itertools import zip_longest
import numpy as np
import pygame.freetype
from themes import OneHalfDark, OneHalfLight


theme = OneHalfDark()
# theme = OneHalfLight()

@dataclass
class ViewBox:
    left: float
    right: float
    bottom: float
    top: float

    def move_horizontally(self, shift: float):
        self.left += shift
        self.right += shift

    def width(self):
        return self.right - self.left

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
        base_interval = 10 ** exponent

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


class PlottingEngine:
    def __init__(self, width, height, df: pl.DataFrame, y_columns, grid=True):
        pygame.init()
        self.WIDTH = width
        self.HEIGHT = height
        self.df = df
        self.y_columns = y_columns
        self.grid=grid
        self.font = pygame.font.SysFont('firacodenerdfont', 10)

        self.view_box = ViewBox(
            df["time"].min(),
            df["time"].max(),
            df.select([pl.col(col) for col in self.y_columns]).min().min_horizontal().item(),
            df.select([pl.col(col) for col in self.y_columns]).max().max_horizontal().item(),
        )

        self.screen = pygame.display.set_mode((self.WIDTH + 100, self.HEIGHT + 100))
        self.plot = pygame.Surface((self.WIDTH, self.HEIGHT))

    def lerp(self, x0, x1, y0, y1, x):
        return (x - x0) / (x1 - x0) * (y1 - y0) + y0
    
    def map_x_to_pixel(self, x):
        x = self.lerp(self.view_box.left, self.view_box.right, 0, self.WIDTH, x)
        if isinstance(x, pl.Expr):
            return x.cast(pl.Int32)
        return int(x)
    
    def map_y_to_pixel(self, y):
        y = self.lerp(self.view_box.top, self.view_box.bottom, 0, self.HEIGHT, y)
        if isinstance(y, pl.Expr):
            return y.cast(pl.Int32)
        return int(y)

    def map_to_pixel(self):
        """Map data coordinates to pixel coordinates for all y-columns."""
        df = self.df.filter(
            pl.col("time").is_between(self.view_box.left, self.view_box.right)
        )

        # Map x (time) to pixel coordinates
        df = df.with_columns(
            self.map_x_to_pixel(pl.col("time")).alias("time")
        #     (
        #         (pl.col("time") - self.view_box.left)
        #         / self.view_box.width()
        #         * self.WIDTH + 1
        #     ).cast(pl.Int32).alias("time")
        )
        df = df.group_by("time").mean().sort("time")

        # Map y-columns to pixel coordinates
        for y_col in self.y_columns:
            df = df.with_columns(
                (
                    self.HEIGHT
                    - (
                        (pl.col(y_col) - self.view_box.bottom)
                        / (self.view_box.top - self.view_box.bottom)
                        * self.HEIGHT
                    )
                ).cast(pl.Int32).alias(y_col)
            )

        return df
    
    def render_legend(self):
        for i, col in enumerate(self.y_columns):
            left = 50 + self.WIDTH + 5
            top = 30 + i * 15
            color = theme.COLORS[i % len(theme.COLORS)]
            pygame.draw.rect(
                self.screen,
                color.rgb(),
                pygame.Rect(left, top, 10, 10),
            )
            self.screen.blit(self.font.render(col, True, theme.BACKGROUND.rgb()), (left + 15, top))

    def update_plot(self):
        self.screen.fill(theme.FOREGROUND.rgb())
        self.plot.fill(theme.BACKGROUND.rgb())
        self.render_legend()
        pixel_df = self.map_to_pixel()
        text_surfaces = []

        if self.grid:

            x_lines, y_lines = compute_grid_lines(self.view_box)

            # Draw the horizontal and vertical grid lines using pygame
            for x in x_lines:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x / 1e6))
                x = self.map_x_to_pixel(x)
                pygame.draw.line(self.plot, theme.FOREGROUND.rgb(), (x, 0), (x, self.HEIGHT))
                text_surfaces.append((self.font.render(timestamp, True, theme.BACKGROUND.rgb(), theme.FOREGROUND.rgb()), (x + 50 - self.font.size(timestamp)[0] // 2, self.HEIGHT + 50)))

            for y in y_lines:
                value = y
                y = self.map_y_to_pixel(y)
                pygame.draw.line(self.plot, theme.FOREGROUND.rgb(), (0, y), (self.WIDTH, y))
                text_surfaces.append((self.font.render(f"{value}", True, theme.BACKGROUND.rgb(), theme.FOREGROUND.rgb()), (0, y + 45)))


        for i, col in enumerate(self.y_columns):
            color = theme.COLORS[i%len(theme.COLORS)]
            data = pixel_df.select(["time", col]).to_numpy()
            if len(data) < 2:
                continue
            pygame.draw.aalines(
                self.plot,
                color.rgb(),
                False,
                data,
                2,
            )

        self.screen.blit(self.plot, (50, 50))
        self.screen.blits(text_surfaces)
        pygame.display.flip()

    def run(self):

        self.update_plot()
        running = True
        while running:
            update = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.TEXTINPUT:
                    if event.text == "h":  # Pan left
                        self.view_box.move_horizontally(-self.view_box.width() * 0.5)
                        update = True
                    elif event.text == "l":  # Pan right
                        self.view_box.move_horizontally(self.view_box.width() * 0.5)
                        update = True
                    elif event.text == "j":  # Zoom in
                        self.view_box.zoom_horizontally(0.5)
                        update = True
                    elif event.text == "k":  # Zoom out
                        self.view_box.zoom_horizontally(2.0)
                        update = True

                    # print(f"self.view_box: {self.view_box}")

                    # Update the plot with the new view
                    if update:
                        self.update_plot()

            time.sleep(0.001)

        pygame.quit()


def main():
    # # Load the data
    df = pl.read_parquet("data.parquet")
    print("df size mb:", df.estimated_size("mb"))


    cols = ["AAPL", "GOOG", "META", "TSLA", "AMZN"]
    PlottingEngine(
        2000,
        1000,
        df,
        cols,
    ).run()


    # import plotly.graph_objects as go

    # fig = go.Figure()
    # for col in cols:
    #     fig.add_trace(go.Scatter(x=df["time"], y=df[col], mode="lines", name=col))

    # fig.update_layout(title="Stock Prices", xaxis_title="Time", yaxis_title="Price")
    # fig.show()

if __name__ == "__main__":
    main()

# fonts 
['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'sansserifcollection', 'segoefluenticons', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'segoeuivariable', 'simsun', 'nsimsun', 'simsunextb', 'sitkatext', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight', 'holomdl2assets', 'cascadiacoderegular', 'cascadiamonoregular', 'harmonyossansscregular', 'harmonyossansscbold', 'notosansjpregular', 'notosansjpbold', 'firacodenerdfont', 'firacodenerdfontmed', 'firacodenerdfontmono', 'firacodenerdfontmonomed', 'firacodenerdfontmonoreg', 'firacodenerdfontmonoret', 'firacodenerdfontmonosembd', 'firacodenerdfontpropo', 'firacodenerdfontpropomed', 'firacodenerdfontproporeg', 'firacodenerdfontproporet', 'firacodenerdfontproposembd', 'firacodenerdfontreg', 'firacodenerdfontret', 'firacodenerdfontsembd', 'simsunextg']
