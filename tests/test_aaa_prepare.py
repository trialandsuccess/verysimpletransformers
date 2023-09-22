import os


def test_before_actual_tests():
    os.system("rm pytest*.vst")