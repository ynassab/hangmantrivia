/**
 * @jest-environment jsdom
 */

require("../../src/frontend/index/scripts/load_animations");

describe("load_animations.js", () => {
    let observeMock;

    beforeEach(() => {
        jest.resetModules();
        document.body.innerHTML = `
            <div class="load-left"></div>
            <div class="load-right"></div>
        `;

        // Mock IntersectionObserver
        observeMock = jest.fn();
        global.IntersectionObserver = jest.fn((callback) => ({
            observe: observeMock,
            disconnect: jest.fn(),
            trigger(entries) {
                callback(entries); // helper to simulate intersection events
            }
        }));
    });

    test("sets up IntersectionObserver on DOMContentLoaded", () => {
        document.dispatchEvent(new Event("DOMContentLoaded"));

        expect(IntersectionObserver).toHaveBeenCalledTimes(1);
        expect(observeMock).toHaveBeenCalledTimes(2); // two elements observed
    });

    test("adds 'show' class when element intersects", () => {
        document.dispatchEvent(new Event("DOMContentLoaded"));

        const observerInstance = IntersectionObserver.mock.results[0].value;
        const el = document.querySelector(".load-left");

        observerInstance.trigger([{ isIntersecting: true, target: el }]);

        expect(el.classList.contains("show")).toBe(true);
    });

    test("does not add 'show' class when element is not intersecting", () => {
        document.dispatchEvent(new Event("DOMContentLoaded"));

        const observerInstance = IntersectionObserver.mock.results[0].value;
        const el = document.querySelector(".load-left");

        observerInstance.trigger([{ isIntersecting: false, target: el }]);

        expect(el.classList.contains("show")).toBe(false);
    });
});
