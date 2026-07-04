// helper_discover.mjs
//
// Route discovery for the content-agnostic smoke test.
//
// Fetches the built site's sitemap.xml and returns every route as a
// normalized, host-less path string. No hardcoded slugs: the sitemap is the
// only source of truth for which routes exist, so this stays correct as
// topics and questions are added or removed.

// ===========================================================================
// normalizeLoc: turn one <loc> URL text into a host-less path string.
//
// - strips the scheme and host, keeping only the path
// - drops any query string and #anchor
// - decodes percent-encoding
// - preserves the trailing-slash form emitted by use_directory_urls
// ===========================================================================
function normalizeLoc(locText) {
	// new URL() parses scheme, host, path, query, and hash for us.
	const parsed = new URL(locText);
	const pathOnly = decodeURIComponent(parsed.pathname);
	return pathOnly;
}

// ===========================================================================
// parseSitemap: turn sitemap.xml text into the normalized route list.
//
// Pure function (no I/O), so both the HTTP path (discoverRoutes) and the
// on-disk path (the runner spec reading site/sitemap.xml at collection time)
// share one source of truth for parsing and normalization.
//
// Returns a deduped array of host-less path strings with "/" first (when
// present). No sampling and no cap: the complete sitemap is the coverage set.
// ===========================================================================
export function parseSitemap(xmlText) {
	// Match every <loc>...</loc> entry. Sitemap XML is simple enough that a
	// focused regex avoids pulling in a third-party XML dependency.
	const locPattern = /<loc>([^<]+)<\/loc>/g;
	const routes = [];
	const seen = new Set();
	let match = locPattern.exec(xmlText);
	while (match !== null) {
		const route = normalizeLoc(match[1]);
		if (!seen.has(route)) {
			seen.add(route);
			routes.push(route);
		}
		match = locPattern.exec(xmlText);
	}

	// Put "/" first when present, so callers that check the home page first
	// get a stable, predictable order.
	const homeIndex = routes.indexOf('/');
	if (homeIndex > 0) {
		routes.splice(homeIndex, 1);
		routes.unshift('/');
	}

	return routes;
}

// ===========================================================================
// discoverRoutes: fetch sitemap.xml over HTTP, return every route.
//
// Thin fetch wrapper around parseSitemap: fetches the built site's sitemap,
// then delegates all parsing and normalization to parseSitemap.
// ===========================================================================
export async function discoverRoutes(baseUrl) {
	const sitemapUrl = `${baseUrl}/sitemap.xml`;
	const response = await fetch(sitemapUrl);
	if (!response.ok) {
		throw new Error(`Failed to fetch sitemap at ${sitemapUrl}: HTTP ${response.status}`);
	}
	const xmlText = await response.text();
	return parseSitemap(xmlText);
}
