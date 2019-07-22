# -*- coding: utf-8 -*-
"""
Created on Sat May  4 20:59:56 2019

@author: Zero
"""

from django import forms
class Sign_in(forms.Form):
    name=forms.CharField(max_length=20)
    work_id=forms.CharField(max_length=20)
    email=forms.CharField(max_length=100)
    password1=forms.CharField(max_length=20)
    password2=forms.CharField(max_length=20)
#        register_time=forms.DateField(auto_now_add=True)
    def __str__(self):
        return self.name

class Login(forms.Form):
    work_id=forms.CharField(max_length=20)
    password1=forms.CharField(max_length=20)
    def __str__(self):
        return self.work_id