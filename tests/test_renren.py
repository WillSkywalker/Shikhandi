#!/usr/bin/env python3

import os
import unittest
from Shikhandi.renren import RenRen

class TestRenRen(unittest.TestCase):

    def setUp(self):
        self.ren = RenRen(os.environ['renren_id'], os.environ['renren_passwd'])
        self.ren.login()

    def tearDown(self):
        self.ren.close()

    # def test_login(self):
    #     self.assertEqual(self.ren.login(), 'Login Successful!')
    #     self.ren.login()

    def test_get_friend_list(self):
        friendlist = self.ren.get_friend_list()
        print(friendlist)
        
