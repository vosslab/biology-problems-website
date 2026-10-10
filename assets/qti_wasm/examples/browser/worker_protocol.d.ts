import type { ConvertResult, FormatInventory } from "../../src/index.js";
/** Worker messages contain the generated Rust DTOs without parallel host models. */
export type WorkerResponse = {
    type: "ready";
    inventory: FormatInventory;
    initMs: number;
} | {
    type: "converted";
    result: ConvertResult;
    conversionMs: number;
} | {
    type: "error";
    message: string;
};
