from django import forms

class TemplateInputForm(forms.Form):
	attributes_number = forms.IntegerField(label='Cantidad de atributos por alumno')
	groups_clusters = forms.IntegerField(label='Cantidad de divisiones (Ej: secciones, dias, etc.)')
	preferences_number = forms.IntegerField(label='Cantidad de temas')


class UploadTemplateForm(forms.Form):
	file = forms.FileField()


class InputForm(forms.Form):
	groups_number = forms.IntegerField(label='Cantidad total de grupos')
	lower_number = forms.IntegerField(label='Numero minimo de alumnos por grupo')
	upper_number = forms.IntegerField(label='Numero maximo de alumnos por grupo')
	file = forms.FileField()
	#CHOICES = (('1', 'Beneficiar disponibilidad',), ('2', 'Minimizar peor preferencia',), ('3', 'Diversidad',))
    #objective = forms.ChoiceField(widget=forms.RadioSelect(), choices=CHOICES, label="Objetivo")