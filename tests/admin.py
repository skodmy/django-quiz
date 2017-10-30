from django.contrib import admin
from .models import SUBJECT_MODEL, TimeConstraint, MarkConstraint, Test, Question, Answer

if not admin.site.is_registered(SUBJECT_MODEL):
    admin.site.register(SUBJECT_MODEL)

admin.site.register(TimeConstraint)
admin.site.register(MarkConstraint)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
