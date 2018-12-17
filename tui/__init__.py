import sys
from blessed import Terminal

from coc.exceptions import *

t = Terminal()

def fullscreen(func):
    def _decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InterfaceException:
            _echo(t.exit_fullscreen)
            raise
    return _decorator

class Interface:
    """ Provides an API to interact through a terminal interface with a user
    """
    def __init__(self):
        _echo(t.enter_fullscreen)
        self._get_geometry()

    @fullscreen
    def error(self, text):
        with t.location(3, t.height-1):
            _echo(t.clear_eol())
            _echo(text)

    @fullscreen
    def prompt(self, text):
        with t.location(3, t.height-3):
            _echo(t.clear_eol())
            _echo(text)

    @fullscreen
    def title(self, text):
        with t.location(3, 0):
            _echo(t.clear_eol())
            _echo(t.bold(text))

    @fullscreen
    def menu_choice(self, options, title=None):
        def draw_menu(renderable):
            rendered = [
                    '({0}) - {1}'.format(a,b)
                    for a,b in
                    renderable
                    ]
            self.prompt('Press a key to select. q to quit, - to scroll up, + to'
                            'scroll down.')
            y = 1
            for item in rendered:
                with t.location(x=5,y=y):
                    _echo(t.clear_eol)
                    _echo(item)
                    y +=1
        if title:
            self.title(title)
        offset = 0
        selection_keys = '0123456789abcdefghijklmnoprstuvwxyz'
        renderable = list(zip(selection_keys,
            options[offset:self.window_height+offset]))
        draw_menu(renderable)
        selection = None
        while True:
            c = self.get_char()
            if c == '+':
                offset += 3
                if offset > len(options) - self.window_height:
                    offset = len(options) - self.window_height
                if offset < 0:
                    offset = 0
                renderable = list(zip(selection_keys,
                    options[offset:self.window_height+offset]))
                draw_menu(renderable)
                continue
            if c == '-':
                offset -= 3
                if offset < 0:
                    offset = 0
                renderable = list(zip(selection_keys,
                    options[offset:self.window_height+offset]))
                draw_menu(renderable)
                continue
            if c == 'q':
                raise ExitMenuException()
            try:
                return dict(renderable)[c]
            except KeyError as e:
                self.error("({0}) is not a valid choice!".format(e.args[0]))

    @fullscreen
    def clear_window(self):
        lines = self.window_height
        with t.location(3,lines):
            while lines:
                _echo(t.clear_eol)
                t.move_y(lines)
                lines -= 1

    @fullscreen
    def get_char(self):
        with t.location(1, self.window_height+3):
            _echo(t.clear_eol())
            with t.cbreak():
                c = sys.stdin.read(1)
        return c

    @fullscreen
    def get_line(self):
        with t.location(1, self.window_height+3):
            _echo(t.clear_eol())
            line = sys.stdin.readline().strip()
        return line

    def _get_geometry(self):
        self.window_height = t.height - 5

def _echo(text):
    """Display ``text`` and flush output."""
    sys.stdout.write(u'{}'.format(text))
    sys.stdout.flush()



interface = Interface()
