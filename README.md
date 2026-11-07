# Zahlenwerk – the number factory

![Zahlenwerk](zahlenwerk-wallpaper.webp)

A cozy browser game about conveyor belts and quick arithmetic. Numbered tiles pile up in the factory. You send them onto the belts and flip the switches so each tile reaches a mailbox whose station turns it into the number that mailbox wants.

Each decision is small ("7 through +3 is 10, so mailbox 2"). The challenge is keeping several tiles moving at once without mixing up their routes, while the factory speeds up.

**Play:** open `index.html` in a browser. There's no build step and nothing to install.

## How to play

1. Tiles pile up in the **factory**. <kbd>Space</kbd> (or a click on the factory) sends the next one.
2. Each **mailbox** shows the number it wants. Its **station** (e.g. `+3`) changes every tile on the way in.
3. Steer with the **switches**: <kbd>1</kbd>–<kbd>4</kbd> (or clicking a mailbox) sets the whole route, <kbd>0</kbd>/<kbd>X</kbd> sends to the recycler. You can also click a single switch.
4. A switch only matters at the moment a tile reaches it. Set the next route once the previous tile has passed.

| Thing | Rule |
|---|---|
| Order runs out of time | You lose a gear ⚙ (you have 5) |
| Wrong number delivered | Tile is sent back: −25 points, combo lost |
| 6 tiles in the factory | The factory jams and sends tiles out by itself, wherever the switches point |
| New shift (every 8 orders) | +1 gear, stations retooled, faster belts, tiles arrive more often |
| Shift 1 / 2 / 3+ | `+` only / `+` and `−` / `×` joins and every mailbox takes two orders |
| <kbd>P</kbd> / <kbd>Esc</kbd> | Pause |

Tiles on the belt show where they're headed with the current switch settings: **✓** fits an order, **✕** doesn't, **♻** goes to the recycler, **2** means another tile reaches that order first. A small ✓ on an order bubble means a tile is already on its way to fill it.

Most tiles the factory produces fill an open order that no other tile is heading for yet. Some are junk that fits nowhere and belongs in the recycler, and more of them show up in later shifts.

## Project layout

```
index.html                 the whole game (canvas + vanilla JS, no dependencies)
assets/*.png               machine sprites rendered in Blender
blender/render_sprites.py  script that models and renders the sprites
zahlenwerk-wallpaper.webp  the original artwork the game is based on
```

If a sprite can't be loaded, the game falls back to drawing that machine with canvas shapes.

## Re-rendering the sprites

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -P blender/render_sprites.py -- "$PWD/assets"
```

The sprites are rendered with Cycles in an orthographic view tilted 37° (so the cylinders match the 0.8 ellipse ratio used in the game). A shadow-catcher plane provides soft drop shadows, and an ink outline is added afterwards around each silhouette. Scale: 1 Blender unit = 50 game px, rendered at 2×.
