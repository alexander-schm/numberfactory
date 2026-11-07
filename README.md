# Zahlenwerk – die Zahlenfabrik

![Zahlenwerk](zahlenwerk-wallpaper.webp)

Ein gemütliches Browserspiel über Förderbänder. Nummerierte Plättchen verlassen die Fabrik, fahren durch Stationen, Addierer und Schranken und müssen den Briefkasten erreichen, der sie haben will. Rechnen musst du nie selbst: Jeder Briefkasten zeigt, was aus dem wartenden Plättchen auf dem Weg dorthin würde. Die Herausforderung liegt im Timing, im Jonglieren mit mehreren Plättchen gleichzeitig und darin, die Maschinen jedes Levels geschickt zu nutzen.

**Spielen:** `index.html` im Browser öffnen. Es gibt keinen Build-Schritt und nichts zu installieren.

## Level

| # | Level | Was ist neu |
|---|---|---|
| 1 | Erste Schicht | Plättchen losschicken und eine Weiche stellen |
| 2 | Recycling | Ausschuss-Plättchen, eine 3-Wege-Weiche, der Recycler |
| 3 | Verteilung | Vier Briefkästen; eine Taste stellt alle Weichen auf dem Weg |
| 4 | Der Addierer | Eine Maschine, die ein Plättchen festhält und es mit dem nächsten zu ihrer Summe verschmilzt |
| 5 | Abstellgleis | Schranken, die du anklickst, um Plättchen anzuhalten und freizugeben |
| 6 | Sonderlieferung | Goldene Plättchen (doppelte Punkte), Joker (passen zu jedem Auftrag), Bomben (ab in den Recycler!) |
| 7 | Halbieren & Tauschen | ½ (ungerade Zahlen zerbrechen), ⇄ Ziffern tauschen (12 → 21) |
| 8 | Großfabrik | Alles auf einmal |

Jedes Level hat ein Ziel (N Aufträge erfüllen, in Addierer-Levels zusätzlich eine Anzahl Summen). Sterne: ★ fürs Schaffen, ★ für kein verlorenes Zahnrad, ★ fürs Schlagen der Par-Zeit. Der Fortschritt wird im Browser gespeichert.

## Steuerung

| Taste | Aktion |
|---|---|
| <kbd>Leertaste</kbd> / Klick auf die Fabrik | Wartendes Plättchen losschicken |
| <kbd>1</kbd>–<kbd>4</kbd> / Klick auf einen Briefkasten | Alle Weichen auf dem Weg zu diesem Briefkasten stellen |
| <kbd>0</kbd> / <kbd>X</kbd> / Klick auf den Recycler | Zum Recycler leiten |
| <kbd>A</kbd> / Klick auf den Addierer | Zum Addierer leiten |
| Klick auf eine Weiche | Nur diese Weiche umstellen (Rechtsklick stellt rückwärts um) |
| Klick auf eine Schranke / <kbd>G</kbd> | Eine Schranke / alle Schranken schließen oder öffnen |
| <kbd>P</kbd> / <kbd>Esc</kbd> | Pause |
| <kbd>M</kbd> / Lautsprecher-Knopf oben rechts | Ton an/aus (wird gespeichert) |

## Das Spielfeld lesen

- **Chips unter jedem Briefkasten** zeigen, als was das wartende Plättchen ankommen würde: `→ 14 ✓` erfüllt einen Auftrag, `(vergeben)` heißt, dass schon ein anderes Plättchen zu diesem Auftrag unterwegs ist, `+ ?` heißt, es würde im Addierer warten.
- **Abzeichen auf fahrenden Plättchen** zeigen, was jedes mit den aktuellen Weichenstellungen tun wird: ✓ Auftrag erfüllen, ✕ falsch, ♻ Recycler, + im Addierer warten, 2 ein anderes Plättchen kommt zuerst an, ! Bombe am falschen Ort. Die Vorhersage spielt alle Plättchen in Ankunftsreihenfolge vorwärts, Addierer-Summen inklusive.
- Eine Weiche zählt nur in dem Moment, in dem ein Plättchen sie erreicht. Du kannst also das nächste Plättchen sofort losschicken und die Route ändern, sobald das vorherige vorbei ist.
- In die Warteschlange der Fabrik passen bis zu 6 Plättchen. Läuft sie über, staut sich die Fabrik und schickt Plättchen dorthin, wohin die Weichen gerade zeigen.

Fairness: Jeder Auftrag wird zusammen mit den Plättchen erzeugt, die ihn erfüllen können, einschließlich beider Hälften einer Addierer-Summe. Wartet ein Plättchen im Addierer, plant die Fabrik als Nächstes einen passenden Partner. Kann kein Auftrag das gehaltene Plättchen gebrauchen, wechselt der Auftrag des Addierers zu einem, der es kann.

## Projektaufbau

```
index.html                 das ganze Spiel (Canvas + Vanilla-JS, keine Abhängigkeiten)
assets/*.png               Maschinen- und Plättchen-Sprites, in Blender gerendert
blender/render_sprites.py  Skript, das die Sprites modelliert und rendert
zahlenwerk-wallpaper.webp  das Originalbild, auf dem das Spiel basiert
```

Zum Testen: `index.html#play=3` startet direkt Level 3, `#play=3&end=win` (oder `lose`) springt zum Ergebnisbildschirm.

Kann ein Sprite nicht geladen werden, zeichnet das Spiel diese Maschine stattdessen mit Canvas-Formen.

## Sprites neu rendern

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -P blender/render_sprites.py -- "$PWD/assets"
```

Die Sprites werden mit Cycles in einer orthografischen, um 37° geneigten Ansicht gerendert (damit die Zylinder zum im Spiel verwendeten Ellipsenverhältnis 0,8 passen). Eine Shadow-Catcher-Ebene sorgt für weiche Schlagschatten, und um jede Silhouette wird nachträglich eine Tinten-Kontur gelegt. Maßstab: 1 Blender-Einheit = 50 Spiel-px, gerendert in 2×.
