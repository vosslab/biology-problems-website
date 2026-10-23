// Protect download identity, grading and rendered media with the shipped WASM and drawing libraries.
// DOM contract: topic_page.py download rows; package_download.js delegated buttons and row status.
// Only fixture HTML/BBQ HTTP responses are replaced in the main journey.
import { test, expect } from "@playwright/test";
import type { Download, Page } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { REPO_ROOT } from "./repo_root.mjs";

const molecule = (id: string, smiles: string) => `<canvas id="${id}" width="180" height="140"></canvas><script>let smiles="${smiles}";let mol=RDKitModule.get_mol(smiles);let mdetails={};mol.draw_to_canvas_with_highlights(canvas,JSON.stringify(mdetails));</script>`;
const bank = [
  `MC\t<p>Identify ethanol.</p><table><caption>Molecule evidence</caption><tr><td>${molecule("ethanol", "CCO")}</td><td>Two carbons</td></tr></table>\tEthanol\tCorrect\tMethane\tIncorrect`,
  `MC\t<p>Identify methane.</p>${molecule("methane", "C")}\tEthanol\tIncorrect\tMethane\tCorrect`,
].join("\n");
const readableBank = "/genetics/topic07/bbq-progeny_probability_practice-explain-MC-questions.txt";
const readablePage = readableBank.replace(/\.txt$/, ".html");

async function host(page: Page) {
  await page.route("**/package_fixture/questions.txt", route => route.fulfill({ body: bank }));
  // Human-readable output supports ordinary HTML stems; RDKit stems are filtered by its writer.
  // Context routing also supplies the bank to its independently loaded viewer tab.
  await page.context().route(`**${readableBank}`, route => route.fulfill({ body:
    "MC\t<p>Identify ethanol.</p>Two carbons and one hydroxyl.\tEthanol\tCorrect\tMethane\tIncorrect\n" +
    "MC\t<p>Identify methane.</p>One carbon and four hydrogens.\tEthanol\tIncorrect\tMethane\tCorrect" }));
  await page.route("**/package_fixture/", route => route.fulfill({ contentType: "text/html", body: `
    <div class="button-container">
      <button class="qpm-package-download" data-bbq="questions.txt" data-format="blackboard_export_zip" data-filename="blackboard.zip">Blackboard</button>
      <button class="qpm-package-download" data-bbq="questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas.zip">Canvas</button>
      <button class="qpm-package-download" data-bbq="${readableBank}" data-format="human_readable" data-filename="questions.html">HTML</button>
      <span class="qpm-package-status" role="status"></span><progress class="qpm-package-progress" hidden></progress>
    </div><script src="/assets/scripts/package_download.js"></script>` }));
  await page.goto("/package_fixture/");
  return page.locator(".button-container");
}

// Python's independent ZIP/XML readers inspect actual downloaded bytes, without converter parsing.
async function inspect(download: Download) {
  const path = await download.path();
  if (!path) { throw new Error("Download was not saved"); }
  const summary = JSON.parse(execFileSync("bash", ["-c", 'source source_me.sh && python3 -c "$1" "$2"', "inspect", `
import base64, json, struct, sys, zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
class Images(HTMLParser):
 def __init__(self): super().__init__(); self.sources=[]
 def handle_starttag(self, tag, attrs):
  if tag == 'img': self.sources += [v for k,v in attrs if k == 'src']
with zipfile.ZipFile(sys.argv[1]) as archive:
 entries={name:archive.read(name) for name in archive.namelist()}
 items=[]; images=[]
 for name, data in entries.items():
  if not name.endswith(('.xml','.dat')): continue
  root=ET.fromstring(data)
  for node in root.iter(): node.tag=node.tag.rsplit('}',1)[-1]
  for item in root.iter('item'):
   maximum=float(item.find('.//decvar').get('maxvalue','100'))
   choices=[]
   for label in item.findall('.//response_label'):
    chosen=label.get('ident'); score=0.; matched=False
    def matches(node):
     if node.tag=='varequal': return node.text == chosen
     if node.tag=='other': return not matched
     if node.tag=='not': return not matches(node[0])
     if node.tag=='and': return all(matches(c) for c in node)
     if node.tag in ('conditionvar','or'): return any(matches(c) for c in node)
     raise ValueError('Unexpected scoring predicate '+node.tag)
    for condition in item.findall('.//respcondition'):
     if matches(condition.find('conditionvar')):
      matched=True
      value=condition.find('setvar')
      if value is not None: score=maximum if value.text=='SCORE.max' else float(value.text)
      if condition.get('continue')=='No': break
    choices.append({'text':''.join(label.itertext()),'score':score/maximum})
   html=' '.join(n.text or '' for n in item.find('presentation').iter() if n.tag in ('mattext','mat_formattedtext'))
   parser=Images(); parser.feed(html)
   for source in parser.sources:
    if 'bbcswebdav/xid-' in source:
     xid=source.split('bbcswebdav/xid-')[1].split('/')[0]
     paths=[p for p in entries if p.startswith('csfiles/home_dir/__xid-'+xid+'.') and p.endswith('.png')]
     assert len(paths)==1, ('Unresolved Blackboard media', source)
     png=entries[paths[0]]
     assert png[:8]==b'\\x89PNG\\r\\n\\x1a\\n'
     width,height=struct.unpack('>II',png[16:24]); assert width>0 and height>0
     images.append({'path':paths[0],'width':width,'height':height,'base64':base64.b64encode(png).decode()})
   items.append({'id':item.findtext('.//bbmd_asi_object_id') or item.get('ident'),'choices':choices,'html':html})
 print(json.dumps({'items':items,'images':images}))
`, path], { encoding: "utf8", cwd: REPO_ROOT }));
  return { summary, bytes: Array.from(await readFile(path)) };
}

test("real downloads preserve source identity, grading and scientific media", async ({ page }) => {
  test.setTimeout(90_000);
  const dependencies: string[] = [];
  const errors: string[] = [];
  page.on("request", request => {
    if (/\/(qpm_wasm|package_render)\//.test(request.url())) { dependencies.push(request.url()); }
  });
  page.on("pageerror", error => errors.push(error.message));
  const row = await host(page);
  expect(dependencies).toEqual([]);
  await page.evaluate(() => localStorage.setItem("selftest_progress_v2", '{"version":2,"completed":{"previous":true}}'));
  const downloaded = page.waitForEvent("download");
  await row.getByRole("button", { name: "Blackboard", exact: true }).click();
  const blackboard = await downloaded;
  expect(blackboard.suggestedFilename()).toBe("blackboard.zip");
  await expect(row.getByRole("status")).toHaveText("Download ready.");
  const inspected = await inspect(blackboard);
  const canonical = await page.evaluate(async ({ bytes, source }) => {
    const api = await import("/assets/qpm_wasm/src/index.js");
    const checked = api.checkPackage({ kind: "zip", bytes: new Uint8Array(bytes) });
    const ids = source.split("\n").map(item => {
      const original = api.convert({ inputFormat: "bbq_text_upload", outputFormat: "html_selftest",
        input: { kind: "file", name: "questions.txt", bytes: new TextEncoder().encode(item) } });
      if (original.status !== "success" || original.artifact?.kind !== "file") { throw new Error("Original item conversion failed"); }
      return new TextDecoder().decode(original.artifact.primary.bytes).match(/id="question_html_([^"]+)"/)![1];
    });
    return { checked, ids };
  }, { bytes: inspected.bytes, source: bank });
  expect(canonical.checked.status).toBe("success");
  expect(canonical.checked.report.errors).toEqual([]);
  expect(canonical.ids).toHaveLength(2);
  expect(inspected.summary.items.map((item: { id: string }) => item.id).sort())
    .toEqual(canonical.ids.map(id => `_${id}_1`).sort());
  expect(inspected.summary.images).toHaveLength(2);
  const ink = await page.evaluate(async images => Promise.all(images.map(async (image: { base64: string }) => {
    const bytes = Uint8Array.from(atob(image.base64), character => character.charCodeAt(0));
    const bitmap = await createImageBitmap(new Blob([bytes], { type: "image/png" }));
    const canvas = document.createElement("canvas");
    canvas.width = bitmap.width; canvas.height = bitmap.height;
    const context = canvas.getContext("2d")!;
    context.drawImage(bitmap, 0, 0);
    const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    let dark = 0;
    for (let index = 0; index < pixels.length; index += 4) {
      if (pixels[index + 3] > 0 && Math.min(pixels[index], pixels[index + 1], pixels[index + 2]) < 200) { dark += 1; }
    }
    bitmap.close();
    return dark;
  })), inspected.summary.images);
  expect(ink.every(count => count > 0)).toBe(true);
  expect(inspected.summary.items.some((item: { html: string }) => /<table|<canvas/.test(item.html))).toBe(false);
  expect(inspected.summary.items.map((item: { choices: unknown[] }) => item.choices)).toEqual([
    [{ text: "Ethanol", score: 1 }, { text: "Methane", score: 0 }],
    [{ text: "Ethanol", score: 0 }, { text: "Methane", score: 1 }],
  ]);
  const canvasDownload = page.waitForEvent("download");
  await row.getByRole("button", { name: "Canvas", exact: true }).click();
  const canvas = await canvasDownload;
  expect(canvas.suggestedFilename()).toBe("canvas.zip");
  const direct = await inspect(canvas);
  const canvasChecked = await page.evaluate(async bytes => {
    const api = await import("/assets/qpm_wasm/src/index.js");
    return api.checkPackage({ kind: "zip", bytes: new Uint8Array(bytes) });
  }, direct.bytes);
  expect(canvasChecked.status).toBe("success");
  expect(canvasChecked.report.errors).toEqual([]);
  expect(direct.summary.items).toHaveLength(2);
  expect(direct.summary.items.map((item: { choices: unknown[] }) => item.choices))
    .toEqual(inspected.summary.items.map((item: { choices: unknown[] }) => item.choices));
  const popupEvent = page.waitForEvent("popup");
  await row.getByRole("button", { name: "HTML", exact: true }).click();
  const popup = await popupEvent;
  await expect(popup.locator("body")).toContainText("Identify ethanol.");
  await expect(popup.locator("body")).toContainText("Identify methane.");
  const namedUrl = new URL(readablePage, page.url()).href;
  await expect(popup).toHaveURL(namedUrl);
  await expect(popup).toHaveTitle(readableBank.split("/").pop()!);
  expect(await popup.evaluate(() => window.opener === null)).toBe(true);
  await popup.reload();
  await expect(popup.locator("body")).toContainText("Identify ethanol.");
  await expect(popup).toHaveURL(namedUrl);
  await popup.close();
  const reopened = await page.context().newPage();
  await reopened.goto(namedUrl);
  await expect(reopened.locator("body")).toContainText("Identify methane.");
  await expect(reopened).toHaveTitle(readableBank.split("/").pop()!);
  await reopened.close();
  expect(await page.evaluate(() => localStorage.getItem("selftest_progress_v2")))
    .toBe('{"version":2,"completed":{"previous":true}}');
  expect(errors).toEqual([]);
});

test("named human-readable page retries a failed bank load", async ({ page }) => {
  let fail = true;
  await page.route(`**${readableBank}`, async route => {
    if (fail) { await route.fulfill({ status: 503, body: "Unavailable" }); }
    else { await route.continue(); }
  });
  await page.goto(readablePage);
  await expect(page.getByRole("status")).toContainText("Could not load question data.");
  fail = false;
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  // Retry uses the actual shipped bank and canonical WASM output.
  await expect(page.locator("pre")).not.toBeEmpty();
  await expect(page.getByRole("button", { name: "Retry", exact: true })).toHaveCount(0);
  expect(new URL(page.url()).pathname).toBe(readablePage);
});

test("failed molecule dependency restores controls and a retry builds the real package", async ({ page }) => {
  test.setTimeout(90_000);
  let fail = true;
  await page.route("**/package_render/rdkit.js", async route => {
    if (fail) { await route.abort(); } else { await route.continue(); }
  });
  const row = await host(page);
  const button = row.getByRole("button", { name: "Blackboard", exact: true });
  await button.click();
  await expect(row.getByRole("status")).toContainText("Could not load molecule drawing.");
  for (const control of await row.getByRole("button").all()) { await expect(control).toBeEnabled(); }
  await expect(row.locator("progress")).toBeHidden();
  fail = false;
  const downloaded = page.waitForEvent("download");
  await button.click();
  expect((await inspect(await downloaded)).summary.items).toHaveLength(2);
  await expect(row.getByRole("status")).toHaveText("Download ready.");
  await expect(button).toBeEnabled();
});
