# Zahlenwerk – the number factory

![Zahlenwerk](zahlenwerk-wallpaper.webp)

A cozy browser puzzle game about conveyor belts and arithmetic. Numbered tiles leave the factory, ride the belts through **+ / − / ×** stations and get routed by switches to mailboxes. Each mailbox wants one exact number.

**Play:** open `index.html` in a browser. There's no build step and nothing to install.

## How to play

1. A numbered tile waits in the **factory**. It only leaves when you click the factory or press <kbd>Space</kbd>.
2. Click a **station** to change its operation (`+`, `−`, `×`). Right-click goes backwards. Click a **switch** to change where tiles go.
3. A **dotted preview** shows where the waiting tile will go and what number it turns into at each station. Send it when the preview ends on **✓**.
4. Fill each mailbox's order before its timer runs out.

| Thing | Rule |
|---|---|
| Order runs out of time | You lose a gear ⚙ (you have 5) |
| Wrong number delivered | Tile is sent back: −25 points, combo lost |
| Shift completed (5 orders) | +1 gear, faster belts, less patient orders |
| Shift 3 and later | The factory pushes waiting tiles out by itself after a while |
| <kbd>R</kbd> / right-click factory | Swap the waiting tile (−10 points) |
| <kbd>P</kbd> / <kbd>Esc</kbd> | Pause |

Tiles that are already moving show a badge: **✓** will fill an order, **✕** won't, **♻** is going to the recycler, **2** means another tile reaches that order first. Changing a station also changes tiles still upstream of it, so watch the badges when you run several tiles at once.

Fairness: every tile the factory produces can fill at least one open order with some combination of station settings. Every order can be reached from at least one starting number 1–9.

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
