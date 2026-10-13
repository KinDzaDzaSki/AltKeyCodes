---
title: "What Is an Alt Code? Alt Codes vs Unicode Code Points"
h1: "What is an Alt code?"
description: "An Alt code is a number from an older Windows code page that you type on the numeric keypad while holding Alt. It is not the same as a Unicode code point. Here is how the two systems differ and why it matters."
slug: "what-is-an-alt-code"
updated: "2026-10-13"
intent: "what is an alt code"
---

An Alt code is a number typed on the numeric keypad while the left **Alt** key is
held down. Releasing Alt inserts the character that number maps to. The mapping comes
from the IBM PC code pages, not from Unicode: three-digit codes use OEM code page 437
and four-digit codes with a leading zero use the Windows-1252 code page. Because
those two tables only hold 256 characters each, Alt codes stop at 255 while Unicode
continues into the hundreds of thousands.

## Two code pages, two tables

| Range | Name | Table | Size |
|---|---|---|---|
| Alt+1 to Alt+255 | OEM codes | Code page 437 | 256 slots |
| Alt+0128 to Alt+0255 | ANSI codes | Windows-1252 | 256 slots |
| `Alt` + decimal, up to 65535 | Decimal code point | BMP subset of Unicode | 65,536 slots |
| `Alt` + `+` then hex | Hex code point, registry opt-in | Full Unicode | 1,114,112 slots |

The first two rows are the classic Alt codes. The bottom two rows are not code pages
at all: they pass a raw Unicode code point through the same key input path.

## Why one symbol can have two Alt codes

Code page 437 and Windows-1252 both came from ASCII, so the first 128 slots agree.
Above 127 they were filled in independently. A degree sign is at position 248 in code
page 437 and at position 176 in Windows-1252, which is why both `Alt+248` and
`Alt+0176` produce °. A heart suit exists only in code page 437, so it has one code,
`Alt+3`, and no four-digit form.

For characters that exist in neither code page there is no legacy Alt code at all.
A check mark is `U+2713`, which is well past both tables, so there is no three-digit
or four-digit Alt code for it. What does work is `Alt` + `10003`, the decimal code
point, on a keyboard that has a numeric keypad.

## Alt code or code point, which do you quote

Quote whichever one the destination understands, and quote both when you are writing
for an audience that might be on either. A support article that says "type Alt+0176"
is useful to a Windows desktop user and useless to a Mac user. The same article saying
"the degree sign is `U+00B0`; on Windows use `Alt+0176`, on macOS use `⌥⇧8`, in HTML
use `&deg;`" is useful to all three. Every symbol page on this site quotes all of them
so you never have to translate.

## What the code page history changed

The characters in the 1 to 31 range have no printable character in Unicode. Code page
437 assigned a picture to each of those slots and the OEM console font drew it, which
is where the well-known `Alt+1` smiley and `Alt+3` heart come from. Those keystrokes
still produce a picture in a console window using a raster font. In a modern
application drawing with a TrueType font, the same input can produce nothing visible,
because the code point being inserted is a control character rather than a picture.

## FAQ

### Is the Alt key on the right the same?

No. The right Alt key is usually mapped to AltGr for composing accented characters.
Only the left Alt key starts a numeric Alt sequence.

### Are Alt codes the same as ASCII codes?

Below 128 they are. ASCII defines the first 128 slots of every code page, so `Alt+65`
gives A for the same reason ASCII 65 is A. Above 127 they diverge, which is the whole
reason the two Alt code tables disagree.

### Do Alt codes still work on current Windows versions?

Yes. The numeric keypad input path is still part of the Windows text input stack. What
has changed is the font: a modern font can only draw the picture for a control code if
the application asks for it to be drawn.
