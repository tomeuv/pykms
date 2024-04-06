#!/usr/bin/python3

import fcntl
import gc
import unittest

import kms


class TestCardMethods(unittest.TestCase):
    def test_card(self):
        card = kms.Card()
        fd = card.fd

        card = None
        gc.collect()
        with self.assertRaises(Exception):
            fcntl.fcntl(fd, fcntl.F_GETFD)

    def test_card_fb_2(self):
        card = kms.Card()
        fd = card.fd

        fb = kms.DumbFramebuffer(card, 640, 480, kms.PixelFormat.XRGB8888)

        map = fb.map(0)
        fb_fd = fb.fd(0)
        fcntl.fcntl(fb_fd, fcntl.F_GETFD)

        card = None
        gc.collect()
        fb = None
        gc.collect()
        with self.assertRaises(Exception):
            fcntl.fcntl(fd, fcntl.F_GETFD)
        with self.assertRaises(Exception):
            fcntl.fcntl(fb_fd, fcntl.F_GETFD)
        self.assertTrue(map.closed)


if __name__ == '__main__':
    unittest.main()
