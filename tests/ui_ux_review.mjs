// UI/UX review driver: visits key mkdocs pages at desktop and mobile
// viewports, saves screenshots to test-results/ui_ux_review/, and prints
// a per-page report (status, title, H1 count, broken-link count, contrast hints).
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = 'http://127.0.0.1:8765';
const OUT = 'test-results/ui_ux_review';
fs.mkdirSync(OUT, { recursive: true });

const pages = [
	{ slug: 'home', url: '/' },
	{ slug: 'subject_biochem', url: '/biochemistry/' },
	{ slug: 'subject_genetics', url: '/genetics/' },
	{ slug: 'subject_lab', url: '/laboratory/' },
	{ slug: 'subject_molbio', url: '/molecular_biology/' },
	{ slug: 'subject_biostats', url: '/biostatistics/' },
	{ slug: 'subject_other', url: '/other/' },
	{ slug: 'topic_biochem01', url: '/biochemistry/topic01/' },
	{ slug: 'topic_biochem20', url: '/biochemistry/topic20/' },
	{ slug: 'topic_genetics01', url: '/genetics/topic01/' },
	{ slug: 'topic_genetics11', url: '/genetics/topic11/' },
	{ slug: 'topic_lab01', url: '/laboratory/topic01/' },
	{ slug: 'topic_lab11', url: '/laboratory/topic11/' },
	{ slug: 'topic_molbio04', url: '/molecular_biology/topic04/' },
	{ slug: 'topic_molbio09', url: '/molecular_biology/topic09/' },
	{ slug: 'topic_biostats05', url: '/biostatistics/topic05/' },
	{ slug: 'topic_biostats08', url: '/biostatistics/topic08/' },
	{ slug: 'topic_other01', url: '/other/topic01/' },
	{ slug: 'daily_puzzles_index', url: '/daily_puzzles/' },
	{ slug: 'daily_peptidyle', url: '/daily_puzzles/peptidyle/' },
	{ slug: 'daily_deletion_mutants', url: '/daily_puzzles/deletion_mutants/' },
	{ slug: 'daily_mutant_screen', url: '/daily_puzzles/mutant_screen/' },
	{ slug: 'daily_biomacromolecule', url: '/daily_puzzles/biomacromolecule/' },
	{ slug: 'tutorials_index', url: '/tutorials/' },
	{ slug: 'tutorial_bbq', url: '/tutorials/bbq_tutorial/' },
	{ slug: 'tutorial_bbq_ultra', url: '/tutorials/bbq_ultra_tutorial/' },
	{ slug: 'tutorial_canvas', url: '/tutorials/canvas_tutorial/' },
	{ slug: 'search_results', url: '/?q=enzyme' },
	{ slug: 'author', url: '/author/' },
	{ slug: 'license', url: '/license/' },
];

const viewports = [
	{ name: 'desktop', width: 1280, height: 900 },
	{ name: 'mobile',  width: 390,  height: 844 },
];

async function evalPage(page) {
	return await page.evaluate(() => {
		const h1s = Array.from(document.querySelectorAll('article h1')).map(e => e.textContent.trim());
		const anchors = Array.from(document.querySelectorAll('article a[href]'));
		const internal = anchors.filter(a => {
			const h = a.getAttribute('href');
			return h && !h.startsWith('http') && !h.startsWith('#') && !h.startsWith('mailto:');
		});
		// rel="noopener" only matters when the link opens in a new tab. Flag
		// only external target=_blank links that are missing it.
		const externalNoRel = anchors.filter(a => {
			const h = a.getAttribute('href') || '';
			if (!h.startsWith('http')) return false;
			const target = (a.getAttribute('target') || '').toLowerCase();
			if (target !== '_blank') return false;
			const rel = (a.getAttribute('rel') || '').toLowerCase();
			return !rel.includes('noopener');
		}).length;
		const imgs = Array.from(document.querySelectorAll('article img'));
		// alt="" is a valid decorative-image marker; only flag images with the attribute completely absent.
		const imgsNoAlt = imgs.filter(i => i.getAttribute('alt') === null).length;
		const smallFontIcons = Array.from(document.querySelectorAll('[style*="font-size: 0.8em"], [style*="font-size:0.8em"]')).length;
		const allTables = Array.from(document.querySelectorAll('article table'));
		const tables = allTables.length;
		// Tables that are visible on page load (i.e., not inside a collapsed <details>).
		const visibleTables = allTables.filter(t => !t.closest('details:not([open])')).length;
		const detailsBlocks = document.querySelectorAll('article details').length;
		const title = document.title;
		const navItems = document.querySelectorAll('.md-nav__item').length;
		return { title, h1count: h1s.length, h1: h1s[0] || null,
			internalLinks: internal.length, externalNoRel,
			imgs: imgs.length, imgsNoAlt, smallFontIcons, tables, visibleTables, detailsBlocks, navItems };
	});
}

const browser = await chromium.launch();
const report = [];
for (const vp of viewports) {
	const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
	const page = await ctx.newPage();
	const brokenLinks = [];
	page.on('response', r => {
		if (r.status() >= 400 && r.url().startsWith(BASE)) {
			brokenLinks.push({ url: r.url(), status: r.status() });
		}
	});
	for (const p of pages) {
		const url = BASE + p.url;
		let status = 0;
		let meta = null;
		try {
			const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
			status = resp ? resp.status() : 0;
			await page.waitForTimeout(300);
			meta = await evalPage(page);
		} catch (e) {
			report.push({ vp: vp.name, slug: p.slug, url: p.url, status: 'ERR', err: String(e).slice(0, 120) });
			continue;
		}
		const shot = path.join(OUT, `${p.slug}_${vp.name}.png`);
		await page.screenshot({ path: shot, fullPage: true });
		report.push({ vp: vp.name, slug: p.slug, url: p.url, status, ...meta, shot });
	}
	if (vp.name === 'desktop') {
		try {
			await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 20000 });
			await page.waitForTimeout(300);
			// Material's palette JS runs at page load and reads localStorage before paint.
			// Use a fresh context with the palette pre-seeded via addInitScript.
			const darkCtx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, colorScheme: 'dark' });
			await darkCtx.addInitScript(() => {
				localStorage.setItem('__palette', JSON.stringify({ index: 1, color: { scheme: 'slate', primary: 'green', accent: 'lime' } }));
			});
			const darkPage = await darkCtx.newPage();
			await darkPage.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 20000 });
			await darkPage.waitForTimeout(500);
			await darkPage.screenshot({ path: path.join(OUT, 'home_dark.png'), fullPage: true });
			await darkPage.goto(BASE + '/biochemistry/', { waitUntil: 'domcontentloaded', timeout: 20000 });
			await darkPage.waitForTimeout(500);
			await darkPage.screenshot({ path: path.join(OUT, 'subject_biochem_dark.png'), fullPage: true });
			await darkCtx.close();
		} catch (e) {
			console.log('dark mode capture failed:', String(e).slice(0, 120));
		}
	}
	await ctx.close();
}
await browser.close();

fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
for (const r of report) {
	console.log(`[${r.vp}] ${r.status} ${r.url}  H1=${r.h1count} imgs=${r.imgs} noAlt=${r.imgsNoAlt} tables=${r.tables} visTables=${r.visibleTables} details=${r.detailsBlocks} extNoRel=${r.externalNoRel}`);
}
console.log(`\nWrote ${report.length} rows to ${OUT}/report.json`);
