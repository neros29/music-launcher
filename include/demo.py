from os import system
from sys import path
from wcwidth import wcwidth

path.append("include/pytui/")
from pytui import Label, Tui, Surface, Character


tui = Tui()
offset = [5, 5]
surface: Surface = tui.append([50, 11], offset, " ", 0)
surface.register_keys(["q", "h", "j", "k", "l"])
surface.fill_bg(255, 0, 0)
lab = Label(surface, "Hello world", [5, 5])
lab.update()

system("clear")
while True:
    if surface.get_event("q"):
        break
    if surface.get_event("h"): 
        offset[0] -= 1

    if surface.get_event("j"): 
        offset[1] += 1

    if surface.get_event("k"): 
        offset[1] -= 1

    if surface.get_event("l"): 
        offset[0] += 1
    surface.set_offset(offset[0], offset[1])
    tui.update_screen()

print(f"width {wcwidth('🧮')}")




