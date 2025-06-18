from django.db import models
from django.db.models.deletion import CASCADE
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from .choices import *


# -------------------------------
# PERSONAL INFO MODEL
# -------------------------------
class Personal_info(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, editable=False, default='Personal_info')
    created = models.DateTimeField(auto_now_add=True)
    age = models.CharField(max_length=120, choices=Age_choices, verbose_name='age', default=None, blank=False)
    country = CountryField(blank_label='')
    education = models.CharField(max_length=120, choices=EducationLevel, verbose_name='education', default=None,
                                 blank=False)
    gender = models.CharField(max_length=300, choices=Gender_choices, verbose_name='gender', default=None, blank=False)
    prolific_username = models.CharField(max_length=100, unique=True, default=None, blank=False,
                                         verbose_name='prolific ID')
    session_id = models.CharField(max_length=100, blank=False, default=None)
    clicked_articles_list = models.JSONField(default=list)
    clicked_articles_details = models.JSONField(default=list)

    last_home = models.DateTimeField(null=True, blank=True,
                                     help_text="When the participant last visited home")

    phase1_start = models.DateTimeField(null=True, blank=True,
                                        help_text="Timestamp when Phase 1 began")
    phase1_elapsed = models.PositiveIntegerField(null=True, blank=True,
                                                 help_text="Seconds spent in Phase 1 before submit")

    # Phase completion flags
    phase_one_complete = models.BooleanField(default=False)
    phase_two_complete = models.BooleanField(default=False)

    # Separate redemption codes for each phase
    redemption_code_phase1 = models.CharField(max_length=50, blank=True, null=True)
    redemption_code_phase2 = models.CharField(max_length=50, blank=True, null=True)

    def next_phase_url(self):
        """
        Returns the URL name for the next phase or sub-view.
        """
        # Debug output to verify flag states
        print(f"DEBUG - Flags: phase_one_complete={self.phase_one_complete}, "
              f"redemption_code_phase1={self.redemption_code_phase1}, "
              f"phase_two_complete={self.phase_two_complete}")

        if not self.phase_one_complete:
            # Make sure we're correctly checking phase one status
            return 'Labels_Nudges:choice_evaluation'
        if not self.redemption_code_phase1:
            return 'Labels_Nudges:redemption', {'phase': 1}
        if not self.phase_two_complete:
            return 'Labels_Nudges:topic_preference'
        if not self.redemption_code_phase2:
            return 'Labels_Nudges:redemption', {'phase': 2}

        return 'Labels_Nudges:thank_u'

    class Meta:
        verbose_name = 'personal_info'
        ordering = ['id']
        db_table = 'personal_info'

    def __str__(self):
        return "{}".format(self.id)


# -------------------------------
# TOPIC PREFERENCE MODEL
# -------------------------------
TOPIC_CHOICES = (
    (-1, "Dislike"),
    (0, "Neutral"),
    (1, "Like"),
)

USAGE_CHOICES = (
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('rarely', 'Rarely'),
)


class Topic_preference(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='topic_preference'
    )
    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    # your existing rating fields
    politikk                       = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Politikk', default=0)
    okonomi_og_naeringsliv         = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Økonomi og næringsliv', default=0)
    kriminalitet_og_rettssaker     = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Kriminalitet og rettssaker', default=0)
    utenriks_og_globale_konflikter = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Utenriks og globale konflikter', default=0)
    samfunn_og_arbeidsliv          = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Samfunn og arbeidsliv', default=0)
    klima_og_miljo                  = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Klima og miljø', default=0)
    helse_og_forskning             = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Helse og forskning', default=0)
    teknologi_og_vitenskap          = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Teknologi og vitenskap', default=0)
    sport                          = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Sport', default=0)
    underholdning_og_kjendiser      = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Underholdning og kjendiser', default=0)
    livsstil_og_helse               = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Livsstil og helse', default=0)
    mat_og_drikke                  = models.IntegerField(choices=TOPIC_CHOICES, verbose_name='Mat og drikke', default=0)

    media_usage  = models.CharField(max_length=20, choices=USAGE_CHOICES)
    media_access = models.CharField(
        max_length=200,
        help_text="Velg alle som gjelder (kommaseparert)"
    )
    news_source  = models.CharField(
        max_length=200,
        help_text="Velg alle som gjelder (kommaseparert)"
    )

    session_id = models.CharField(
        max_length=100,
        null=True,
        default=''
    )

    # New: maintain a history of each wave’s preferences
    history = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of {"
            "'timestamp': ISO8601 string, "
            "'preferences': {field_name: value, …}"
            "}"
        )
    )

    class Meta:
        verbose_name = 'topic_preference'
        ordering = ['id']
        db_table = 'topic_preference'

    def __str__(self):
        return str(self.id)


# -------------------------------
# Article Click
# -------------------------------
class ArticleClick(models.Model):
    person = models.ForeignKey(Personal_info, on_delete=models.CASCADE)
    phase = models.PositiveSmallIntegerField(  # 1, 2 or 3
        help_text="Which phase these clicks belong to"
    )
    session_id = models.CharField(
        max_length=40, null=True, blank=True,
        help_text="Django session_key"
    )
    clicked_at = models.DateTimeField(
        auto_now=True,
        help_text="When the user submitted their clicks"
    )

    # Phase-specific timing (only used in phase 1)
    phase1_start = models.DateTimeField(
        null=True, blank=True,
        help_text="Timestamp when Phase 1 began"
    )
    phase1_elapsed = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Seconds spent in Phase 1 before submit"
    )

    phase2_start = models.DateTimeField(null=True, blank=True)
    phase2_elapsed = models.PositiveIntegerField(null=True, blank=True)

    total_clicked = models.PositiveIntegerField(null=True, blank=True)
    percent_familiar = models.FloatField(null=True, blank=True)

    # New: one JSONField of click objects
    click_data = models.JSONField(
        default=list,
        help_text=(
            "List of {"
            '"id": str, '
            '"title": str, '
            '"similarity": float, '
            '"cluster": str, '
            '"explore": bool, '
            '"source": str, '
            '"topics": [str], '
            '"clicked_at": str'
            "}"
        )
    )

    class Meta:
        unique_together = (("person", "phase"),)
        indexes = [
            models.Index(fields=["session_id"]),
        ]

    def __str__(self):
        return f"Clicks for {self.person} – phase {self.phase}"


# -------------------------------
# Ghs_fk and Ghs_fk2 Models (unchanged)
# -------------------------------
class Ghs_fk(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, editable=False, default='Knowledge health')
    person = models.ForeignKey(Personal_info, on_delete=models.CASCADE)
    FK_1 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_1', default=None, blank=False)
    FK_2 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_2', default=None, blank=False)
    FK_3 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_3', default=None, blank=False)
    FK_4 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_4', default=None, blank=False)
    FK_5 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_5', default=None, blank=False)
    FK_6 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_6', default=None, blank=False)
    FK_7 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_7', default=None, blank=False)
    FK_8 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_8', default=None, blank=False)
    FK_9 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_9', default=None, blank=False)
    FK_10 = models.CharField(max_length=300, choices=FK__choices, verbose_name='FK_10', default=None, blank=False)
    session_id = models.CharField(max_length=100, blank=False, default='')

    class Meta:
        verbose_name = 'Ghs_fk'
        ordering = ['id']
        db_table = 'ghs_fk'

    def __str__(self):
        return "{}".format(self.id)


class Ghs_fk2(models.Model):
    # tie one record per person
    person = models.OneToOneField(
        Personal_info,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='ghs_fk2'
    )
    # keep your session id and title as before
    session_id = models.CharField(max_length=100)
    title = models.CharField(max_length=50, editable=False, default='Ghs_fk2')

    # ←— new JSONField to accumulate each round’s responses
    iterations = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of response dictionaries per iteration, each containing: "
            "like_chosen, looking_forward, fit_preferences, know_better, "
            "interesting, fitted_preferences, relevant, similar_to_each_other, "
            "differed_topics, diversity_high, and timestamp."
        )
    )

    class Meta:
        db_table = 'ghs_fk2'


# -------------------------------
# NewsRec Model (unchanged)
# -------------------------------
class NewsRec(models.Model):
    id = models.AutoField(primary_key=True)
    article_url = models.CharField(max_length=500, blank=True, null=True)
    title = models.CharField(max_length=500, default="Some String")
    category = models.CharField(max_length=50, default="", blank=True)
    text = models.TextField(default="Some String")
    image = models.ImageField(upload_to='images/UMAP/', default="", blank=True)
    summary_neutral = models.TextField(default="", blank=True)
    summary_fearful = models.TextField(default="", blank=True)
    summary_fear_hope = models.TextField(default="", blank=True)
    fetched_date = models.DateField(null=True, blank=True)  # New field

    class Meta:
        verbose_name = 'NewsRec'
        ordering = []
        db_table = 'NewsRec'

    def __str__(self):
        return self.title


# -------------------------------
# ClimateNews Model (MODIFIED)
# -------------------------------
class ClimateNews(models.Model):
    id = models.AutoField(primary_key=True)
    article_url = models.TextField(default="Some String")
    title = models.TextField(default="Some String")
    author = models.TextField(default="Some String")
    type = models.TextField(default="Some String")
    category = models.TextField(default="Some String")
    subcategory = models.TextField(default="Some String")
    text = models.TextField(default="Some String")
    date = models.TextField(default="Some String")
    time = models.TextField(default="Some String")
    image_url = models.TextField(default="Some String")
    image_caption = models.TextField(default="Some String")
    author_bio = models.TextField(default="Some String")
    subtype = models.TextField(default="Some String")

    class Meta:
        verbose_name = 'ClimateNews'
        ordering = []
        db_table = 'ClimateNews'

    def __str__(self):
        return self.title


# -------------------------------
# Recommendations Model (unchanged)
# -------------------------------
class Recommendations(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Personal_info, on_delete=models.CASCADE)
    recommended_recipes = models.CharField(max_length=500)
    healthiness = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'recommendations'
        db_table = 'Recommendations'


# -------------------------------
# SelectedRecipe Model (unchanged)
# -------------------------------
class SelectedRecipe(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Personal_info, blank=False, on_delete=models.CASCADE)
    recipe_id = models.IntegerField()
    recipe_name = models.CharField(max_length=200)
    Nutri_score = models.CharField(max_length=100)
    fsa_score = models.CharField(max_length=100)
    healthiness = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        unique_together = ('person', 'recipe_id')
        verbose_name = 'selectedRecipe'
        db_table = 'selectedrecipe'

    def __str__(self):
        return self.healthiness


# -------------------------------
# EvaluateChoices Models (unchanged)
# -------------------------------
class EvaluateChoices(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, editable=False, default='EvaluateChoices')
    person = models.ForeignKey(Personal_info, on_delete=models.CASCADE)
    read_more = models.CharField(max_length=100, choices=FK__choices, verbose_name='read_more', default=None,
                                 blank=False)
    liked_news = models.CharField(max_length=100, choices=FK__choices, verbose_name='liked_news', default=None,
                                  blank=False)
    trust_news = models.CharField(max_length=100, choices=FK__choices, verbose_name='trust_news', default=None,
                                  blank=False)
    fit_preference = models.CharField(max_length=100, choices=FK__choices, verbose_name='fit_preference', default=None,
                                      blank=False)
    mood_fit = models.CharField(max_length=100, choices=FK__choices, verbose_name='mood_fit', default=None, blank=False)
    recommend_news = models.CharField(max_length=100, choices=FK__choices, verbose_name='recommend_news', default=None,
                                      blank=False)
    many_to_choose = models.CharField(max_length=100, choices=FK__choices2, verbose_name='many_to_choose', default=None,
                                      blank=False)
    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices'
        ordering = ['id']
        db_table = 'EvaluateChoices'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices2(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices2')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices2'
        ordering = ['id']
        db_table = 'EvaluateChoices2'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices3(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices3')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    # created = models.DateTimeField(auto_now_add=True)
    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices3'
        ordering = ['id']
        db_table = 'EvaluateChoices3'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices4(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices4')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    liked_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='liked_news4',
                                  default=None,
                                  blank=False
                                  )
    trust_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='trust_news4',
                                  default=None,
                                  blank=False
                                  )
    fit_preference = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='fit_preference4',
                                      default=None,
                                      blank=False
                                      )

    recommend_news = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='recommend_news4',
                                      default=None,
                                      blank=False
                                      )

    # created = models.DateTimeField(auto_now_add=True)
    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices4'
        ordering = ['id']
        db_table = 'EvaluateChoices4'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices5(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices5')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    liked_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='liked_news5',
                                  default=None,
                                  blank=False
                                  )
    trust_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='trust_news5',
                                  default=None,
                                  blank=False
                                  )
    fit_preference = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='fit_preference5',
                                      default=None,
                                      blank=False
                                      )
    # know_many = models.CharField(max_length=100,
    # choices=FK__choices,
    # verbose_name='know_many',
    # default=None,
    # blank=False
    # )
    recommend_news = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='recommend_news5',
                                      default=None,
                                      blank=False
                                      )

    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices5'
        ordering = ['id']
        db_table = 'EvaluateChoices5'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices6(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices6')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    liked_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='liked_news6',
                                  default=None,
                                  blank=False
                                  )
    trust_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='trust_news6',
                                  default=None,
                                  blank=False
                                  )
    fit_preference = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='fit_preference6',
                                      default=None,
                                      blank=False
                                      )

    recommend_news = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='recommend_news6',
                                      default=None,
                                      blank=False
                                      )

    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices6'
        ordering = ['id']
        db_table = 'EvaluateChoices6'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices7(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices7')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    liked_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='liked_news7',
                                  default=None,
                                  blank=False
                                  )
    trust_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='trust_news7',
                                  default=None,
                                  blank=False
                                  )
    fit_preference = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='fit_preference7',
                                      default=None,
                                      blank=False
                                      )

    recommend_news = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='recommend_news7',
                                      default=None,
                                      blank=False
                                      )

    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices7'
        ordering = ['id']
        db_table = 'EvaluateChoices7'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices8(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices8')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    liked_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='liked_news8',
                                  default=None,
                                  blank=False
                                  )
    trust_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='trust_news8',
                                  default=None,
                                  blank=False
                                  )
    fit_preference = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='fit_preference8',
                                      default=None,
                                      blank=False
                                      )

    recommend_news = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='recommend_news8',
                                      default=None,
                                      blank=False
                                      )

    # --- choice difficulty-------

    many_to_choose = models.CharField(max_length=100,
                                      choices=FK__choices2,
                                      verbose_name='many_to_choose',
                                      default=None,
                                      blank=False
                                      )

    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices8'
        ordering = ['id']
        db_table = 'EvaluateChoices8'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices9(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices9')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    liked_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='liked_news9',
                                  default=None,
                                  blank=False
                                  )
    trust_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='trust_news9',
                                  default=None,
                                  blank=False
                                  )
    fit_preference = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='fit_preference9',
                                      default=None,
                                      blank=False
                                      )

    recommend_news = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='recommend_news9',
                                      default=None,
                                      blank=False
                                      )

    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices9'
        ordering = ['id']
        db_table = 'EvaluateChoices9'

    def __str__(self):
        return "{}".format(self.id)


class EvaluateChoices10(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='EvaluateChoices10')

    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    liked_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='liked_news10',
                                  default=None,
                                  blank=False
                                  )
    trust_news = models.CharField(max_length=100,
                                  choices=FK__choices,
                                  verbose_name='trust_news10',
                                  default=None,
                                  blank=False
                                  )
    fit_preference = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='fit_preference10',
                                      default=None,
                                      blank=False
                                      )

    recommend_news = models.CharField(max_length=100,
                                      choices=FK__choices,
                                      verbose_name='recommend_news10',
                                      default=None,
                                      blank=False
                                      )

    created = models.CharField(max_length=1000, blank=False, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)

    class Meta:
        verbose_name = 'EvaluateChoices10'
        ordering = ['id']
        db_table = 'EvaluateChoices10'

    def __str__(self):
        return "{}".format(self.id)
