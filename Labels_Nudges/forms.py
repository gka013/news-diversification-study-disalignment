# from tkinter.tix import Select
from django import forms
from django.core.exceptions import ValidationError
from django.db import close_old_connections, models
from django.db.models import fields
from django.forms import widgets
from .models import Personal_info,EvaluateChoices, EvaluateChoices2, \
    EvaluateChoices3, EvaluateChoices4, EvaluateChoices5, EvaluateChoices6, EvaluateChoices7, EvaluateChoices8, \
    EvaluateChoices9, EvaluateChoices10, Ghs_fk, Ghs_fk2, Topic_preference
from django.forms import formset_factory, modelformset_factory


class Personal_infoForm(forms.ModelForm):
    class Meta:
        model = Personal_info
        # Option A: Explicitly list the fields you want to show:
        fields = [
            'gender',
            'age',
            'country',
            'education',
        ]

        widgets = {
            'gender': forms.RadioSelect(attrs={'label_suffix': ''}),
            'age': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'gender': 'gender',
            'age': 'age',
            'country': 'country',
            'education': 'education',
        }


class Topic_preferenceForm(forms.ModelForm):
    class Meta:
        model = Topic_preference
        # Exclude automatically set fields.
        exclude = ('id', 'person', 'created', 'title', 'session_id')
        # Use HiddenInput so your UI’s thumbs buttons update these values.
        widgets = {
            'politikk': forms.HiddenInput(),
            'okonomi_og_naeringsliv': forms.HiddenInput(),
            'kriminalitet_og_rettssaker': forms.HiddenInput(),
            'utenriks_og_globale_konflikter': forms.HiddenInput(),
            'samfunn_og_arbeidsliv': forms.HiddenInput(),
            'klima_og_miljo': forms.HiddenInput(),
            'helse_og_forskning': forms.HiddenInput(),
            'teknologi_og_vitenskap': forms.HiddenInput(),
            'sport': forms.HiddenInput(),
            'underholdning_og_kjendiser': forms.HiddenInput(),
            'livsstil_og_helse': forms.HiddenInput(),
            'mat_og_drikke': forms.HiddenInput(),
        }
        labels = {
            'politikk': 'Politikk',
            'okonomi_og_naeringsliv': 'Økonomi og næringsliv',
            'kriminalitet_og_rettssaker': 'Kriminalitet og rettssaker',
            'utenriks_og_globale_konflikter': 'Utenriks og globale konflikter',
            'samfunn_og_arbeidsliv': 'Samfunn og arbeidsliv',
            'klima_og_miljo': 'Klima og miljø',
            'helse_og_forskning': 'Helse og forskning',
            'teknologi_og_vitenskap': 'Teknologi og vitenskap',
            'sport': 'Sport',
            'underholdning_og_kjendiser': 'Underholdning og kjendiser',
            'livsstil_og_helse': 'Livsstil og helse',
            'mat_og_drikke': 'Mat og drikke',
            # Media usage as radio buttons
            'media_usage': forms.RadioSelect(),
        }


class Ghs_fkForm(forms.ModelForm):
    class Meta:
        model = Ghs_fk
        exclude = ('id', 'person', 'created', 'title', 'session_id')
        widgets = {
            'FK_1': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_2': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_3': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_4': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_5': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_6': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_7': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_8': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_9': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_10': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_11': forms.RadioSelect(attrs={'label_suffix': '', }),
            'FK_12': forms.RadioSelect(attrs={'label_suffix': '', })
        }

        # Shortform PANAS-X
        labels = {
            'FK_1': 'I currently feel upset.',
            'FK_2': 'I currently feel hostile.',
            'FK_3': 'I currently feel alert.',
            'FK_4': 'I currently feel ashamed.',
            'FK_5': 'I currently feel inspired.',
            'FK_6': 'I currently feel nervous.',
            'FK_7': 'I currently feel determined.',
            'FK_8': 'I currently feel attentive.',
            'FK_9': 'I currently feel afraid.',
            'FK_10': 'I currently feel active.'
        }


likert_scale = [
    ('1', '1 - Strongly Disagree'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5 - Strongly Agree')
]
popularity_stars = [
    ('3.8', '3 stars'),
    ('4', '4 stars'),
    ('0', 'No preferences')
]


class Ghs_fk2Form(forms.Form):
    like_chosen = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="I like the articles I’ve chosen"
    )
    looking_forward = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="I was/am looking forward to reading the chosen articles"
    )
    fit_preferences = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="The chosen articles fit my general preferences"
    )
    know_better = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="I would know several articles that are better than the ones I’ve chosen"
    )
    interesting = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="I found the recommended articles to be interesting"
    )
    fitted_preferences = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="The recommended articles fitted my preferences"
    )
    relevant = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="The recommended articles were relevant to me"
    )
    similar_to_each_other = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="The recommended articles were similar to each other"
    )
    differed_topics = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="The recommended articles differed in terms of their topics"
    )
    diversity_high = forms.ChoiceField(
        choices=likert_scale,
        widget=forms.RadioSelect(attrs={'label_suffix': ''}),
        label="The diversity in the recommended list of articles was high"
    )
class ChoiceEvaluationForm(forms.ModelForm):
    class Meta:
        model = EvaluateChoices
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'read_more': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'mood_fit': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # choice difficulty

            'many_to_choose': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            'read_more': 'I want to read more of this article.',
            'liked_news': "I like this article.",
            'trust_news': "I trust the article's content.",
            'fit_preference': "The content of the article align with my general preferences.",
            'mood_fit': 'The content of this article aligns well with my mood.',
            'recommend_news': 'I would like to share this article with others.',

            # Choice difficulty
            'many_to_choose': 'Which color is mentioned in the text above?',

        }


class ChoiceEvaluationForm2(forms.ModelForm):
    class Meta:
        model = EvaluateChoices2
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'intention_to_act1': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'intention_to_act2': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'intention_to_act3': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'intention_to_act4': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'understanding': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'clarity': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'permissibility': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
        }

        labels = {
            'intention_to_act1': 'I plan to take some actions to stop global warming.',
            'intention_to_act2': 'I personally do not intend to do much to stop global warming.',
            'intention_to_act3': 'I will make some efforts to mitigate the negative effects of global warming.',
            'intention_to_act4': 'I intend to take concrete steps to do something to mitigate the negative effects of '
                                 'global warming.',
            'understanding': 'I understand the information provided to me.',
            'clarity': "The news article preview is written clearly.",
            'permissibility': "It is appropriate to use AI to summarize news articles.",
            'trust': "I trust AI to write a fair and balanced summary.",
        }


class ChoiceEvaluationForm3(forms.ModelForm):
    class Meta:
        model = EvaluateChoices3
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'intention_to_act1': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'intention_to_act2': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'intention_to_act3': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'intention_to_act4': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'understanding': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'clarity': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'permissibility': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
        }

        labels = {
            'intention_to_act1': 'I plan to take some actions to stop global warming.',
            'intention_to_act2': 'I personally do not intend to do much to stop global warming.',
            'intention_to_act3': 'I will make some efforts to mitigate the negative effects of global warming.',
            'intention_to_act4': 'I intend to take concrete steps to do something to mitigate the negative effects of '
                                 'global warming.',
            'understanding': 'I understand the information provided to me.',
            'clarity': "The news article preview is written clearly.",
            'permissibility': "It is appropriate to use AI to summarize news articles.",
            'trust': "I trust AI to write a fair and balanced summary.",
        }


class ChoiceEvaluationForm4(forms.ModelForm):
    class Meta:
        model = EvaluateChoices4
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'know_many': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            # Choice satisfaction
            'liked_news': "I have read the entire news article.",
            'trust_news': "I trust the article's content.",
            'fit_preference': "I agree with the article's content.",
            # 'know_many': 'I know many recipes that I like more than the one I have chosen',
            'recommend_news': 'I would recommend the chosen article to others.',

        }


class ChoiceEvaluationForm5(forms.ModelForm):
    class Meta:
        model = EvaluateChoices5
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'know_many': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # choice difficulty

            # 'many_to_choose': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'diet_restriction': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'easy_choice': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'choice_overwhelming': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # Perceived effort
            # 'sys_time': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'unders_sys': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'many_actions': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            # Choice satisfaction
            'liked_news': "I have read the entire news article",
            'trust_news': "I trust the article's content ",
            'fit_preference': "I agree with the article's content",
            # 'know_many': 'I know many recipes that I like more than the one I have chosen',
            'recommend_news': 'I would recommend the chosen article to others',

            # Choice difficulty
            # 'many_to_choose': 'I changed my mind several times before making a decision ',
            # 'diet_restriction': 'Do you have any dietary restrictions',
            # 'easy_choice': 'It was easy to make this choice ',
            # 'choice_overwhelming': 'Making a choice was overwhelming ',

            # Perceived effort
            # 'sys_time':'The system takes up a lot of time',
            # 'unders_sys':'I quickly understood the functionalities of the system',
            # 'many_actions':'Many actions were required to use the system'
        }


class ChoiceEvaluationForm6(forms.ModelForm):
    class Meta:
        model = EvaluateChoices6
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'know_many': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # choice difficulty

            # 'many_to_choose': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'diet_restriction': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'easy_choice': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'choice_overwhelming': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # Perceived effort
            # 'sys_time': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'unders_sys': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'many_actions': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            # Choice satisfaction
            'liked_news': "I have read the entire news article",
            'trust_news': "I trust the article's content ",
            'fit_preference': "I agree with the article's content",
            # 'know_many': 'I know many recipes that I like more than the one I have chosen',
            'recommend_news': 'I would recommend the chosen article to others',

            # Choice difficulty
            # 'many_to_choose': 'I changed my mind several times before making a decision ',
            # 'diet_restriction': 'Do you have any dietary restrictions',
            # 'easy_choice': 'It was easy to make this choice ',
            # 'choice_overwhelming': 'Making a choice was overwhelming ',

            # Perceived effort
            # 'sys_time':'The system takes up a lot of time',
            # 'unders_sys':'I quickly understood the functionalities of the system',
            # 'many_actions':'Many actions were required to use the system'
        }


class ChoiceEvaluationForm7(forms.ModelForm):
    class Meta:
        model = EvaluateChoices7
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'know_many': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # choice difficulty

            # 'many_to_choose': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'diet_restriction': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'easy_choice': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'choice_overwhelming': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # Perceived effort
            # 'sys_time': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'unders_sys': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'many_actions': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            # Choice satisfaction
            'liked_news': "I have read the entire news article",
            'trust_news': "I trust the article's content ",
            'fit_preference': "I agree with the article's content",
            # 'know_many': 'I know many recipes that I like more than the one I have chosen',
            'recommend_news': 'I would recommend the chosen article to others',

            # Choice difficulty
            # 'many_to_choose': 'I changed my mind several times before making a decision ',
            # 'diet_restriction': 'Do you have any dietary restrictions',
            # 'easy_choice': 'It was easy to make this choice ',
            # 'choice_overwhelming': 'Making a choice was overwhelming ',

            # Perceived effort
            # 'sys_time':'The system takes up a lot of time',
            # 'unders_sys':'I quickly understood the functionalities of the system',
            # 'many_actions':'Many actions were required to use the system'
        }


class ChoiceEvaluationForm8(forms.ModelForm):
    class Meta:
        model = EvaluateChoices8
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'know_many': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # choice difficulty

            'many_to_choose': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'diet_restriction': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'easy_choice': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'choice_overwhelming': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # Perceived effort
            # 'sys_time': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'unders_sys': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'many_actions': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            # Choice satisfaction
            'liked_news': "I have read the entire news article",
            'trust_news': "I trust the article's content ",
            'fit_preference': "I agree with the article's content",
            # 'know_many': 'I know many recipes that I like more than the one I have chosen',
            'recommend_news': 'I would recommend the chosen article to others',

            # Choice difficulty
            'many_to_choose': 'Which color is mentioned in the text above?',
            # 'diet_restriction': 'Do you have any dietary restrictions',
            # 'easy_choice': 'It was easy to make this choice ',
            # 'choice_overwhelming': 'Making a choice was overwhelming ',

            # Perceived effort
            # 'sys_time':'The system takes up a lot of time',
            # 'unders_sys':'I quickly understood the functionalities of the system',
            # 'many_actions':'Many actions were required to use the system'
        }


class ChoiceEvaluationForm9(forms.ModelForm):
    class Meta:
        model = EvaluateChoices9
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'know_many': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # choice difficulty

            # 'many_to_choose': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'diet_restriction': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'easy_choice': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'choice_overwhelming': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # Perceived effort
            # 'sys_time': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'unders_sys': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'many_actions': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            # Choice satisfaction
            'liked_news': "I have read the entire news article",
            'trust_news': "I trust the article's content ",
            'fit_preference': "I agree with the article's content",
            # 'know_many': 'I know many recipes that I like more than the one I have chosen',
            'recommend_news': 'I would recommend the chosen article to others',

            # Choice difficulty
            # 'many_to_choose': 'I changed my mind several times before making a decision ',
            # 'diet_restriction': 'Do you have any dietary restrictions',
            # 'easy_choice': 'It was easy to make this choice ',
            # 'choice_overwhelming': 'Making a choice was overwhelming ',

            # Perceived effort
            # 'sys_time':'The system takes up a lot of time',
            # 'unders_sys':'I quickly understood the functionalities of the system',
            # 'many_actions':'Many actions were required to use the system'
        }


class ChoiceEvaluationForm10(forms.ModelForm):
    class Meta:
        model = EvaluateChoices10
        exclude = ('id', 'created', 'title', 'person', 'session_id')
        widgets = {

            # choice satisfaction
            'liked_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'trust_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'fit_preference': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'know_many': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            'recommend_news': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # choice difficulty

            # 'many_to_choose': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'diet_restriction': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'easy_choice': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'choice_overwhelming': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

            # Perceived effort
            # 'sys_time': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'unders_sys': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),
            # 'many_actions': forms.RadioSelect(attrs={'label_suffix': '', 'required': True}),

        }
        labels = {

            # Choice satisfaction
            'liked_news': "I have read the entire news article",
            'trust_news': "I trust the article's content ",
            'fit_preference': "I agree with the article's content",
            # 'know_many': 'I know many recipes that I like more than the one I have chosen',
            'recommend_news': 'I would recommend the chosen article to others',

            # Choice difficulty
            # 'many_to_choose': 'I changed my mind several times before making a decision ',
            # 'diet_restriction': 'Do you have any dietary restrictions',
            # 'easy_choice': 'It was easy to make this choice ',
            # 'choice_overwhelming': 'Making a choice was overwhelming ',

            # Perceived effort
            # 'sys_time':'The system takes up a lot of time',
            # 'unders_sys':'I quickly understood the functionalities of the system',
            # 'many_actions':'Many actions were required to use the system'
        }
