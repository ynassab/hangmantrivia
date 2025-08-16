/**
 * @file tests/frontend/hangmantrivia.test.js
 * Jest tests for src/frontend/hangmantrivia/scripts/hangmantrivia.js
 */

let moduleExports;
let DOMCache;
let domElements;

function loadModuleWithDOM() {
    jest.resetModules();

    // Load the module
    moduleExports = require('../../src/frontend/hangmantrivia/scripts/hangmantrivia.js');

    // Get DOMCache from exports
    DOMCache = moduleExports.DOMCache;

    // Create DOM elements cache
    domElements = new DOMCache();

    // Set the DOM in the module
    moduleExports.setDOM(domElements);

    // Initialize game state for testing
    moduleExports.setGameState({
        chosenDifficulty: 'normal',
        seenAnswersStorageName: 'seenAnswersNormal',
        highScoreStorageName: 'highScoreNormal',
        seenAnswers: [],
        wrongGuesses: [],
        strikeCount: 0,
        score: 0,
        highScore: 0,
        maxStrikes: 7,
        lockGame: false,
        difficultySelected: true,
    });
}

beforeEach(() => {
    document.body.innerHTML = `
        <div id="clue-display"></div>
        <div id="answer-display" data-answer="" data-answer-so-far=""></div>
        <div id="status-display"></div>
        <div id="scorestrike-display"></div>
        <div id="score-display"></div>
        <div id="highscore-display"></div>
        <div id="strike-display"></div>
        <div id="landscape-warning-container"></div>
        <div id="landscape-warning"></div>
        <main></main>
        <div id="keyboard-container"></div>
        <div id="keyboard"></div>
        <div id="game-title"></div>
        <div id="intro-page"></div>
        <div id="game-page"></div>
        <div id="copyright-notice"></div>
        <button class="difficulty-button" data-difficulty="normal"></button>
    `;

    // Mock device detection before requiring the main module
    global.isMobileOrTablet = jest.fn(() => false);
    global.window.isMobileOrTablet = global.isMobileOrTablet;

    jest.resetModules(); // ensure a clean require cache

    // Now load hangmantrivia.js which will see our mock already in place
    loadModuleWithDOM();

    // Mock screen size for orientation tests
    Object.defineProperty(global, 'screen', {
        value: { availHeight: 800, availWidth: 600 },
        writable: true,
        configurable: true,
    });
});

describe('Hangman Trivia Frontend', () => {
    describe('Event listeners', () => {
        test('DOMContentLoaded block executes', () => {
            // Mock fetch to warm up Lambda
            global.fetch = jest.fn().mockResolvedValue({
                status: 200,
                json: async () => ({ wakeUp: 'Hello from Hangman Trivia!' })
            });

            const addEventListenerSpy = jest.spyOn(document, "addEventListener");

            document.dispatchEvent(new Event("DOMContentLoaded"));

            expect(addEventListenerSpy).toHaveBeenCalledWith("newclue", expect.any(Function));
            expect(addEventListenerSpy).toHaveBeenCalledWith("keydown", expect.any(Function));
        })
    });

    describe('Event listeners', () => {
        test('DOMContentLoaded block executes', () => {
            // Mock fetch to warm up Lambda
            global.fetch = jest.fn().mockResolvedValue({
                status: 200,
                json: async () => ({ wakeUp: 'Hello from Hangman Trivia!' })
            });

            const addEventListenerSpy = jest.spyOn(document, "addEventListener");

            document.dispatchEvent(new Event("DOMContentLoaded"));

            expect(addEventListenerSpy).toHaveBeenCalledWith("newclue", expect.any(Function));
            expect(addEventListenerSpy).toHaveBeenCalledWith("keydown", expect.any(Function));
        })
    });

    describe('isUpperCaseAlpha', () => {
        test('returns true for uppercase letters', () => {
            expect(moduleExports.isUpperCaseAlpha('A')).toBe(true);
            expect(moduleExports.isUpperCaseAlpha('Z')).toBe(true);
        });

        test('returns false for lowercase letters, non-letters, empty string', () => {
            expect(moduleExports.isUpperCaseAlpha('a')).toBe(false);
            expect(moduleExports.isUpperCaseAlpha('1')).toBe(false);
            expect(moduleExports.isUpperCaseAlpha('')).toBe(false);
            expect(moduleExports.isUpperCaseAlpha('#')).toBe(false);
        });

        test('safely handles null/undefined input', () => {
            expect(moduleExports.isUpperCaseAlpha(null)).toBe(false);
            expect(moduleExports.isUpperCaseAlpha(undefined)).toBe(false);
        });
    });

    describe('setCharAt', () => {
        test('replaces character at index', () => {
            expect(moduleExports.setCharAt('test', 1, 'A')).toBe('tAst');
        });

        test('returns original string if index out of bounds', () => {
            expect(moduleExports.setCharAt('test', 10, 'A')).toBe('test');
        });
    });

    describe('constructWithSpaces', () => {
        test('constructs spaced string from array', () => {
            const arr = ['A', 'B', 'C'];
            const result = moduleExports.constructWithSpaces(arr, 2, c => c.toLowerCase());
            expect(result).toBe('a&nbsp;&nbsp;b&nbsp;&nbsp;c');
        });

        test('constructs spaced string from string', () => {
            const str = 'AB';
            const result = moduleExports.constructWithSpaces(str, 1, c => c);
            expect(result).toBe('A&nbsp;B');
        });

        test('handles single-char input', () => {
            const result = moduleExports.constructWithSpaces('A', 3, c => c);
            expect(result).toBe('A');
        });
    });

    describe('handleOrientationChange', () => {
        test('sets portrait mode display values', () => {
            // Update screen mock for portrait mode
            Object.defineProperty(global, 'screen', {
                value: { availHeight: 800, availWidth: 600 },
                writable: true,
                configurable: true,
            });

            moduleExports.handleOrientationChange();
            expect(domElements.landscapeWarningContainer.style.display).toBe('none');
            expect(domElements.mainElem.style.display).toBe('block');
        });

        test('sets landscape mode display values', () => {
            // Update screen mock for landscape mode
            Object.defineProperty(global, 'screen', {
                value: { availHeight: 500, availWidth: 800 },
                writable: true,
                configurable: true,
            });

            moduleExports.handleOrientationChange();
            expect(domElements.landscapeWarningContainer.style.display).toBe('flex');
            expect(domElements.mainElem.style.display).toBe('none');
        });

        test('hides keyboard if difficulty not selected', () => {
            moduleExports.setGameState({ difficultySelected: false });
            Object.defineProperty(global, 'screen', {
                value: { availHeight: 900, availWidth: 800 },
                writable: true,
            });
            moduleExports.handleOrientationChange();
            expect(domElements.keyboardContainer.style.display).not.toBe('flex');
        });
    });

    describe('dispatchKeydownEvent', () => {
        test('dispatches keydown event with given key', () => {
            const listener = jest.fn();
            document.addEventListener('keydown', listener);
            moduleExports.dispatchKeydownEvent('A');
            expect(listener).toHaveBeenCalled();
            expect(listener.mock.calls[0][0].key).toBe('A');
        });
    });

    describe('flash functions', () => {
        beforeEach(() => {
            jest.useFakeTimers('legacy');
        });

        afterEach(() => {
            jest.useRealTimers();
        });

        test('flashScore toggles class', () => {
            const addSpy = jest.spyOn(domElements.scoreDisplay.classList, 'add');
            const removeSpy = jest.spyOn(domElements.scoreDisplay.classList, 'remove');
            moduleExports.flashScore();
            expect(addSpy).toHaveBeenCalledWith('score-flash');
            jest.runAllTimers();
            expect(removeSpy).toHaveBeenCalledWith('score-flash');
        });

        test('flashHighScore toggles class', () => {
            const addSpy = jest.spyOn(domElements.highScoreDisplay.classList, 'add');
            const removeSpy = jest.spyOn(domElements.highScoreDisplay.classList, 'remove');
            moduleExports.flashHighScore();
            expect(addSpy).toHaveBeenCalledWith('highscore-flash');
            jest.runAllTimers();
            expect(removeSpy).toHaveBeenCalledWith('highscore-flash');
        });

        test('flashStrikes toggles class', () => {
            const addSpy = jest.spyOn(domElements.strikeDisplay.classList, 'add');
            const removeSpy = jest.spyOn(domElements.strikeDisplay.classList, 'remove');
            moduleExports.flashStrikes();
            expect(addSpy).toHaveBeenCalledWith('strike-flash');
            jest.runAllTimers();
            expect(removeSpy).toHaveBeenCalledWith('strike-flash');
        });

        test('flashBackground toggles class', () => {
            const addSpy = jest.spyOn(document.body.classList, 'add');
            const removeSpy = jest.spyOn(document.body.classList, 'remove');
            moduleExports.flashBackground();
            expect(addSpy).toHaveBeenCalledWith('background-flash');
            jest.runAllTimers();
            expect(removeSpy).toHaveBeenCalledWith('background-flash');
        });
    });

    describe('updateScore', () => {
        beforeEach(() => {
            jest.useFakeTimers('legacy');

            // Reset game state for each test
            moduleExports.setGameState({
                score: 0,
                highScore: 0,
                highScoreStorageName: 'highScoreNormal',
            });
        });

        afterEach(() => {
            jest.useRealTimers();
        });

        test('increments score and updates DOM', () => {
            const initialState = moduleExports.getGameState();
            expect(initialState.score).toBe(0);

            moduleExports.updateScore(5);

            const newState = moduleExports.getGameState();
            expect(newState.score).toBe(5);
            expect(domElements.scoreDisplay.innerText).toBe('Score: 5');
        });

        test('updates high score when beaten', () => {
            const initialState = moduleExports.getGameState();
            expect(initialState.highScore).toBe(0);

            moduleExports.updateScore(10);

            const newState = moduleExports.getGameState();
            expect(newState.highScore).toBe(10);
            expect(domElements.highScoreDisplay.innerText).toBe('High Score: 10');
        });

        test('does not update high score if not beaten', () => {
            moduleExports.setGameState({
                score: 5,
                highScore: 10,
                highScoreStorageName: 'highScoreNormal',
            });
            moduleExports.updateScore(1);
            expect(moduleExports.getGameState().highScore).toBe(10);
        });
    });

    describe('handleNewClue', () => {
        beforeEach(() => {
            // Mock fetch to return clue and answer
            global.fetch = jest.fn().mockResolvedValue({
                status: 200,
                json: async () => ({ clue: 'Test clue', answer: 'ABC' })
            });
        });

        test('stores seen answers and updates clue, normal difficulty', async () => {
            await moduleExports.setGameState({ chosenDifficulty: 'normal' });
            await moduleExports.handleNewClue();
            expect(domElements.clueDisplay.innerHTML).toBe('Test clue');
            expect(localStorage.getItem('seenAnswersNormal')).toContain('ABC');
        });

        test('stores seen answers and updates clue, hard difficulty', async () => {
            await moduleExports.setGameState({ chosenDifficulty: 'hard' });
            await moduleExports.handleNewClue();
            expect(domElements.clueDisplay.innerHTML).toBe('Test clue');
            expect(localStorage.getItem('seenAnswersHard')).toContain('ABC');
        });

        test('stores seen answers and updates clue, drunk difficulty', async () => {
            await moduleExports.setGameState({ chosenDifficulty: 'drunk' });
            await moduleExports.handleNewClue();
            expect(domElements.clueDisplay.innerHTML).toBe('Test clue');
            expect(localStorage.getItem('seenAnswersDrunk')).toContain('ABC');
        });

        test('handles 204 No Content', async () => {
            global.fetch = jest.fn().mockResolvedValue({ status: 204 });
            await moduleExports.setGameState({ chosenDifficulty: 'normal' });
            await moduleExports.handleNewClue();
            expect(domElements.statusDisplay.innerText).toContain('No more clues');
        });
    });

    describe('handleKeyPress', () => {
        beforeEach(() => {
            domElements.answerDisplay.setAttribute('data-answer', 'ABC');
            domElements.answerDisplay.setAttribute('data-answer-so-far', '__C');

            // Reset game state for each test
            moduleExports.setGameState({
                wrongGuesses: [],
                maxStrikes: 3,
                strikeCount: 0,
                score: 0,
                highScore: 0,
                lockGame: false,
            });
        });

        test('processes correct guess', () => {
            moduleExports.handleKeyPress({ key: 'A' });

            // Check that the answer display was updated with the correct letter
            expect(domElements.answerDisplay.innerHTML).toContain('A');
            expect(domElements.answerDisplay.getAttribute('data-answer-so-far')).toContain('A');

            // Score should have increased
            const newState = moduleExports.getGameState();
            expect(newState.score).toBe(1);
        });

        test('processes wrong guess', () => {
            moduleExports.handleKeyPress({ key: 'D' });

            // Check that wrong guess was added to status display
            expect(domElements.statusDisplay.innerHTML).toContain('D');

            // Check that strike count increased
            const newState = moduleExports.getGameState();
            expect(newState.strikeCount).toBe(1);
            expect(newState.wrongGuesses).toContain('D');
            expect(domElements.strikeDisplay.innerText).toBe('Strikes: 1 of 3');
        });

        test('handles game over when max strikes reached', () => {
            jest.useFakeTimers('legacy');

            // Set up state close to game over
            moduleExports.setGameState({
                wrongGuesses: ['D', 'E'],
                strikeCount: 2,
                maxStrikes: 3,
                lockGame: false,
            });

            // Make the final wrong guess
            moduleExports.handleKeyPress({ key: 'F' });

            const newState = moduleExports.getGameState();
            expect(newState.strikeCount).toBe(3);
            expect(newState.lockGame).toBe(true);
            expect(domElements.statusDisplay.innerHTML).toContain('Game over!');

            jest.useRealTimers();
        });

        test('handles win condition', () => {
            jest.useFakeTimers('legacy');

            // Set up answer display to be almost complete
            domElements.answerDisplay.setAttribute('data-answer', 'AB');
            domElements.answerDisplay.setAttribute('data-answer-so-far', 'A_');

            moduleExports.setGameState({
                wrongGuesses: [],
                strikeCount: 0,
                score: 10,
                lockGame: false,
            });

            // Make the final correct guess
            moduleExports.handleKeyPress({ key: 'B' });

            const newState = moduleExports.getGameState();
            expect(newState.lockGame).toBe(true);
            expect(domElements.statusDisplay.innerHTML).toContain('Well done!');
            // Score should have increased (1 for correct guess + bonus for completing word)
            expect(newState.score).toBeGreaterThan(10);

            jest.useRealTimers();
        });

        test('ignores repeated guesses', () => {
            // Set up a letter that's already been guessed correctly
            domElements.answerDisplay.setAttribute('data-answer', 'AAB');
            domElements.answerDisplay.setAttribute('data-answer-so-far', 'AA_');

            const initialState = moduleExports.getGameState();

            // Try to guess 'A' again
            moduleExports.handleKeyPress({ key: 'A' });

            const newState = moduleExports.getGameState();
            // Score should not have changed
            expect(newState.score).toBe(initialState.score);
        });

        test('ignores guesses when game is locked', () => {
            moduleExports.setGameState({
                lockGame: true,
            });

            const initialState = moduleExports.getGameState();

            moduleExports.handleKeyPress({ key: 'A' });

            const newState = moduleExports.getGameState();
            // Nothing should have changed
            expect(newState.score).toBe(initialState.score);
            expect(newState.strikeCount).toBe(initialState.strikeCount);
        });

        test('returns early if no answer', () => {
            domElements.answerDisplay.setAttribute('data-answer', '');
            domElements.answerDisplay.setAttribute('data-answer-so-far', '');
            const stateBefore = moduleExports.getGameState();
            moduleExports.handleKeyPress({ key: 'A' });
            expect(moduleExports.getGameState()).toEqual(stateBefore);
        });

        test('ignores letter already in wrong guesses', () => {
            domElements.answerDisplay.setAttribute('data-answer', 'ABC');
            domElements.answerDisplay.setAttribute('data-answer-so-far', '__C');
            moduleExports.setGameState({ wrongGuesses: ['D'] });
            moduleExports.handleKeyPress({ key: 'D' });
            expect(moduleExports.getGameState().wrongGuesses).toEqual(['D']);
        });

        test('awards different bonus points for word length', () => {
            const lengths = [4, 8, 12, 18, 25];
            lengths.forEach(len => {
                const word = 'A'.repeat(len-1) + 'B';
                domElements.answerDisplay.setAttribute('data-answer', word);
                domElements.answerDisplay.setAttribute('data-answer-so-far', 'A'.repeat(len-1) + '_');
                moduleExports.setGameState({ score: 0, lockGame: false });
                moduleExports.handleKeyPress({ key: 'B' });
                expect(moduleExports.getGameState().score).toBeGreaterThan(0);
            });
        });
    });

    describe('Game State Management', () => {
        test('getGameState returns current state', () => {
            const state = moduleExports.getGameState();
            expect(state).toHaveProperty('score');
            expect(state).toHaveProperty('highScore');
            expect(state).toHaveProperty('strikeCount');
            expect(state).toHaveProperty('wrongGuesses');
            expect(state).toHaveProperty('lockGame');
        });

        test('setGameState updates state correctly', () => {
            const newState = {
                score: 100,
                highScore: 150,
                strikeCount: 2,
                wrongGuesses: ['X', 'Y'],
                lockGame: true,
            };

            moduleExports.setGameState(newState);
            const retrievedState = moduleExports.getGameState();

            expect(retrievedState.score).toBe(100);
            expect(retrievedState.highScore).toBe(150);
            expect(retrievedState.strikeCount).toBe(2);
            expect(retrievedState.wrongGuesses).toEqual(['X', 'Y']);
            expect(retrievedState.lockGame).toBe(true);
        });

        test('setGameState handles partial updates', () => {
            // Set initial state
            moduleExports.setGameState({
                score: 50,
                highScore: 75,
            });

            // Update only score
            moduleExports.setGameState({
                score: 60,
            });

            const state = moduleExports.getGameState();
            expect(state.score).toBe(60);
            expect(state.highScore).toBe(75); // Should remain unchanged
        });
    });

    describe('DOM Management', () => {
        test('getDOM returns current DOM cache', () => {
            const dom = moduleExports.getDOM();
            expect(dom).toBe(domElements);
            expect(dom).toHaveProperty('scoreDisplay');
            expect(dom).toHaveProperty('answerDisplay');
        });

        test('setDOM updates DOM reference', () => {
            const mockDOM = { test: 'mock' };
            moduleExports.setDOM(mockDOM);
            const retrievedDOM = moduleExports.getDOM();
            expect(retrievedDOM).toBe(mockDOM);

            // Reset to original DOM for other tests
            moduleExports.setDOM(domElements);
        });
    });
});
