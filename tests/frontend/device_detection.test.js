/**
 * @jest-environment jsdom
 */

const isMobileOrTablet = require("../../src/frontend/index/scripts/device_detection").isMobileOrTablet;

function overwriteUserAgent(overwrittenUserAgent) {
        navigator.__defineGetter__('userAgent', function(){
                return overwrittenUserAgent;
        });
}

describe("device_detection.js", () => {
    beforeEach(() => {
        jest.resetModules(); // Clear cache before each test
        global.navigator = { userAgent: "", vendor: "", maxTouchPoints: 0 };
        global.window = {}; // minimal window object
    });

    test("detects Android mobile device", () => {
        overwriteUserAgent("Mozilla/5.0 (Linux; Android 9; Mobile)");

        expect(isMobileOrTablet()).toBe(true);
    });

    test("detects iPhone", () => {
        overwriteUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)");
        expect(isMobileOrTablet()).toBe(true);
    });

    test("detects iPad (Macintosh UA with touch)", () => {
        overwriteUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15)");
        navigator.maxTouchPoints = 5;
        expect(isMobileOrTablet()).toBe(true);
    });

    test("detects desktop (non-mobile)", () => {
        overwriteUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64)");
        expect(isMobileOrTablet()).toBe(false);
    });
});
