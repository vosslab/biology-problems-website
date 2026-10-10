/// <reference lib="webworker" />
import { convert, formats, initialize } from "../../src/index.js";
const worker = self;
function post(message) {
    worker.postMessage(message);
}
async function start() {
    const started = performance.now();
    const response = await fetch(new URL("../../generated/qti_wasm_bg.wasm", import.meta.url));
    if (!response.ok)
        throw new Error(`Wasm load failed (${response.status})`);
    await initialize(new Uint8Array(await response.arrayBuffer()));
    worker.onmessage = (event) => {
        const started = performance.now();
        try {
            post({ type: "converted", result: convert(event.data), conversionMs: performance.now() - started });
        }
        catch (error) {
            post({ type: "error", message: error instanceof Error ? error.message : String(error) });
        }
    };
    post({ type: "ready", inventory: formats(), initMs: performance.now() - started });
}
void start().catch((error) => {
    post({ type: "error", message: error instanceof Error ? error.message : String(error) });
});
