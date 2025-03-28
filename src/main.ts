import { readdir } from "fs/promises";
import { intToRGBA, Jimp } from "jimp";
import { basename, extname, join, resolve } from "path";

const convertPngToSvg = async (inputPath: string, outputPath: string) => {
	const image = await Jimp.read(inputPath);
	const { width, height } = image;

	let svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 ${width} ${height}' width='${width}' height='${height}'>`;

	for (let y = 0; y < height; y++) {
		for (let x = 0; x < width; x++) {
			const color = image.getPixelColor(x, y);
			const { r, g, b, a } = intToRGBA(color);

			if (a > 0) {
				const hexColor = `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b
					.toString(16)
					.padStart(2, "0")}`;
				svg += `<rect x='${x}' y='${y}' width='1' height='1' fill='${hexColor}'/>`;
			}
		}
	}

	svg += `</svg>`;

	svg = svg.replace(/\s+/g, " ").trim();

	await Bun.write(outputPath, svg);
	console.log(`${inputPath} → ${outputPath}`);
};

const processDirectory = async (directory: string) => {
	try {
		const files = await readdir(directory);
		const pngFiles = files.filter(file => extname(file).toLowerCase() === ".png");

		if (pngFiles.length === 0) {
			console.log(`No .png files found in the provided directory: ${resolve(directory)}`);
			return;
		}

		for (const file of pngFiles) {
			const inputPath = join(directory, file);
			const outputPath = join(directory, `${Bun.argv[3] ?? "png2svg"}/${basename(file, ".png")}.svg`);
			await convertPngToSvg(inputPath, outputPath);
		}

		console.log(`${files.length} .png files converted to .svg`);
	} catch (error) {
		console.error("Error processing directory:", error);
	}
};

processDirectory(Bun.argv[2] ?? ".");
