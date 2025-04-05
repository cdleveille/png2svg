#!/usr/bin/env python3
import os
from PIL import Image
import svgwrite
from collections import defaultdict

def png_to_svg_optimized(input_file, output_file=None, scale=1):
    """
    Convert a PNG pixel art image to SVG with shape optimization
    by merging adjacent pixels of the same color

    Args:
        input_file: Path to the input PNG file
        output_file: Path to save the output SVG file (defaults to same name with .svg)
        scale: Optional scale factor for the output SVG
    """
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.svg"

    # Open the image and ensure it's in RGBA mode
    img = Image.open(input_file).convert('RGBA')
    width, height = img.size

    # Get pixel data as a 2D array for easier neighbor checking
    pixel_data = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel = img.getpixel((x, y))
            row.append(pixel)
        pixel_data.append(row)

    # Create SVG drawing
    drawing = svgwrite.Drawing(
        output_file,
        size=(width * scale, height * scale),
        viewBox=f"0 0 {width} {height}"
    )

    # Function to create color key
    def color_key(rgba):
        r, g, b, a = rgba
        return f"#{r:02x}{g:02x}{b:02x}|{a}"

    # Step 1: Scan horizontally to create horizontal strips
    horizontal_strips = []
    for y in range(height):
        x = 0
        while x < width:
            pixel = pixel_data[y][x]
            # Skip transparent pixels
            if pixel[3] == 0:
                x += 1
                continue

            # Find how far this color extends horizontally
            start_x = x
            while x < width and pixel_data[y][x] == pixel:
                x += 1

            # Add horizontal strip
            strip_width = x - start_x
            strip = {
                'x': start_x,
                'y': y,
                'width': strip_width,
                'height': 1,
                'color': pixel
            }
            horizontal_strips.append(strip)

    # Step 2: Merge vertical strips where possible
    merged_rectangles = []

    # Group horizontal strips by x and width
    strips_by_position = defaultdict(list)
    for strip in horizontal_strips:
        key = (strip['x'], strip['width'])
        strips_by_position[key].append(strip)

    # For each group, try to merge vertically
    for (x, width), strips in strips_by_position.items():
        # Sort strips by y-position
        strips.sort(key=lambda s: s['y'])

        current_rect = None
        for strip in strips:
            if (current_rect is None or
                strip['y'] != current_rect['y'] + current_rect['height'] or
                strip['color'] != current_rect['color']):
                # Start a new rectangle
                if current_rect:
                    merged_rectangles.append(current_rect)
                current_rect = dict(strip)
            else:
                # Extend current rectangle vertically
                current_rect['height'] += 1

        # Add the last rectangle
        if current_rect:
            merged_rectangles.append(current_rect)

    # Add rectangles to SVG
    for rect in merged_rectangles:
        r, g, b, a = rect['color']
        color = f"#{r:02x}{g:02x}{b:02x}"

        if a < 255:
            opacity = a / 255
            drawing.add(drawing.rect(
                insert=(rect['x'], rect['y']),
                size=(rect['width'], rect['height']),
                fill=color,
                fill_opacity=opacity
            ))
        else:
            drawing.add(drawing.rect(
                insert=(rect['x'], rect['y']),
                size=(rect['width'], rect['height']),
                fill=color
            ))

    # Save the SVG
    drawing.save()
    print(f"Converted {input_file} to {output_file}")
    print(f"Optimized from {width*height} potential pixels to {len(merged_rectangles)} rectangles")
    return output_file

def process_directory(directory, scale=1):
    """Process all PNG files in a directory"""
    png_files = [f for f in os.listdir(directory) if f.lower().endswith('.png')]
    for png_file in png_files:
        input_path = os.path.join(directory, png_file)
        png_to_svg_optimized(input_path, scale=scale)

if __name__ == "__main__":
    process_directory('.', scale=1)
