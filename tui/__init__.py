import sys
import textwrap
import curses
from blessed import Terminal

from coc.exceptions import *

t = Terminal()
w = textwrap.TextWrapper(fix_sentence_endings = True)
_pause_sequence = False
in_fullscreen = True
window_height = 0
window_width = 0
_screenbuffer = ''

def _fullscreen(func):
    def _decorator(*args, **kwargs):
        global in_fullscreen
        try:
            return func(*args, **kwargs)
        except InterfaceException:
            if in_fullscreen:
                _echo(t.exit_fullscreen)
                in_fullscreen = False
            raise
    return _decorator

def _get_geometry():
    global window_height
    global window_width
    window_height = t.height - 6
    window_width = t.width - 4
    w.width = window_width

def _dump_buffer(func):
    def _decorator(*args, **kwargs):
        global _screenbuffer
        _screenbuffer = ''
        return func(*args, **kwargs)
    return _decorator

def _clean_up_errors(func):
    def _decorator(*args, **kwargs):
        ret = func(*args, **kwargs)
        with t.location(3,t.height-1):
            _echo(t.clear_eol)
        return ret
    return _decorator


class Interface:
    """ Provides an API to interact through a terminal interface with a user
    """
    def __init__(self):
        _echo(t.enter_fullscreen)
        _get_geometry()

    @_fullscreen
    @_dump_buffer
    def clear(self):
        return self.blank_window()

    @_fullscreen
    def blank_window(self):
        lines = window_height
        with t.hidden_cursor():
            while lines:
                with t.location(y=lines+1, x=3):
                    _echo(t.clear_eol)
                lines -= 1

    @_fullscreen
    def error(self, text):
        with t.location(3, t.height-1):
            _echo(t.clear_eol())
            _echo(text)

    @_fullscreen
    def title(self, text):
        with t.location(3, 0):
            _echo(t.clear_eol())
            _echo(t.bold(text))

    @_fullscreen
    def prompt(self, text):
        try:
            text = text.splitlines()[0]
            text = text[:window_width - 4]
        except IndexError:
            pass
        with t.location(3, t.height-3):
            _echo(t.clear_eol())
            _echo(text)

    @_fullscreen
    def print(self, text=None, pause=True, buffer='use'):
        global _screenbuffer
        global window_height
        if buffer == 'flush':
            _screenbuffer = ''
        self.blank_window()
        offset = 0
        lines = list()
        if text:
            if buffer == 'ignore':
                for line in text.splitlines():
                    lines.extend(w.wrap(line))
            else:
                _screenbuffer = _screenbuffer + '\n\n' + text
                for line in _screenbuffer.splitlines():
                    lines.extend(w.wrap(line))
        else:
            for line in _screenbuffer.splitlines():
                lines.extend(w.wrap(line))
        lines.reverse()
        while True:
            y = window_height+1
            for item in lines[offset:window_height+offset]:
                with t.location(x=3, y=y):
                    _echo(t.clear_eol)
                    _echo(item)
                y -=1
            if pause:
                c = '_'
                while c not in ' +-':
                    c = self.get_char()
                if c == '+':
                    offset = min(offset + 3, len(lines) - window_height)
                elif c == '-':
                    offset = max(0, offset - 3)
                else:
                    return
            else:
                return

    @_fullscreen
    @_clean_up_errors
    def menu_choice(self, choices, title=None):
        def draw_menu(renderable):
            self.blank_window()
            rendered = [
                    '({0}) - {1}'.format(a,b)
                    for a,b in
                    renderable
                    ]
            self.prompt('Press a key to select. q to quit, - to scroll up, + to'
                            'scroll down.')
            y = 2
            for item in rendered:
                with t.location(x=5,y=y):
                    _echo(t.clear_eol)
                    _echo(item)
                y +=1
        global window_height
        offset = 0
        if title:
            self.title(title)
        selection_keys = '0123456789abcdefghijklmnoprstuvwxyz'
        renderable = list(zip(selection_keys,
            choices[offset:window_height+offset]))
        draw_menu(renderable)
        selection = None
        while True:
            c = self.get_char()
            if c == '+':
                offset += 3
                if offset > len(choices) - window_height:
                    offset = len(choices) - window_height
                if offset < 0:
                    offset = 0
                renderable = list(zip(selection_keys,
                    choices[offset:window_height+offset]))
                draw_menu(renderable)
                continue
            if c == '-':
                offset -= 3
                if offset < 0:
                    offset = 0
                renderable = list(zip(selection_keys,
                    choices[offset:window_height+offset]))
                draw_menu(renderable)
                continue
            if c == 'q':
                raise ExitMenuException()
            try:
                return dict(renderable)[c]
            except KeyError as e:
                self.error("that's not a valid choice!".format(e.args[0]))

    @_fullscreen
    @_clean_up_errors
    def boolean_choice(self, text=None, prompt="Press (y) or (n) to choose.", title=None):
        if title is not None:
            self.title(title)
        self.clear()
        self.prompt(prompt)
        if text:
            self.print(text, pause=False, buffer='ignore')
        while True:
            b = self.get_char()
            if b == 'y':
                return True
            if b == 'n':
                return False

    @_fullscreen
    def get_char(self, text=None, prompt=None, title=None):
        if prompt:
            self.prompt(prompt)
        if title:
            self.title(title)
        if text:
            self.print(text, pause=False, dump_buffer=True)
        with t.location(1, window_height+4):
            _echo(t.clear_eol())
            with t.hidden_cursor():
                with t.cbreak():
                    c = t.getch()
        return c

    @_fullscreen
    def get_line(self, prompt=None, title=None):
        if prompt:
            self.prompt(prompt)
        if title:
            self.title(title)
        with t.location(1, window_height+4):
            _echo(t.clear_eol())
            line = input()
        return line

    @_fullscreen
    @_clean_up_errors
    def get_quantity(self, max, min, is_float=False, autoround=True, text=None, prompt=None, title=None):
        try:
            max = float(max) if is_float else int(max)
            min = float(min) if is_float else int(min)
        except ValueError as e:
            raise InterfaceException("requested a quantity with non-numeric"
                    " value bounds (value was {0})".format(str(e.args[0])))
        if prompt:
            self.prompt(prompt)
        else:
            self.prompt('Enter a whole number between {0} and {1}'.format(min, max))
        if title:
            self.title(title)
        if text:
            self.print(text, pause=False, buffer='ignore')
        while True:
            with t.location(1, window_height+4):
                _echo(t.clear_eol())
                raw = sys.stdin.readline().strip()
                try:
                    q = float(raw) if is_float else int(raw)
                except ValueError:
                    self.error("That's not a number!")
                    continue
            if q > max:
                if autoround:
                    return max
                else:
                    self.error("Too high! Maximum value is {0}".format(str(max)))
            elif q < min:
                if autoround:
                    return min
                else:
                    self.error("Too low! Minimum value is {0}".format(str(min)))
            else:
                return q

def _echo(text):
    """Display ``text`` and flush output."""
    sys.stdout.write(u'{}'.format(text))
    sys.stdout.flush()

interface = Interface()
