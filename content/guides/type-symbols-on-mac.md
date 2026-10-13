---
title: "How to Type Symbols on a Mac (Option Keys and Character Viewer)"
h1: "How to type symbols on a Mac"
description: "Macs do not use Alt codes. They use Option key shortcuts and the Character Viewer. Here are the shortcuts for common symbols, the hex entry method, and how to find any character."
slug: "type-symbols-on-mac"
updated: "2026-10-13"
intent: "type symbols on mac"
---

Macs do not use Alt codes. Alt codes are a Windows feature that reads the numeric
keypad, and a Mac keyboard does not send that sequence. On macOS you type symbols two
ways: a direct **Option** key shortcut for the symbols Apple mapped, or the
**Character Viewer**, which contains every character in Unicode and accepts a hex
codepoint. The shortcuts below assume a **US keyboard layout**; other layouts remap
several of them.

## Option key shortcuts

Hold **Option** and press the key, adding **Shift** where shown.

| Shortcut | Symbol | Name |
|---|---|---|
| `⌥⇧8` | ° | Degree sign |
| `⌥G` | © | Copyright sign |
| `⌥R` | ® | Registered sign |
| `⌥2` | ™ | Trademark sign |
| `⌥8` | • | Bullet |
| `⌥/` | ÷ | Division sign |
| `⌥=` | ≠ | Not equal to |
| `⌥⇧=` | ± | Plus-minus sign |
| `⌥,` | ≤ | Less than or equal to |
| `⌥.` | ≥ | Greater than or equal to |
| `⌥V` | √ | Square root |
| `⌥P` | π | Greek small letter pi |
| `⌥Z` | Ω | Greek capital letter omega |
| `⌥D` | ∂ | Partial differential |
| `⌥F` | ƒ | Latin small letter f with hook |
| `⌥W` | ∑ | N-ary summation |
| `⌥-` | – | En dash |
| `⌥⇧-` | — | Em dash |
| `⌥;` | … | Horizontal ellipsis |
| `⌥1` | ¡ | Inverted exclamation mark |
| `⌥⇧/` | ¿ | Inverted question mark |
| `⌥L` | ¬ | Not sign |
| `⌥⇧2` | € | Euro sign |
| `⌥3` | £ | Pound sign |
| `⌥Y` | ¥ | Yen sign |
| `⌥4` | ¢ | Cent sign |
| `⌥S` | ß | Latin small letter sharp s |
| `⌥O` | ø | Latin small letter o with stroke |
| `⌥'` | æ | Latin small letter ae |
| `⌥T` | † | Dagger |
| `⌥⇧R` | ‰ | Per mille sign |
| `⌥6` | § | Section sign |
| `⌥7` | ¶ | Pilcrow sign |
| `⌥5` | ﬁ | Latin small ligature fi |
| `⌥⇧5` | ﬂ | Latin small ligature fl |

The two ligature entries sit next to each other on the keyboard because they are the
same key with and without Shift. Where a shortcut produces something other than the
character listed here, your keyboard layout has remapped it; check the Character
Viewer, which is layout-independent.

Accented letters have their own pattern. The vowel keys are dead keys: press the
Option combination, release, then press the letter.

| Shortcut | Accent | Example |
|---|---|---|
| `⌥E` | acute | `⌥E` then `e` gives é |
| `` ⌥` `` | grave | `` ⌥` `` then `e` gives è |
| `⌥I` | circumflex | `⌥I` then `e` gives ê |
| `⌥U` | diaeresis | `⌥U` then `u` gives ü |
| `⌥N` | tilde | `⌥N` then `n` gives ñ |

## The Character Viewer works for every character

Anything Unicode contains is reachable here, including symbols with no Option
shortcut.

1. Press **⌃⌘Space** (Control + Command + Space) to open the Character Viewer.
2. Use the search field to find the character by name. Searching `check mark` finds ✓
   and `snowflake` finds ❄.
3. Click the character to insert it at the cursor.

Recent and favourite characters appear at the top of the panel, so a character you use
often is one click away after the first time.

## Typing a character by hex codepoint

The Character Viewer accepts a raw code point. Open it with **⌃⌘Space**, type the hex
value of the character into the search field, and it resolves directly. A search for
`2713` returns ✓. This is the closest macOS equivalent of typing an Alt code, and it
works for every character in Unicode rather than only the ones Windows has a code for.

## FAQ

### Why does Option not start a character code the way Alt does?

Option is a composable modifier. macOS composes a fixed mapping of Option plus key to
character, and does not read a numeric sequence after the modifier key. The
equivalent input path is the hex field in the Character Viewer.

### Do Option shortcuts work the same on a UK or German layout?

No. Several shortcuts are layout-specific, and on non-US layouts some Option
combinations produce accented letters instead of symbols. The Character Viewer is
layout-independent and always reliable.

### How do I insert a symbol in Pages, Word or Google Docs on a Mac?

Use **⌃⌘Space** in all of them. Apple's Character Viewer is available system-wide, so
the same shortcut works in any text field in any application.
