from django import forms


CITIES = (  
    ('Washington DC', "Washington DC" ),
    ('Barcelona', "Barcelona"),
)

class findMyReviewsForm(forms.Form):
	city = forms.CharField(label="What's your city?", widget=forms.Select(choices=CITIES))
	name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control input-sm'}))
	From = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
	To = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))      
	# email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control input-sm'}))
	# topic = forms.ChoiceField(choices=TOPICS, required=True, widget=forms.Select(attrs={'class' : 'form-control input-sm'}))
	# comment = forms.CharField(required=True, widget=forms.Textarea(attrs={'class' : 'form-control input-sm'}))
