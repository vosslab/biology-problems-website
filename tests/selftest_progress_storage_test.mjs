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
	assert.equal(api.isCompleted('aaaa_0001'), false);
	const result = api.markCompleted('aaaa_0001');
	assert.equal(result.changed, true);
	assert.equal(api.isCompleted('aaaa_0001'), true);
	const second = api.markCompleted('aaaa_0001');
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
	assert.equal(blockedState.version, 1);
	assert.deepEqual(Object.keys(blockedState.completed), []);
	assert.equal(api.markCompleted('aaaa_0001').changed, false);
}

{
	const { api, localStorage } = loadProgress();
	localStorage.setItem('selftest_progress_v1', '{bad json');
	const badState = api.loadState();
	assert.equal(badState.version, 1);
	assert.deepEqual(Object.keys(badState.completed), []);
}

// Existing v1 records survive new variants and a reload without bank migration.
{
	const storage = makeLocalStorage();
	const timestamp = '2026-10-09T12:00:00Z';
	storage.setItem('selftest_progress_v1', JSON.stringify({ version: 1, completed: {
		'aaaa_0001': { firstCorrectAt: timestamp },
		'older_0002': { firstCorrectAt: timestamp },
	} }));
	const { api } = loadProgress(storage);
	assert.equal(api.isCompleted('aaaa_0001'), true);
	assert.equal(api.isCompleted('bbbb_0002'), false);
	api.markCompleted('bbbb_0002');
	const reloaded = loadProgress(storage).api;
	assert.equal(reloaded.isCompleted('aaaa_0001'), true);
	assert.equal(reloaded.isCompleted('bbbb_0002'), true);
	assert.equal(reloaded.loadState().completed.older_0002.firstCorrectAt, timestamp);
	assert.equal(reloaded.loadState().completed.aaaa_0001.firstCorrectAt, timestamp);
}

console.log('selftest_progress_storage_test.mjs passed');
