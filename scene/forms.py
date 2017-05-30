# -*- coding: cp850 -*
from django import forms

class FirstStepForm(forms.Form):
    ''' define global topologic variables '''
    name = forms.CharField(label='Nombre', max_length=100)
    lineNumber = forms.IntegerField(label='Cantidad de líneas')

    

class SecondStepForm(forms.Form):
    ''' upload topologic file '''
    pass

class ThirdStepForm(forms.Form):
    ''' define global systemic variables '''
    pass

class FourthStepForm(forms.Form):
    ''' upload systemic file '''
    pass

class FithStepForm(forms.Form):
    ''' define operational global variables '''
    pass

class SixthStepForm(forms.Form):
    ''' upload operational file '''
    pass

class SeventhStepForm(forms.Form):
    ''' upload velocity file (optional) '''
    pass



