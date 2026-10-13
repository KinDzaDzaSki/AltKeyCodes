---
title: "Windows Alt+X Hex Codes: Type Any Unicode Character"
h1: "Windows Alt+X hex codes"
description: "Type a Unicode hex code point then press Alt and X to convert it into the character in Word, WordPad and Outlook. Here is how the method works, where it stops, and the registry setting for the numpad form."
slug: "unicode-alt-x-hex-codes-windows"
updated: "2026-10-13"
intent: "alt x unicode hex windows"
---

The Alt+X method converts a hex code point into the character it represents. Type
**2713** into a document, press **Alt** and **X** together, and the four digits are
replaced with ✓. The sequence is handled by the application rather than by Windows
itself, which is why it works in Microsoft Word, WordPad, Outlook, and some other
rich text editors but not in Notepad, browsers or most chat applications.

## The method

1. Type the hex code point where you want the character. Do not include `0x` or the
   `U+` prefix.
2. Press **Alt** and **X** at the same time.
3. The digits are replaced by the character.

Pressing **Alt** and **X** again reverses the conversion and puts the hex code back,
which makes it easy to check what a character is. Select a character you did not
type, press **Alt** and **X**, and Word shows you its code point.

The value is the same number listed as the Unicode code point on this site's symbol
pages, so a page showing `U+2713` is telling you to type `2713`.

## Where it works

| Application | Alt+X support |
|---|---|
| Word, WordPad, Outlook | Yes |
| LibreOffice Writer | Yes, with the same key combination |
| Notepad | No |
| Browsers and web forms | No |
| Most chat and messaging clients | No |

Treat it as a word processing feature. If you need a character somewhere that does not
support it, use the HTML escape, a CSS escape, or copy the character.

## The numpad hex form

Windows itself has a second, undocumented in the user interface, hex input path.
Adding a registry value turns it on:

```
HKEY_CURRENT_USER\Control Panel\Input Method
  Value name:  EnableHexNumpad
  Value type:  REG_SZ
  Value data:  1
```

Restart after adding it. Then hold **Alt**, press the **+** key on the numeric keypad,
type the hex code point, and release **Alt**. So **Alt** + **+** then `2713` then
release Alt inserts ✓.

This route also needs a numeric keypad, and it registers as a system-wide input
method rather than an application feature. It is worth setting up only if you type
symbols often enough that the Character Viewer and copy-paste have become too slow.
If you have no numpad, none of the Alt-based routes are available to you and you
should use the [Character Viewer](/how-to/type-symbols-without-a-numpad/) instead.

## Why the hex codepoint is more useful than an Alt code

Legacy Alt codes only cover 255 characters, taken from two older code pages. The hex
code point is the character's real identifier in Unicode and exists for every one of
the more than 150,000 assigned characters. Once you know that the character you want
is `U+2713`, that single number works in Word with Alt+X, in HTML as `&#x2713;`, in
CSS as `\2713`, in Python with `\u2713`, and in the macOS Character Viewer search
field. A legacy Alt code works in one place.

## FAQ

### Why does Alt+X do nothing in my document?

Either the application does not implement it, or there is no valid hex code under
the cursor. Alt+X needs the cursor immediately after a run of hex digits. Place the
cursor directly after the last digit and try again.

### Can I use more than four digits?

Yes. Unicode code points above `U+FFFF` are written with five or six hex digits, such
as `1F600` for a grinning face. Alt+X accepts those values.

### Does Alt+X change the document character encoding?

No. It inserts the character into the document using whatever encoding the file
already uses. In a modern Word file that is Unicode, so any character is available.
