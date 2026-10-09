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
	const listeners = new Map();
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
			addEventListener(name, listener) { listeners.set(name, listener); },
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
	return { api: context.module.exports, window: context.window, document: context.document, listeners };
}

{
	const resultElement = { textContent: 'CORRECT' };
	const { api, listeners } = loadProgress(resultElement);
	await listeners.get('selftest:graded')({
		detail: { crc: 'aaaa_0001', verdict: 'full-correct' },
		target: { isConnected: true, dataset: { bbq: 'bbq-fret_overlap_colors-questions.txt' } },
	});
	assert.equal(api.isCompleted('bbq-fret_overlap_colors-questions.txt'), true);
	assert.equal(api.isCompleted('aaaa_0001'), false);
}

{
	const resultElement = { textContent: 'incorrect' };
	const { api, listeners } = loadProgress(resultElement);
	await listeners.get('selftest:graded')({
		detail: { crc: 'aaaa_0001', verdict: 'incorrect' },
		target: { isConnected: true, dataset: { bbq: 'bbq-fret_overlap_colors-questions.txt' } },
	});
	assert.equal(api.isCompleted('bbq-fret_overlap_colors-questions.txt'), false);
}

// A rerolled CRC earns the same one completion credit for its BBQ problem set;
// a different set remains incomplete.
{
	const { api, window, document, listeners } = loadProgress({ textContent: 'CORRECT' });
	const original = { questionId: 'bbq-fret_overlap_colors-questions.txt', crc: 'bbbb_0002',
		pagePath: 'biology/topic01/index.md', topicKey: 'topic01' };
	const unchanged = { questionId: 'bbq-other_problem_set-questions.txt', crc: 'aaaa_0001',
		pagePath: original.pagePath, topicKey: original.topicKey };
	const manifest = { questions: [original, unchanged] };
	window.fetch = async () => ({ ok: true, json: async () => manifest });
	api.markCompleted(original.questionId);
	await listeners.get('selftest:graded')({
		detail: { crc: 'cccc_0003', verdict: 'full-correct' },
		target: { isConnected: true, dataset: { bbq: original.questionId } },
	});
	assert.equal(api.isCompleted(original.questionId), true);
	assert.equal(api.isCompleted(unchanged.questionId), false);
	await listeners.get('selftest:graded')({
		detail: { crc: 'aaaa_0001', verdict: 'full-correct' },
		target: { isConnected: true, dataset: { bbq: unchanged.questionId } },
	});
	assert.equal(api.isCompleted(unchanged.questionId), true);
	assert.equal(manifest.questions[0].questionId, original.questionId);
}

console.log('selftest_progress_dom_test.mjs passed');
