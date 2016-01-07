import unittest
from pydicter import is_relevant_file, is_directory

class TestPydicter(unittest.TestCase):

    def test_relevant_files(self):
        self.assertTrue(is_relevant_file({'href':'test.mp4'}))
        self.assertTrue(is_relevant_file({'href':'test.mkv'}))
        self.assertTrue(is_relevant_file({'href':'test.avi'}))
        self.assertFalse(is_relevant_file({'href':'test.xxx'}))
        self.assertFalse(is_relevant_file({'href':'testavi'}))
        self.assertFalse(is_relevant_file({'href':'testmkv'}))
        self.assertFalse(is_relevant_file({'href':'testmp4'}))

    def test_directory(self):
        self.assertTrue(is_directory('some/random/url/'))
        self.assertFalse(is_directory('not/some/random/url'))


if __name__ == '__main__':
    unittest.main()
