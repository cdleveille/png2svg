# png2svg

Convert all PNG files in a directory to SVG format. Works best for low-res images such as pixel art.

## Usage

Run source code via bun...

```bash
bun run src/main.ts [<png_path>] [<svg_path>]
```

...or via compiled executable...

```bash
bun run compile
cd build
png2svg [<png_path>] [<svg_path>]
```

## Arguments

-   `png_path`: Path to read the input PNG files from. If not provided, defaults to `"."`.
-   `svg_path`: Path to write the output SVG files to. If not provided, defaults to `"./png2svg/"`.
