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

function loadProgress(resultElement) {
	const localStorage = makeLocalStorage();
	const context = {
		URL,
		window: {
			localStorage,
			location: { pathname: '/biology/topic01/' },
			fetch() {
				return Promise.reject(new Error('manifest not loaded in unit test'));
			},
			setTimeout() {},
			confirm() {
				return true;
			},
			checkAnswer_aaaa_0001() {
				return 'checked';
			},
		},
		document: {
			currentScript: { src: 'https://example.org/assets/scripts/selftest_progress.js' },
			readyState: 'loading',
			body: {
				appendChild() {},
			},
			addEventListener() {},
			createElement() {
				return {
					setAttribute() {},
					textContent: '',
					className: '',
					id: '',
					parentNode: null,
				};
			},
			getElementById(id) {
				if (id === 'result_aaaa_0001') {
					return resultElement;
				}
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
	return { api: context.module.exports, window: context.window, document: context.document };
}

{
	const resultElement = { textContent: 'CORRECT' };
	const { api, window } = loadProgress(resultElement);
	const rows = [{
		questionId: 'aaaa_0001',
		crc: 'aaaa_0001',
		topicKey: 'topic01',
	}];
	const manifest = { questions: rows };
	api._test.wrapAnswerChecks(rows, manifest);
	const checked = window.checkAnswer_aaaa_0001();
	assert.equal(checked, 'checked');
	assert.equal(api.isCompleted('aaaa_0001'), true);
	const wrapped = window.checkAnswer_aaaa_0001;
	api._test.wrapAnswerChecks(rows, manifest);
	assert.equal(window.checkAnswer_aaaa_0001, wrapped);
}

{
	const resultElement = { textContent: 'incorrect' };
	const { api, window } = loadProgress(resultElement);
	const rows = [{
		questionId: 'aaaa_0001',
		crc: 'aaaa_0001',
		topicKey: 'topic01',
	}];
	const manifest = { questions: rows };
	api._test.wrapAnswerChecks(rows, manifest);
	window.checkAnswer_aaaa_0001();
	assert.equal(api.isCompleted('aaaa_0001'), false);
}

// Completing an unchanged question uses the current variant in another slot.
{
	const { api, window, document } = loadProgress({ textContent: 'CORRECT' });
	const original = { questionId: 'bbbb_0002', crc: 'bbbb_0002', bankId: 'bank-b',
		pagePath: 'biology/topic01/index.md', topicKey: 'topic01' };
	const unchanged = { questionId: 'aaaa_0001', crc: 'aaaa_0001', bankId: 'bank-a',
		pagePath: original.pagePath, topicKey: original.topicKey };
	const manifest = { questions: [original, unchanged] };
	let displayed = 'bbbb_0002';
	document.querySelectorAll = () => [{ dataset: { bankId: 'bank-b' },
		querySelector: () => ({ id: 'question_html_' + displayed }) }];
	const count = { textContent: '' };
	document.querySelector = (selector) => selector === '[data-selftest-topic-count]' ? count : null;
	api.markCompleted('bbbb_0002');
	api._test.wrapAnswerChecks([unchanged], manifest);
	displayed = 'cccc_0003';
	window.checkAnswer_aaaa_0001();
	assert.equal(count.textContent, '1 / 2 completed');
	assert.equal(api.isCompleted('cccc_0003'), false);
	displayed = 'bbbb_0002';
	window.checkAnswer_aaaa_0001();
	assert.equal(count.textContent, '2 / 2 completed');
	assert.equal(manifest.questions[0].questionId, 'bbbb_0002');
}

console.log('selftest_progress_dom_test.mjs passed');
