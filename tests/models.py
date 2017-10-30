from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import time
from inspect import isclass


SUBJECT_MODEL = getattr(settings, 'SUBJECT_MODEL', None.__class__)
SUBJECT_MODEL = SUBJECT_MODEL if isclass(SUBJECT_MODEL) else getattr(SUBJECT_MODEL, '__class__', None.__class__)
if not issubclass(SUBJECT_MODEL, models.Model) or getattr(getattr(SUBJECT_MODEL, 'Meta', None), 'abstract', False):
    class Subject(models.Model):
        name = models.CharField(max_length=100)
        description = models.TextField(blank=True)

        def __str__(self):
            return self.name
    SUBJECT_MODEL = Subject
setattr(SUBJECT_MODEL, 'tests', property(lambda self: Test.objects.filter(subject=self)))


class TimeConstraint(models.Model):
    value = models.TimeField(default=time(0))

    def __str__(self):
        return 'infinite' if self.value == time(0) else str(self.value)


class MarkConstraint(models.Model):
    max_value = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.max_value)


class Test(models.Model):
    title = models.CharField(max_length=140)
    subject = models.ForeignKey(SUBJECT_MODEL)
    users = models.ManyToManyField(User)
    time_constraint = models.ForeignKey(TimeConstraint)

    @property
    def questions(self):
        return Question.objects.filter(test=self)

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test)
    text = models.CharField(max_length=150)

    @property
    def answers(self):
        return Answer.objects.filter(question=self)

    def __str__(self):
        return "{}?".format(self.text)


class Answer(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=100)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
