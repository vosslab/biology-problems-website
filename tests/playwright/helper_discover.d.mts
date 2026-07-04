// Type declarations for helper_discover.mjs. Runtime behavior lives in the
// .mjs; this file only declares signatures so the .ts spec type-checks.

// Parse sitemap.xml text into the normalized, deduped, "/"-first route list.
export declare function parseSitemap(xmlText: string): string[];

// Fetch sitemap.xml over HTTP from baseUrl and return the normalized route list.
export declare function discoverRoutes(baseUrl: string): Promise<string[]>;
