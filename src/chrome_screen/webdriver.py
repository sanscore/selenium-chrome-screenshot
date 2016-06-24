#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ChromeScreenshot is a wrapper class for the default Chrome
webdriver which lacks the capability to take a full-page
screenshot.

https://bugs.chromium.org/p/chromedriver/issues/detail?id=294
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals, )

import base64
from time import sleep

from selenium.webdriver import Chrome
from wand.image import Image

LEFT = 0
TOP = 1
RIGHT = 2
BOTTOM = 3


class ChromeScreenshot(Chrome):
    """
    ChromeScreenshot is a wrapper class for the default Chrome
    webdriver which lacks the capability to take a full-page
    screenshot.

    https://bugs.chromium.org/p/chromedriver/issues/detail?id=294
    """

    @property
    def __document_width(self):
        """Returns the width of the webpage.

        The page's "width" is determined by the greatest of following:
            * document.body.scrollWidth
            * document.body.offsetWidth
            * document.documentElement.clientWidth
            * document.documentElement.scrollWidth
            * document.documentElement.offsetWidth

        Args:
            None

        Returns:
            An integer representing the page's width.
        """
        return self.execute_script(
            """return Math.max(document.body.scrollWidth,
                               document.body.offsetWidth,
                               document.documentElement.clientWidth,
                               document.documentElement.scrollWidth,
                               document.documentElement.offsetWidth)""")

    @property
    def __document_height(self):
        """Returns the height of the webpage.

        The page's "height" is determined by the greatest of following:
            * document.body.scrollHeight
            * document.body.offsetHeight
            * document.documentElement.clientHeight
            * document.documentElement.scrollHeight
            * document.documentElement.offsetHeight

        Args:
            None

        Returns:
            An integer representing the page's height.
        """
        return self.execute_script(
            """return Math.max(document.body.scrollHeight,
                               document.body.offsetHeight,
                               document.documentElement.clientHeight,
                               document.documentElement.scrollHeight,
                               document.documentElement.offsetHeight)""")

    @property
    def __viewport_width(self):
        """Returns the width of the browser's visible area.

        The visible width is determined by `window.innerWidth` or
        by `document.body.clientWidth`.

        Args:
            None

        Returns:
            An integer representing the visible width.
        """
        return self.execute_script(
            "return window.innerWidth || document.body.clientWidth")

    @property
    def __viewport_height(self):
        """Returns the height of the browser's visible area.

        The visible height is determined by `window.innerHeight` or
        by `document.body.clientHeight`.

        Args:
            None

        Returns:
            An integer representing the visible height.
        """
        return self.execute_script(
            "return window.innerHeight || document.body.clientHeight")

    def __scrollbars_hide(self):
        """Hides Chrome's scrollbars.

        Creates a new <style> element to contain the CSS rule for hiding
        the browser scrollbars. `::-webkit-scrollbar {width: 0px;}`

        Args:
            None

        Returns:
            None
        """
        self.execute_script(
            "var sheet = document.createElement('style'); "
            "sheet.id = 'chrome_screenshot_fix'; "
            "sheet.innerHTML = '::-webkit-scrollbar {width: 0px;}'; "
            "document.body.appendChild(sheet); ")

    def __scrollbars_restore(self):
        """Restores Chrome's scrollbars.

        Delete the <style> element created by __scrollbars_hide()

        Args:
            None

        Returns:
            None
        """
        self.execute_script(
            "var sheet = document.getElementById('chrome_screenshot_fix'); "
            "document.body.removeChild(sheet); ")

    def __scroll_to(self, x, y):
        """Scroll the browser to a cartesian point.

        Args:
            x: An integer for the leftmost position.
            y: An integer for the topmost position.

        Returns:
            None
        """
        self.execute_script('window.scrollTo({}, {})'.format(x, y))

    def __iter_rects(self, dimensions=None):
        """Generator function used to scroll the browser.

        Args:
            dimensions: When None, record the page's present dimensions.
                Otherwise, dimensions takes a 2-tuple that represents
                the desired width and height to trace.

        Yields:
            tuple: A 4-tuple (left, top, right, bottom)
        """
        if dimensions:
            doc_width, doc_height = dimensions
        else:
            doc_width = self.__document_width
            doc_height = self.__document_height

        top = 0
        while top < doc_height:
            bottom = top + self.__viewport_height

            if bottom > doc_height:
                bottom = doc_height
                top = bottom - self.__viewport_height

            left = 0
            while left < doc_width:
                right = left + self.__viewport_width

                if right > doc_width:
                    right = doc_width
                    left = right - self.__viewport_width

                yield (left, top, right, bottom)

                left += self.__viewport_width

            top += self.__viewport_height

    def __iter_screenshots(self, dimensions=None):
        """Generator function to grab screenshots.

        Args:
            dimensions: When None, record the page's present dimensions.
                Otherwise, dimensions takes a 2-tuple that represents
                the desired width and height to trace.

        Yields:
            tuple: A base64 encoded string of PNG screenshot
                and a 4-tuple (left, top, right, bottom).
        """
        for n, rect in enumerate(self.__iter_rects(dimensions)):
            self.__scroll_to(rect[LEFT], rect[TOP])
            sleep(0.2)

            yield (super(ChromeScreenshot, self).get_screenshot_as_base64(),
                   rect)

    def __screenshot_png(self, func):
        """Helper function that produces the screenshot.

        Produces a stitched together screenshot of the current webpage.
        Automatically hides and restores Chrome's scrollbars.

        Args:
            func: A helper function which will be passed the finalized
                screenshot. Whatever is returned by `func` is returned
                by this function.

        Returns:
            Whatever is returned by func(screenshot).
        """
        self.__scrollbars_hide()

        doc_width = self.__document_width
        doc_height = self.__document_height
        with Image(width=doc_width*2, height=doc_height*2) as screenshot:
            for data, rect in self.__iter_screenshots((doc_width,doc_height)):
                rect_width = (rect[RIGHT] - rect[LEFT]) * 2
                rect_height = (rect[BOTTOM] - rect[TOP]) * 2

                with Image(blob=base64.b64decode(data),
                           format='png') as shot:
                    screenshot.composite(image=shot,
                                         left=rect[LEFT]*2,
                                         top=rect[TOP]*2)
                del data

            _ret = func(screenshot)

        self.__scrollbars_restore()
        return _ret

    def prepare_page(self, max=100):
        """Scroll through the page without taking screenshots.

        Scroll through the page completely without taking any screenshots.
        This is handy specifically for websites that are optimized to
        only load content as the user scrolls. For such sites, like the
        New York Times' website, an inaccurate screenshot will be generated.

        Args:
            max: Limit to N scrolls; default 100.

        Returns:
            None
        """
        count = 0
        for rect in self.__iter_rects():
            if count < max:
                self.__scroll_to(rect[LEFT], rect[TOP])
            count += 1

    def get_screenshot_as_base64(self):
        """Returns screenshot as base64 encoded string.

        Args:
            None

        Returns:
            A base64 encoded PNG image.
        """
        def _base64(screenshot):
            return base64.b64decode(screenshot.make_blob(format='png'))
        return self.__screenshot_png(_base64)

    def get_screenshot_as_file(self, filename):
        """Save screenshot to file.

        Args:
            filename: A file path to save the PNG.

        Returns:
            True
        """
        def _save(screenshot):
            screenshot.save(filename=filename)
            return True
        return self.__screenshot_png(_save)

    def get_screenshot_as_png(self):
        """Returns screenshot as a binary string.

        Args:
            None

        Returns:
            Screenshot as a binary string.
        """
        def _bin(screenshot):
            return screenshot.make_blob(format='png')
        return self.__screenshot_png(_bin)


if __name__ == '__main__':
    driver = ChromeScreenshot()
    zurl = "http://www.python.org"

    driver.get(zurl)
    driver.save_screenshot('screenshot.png')

    driver.close()
    driver.quit()
