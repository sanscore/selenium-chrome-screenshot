import sys

from chrome_screen.webdriver import ChromeScreenshot

# TODO: Create REAL TESTS
#   * Find some method that should create perfect rendering, canvas? svg? ??
#   * Create some Test Cards using 'perfect rendering' method.
#   * Screenshot page
#   * Use Wand\Image Magick to check for correctness
#       * Compositing Difference
#       * Check RGB values at specific points
#       * Allow for fuzziness?


def test_python_org():
    driver = ChromeScreenshot()
    zurl = "http://www.python.org"

    driver.get(zurl)
    driver.save_screenshot(
        'screenshot-py{}{}.png'.format(*sys.version_info[:2]))

    driver.close()
    driver.quit()
