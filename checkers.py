from tui import TUI
import argparse

def start(online, nrows, gamedisplay, **kwargs):
    if online == 1:
        raise NotImplementedError("Online Functionality not implemented")
    if gamedisplay == "tui":
        if online == 0:
            game = TUI(2, nrows)
            game.play()
    else:
        raise Exception("Invalid argument")

parser = argparse.ArgumentParser(description='Let\'s play checkers')
parser.set_defaults(method = start)
parser.add_argument("-o", "--online", type = int, choices = [0,1], default = 0)
parser.add_argument("-n", "--nrows", type = int, default = 3)
parser.add_argument("-g", "--gamedisplay", type = str, default = "tui")
args = parser.parse_args()
args.method(**vars(args))
