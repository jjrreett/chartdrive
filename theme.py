from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Color:
    value: int

    def hex(self) -> str:
        """Return the color as a hex string."""
        return f"#{self.value:06x}"

    def rgb(self) -> tuple:
        """Convert the integer value to an RGB tuple."""
        return Color.int_to_rgb(self.value)

    @lru_cache
    @staticmethod
    def int_to_rgb(value: "int") -> tuple:
        """Convert an integer color to an RGB tuple."""
        return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

    def int(self) -> int:
        """Return the color as an integer."""
        return self.value

    @lru_cache
    @staticmethod
    def hex_to_int(hex_color: str) -> int:
        """Convert a hex string (e.g., #RRGGBB) to an integer."""
        return int(hex_color.lstrip("#"), 16)

    def lighten(self, amount: int = 0x0F0F0F) -> "Color":
        """Lighten the color by a fixed amount."""
        r, g, b = self.rgb()
        r = min(r + (amount >> 16) & 0xFF, 255)
        g = min(g + (amount >> 8) & 0xFF, 255)
        b = min(b + amount & 0xFF, 255)
        return Color((r << 16) | (g << 8) | b)


class CircularTuple(tuple):
    def __new__(cls, *args):
        return super().__new__(cls, args)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return CircularTuple(super().__getitem__(key))
        return super().__getitem__(key % len(self))


class Theme:
    def __init__(
        self,
        fg0,
        bg0,
        red,
        green,
        yellow,
        blue,
        magenta,
        cyan,
        fg1=None,
        bg1=None,
        br_red=None,
        br_green=None,
        br_yellow=None,
        br_blue=None,
        br_magenta=None,
        br_cyan=None,
    ):
        self.red: Color = red
        self.green: Color = green
        self.yellow: Color = yellow
        self.blue: Color = blue
        self.magenta: Color = magenta
        self.cyan: Color = cyan
        self.fg0: Color = fg0
        self.bg0: Color = bg0
        self.accents = CircularTuple(
            red,
            green,
            yellow,
            blue,
            magenta,
            cyan,
        )
        self.fg1 = fg1 if fg1 else fg0
        self.bg1 = bg1 if bg1 else bg0
        self.br_red = br_red if br_red else red
        self.br_green = br_green if br_green else green
        self.br_yellow = br_yellow if br_yellow else yellow
        self.br_blue = br_blue if br_blue else blue
        self.br_magenta = br_magenta if br_magenta else magenta
        self.br_cyan = br_cyan if br_cyan else cyan
        self.br_accents = CircularTuple(
            self.br_red,
            self.br_green,
            self.br_yellow,
            self.br_blue,
            self.br_magenta,
            self.br_cyan,
        )


onehalfdark = Theme(
    fg0=Color(0xDCDFE4),
    bg0=Color(0x282C34),
    red=Color(0xE06C75),
    green=Color(0x98C379),
    yellow=Color(0xE5C07B),
    blue=Color(0x61AFEF),
    magenta=Color(0xC678DD),
    cyan=Color(0x56B6C2),
)

onehalflight = Theme(
    fg0=Color(0x383A42),
    bg0=Color(0xFAFAFA),
    red=Color(0xE45649),
    green=Color(0x50A14F),
    yellow=Color(0xC18401),
    blue=Color(0x0184BC),
    magenta=Color(0xA626A4),
    cyan=Color(0x0997B3),
)

selenizeddark = Theme(
    fg0=Color(0xADBCBC),
    bg0=Color(0x103C48),
    red=Color(0xFA5750),
    green=Color(0x75B938),
    yellow=Color(0xDBB32D),
    blue=Color(0x4695F7),
    magenta=Color(0xF275BE),
    cyan=Color(0x41C7B9),
    # orange = Color(0xed8649),
    # violet = Color(0xaf88eb),
    fg1=Color(0xCAD8D9),
    bg1=Color(0x184956),
    br_red=Color(0xFF665C),
    br_green=Color(0x84C747),
    br_yellow=Color(0xEBC13D),
    br_blue=Color(0x58A3FF),
    br_magenta=Color(0xFF84CD),
    br_cyan=Color(0x53D6C7),
    # br_orange = Color(0xfd9456),
    # br_violet = Color(0xbd96fa),
)

selenizedblack = Theme(
    fg0=Color(0xB9B9B9),
    bg0=Color(0x181818),
    red=Color(0xED4A4A),
    green=Color(0x70B43C),
    yellow=Color(0xDBB32D),
    blue=Color(0x368AEB),
    magenta=Color(0xEB6EB7),
    cyan=Color(0x3FC5B7),
    # orange = Color(0xe67f4),
    # violet = Color(0xa580e),
    fg1=Color(0xDEDEDE),
    bg1=Color(0x252525),
    br_red=Color(0xED4A4A),
    br_green=Color(0x70B43C),
    br_yellow=Color(0xDBB32D),
    br_blue=Color(0x368AEB),
    br_magenta=Color(0xEB6EB7),
    br_cyan=Color(0x3FC5B7),
)

tangodark = Theme(
    fg0=Color(0xD3D7CF),
    bg0=Color(0x2E3436),
    red=Color(0xEF2929),
    green=Color(0x8AE234),
    yellow=Color(0xFCE94F),
    blue=Color(0x729FCF),
    magenta=Color(0xAD7FA8),
    cyan=Color(0x34E2E2),
    # orange = Color(0xC4A000),  # brown
    # violet = Color(0x75507B),  # dark magenta
    fg1=Color(0xEEEEEC),
    bg1=Color(0x555753),
    br_red=Color(0xCC0000),  # dark red
    br_green=Color(0x4E9A06),  # dark green
    br_yellow=Color(0xC4A000),  # brown
    br_blue=Color(0x3465A4),  # dark blue
    br_magenta=Color(0x75507B),  # dark magenta
    br_cyan=Color(0x06989A),  # dark cyan
    # br_orange = Color(0xC4A000),  # brown
    # br_violet = Color(0x75507B),  # dark magenta
)

themes = {
    "onehalfdark": onehalfdark,
    "onehalflight": onehalflight,
    "selenizeddark": selenizeddark,
    "selenizedblack": selenizedblack,
    "tangodark": tangodark,
}


WHITE = Color(0xFFFFFF)
BLACK = Color(0x000000)
RED = Color(0xFF0000)
GREEN = Color(0x00FF00)
BLUE = Color(0x0000FF)
YELLOW = Color(0xFFFF00)
MAGENTA = Color(0xFF00FF)
CYAN = Color(0x00FFFF)
ORANGE = Color(0xFFA500)
VIOLET = Color(0xEE82EE)


if __name__ == "__main__":
    # Create a theme object

    from rich.console import Console
    from rich.style import Style

    def render_palette(theme: Theme):
        console = Console()
        console.print(
            "  abc123  ",
            style=Style(color=theme.fg0.hex(), bgcolor=theme.bg0.hex()),
            end="",
        )
        console.print(
            "  abc123  ", style=Style(color=theme.fg1.hex(), bgcolor=theme.bg0.hex())
        )
        console.print(
            "  abc123  ",
            style=Style(color=theme.fg0.hex(), bgcolor=theme.bg1.hex()),
            end="",
        )
        console.print(
            "  abc123  ", style=Style(color=theme.fg1.hex(), bgcolor=theme.bg1.hex())
        )
        console.print(
            "  abc123  ",
            style=Style(color=theme.bg0.hex(), bgcolor=theme.fg0.hex()),
            end="",
        )
        console.print(
            "  abc123  ", style=Style(color=theme.bg1.hex(), bgcolor=theme.fg0.hex())
        )
        console.print(
            "  abc123  ",
            style=Style(color=theme.bg0.hex(), bgcolor=theme.fg1.hex()),
            end="",
        )
        console.print(
            "  abc123  ", style=Style(color=theme.bg1.hex(), bgcolor=theme.fg1.hex())
        )
        for color, br_color in zip(theme.accents, theme.br_accents):
            for bg in (theme.bg0, theme.bg1, theme.fg0, theme.fg1):
                console.print(
                    "  abc123  ",
                    style=Style(color=color.hex(), bgcolor=bg.hex()),
                    end="",
                )
                console.print(
                    "  abc123  ", style=Style(color=br_color.hex(), bgcolor=bg.hex())
                )

    for name, theme in themes.items():
        print(name)
        render_palette(theme)
