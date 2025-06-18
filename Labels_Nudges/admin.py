from django.contrib import admin
from django.db.models.base import Model
from .models import *

# Register your models here.

import csv
from django.http import HttpResponse

from import_export.admin import ImportExportModelAdmin
from django import forms


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


def export_as_csv_action(description="Export selected objects as CSV file", fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

        # opts = modeladmin.model._meta
        # field_names = set([field.name for field in opts.fields])

        # if fields:
        #     fieldset = set(fields)
        #     field_names = field_names & fieldset

        # elif exclude:
        #     excludeset = set(exclude)
        #     field_names = field_names - excludeset

        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

        # writer = csv.writer(response)

        # if header:
        #     writer.writerow(list(field_names))
        # for obj in queryset:
        #     writer.writerow([str(getattr(obj, field)).encode("utf-8","replace") for field in field_names])

        # return response

    export_as_csv.short_description = description
    return export_as_csv


# @admin.register(Personal_info)
class Personal_infoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'prolific_username',
        'session_id',
        'created',
        'age',
        'gender',
        'country',
        'education',
        'phase_one_complete',
        'redemption_code_phase1',
        'phase_two_complete',
        'redemption_code_phase2',
        'clicked_articles_list',
    )
    list_filter = (
        'phase_one_complete',
        'phase_two_complete',
        'gender',
        'education',
        'country',
    )
    search_fields = (
        'prolific_username',
        'session_id',
        'id',
    )
    actions = [
        export_as_csv_action("Export selected as CSV")
    ]


class Topic_preferenceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'person',
        'session_id',
        'history'

    )
    actions = [export_as_csv_action("CSV Export")]


class ClimateNewsAdmin(ImportExportModelAdmin):
    list_display = ('id', 'article_url', 'title', 'author', 'type', 'category', 'subcategory', 'text'
                    , 'date', 'time', 'image_url', 'image_caption', 'author_bio', 'subtype')
    actions = [export_as_csv_action("CSV Export")]


class NewsRecAdmin(ImportExportModelAdmin):
    list_display = (
        'id', 'article_url', 'title', 'category', 'text', 'summary_neutral', 'summary_fearful', 'summary_fear_hope',
        'image')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'read_more', 'liked_news', 'trust_news', 'fit_preference', 'mood_fit',
                    'recommend_news', 'many_to_choose', 'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin2(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id',
                    'created')
    actions = [export_as_csv_action("CSV Export")]


# 'sys_time','unders_sys','many_actions',,'many_to_choose','easy_choice','choice_overwhelming','know_many','prepare_recipes'

class EvaluateChoicesAdmin3(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id',
                    'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin4(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'liked_news', 'trust_news', 'fit_preference',
                    'recommend_news', 'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin5(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'liked_news', 'trust_news', 'fit_preference',
                    'recommend_news', 'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin6(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'liked_news', 'trust_news', 'fit_preference',
                    'recommend_news', 'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin7(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'liked_news', 'trust_news', 'fit_preference',
                    'recommend_news', 'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin8(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'liked_news', 'trust_news', 'fit_preference',
                    'recommend_news', 'many_to_choose', 'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin9(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'liked_news', 'trust_news', 'fit_preference',
                    'recommend_news', 'created')
    actions = [export_as_csv_action("CSV Export")]


class EvaluateChoicesAdmin10(admin.ModelAdmin):
    list_display = ('id', 'person', 'session_id', 'liked_news', 'trust_news', 'fit_preference',
                    'recommend_news', 'created')
    actions = [export_as_csv_action("CSV Export")]


class RecommedationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'person', 'recommended_recipes', 'healthiness', 'created')
    actions = [export_as_csv_action("CSV Export")]


class Ghs_fkAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'person', 'FK_1', 'FK_2', 'FK_3', 'FK_4', 'FK_5', 'FK_6', 'FK_7', 'FK_8', 'FK_9', 'FK_10')
    actions = [export_as_csv_action("CSV Export")]


class Ghs_fkAdmin2(admin.ModelAdmin):
    list_display = (
        'person',
        'session_id',
        'iterations',
    )
    actions = [export_as_csv_action("CSV Export")]


class ArticleClickAdmin(admin.ModelAdmin):
    class ArticleClickAdmin(admin.ModelAdmin):
        list_display = (
            'person',
            'phase',
            'session_id',
            'article_ids',
            'cluster_ids',
            'titles',
            'sources',
            'clicked_at',
        )
        # You can filter on phase, session, date. JSONFields won’t work in list_filter.
        list_filter = (
            'phase',
            'session_id',
            'clicked_at',
        )
        # Search in your JSONFields as text, or remove entirely if it’s too noisy.
        search_fields = (
            'person__ids',
            'article_ids',
            'cluster_ids',
            'titles',
            'sources',
        )
        date_hierarchy = 'clicked_at'

admin.site.register(ArticleClick, ArticleClickAdmin)
admin.site.register(Topic_preference, Topic_preferenceAdmin)
admin.site.register(Ghs_fk, Ghs_fkAdmin)
admin.site.register(Ghs_fk2, Ghs_fkAdmin2)
admin.site.register(NewsRec, NewsRecAdmin)
admin.site.register(EvaluateChoices, EvaluateChoicesAdmin)
admin.site.register(EvaluateChoices2, EvaluateChoicesAdmin2)
admin.site.register(EvaluateChoices3, EvaluateChoicesAdmin3)
admin.site.register(EvaluateChoices4, EvaluateChoicesAdmin4)
admin.site.register(EvaluateChoices5, EvaluateChoicesAdmin5)
admin.site.register(EvaluateChoices6, EvaluateChoicesAdmin6)
admin.site.register(EvaluateChoices7, EvaluateChoicesAdmin7)
admin.site.register(EvaluateChoices8, EvaluateChoicesAdmin8)
admin.site.register(EvaluateChoices9, EvaluateChoicesAdmin9)
admin.site.register(EvaluateChoices10, EvaluateChoicesAdmin10)
admin.site.register(Personal_info, Personal_infoAdmin)
admin.site.register(Recommendations, RecommedationsAdmin)
admin.site.register(ClimateNews, ClimateNewsAdmin)

# https://personalizedrecipe2.herokuapp.com/
