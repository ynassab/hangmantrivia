/**
 * Hangman Trivia Frontend
 *
 * Provides the frontend interface for the hangman trivia web app. Handles user
 * letter guessing (via physical or virtual keyboard), communicates with the backend
 * to fetch trivia questions, and displays game state with visual feedback animations.
 * Features mobile-responsive design with portrait mode enforcement and persistent
 * high score tracking across varying difficulty levels.
 *
 * @author Yahia Nassab
 */

"use strict"

/**
 * DOM Cache Class
 *
 * Manages references to frequently accessed DOM elements to improve performance
 * by avoiding repeated querySelector calls during game execution.
 */
class DOMCache {
    constructor() {
        this.cacheElements();
    }

    cacheElements() {
        this.clueDisplay = document.querySelector('#clue-display');
        this.answerDisplay = document.querySelector('#answer-display');
        this.statusDisplay = document.querySelector('#status-display');
        this.scorestrikeDisplay = document.querySelector('#scorestrike-display');
        this.scoreDisplay = document.querySelector('#score-display');
        this.highScoreDisplay = document.querySelector('#highscore-display');
        this.strikeDisplay = document.querySelector('#strike-display');
        this.landscapeWarningContainer = document.querySelector('#landscape-warning-container');
        this.landscapeWarning = document.querySelector('#landscape-warning');
        this.mainElem = document.querySelector('main');
        this.keyboardContainer = document.querySelector('#keyboard-container');
        this.keyboardElem = document.querySelector('#keyboard');
        this.gameTitle = document.querySelector('#game-title');
        this.introPage = document.querySelector('#intro-page');
        this.gamePage = document.querySelector('#game-page');
        this.copyrightNotice = document.querySelector('#copyright-notice');
        this.difficultyButtons = document.querySelectorAll('.difficulty-button');
    }
}

let DOM;

let chosenDifficulty;
let seenAnswersStorageName;
let highScoreStorageName;
let seenAnswers;
let wrongGuesses;
let strikeCount = 0;
let score = 0;
let highScore;
let maxStrikes = 7;
let lockGame = false;
let difficultySelected = false;

const flashRemovalTimeMilliseconds = 500;
const keyboardContainerStyleDisplay = 'flex';
const keyboardElemStyleDisplay = 'inline';

const getDataAPIEndpoint = 'https://wbr1jh5ceh.execute-api.us-east-1.amazonaws.com/default/';

/**
 * Main initialization function - sets up the game when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', async () => {
    DOM = new DOMCache();

    difficultySelected = false;

    DOM.difficultyButtons.forEach(button => button.addEventListener('click', async (event) => {
        difficultySelected = true;
        chosenDifficulty = event.target.getAttribute('data-difficulty');

        DOM.gameTitle.style.display = 'none';
        DOM.introPage.style.display = 'none';
        DOM.gamePage.style.display = 'block';
        DOM.copyrightNotice.style.display = 'none';

        document.querySelectorAll('.keyboard-key').forEach(function (keyElement) {
            keyElement.addEventListener('click', function () {
                dispatchKeydownEvent(keyElement.textContent);
            });
        });

        document.dispatchEvent(new Event('orientationchange'));
        document.dispatchEvent(new Event('newclue'));
    }));

    DOM.scoreDisplay.innerText = 'Score: 0';
    DOM.strikeDisplay.innerText = `Strikes 0 of ${maxStrikes}`;

    if (window.isMobileOrTablet()) {
        handleOrientationChange();
        window.addEventListener('orientationchange', function () {
            // Wait for resize event dispatch after orientation change to detect correct screen height
            var orientationChange = function () {
                handleOrientationChange();
                window.removeEventListener('resize', orientationChange);
            };
            window.addEventListener('resize', orientationChange);
        });

    }

    document.addEventListener('newclue', handleNewClue);
    document.addEventListener('keydown', event => handleKeyPress(event));

    // Send a wake-up request to the AWS Lambda function to avoid cold start
    await fetch(getDataAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            wakeUp: 'Hello from Hangman Trivia!',
        })
    });

});

/**
 * Handles device orientation changes for mobile devices
 *
 * Enforces portrait mode for optimal gameplay experience. The game uses a custom
 * virtual keyboard embedded in the web app instead of the device's built-in keyboard
 * for two reasons:
 * 1) The built-in keyboard takes up too much screen space
 * 2) Maintaining focus on input elements to trigger the built-in keyboard was unreliable
 *
 * However, in landscape mode, the virtual keyboard would cover the clue and answer
 * components, making the game unplayable. Therefore, portrait mode is required and
 * a warning is displayed when the device is in landscape orientation.
 */
function handleOrientationChange() {
    if (screen.availHeight > screen.availWidth) {
        // Portrait mode
        DOM.landscapeWarningContainer.style.display = 'none';
        DOM.landscapeWarning.style.display = 'none';
        DOM.mainElem.style.display = 'block';
        if (difficultySelected) {
            DOM.keyboardContainer.style.display = keyboardContainerStyleDisplay;
            DOM.keyboardElem.style.display = keyboardElemStyleDisplay;
        }
    } else {
        // Landscape mode
        DOM.landscapeWarningContainer.style.display = 'flex';
        DOM.landscapeWarning.style.display = 'inline';
        DOM.mainElem.style.display = 'none';
        DOM.keyboardContainer.style.display = 'none';
        DOM.keyboardElem.style.display = 'none';
    }
}

/**
 * Dispatches a keyboard event for virtual keyboard clicks
 *
 * Allows the virtual keyboard buttons to trigger the same handlers as physical
 * keyboard input.
 *
 * @param {string} keyValue - The character value of the key to simulate
 */
function dispatchKeydownEvent(keyValue) {
    const event = new KeyboardEvent('keydown', {
        key: keyValue,
        bubbles: true,
        cancelable: true
    });
    document.dispatchEvent(event);
}

/**
 * Handles the start of a new trivia clue/round
 *
 * Fetches a new trivia question from the backend API, updates the UI with the clue,
 * and prepares the answer display with blanks. Manages localStorage for tracking
 * seen answers and high scores.
 */
async function handleNewClue() {
    lockGame = false;

    switch (chosenDifficulty) {
        case 'normal':
            seenAnswersStorageName = 'seenAnswersNormal';
            highScoreStorageName = 'highScoreNormal';
            break;
        case 'hard':
            seenAnswersStorageName = 'seenAnswersHard';
            highScoreStorageName = 'highScoreHard';
            break;
        case 'drunk':
            seenAnswersStorageName = 'seenAnswersDrunk';
            highScoreStorageName = 'highScoreDrunk';
            break;
    }

    seenAnswers = JSON.parse(localStorage.getItem(seenAnswersStorageName)) || [];
    highScore = JSON.parse(localStorage.getItem(highScoreStorageName)) || 0;

    DOM.highScoreDisplay.innerText = `High Score: ${highScore}`;

    // AWS Lambda API Gateway endpoint
    const response = await fetch(getDataAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            difficulty: chosenDifficulty,
            seen: seenAnswers
        })
    });

    if (response.status === 204) {  // No content
        DOM.statusDisplay.innerText = 'No more clues available for this difficulty level!';
        return;
    } else {
        DOM.statusDisplay.innerText = '';
    }

    const { clue, answer } = await response.json();

    seenAnswers.push(answer);
    localStorage.setItem(seenAnswersStorageName, JSON.stringify(seenAnswers));

    // Show keyboard
    if (window.isMobileOrTablet()) {
        DOM.keyboardContainer.style.display = keyboardContainerStyleDisplay;
        DOM.keyboardElem.style.display = keyboardElemStyleDisplay;
    }

    // Show clue
    DOM.clueDisplay.innerHTML = clue;

    // Show answer (obfuscated)
    let answerSoFar = '';
    let constructedAnswerDisplay = constructWithSpaces(answer, 2, (char) => {
        let newChar = isUpperCaseAlpha(char) ? '_' : char;
        answerSoFar += newChar;
        return newChar;
    })

    DOM.answerDisplay.innerHTML = constructedAnswerDisplay;
    DOM.answerDisplay.setAttribute('data-answer', answer);
    DOM.answerDisplay.setAttribute('data-answer-so-far', answerSoFar);
    DOM.scorestrikeDisplay.style.opacity = 1;  // Only show score and strikes when clue and answer are ready
    wrongGuesses = [];
}

/**
 * Handles keyboard input for letter guessing
 *
 * Processes letter guesses, updates the display, tracks correct/incorrect guesses,
 * manages strikes, and handles win/lose conditions.
 *
 * @param {KeyboardEvent} event - The keyboard event containing the pressed key
 */
function handleKeyPress(event) {
    const letter = event.key.toUpperCase();
    const answer = DOM.answerDisplay.getAttribute('data-answer');
    let answerSoFar = DOM.answerDisplay.getAttribute('data-answer-so-far');

    if (lockGame) return;
    if (!isUpperCaseAlpha(letter)) return;
    if (!answer || !answerSoFar) return;
    if (answerSoFar.includes(letter)) return;
    if (wrongGuesses.includes(letter)) return;

    let correctGuess = false;
    let constructedAnswerDisplay = constructWithSpaces(answer, 2, (char, index) => {
        if (char === letter) {
            correctGuess = true;
            answerSoFar = setCharAt(answerSoFar, index, letter);
            return letter;
        } else {
            return answerSoFar[index];
        }
    })
    DOM.answerDisplay.innerHTML = constructedAnswerDisplay;
    DOM.answerDisplay.setAttribute('data-answer-so-far', answerSoFar);

    if (correctGuess) {
        updateScore(1);
    } else {
        // flashBackground();

        // Update strikes
        flashStrikes();
        strikeCount++;
        DOM.strikeDisplay.innerText = `Strikes: ${strikeCount} of ${maxStrikes}`;

        if (strikeCount === maxStrikes) {
            lockGame = true;

            let revealedAnswer = constructWithSpaces(answer, 2, char => char);
            DOM.answerDisplay.innerHTML = revealedAnswer;

            let newGameTimer = 3;
            DOM.statusDisplay.innerHTML = `Game over! Starting new game in ${newGameTimer} seconds`;
            let newGameIntervalID = setInterval(() => {
                newGameTimer--;
                DOM.statusDisplay.innerHTML = `Game over! Starting new game in ${newGameTimer} seconds`;
                if (newGameTimer === 0) {
                    clearInterval(newGameIntervalID);
                    score = 0;
                    DOM.scoreDisplay.innerText = `Score: ${score}`;
                    strikeCount = 0;
                    DOM.strikeDisplay.innerText = `Strikes: ${strikeCount} of ${maxStrikes}`;
                    document.dispatchEvent(new Event('newclue'));
                }
            }, 1000);

        } else {
            // Update wrong guesses
            wrongGuesses.push(letter);
            let wrongGuessesDisplayText = constructWithSpaces(wrongGuesses, 3, char => char)
            DOM.statusDisplay.innerHTML = wrongGuessesDisplayText;
        }
    }

    if (answerSoFar === answer) {
        lockGame = true;
        // statusDisplay.innerHTML = `Well done! &#128512;`;  // Grinning face emoji
        DOM.statusDisplay.innerHTML = `Well done!`;

        // Shorter words score more points
        if (answer.length <= 5) {
            updateScore(25);
        } else if (5 < answer.length <= 10) {
            updateScore(20);
        } else if (10 < answer.length <= 15) {
            updateScore(15);
        } else if (15 < answer.length <= 20) {
            updateScore(10);
        } else if (answer.length > 20) {
            updateScore(5);
        }

        setTimeout(() => {
            document.dispatchEvent(new Event('newclue'));
        }, 1000);
    }
}

/**
 * Checks if a character is an uppercase letter
 *
 * @param {string} char - Character to check
 * @returns {boolean} True if character is uppercase A-Z
 */
function isUpperCaseAlpha(char) {
    return typeof char === "string" && char.length === 1
        && (char >= "A" && char <= "Z");
}

/**
 * Replaces a character at a specific index in a string
 *
 * @param {string} str - Original string
 * @param {number} index - Index to replace at
 * @param {string} chr - New character
 * @returns {string} Modified string
 */
function setCharAt(str, index, chr) {
    if (index > str.length - 1) return str;
    return str.substring(0, index) + chr + str.substring(index + 1);
}

/**
 * Constructs a display string with consistent spacing between characters
 *
 * Used for formatting the answer display and wrong guesses list with proper spacing.
 *
 * @param {string|Array} iterable - String or array to process
 * @param {number} numSpaces - Number of spaces between characters
 * @param {Function} callback - Function to process each character
 * @returns {string} Formatted display string with HTML spaces
 */
function constructWithSpaces(iterable, numSpaces, callback) {
    let constructedDisplay = '';
    let spaceBuffer = '&nbsp;'.repeat(numSpaces);
    let newChar, lastChar;
    for (let i = 0; i < iterable.length - 1; i++) {
        newChar = callback(iterable[i], i);
        constructedDisplay += newChar + spaceBuffer;
    }
    lastChar = callback(iterable[iterable.length - 1], iterable.length - 1);
    constructedDisplay += lastChar;
    return constructedDisplay;
}

/**
 * Updates the player's score and checks for high score
 *
 * Adds points to the current score, updates the display with visual feedback,
 * and handles high score tracking with localStorage persistence.
 *
 * @param {number} increment - Points to add to the score
 */
function updateScore(increment) {
    flashScore();
    score += increment;
    DOM.scoreDisplay.innerText = `Score: ${score}`;
    if (score > highScore) {
        flashHighScore();
        highScore = score;
        DOM.highScoreDisplay.innerText = `High Score: ${highScore}`;
        localStorage.setItem(highScoreStorageName, JSON.stringify(highScore));
    }
}

/**
 * Flashes the background color for visual feedback
 * Currently unused but available for wrong guess indication
 */
function flashBackground() {
    let backgroundFlashClass = 'background-flash';
    document.body.classList.add(backgroundFlashClass);
    setTimeout(() => {
        document.body.classList.remove(backgroundFlashClass);
    }, flashRemovalTimeMilliseconds);
}

/**
 * Flashes the score display when points are earned
 * Provides visual feedback for correct guesses
 */
function flashScore() {
    let scoreFlashClass = 'score-flash';
    DOM.scoreDisplay.classList.add(scoreFlashClass);
    setTimeout(() => {
        DOM.scoreDisplay.classList.remove(scoreFlashClass);
    }, flashRemovalTimeMilliseconds);
}

/**
 * Flashes the high score display when a new high score is achieved
 * Provides visual feedback for high score milestones
 */
function flashHighScore() {
    let highScoreFlashClass = 'highscore-flash';
    DOM.highScoreDisplay.classList.add(highScoreFlashClass);
    setTimeout(() => {
        DOM.highScoreDisplay.classList.remove(highScoreFlashClass);
    }, flashRemovalTimeMilliseconds);
}

/**
 * Flashes the strikes display when an incorrect guess is made
 * Provides visual feedback for wrong answers
 */
function flashStrikes() {
    let strikeFlashClass = 'strike-flash';
    DOM.strikeDisplay.classList.add(strikeFlashClass);
    setTimeout(() => {
        DOM.strikeDisplay.classList.remove(strikeFlashClass);
    }, flashRemovalTimeMilliseconds);
}
