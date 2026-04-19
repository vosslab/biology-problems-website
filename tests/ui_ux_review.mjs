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
	{ slug: 'topic_genetics01', url: '/genetics/topic01/' },
	{ slug: 'topic_lab01', url: '/laboratory/topic01/' },
	{ slug: 'daily_puzzles_index', url: '/daily_puzzles/' },
	{ slug: 'daily_peptidyle', url: '/daily_puzzles/peptidyle/' },
	{ slug: 'tutorials_index', url: '/tutorials/' },
	{ slug: 'tutorial_bbq', url: '/tutorials/bbq_tutorial/' },
	{ slug: 'author', url: '/author/' },
	{ slug: 'license', url: '/license/' },
	{ slug: 'biotechnology_orphan', url: '/biotechnology/' },
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
		const externalNoRel = anchors.filter(a => {
			const h = a.getAttribute('href') || '';
			if (!h.startsWith('http')) return false;
			const rel = (a.getAttribute('rel') || '').toLowerCase();
			return !rel.includes('noopener');
		}).length;
		const imgs = Array.from(document.querySelectorAll('article img'));
		const imgsNoAlt = imgs.filter(i => !i.getAttribute('alt')).length;
		const smallFontIcons = Array.from(document.querySelectorAll('[style*="font-size: 0.8em"], [style*="font-size:0.8em"]')).length;
		const tables = document.querySelectorAll('article table').length;
		const title = document.title;
		const navItems = document.querySelectorAll('.md-nav__item').length;
		return { title, h1count: h1s.length, h1: h1s[0] || null,
			internalLinks: internal.length, externalNoRel,
			imgs: imgs.length, imgsNoAlt, smallFontIcons, tables, navItems };
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
			const toggleLabel = await page.$('form[data-md-component="palette"] label');
			if (toggleLabel) { await toggleLabel.click(); await page.waitForTimeout(400); }
			await page.screenshot({ path: path.join(OUT, 'home_dark.png'), fullPage: true });
			await page.goto(BASE + '/biochemistry/', { waitUntil: 'domcontentloaded', timeout: 20000 });
			await page.waitForTimeout(400);
			await page.screenshot({ path: path.join(OUT, 'subject_biochem_dark.png'), fullPage: true });
		} catch (e) {
			console.log('dark mode capture failed:', String(e).slice(0, 120));
		}
	}
	await ctx.close();
}
await browser.close();

fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
for (const r of report) {
	console.log(`[${r.vp}] ${r.status} ${r.url}  H1=${r.h1count} imgs=${r.imgs} noAlt=${r.imgsNoAlt} smallIcons=${r.smallFontIcons} tables=${r.tables} extNoRel=${r.externalNoRel}`);
}
console.log(`\nWrote ${report.length} rows to ${OUT}/report.json`);
