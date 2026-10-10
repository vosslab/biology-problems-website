import { mkdir, readFile, realpath, writeFile } from "node:fs/promises";
import { basename, dirname, resolve, sep } from "node:path";
import { convert, formats, initialize } from "../src/index.js";
await initialize(new Uint8Array(await readFile(new URL("../generated/qti_wasm_bg.wasm", import.meta.url))));
const [inputPath, inputFormat = "bbq_text_upload", outputFormat = "blackboard_qti_v2_1", outputDirectory, ...companionPaths] = process.argv.slice(2);
if (!inputPath || !outputDirectory) {
    throw new Error("Usage: npm run example:node -- INPUT INPUT_FORMAT OUTPUT_FORMAT OUTPUT_DIRECTORY [ASSET_NAME=PATH ...]");
}
const output = formats().formats.find((format) => format.name === outputFormat && format.canWrite);
if (!output)
    throw new Error(`Unknown output format: ${outputFormat}`);
const root = resolve(outputDirectory);
await mkdir(root, { recursive: true });
const canonicalRoot = await realpath(root);
const companions = await Promise.all(companionPaths.map(async (argument) => {
    const separator = argument.indexOf("=");
    const path = separator < 0 ? argument : argument.slice(separator + 1);
    const name = separator < 0 ? basename(path) : argument.slice(0, separator);
    return { name, bytes: new Uint8Array(await readFile(path)) };
}));
const result = convert({
    inputFormat,
    outputFormat,
    input: { kind: "file", name: inputPath.split(/[\\/]/).at(-1) ?? "questions.txt", bytes: new Uint8Array(await readFile(inputPath)), companions },
    allowMixed: true,
    outputName: output.defaultOutputName,
    document: { title: "Node question bank", date: "2026-01-01" },
    shuffleSeed: 0,
});
for (const warning of result.warnings)
    console.error(`${warning.stage}: ${warning.message}`);
if (result.status === "error")
    throw new Error(`${result.error.category}: ${result.error.message}`);
const artifact = result.artifact;
const files = artifact === null ? [] : artifact.kind === "file" ? [artifact.primary, ...artifact.companions] : artifact.entries;
for (const file of files)
    await persist(file);
console.log(`Converted ${result.itemCount} item(s); wrote ${files.length} file(s) to ${root}`);
async function persist(file) {
    // ASVS 5.3.2: revalidate logical names at the filesystem persistence boundary.
    if (!file.name || file.name.includes("\\") || file.name.includes(":") || /[\x00-\x1f\x7f]/.test(file.name) || file.name.split("/").some((part) => part === "" || part === "." || part === "..")) {
        throw new Error(`Unsafe output name: ${file.name}`);
    }
    const path = resolve(root, file.name);
    if (!path.startsWith(root + sep))
        throw new Error(`Output escaped destination: ${file.name}`);
    await mkdir(dirname(path), { recursive: true });
    const canonicalParent = await realpath(dirname(path));
    if (canonicalParent !== canonicalRoot && !canonicalParent.startsWith(canonicalRoot + sep))
        throw new Error(`Output parent escaped destination: ${file.name}`);
    await writeFile(path, file.bytes, { flag: "wx" });
}
