#!/usr/bin/env python3

from __future__ import annotations

from ctypes import cdll
import xcffib
import xcffib.xproto

import os
import sys

# It's hard to import from the current dir... So add the current directory to PYTHONPATH
sys.path.append(os.path.dirname(__file__))

os.environ['PYOPENGL_PLATFORM'] = 'egl'

from cube_egl import EglState, EglSurface
from cube_gl import GlScene

class X11Window:
    def __init__(self, fullscreen: bool = False, num_frames: int | None = None):
        self.fullscreen = fullscreen
        self.num_frames = num_frames

        # Connect to X server using XCB
        self.conn = xcffib.connect()
        self.setup = self.conn.get_setup()
        self.screen = self.setup.roots[0] # type: ignore

        # Set up window dimensions
        if self.fullscreen:
            self.width = self.screen.width_in_pixels
            self.height = self.screen.height_in_pixels
        else:
            self.width = 600
            self.height = 600

        # Create window
        self.window_id = self.conn.generate_id()

        mask = (
            xcffib.xproto.CW.OverrideRedirect |
            xcffib.xproto.CW.EventMask
        )

        values = [
            0,  # Override redirect
            xcffib.xproto.EventMask.Exposure |
            xcffib.xproto.EventMask.KeyPress |
            xcffib.xproto.EventMask.StructureNotify  # For resize events
        ]

        self.conn.core.CreateWindow(
            self.screen.root_depth,
            self.window_id,
            self.screen.root,
            0, 0,                     # x, y
            self.width, self.height,  # width, height
            0,                        # border width
            xcffib.xproto.WindowClass.InputOutput,
            self.screen.root_visual,
            mask,
            values
        )

        # Set up WM_DELETE_WINDOW protocol
        self.wm_protocols = self.conn.core.InternAtom(
            False, len('WM_PROTOCOLS'), 'WM_PROTOCOLS'
        ).reply().atom

        self.wm_delete_window = self.conn.core.InternAtom(
            False, len('WM_DELETE_WINDOW'), 'WM_DELETE_WINDOW'
        ).reply().atom

        self.conn.core.ChangeProperty(
            xcffib.xproto.PropMode.Replace,
            self.window_id,
            self.wm_protocols,
            xcffib.xproto.Atom.ATOM,
            32, 1,
            [self.wm_delete_window]
        )

        if self.fullscreen:
            self._set_fullscreen()

        self.conn.core.MapWindow(self.window_id)
        self.conn.flush()

    def _set_fullscreen(self):
        """Set the window to fullscreen using EWMH"""
        net_wm_state = '_NET_WM_STATE'
        net_wm_state_fullscreen = '_NET_WM_STATE_FULLSCREEN'

        cookie = self.conn.core.InternAtom(False, len(net_wm_state), net_wm_state)
        reply = cookie.reply()

        cookie2 = self.conn.core.InternAtom(False, len(net_wm_state_fullscreen),
                                          net_wm_state_fullscreen)
        reply2 = cookie2.reply()

        self.conn.core.ChangeProperty(
            xcffib.xproto.PropMode.Replace,
            self.window_id,
            reply.atom,
            xcffib.xproto.Atom.ATOM,
            32, 1,
            [reply2.atom]
        )

    def main_loop(self, egl_state, egl_surface, gl_scene):
        """Main event and render loop"""
        framenum = 0
        need_exit = False

        egl_surface.make_current()
        egl_surface.swap_buffers()

        while True:
            event = self.conn.poll_for_event()
            while event:
                if isinstance(event, xcffib.xproto.ExposeEvent):
                    pass  # Handle expose event if needed

                elif isinstance(event, xcffib.xproto.KeyPressEvent):
                    if event.detail in (24, 9):  # Q or ESC key
                        print('Exit due to keypress')
                        need_exit = True

                elif isinstance(event, xcffib.xproto.ConfigureNotifyEvent):
                    if (event.width != self.width or event.height != self.height):
                        self.width = event.width
                        self.height = event.height
                        gl_scene.set_viewport(self.width, self.height)

                elif isinstance(event, xcffib.xproto.ClientMessageEvent):
                    if event.data.data32[0] == self.wm_delete_window:
                        print('Exit due to window close')
                        need_exit = True

                event = self.conn.poll_for_event()

            if self.num_frames and framenum >= self.num_frames:
                need_exit = True

            if need_exit:
                break

            gl_scene.draw(framenum)
            egl_surface.swap_buffers()
            framenum += 1

    def cleanup(self):
        """Clean up XCB resources"""
        self.conn.core.UnmapWindow(self.window_id)
        self.conn.core.DestroyWindow(self.window_id)
        self.conn.flush()
        self.conn.disconnect()

def main_x11(fullscreen: bool = False, num_frames: int | None = None):
    window = X11Window(fullscreen, num_frames)

    # Get X11 Display for EGL initialization
    x11 = cdll.LoadLibrary('libX11.so.6')
    native_display = x11.XOpenDisplay(None)
    egl_state = EglState(native_display)
    egl_surface = EglSurface(egl_state, window.window_id)

    gl_scene = GlScene()

    gl_scene.set_viewport(window.width, window.height)

    window.main_loop(egl_state, egl_surface, gl_scene)

    window.cleanup()

if __name__ == '__main__':
    main_x11()
