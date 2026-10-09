import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

function makeLocalStorage() {
	const data = new Map();
	return {
		getItem(key) {
			return data.has(key) ? data.get(key) : null;
		},
		setItem(key, value) {
			data.set(key, String(value));
		},
		removeItem(key) {
			data.delete(key);
		},
	};
}

function loadProgress(localStorage = makeLocalStorage()) {
	const context = {
		URL,
		window: {
			localStorage,
			location: { pathname: '/' },
			fetch() {
				return Promise.reject(new Error('manifest not loaded in unit test'));
			},
			setTimeout() {},
			confirm() {
				return true;
			},
		},
		document: {
			currentScript: { src: 'https://example.org/assets/scripts/selftest_progress.js' },
			readyState: 'loading',
			addEventListener() {},
			getElementById() {
				return null;
			},
			querySelector() {
				return null;
			},
		},
		module: { exports: {} },
	};
	context.window.document = context.document;
	context.window.window = context.window;
	vm.createContext(context);
	const source = fs.readFileSync('site_docs/assets/scripts/selftest_progress.js', 'utf8');
	vm.runInContext(source, context);
	return { api: context.module.exports, localStorage };
}

{
	const { api } = loadProgress();
	assert.equal(api.isCompleted('bbq-fret_overlap_colors-questions.txt'), false);
	const result = api.markCompleted('bbq-fret_overlap_colors-questions.txt');
	assert.equal(result.changed, true);
	assert.equal(api.isCompleted('bbq-fret_overlap_colors-questions.txt'), true);
	const second = api.markCompleted('bbq-fret_overlap_colors-questions.txt');
	assert.equal(second.changed, false);
}

{
	const blocked = {
		getItem() {
			throw new Error('blocked');
		},
		setItem() {
			throw new Error('blocked');
		},
		removeItem() {
			throw new Error('blocked');
		},
	};
	const { api } = loadProgress(blocked);
	assert.equal(api.storageStatus().available, false);
	const blockedState = api.loadState();
	assert.equal(blockedState.version, 2);
	assert.deepEqual(Object.keys(blockedState.completed), []);
	assert.equal(api.markCompleted('bbq-fret_overlap_colors-questions.txt').changed, false);
}

{
	const { api, localStorage } = loadProgress();
	localStorage.setItem('selftest_progress_v2', '{bad json');
	const badState = api.loadState();
	assert.equal(badState.version, 2);
	assert.deepEqual(Object.keys(badState.completed), []);
}

// Earlier CRC records are intentionally ignored. A problem-set completion is
// keyed by its stable BBQ filename, so every generated variant shares credit.
{
	const storage = makeLocalStorage();
	const timestamp = '2026-10-09T12:00:00Z';
	storage.setItem('selftest_progress_v1', JSON.stringify({ version: 1, completed: {
		'aaaa_0001': { firstCorrectAt: timestamp },
	} }));
	const { api } = loadProgress(storage);
	assert.equal(api.isCompleted('aaaa_0001'), false);
	assert.equal(api.isCompleted('bbq-fret_overlap_colors-questions.txt'), false);
	api.markCompleted('bbq-fret_overlap_colors-questions.txt');
	const reloaded = loadProgress(storage).api;
	assert.equal(reloaded.isCompleted('bbq-fret_overlap_colors-questions.txt'), true);
	assert.equal(reloaded.isCompleted('bbq-a_different_problem_set.txt'), false);
	assert.deepEqual(Object.keys(reloaded.loadState().completed), [
		'bbq-fret_overlap_colors-questions.txt',
	]);
	assert.equal(reloaded.loadState().completed['bbq-fret_overlap_colors-questions.txt'].firstCorrectAt !== timestamp, true);
}

// A shared problem-set filename may appear on more than one reachable page.
// It remains one achievement wherever the dashboard or topic summary sees it.
{
	const { api } = loadProgress();
	api.markCompleted('bbq-fret_overlap_colors-questions.txt');
	const summary = api.topicSummary('topic01', { questions: [
		{ questionId: 'bbq-fret_overlap_colors-questions.txt', topicKey: 'topic01' },
		{ questionId: 'bbq-fret_overlap_colors-questions.txt', topicKey: 'topic01' },
		{ questionId: 'bbq-a_different_problem_set.txt', topicKey: 'topic01' },
	] });
	assert.equal(summary.completed, 1);
	assert.equal(summary.total, 2);
	assert.equal(summary.isComplete, false);
}

console.log('selftest_progress_storage_test.mjs passed');
