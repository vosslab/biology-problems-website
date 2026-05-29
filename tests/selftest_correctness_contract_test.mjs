import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

function loadProgress() {
	const context = {
		window: {
			localStorage: {
				getItem() { return null; },
				setItem() {},
				removeItem() {},
			},
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
	return context.module.exports;
}

function result(text) {
	return { textContent: text };
}

const api = loadProgress();

assert.equal(api.classifyResultElement(result('CORRECT')), 'full-correct');
assert.equal(api.classifyResultElement(result('incorrect')), 'incorrect');
assert.equal(api.classifyResultElement(result('Please select an answer.')), 'no-answer');
assert.equal(api.classifyResultElement(result('Please enter a value.')), 'no-answer');
assert.equal(api.classifyResultElement(result('Please enter a valid number.')), 'no-answer');
assert.equal(api.classifyResultElement(result('Too high. Try again.')), 'incorrect');
assert.equal(api.classifyResultElement(result('Too low. Try again.')), 'incorrect');
assert.equal(api.classifyResultElement(result('Total Score: 4 out of 4')), 'full-correct');
assert.equal(api.classifyResultElement(result('Total Score: 3 out of 4')), 'partial');
assert.equal(api.classifyResultElement(result('Correct positions: 5 of 5')), 'full-correct');
assert.equal(api.classifyResultElement(result('Correct positions: 2 of 5')), 'partial');
assert.equal(api.classifyResultElement(result('Correct: 2 of 2')), 'full-correct');
assert.equal(api.classifyResultElement(result('Correct: 1 of 2')), 'partial');
assert.equal(
	api.classifyResultElement(result('Too few answers selected. You got 1 out of 2 correct.')),
	'partial',
);
assert.equal(api.classifyResultElement(result('unexpected wording')), 'unknown');

console.log('selftest_correctness_contract_test.mjs passed');
