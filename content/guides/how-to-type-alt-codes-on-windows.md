---
title: "How to Type Alt Codes on Windows (With and Without a Numpad)"
h1: "How to type Alt codes on Windows"
description: "Alt codes are typed with the left Alt key plus the numeric keypad. Here is the full method, the three-digit and four-digit code tables, and what to do when your keyboard has no numpad."
slug: "how-to-type-alt-codes-on-windows"
updated: "2026-10-13"
intent: "how to type alt codes"
---

An Alt code is a number you type on the numeric keypad while holding the left
**Alt** key. Releasing Alt makes Windows insert the character for that number.
The method only works on the physical numeric keypad, so a desktop keyboard or a
full-size laptop keyboard is required. Three-digit codes such as **Alt+3** produce
characters from the OEM code page; four-digit codes with a leading zero such as
**Alt+0176** produce characters from the Windows (ANSI) code page. Both tables
exist, which is why one symbol can have two valid Alt codes.

## The exact keystrokes

1. Turn **Num Lock** on. The Num Lock light on the keypad must be lit.
2. Click where you want the character to appear so the cursor is in the right place.
3. Press and hold the **Alt** key. Use the Alt key on the left of the space bar.
4. Type the code on the **numeric keypad**, not the number row above the letters.
5. Release **Alt**. The character appears.

For **Alt+3** you hold Alt, tap the **3** on the keypad, and release. A black heart
suit appears. For **Alt+0176** you hold Alt, type **0**, **1**, **7**, **6**, and
release. A degree sign appears.

## Three-digit codes and four-digit codes are different tables

The two ranges are not two ways of writing the same thing.

| Range | Table | Example | Character |
|---|---|---|---|
| Alt+1 to Alt+255 | OEM code page 437 | Alt+3 | ♥ |
| Alt+0128 to Alt+0255 | Windows-1252 (ANSI) | Alt+0176 | ° |
| Alt+0 to Alt+255 | Some applications accept both | Alt+248 | ° |

Below 128 the two tables agree because both inherit ASCII. Above 127 they diverge.
Alt+248 gives a degree sign from code page 437, and Alt+0176 gives the same degree
sign from Windows-1252, but Alt+130 and Alt+0130 produce different characters.

The characters in the 1 to 31 range are the awkward ones. Code page 437 assigns a
picture to each of those slots, so **Alt+1** gives a white smiley and **Alt+3** gives
a heart. Those numbers are not printable Unicode characters. They draw a picture
only because the OEM console font places a glyph in that cell. In a modern
application using a TrueType font, the same keystroke can insert nothing visible or
an invisible control character.

## When Num Lock is on and nothing appears

The most common cause is typing the code on the number row instead of the keypad.
Windows receives those keys as ordinary digit characters and there is no Alt code
sequence to complete. The second most common cause is a laptop that folds the numpad
into the letter keys. Hold **Fn** and check whether keys such as **U**, **I**,
**O**, **J**, **K** and **L** carry small number labels. If they do, hold **Fn** as
well as **Alt** while you type the code.

If you need a character and neither of those applies, the Alt code method is not
available to you on that keyboard. Use the [Character Viewer / Emoji
panel](/how-to/type-symbols-without-a-numpad/), an HTML entity, or copy the
character directly.

## Finding the right code

Every symbol page on this site lists its legacy Alt code, its decimal codepoint and
its hex codepoint, so you can pick whichever method your keyboard supports. Search
the symbol by name if you do not know the number.

## FAQ

### Does the Alt code method work on Windows 11?

Yes. The numeric keypad entry path is a long-standing part of the Windows text input
stack and has not been removed. Num Lock must still be on, and the left Alt key must
still be used.

### Why does the right Alt key not work?

The right Alt key is often mapped to **AltGr**, which composes accented characters
rather than starting a numeric Alt sequence. Use the Alt key on the left of the space
bar.

### Can I use Alt codes in a browser?

Yes, in any text field that accepts keyboard input, including address bars, search
boxes and web forms. The browser does not intercept the sequence.
