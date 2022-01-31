"""
A decorator to enable windows virtual terminal processing, which allows terminals to use
the ansi control codes for color supported by Linux / MacOS.

"""

__all__ = ["enable_windows_virtual_terminal_processing"]

from contextlib import contextmanager
import ctypes

import platform

WINDOWS = platform.system() == "Windows"

if WINDOWS:
    from ctypes.wintypes import DWORD, byref

    _STD_OUTPUT_HANDLE = -11
    _ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)

    def _get_console_mode() -> int:
        """Get the current console mode."""
        mode = DWORD()
        _KERNEL32.GetConsoleMode(_STD_OUTPUT_HANDLE, byref(mode))
        return mode.value

    def _set_console_mode(mode: int) -> bool:
        """Set the current console mode."""
        success = _KERNEL32.SetConsoleMode(
            _STD_OUTPUT_HANDLE, mode | _ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )
        return success

    @contextmanager
    def enable_windows_virtual_terminal_processing():
        """Context manager to enable virtual terminal processing on enter,
        and restore the previous setting on exit. Does nothing if run on
        a non-Widows platfrom.

        """
        current_console_mode = _get_console_mode()
        success = _set_console_mode(
            current_console_mode | _ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )
        yield
        if success:
            _set_console_mode(current_console_mode)

else:

    @contextmanager
    def enable_windows_virtual_terminal_processing():
        """Context manager to enable virtual terminal processing on enter,
        and restore the previous setting on exit. Does nothing if run on
        a non-Widows platfrom.

        """
        yield
