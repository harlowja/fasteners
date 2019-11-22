import unittest
import os.path
import tempfile

from fasteners import fs_lock, lock


class FileLockTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.lock_path = os.path.join(self.temp_dir, 'lock.txt')
        self.lk = fs_lock.FileLock(self.lock_path)

    def tearDown(self):
        if os.path.exists(self.lock_path):
            os.unlink(self.lock_path)
        os.rmdir(self.temp_dir)

    def test_acquire(self):
        self.lk.acquire()
        try:
            self.assertTrue(self.lk.holds_lock())
        finally:
            self.lk.release()
        self.assertFalse(self.lk.holds_lock())

    def test_acquire_shared(self):
        self.lk.acquire_shared()
        try:
            self.assertTrue(self.lk.holds_lock())
        finally:
            self.lk.release_shared()
        self.assertFalse(self.lk.holds_lock())

    def test_acquire_ctx(self):
        with self.lk:
            self.assertTrue(self.lk.holds_lock())

    def test_acquire_shared_ctx(self):
        with self.lk.shared:
            self.assertTrue(self.lk.holds_lock())
