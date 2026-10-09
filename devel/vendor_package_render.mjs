// Refresh: npm ci --ignore-scripts --prefix devel/package_render_vendor
// Then: node devel/vendor_package_render.mjs
import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const packages = path.join(root, "devel/package_render_vendor/node_modules");
const output = path.join(root, "site_docs/assets/package_render");
const rdkitLicense = "https://raw.githubusercontent.com/rdkit/rdkit/"
	+ "fece8caa860bdf6c9c82bdb9253f22a0cf87150c/license.txt";
const entries = [
	["modern-screenshot/dist/index.mjs", "modern_screenshot.mjs"],
	["modern-screenshot/LICENSE", "modern_screenshot_license.txt"],
	["@rdkit/rdkit/dist/RDKit_minimal.js", "rdkit.js"],
	["@rdkit/rdkit/dist/RDKit_minimal.wasm", "rdkit.wasm"],
];
await mkdir(output, { recursive: true });
const files = {};
for (const [source, destination] of entries) {
	const bytes = await readFile(path.join(packages, source));
	await writeFile(path.join(output, destination), bytes);
	files[destination] = createHash("sha256").update(bytes).digest("hex");
}
// npm omits RDKit's license text; preserve the upstream BSD license at a pinned revision.
const response = await fetch(rdkitLicense);
if (!response.ok) { throw new Error("Could not retrieve RDKit's pinned license."); }
const license = Buffer.from(await response.arrayBuffer());
await writeFile(path.join(output, "rdkit_license.txt"), license);
files["rdkit_license.txt"] = createHash("sha256").update(license).digest("hex");
const dependencies = JSON.parse(await readFile(
	path.join(root, "devel/package_render_vendor/package.json"), "utf8",
)).dependencies;
const manifest = { dependencies, rdkitLicense, files };
await writeFile(path.join(output, "source.json"), JSON.stringify(manifest, null, 2) + "\n");
console.log("Vendored browser package rendering assets.");
