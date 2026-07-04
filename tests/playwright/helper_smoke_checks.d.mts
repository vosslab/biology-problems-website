// Type declarations for helper_smoke_checks.mjs. Runtime behavior lives in the
// .mjs; this file only declares signatures so the .ts spec type-checks.

import type { Page } from "@playwright/test";

// Assert the core mkdocs-material shell renders on this route. Throws on a miss.
export declare function checkPageStructure(page: Page, route: string): Promise<void>;

// Drive the first self-test on the page (if any). Throws on a broken or
// inoperable self-test; returns whether one was present and driven.
export declare function driveSelfTestIfPresent(
	page: Page,
	route: string,
): Promise<{ present: boolean; driven: boolean }>;
