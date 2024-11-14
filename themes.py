from dataclasses import dataclass

@dataclass
class Color:
    value: int
    
    def hex(self) -> str:
        """Return the color as a hex string."""
        return f"#{self.value:06x}"
    
    def rgb(self) -> tuple:
        """Convert the integer value to an RGB tuple."""
        return self.int_to_rgb(self.value)
    
    def int(self) -> int:
        """Return the color as an integer."""
        return self.value
    
    @staticmethod
    def int_to_rgb(value: int) -> tuple:
        """Convert an integer color to an RGB tuple."""
        return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)
    
    @staticmethod
    def hex_to_int(hex_color: str) -> int:
        """Convert a hex string (e.g., #RRGGBB) to an integer."""
        return int(hex_color.lstrip('#'), 16)


class Theme:
    BLACK: Color
    RED: Color
    GREEN: Color
    YELLOW: Color
    BLUE: Color
    MAGENTA: Color
    CYAN: Color
    WHITE: Color
    FOREGROUND: Color
    BACKGROUND: Color

    COLORS: list[Color]

    def __init__(self):
        # This ensures that the `COLORS` field is always initialized
        # after the object is created.
        object.__setattr__(self, 'COLORS', [
            self.BLACK, self.RED, self.GREEN, self.YELLOW, self.BLUE,
            self.MAGENTA, self.CYAN, self.WHITE
        ])



class OneHalfDark(Theme):
    BLACK = Color(0x282c34)
    RED = Color(0xe06c75)
    GREEN = Color(0x98c379)
    YELLOW = Color(0xe5c07b)
    BLUE = Color(0x61afef)
    MAGENTA = Color(0xc678dd)
    CYAN = Color(0x56b6c2)
    WHITE = Color(0xdcdfe4)
    FOREGROUND = Color(0xdcdfe4)
    BACKGROUND = Color(0x282c34)

    COLORS = [
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    ]


class OneHalfLight(Theme):
    BLACK = Color(0x383a42)
    RED = Color(0xe45649)
    GREEN = Color(0x50a14f)
    YELLOW = Color(0xc18401)
    BLUE = Color(0x0184bc)
    MAGENTA = Color(0xa626a4)
    CYAN = Color(0x0997b3)
    WHITE = Color(0xfafafa)
    FOREGROUND = Color(0x383a42)
    BACKGROUND = Color(0xfafafa)

    COLORS = [
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    ]
    


if __name__ == '__main__':
    # Create a theme object
    theme = OneHalfDark()
    print(theme)
    print(theme.BLACK.hex())
    print(theme.BLACK.rgb())
    print(theme.BLACK.int())
    print(theme.COLORS)