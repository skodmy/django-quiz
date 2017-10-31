from django.db import models
from django.conf import settings
from datetime import time


SUBJECT_MODEL = getattr(settings, 'TESTS_SUBJECT_MODEL', None.__class__)

if SUBJECT_MODEL is None:
    class Subject(models.Model):
        name = models.CharField(max_length=100)
        description = models.TextField(blank=True)

        def __str__(self):
            return self.name
    SUBJECT_MODEL = Subject
elif isinstance(SUBJECT_MODEL, str):
    from importlib import import_module
    app_label, model_cls_name = SUBJECT_MODEL.split('.')
    SUBJECT_MODEL = getattr(import_module('{}.models'.format(app_label)), model_cls_name)

setattr(SUBJECT_MODEL, 'tests', property(lambda self: Test.objects.filter(subject=self)))


class BaseConstraint(models.Model):
    max_value = None

    class Meta:
        abstract = True


class TimeConstraint(BaseConstraint):
    max_value = models.TimeField(default=time(0))

    def __str__(self):
        return 'infinite' if self.max_value == time(0) else str(self.max_value)


class MarkConstraint(BaseConstraint):
    max_value = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.max_value)


class AttemptsConstraint(BaseConstraint):
    max_value = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return 'times: {}'.format(str(self.max_value))


class Test(models.Model):
    title = models.CharField(max_length=140)
    subject = models.ForeignKey(SUBJECT_MODEL)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    time_constraint = models.ForeignKey(TimeConstraint)
    mark_constraint = models.ForeignKey(MarkConstraint)
    attempts_constraint = models.ForeignKey(AttemptsConstraint)

    @property
    def questions(self):
        return Question.objects.filter(test=self)

    @property
    def question_price(self):
        questions_count = self.questions.count()
        if questions_count == 0:
            return 0.0
        return self.mark_constraint.max_value / questions_count

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test)
    text = models.CharField(max_length=150)

    @property
    def answers(self):
        return Answer.objects.filter(question=self)

    @property
    def correct_answers(self):
        return self.answers.filter(correct=True)

    @property
    def incorrect_answers(self):
        return self.answers.exclude(correct=True)

    @property
    def price(self):
        questions_count = self.test.questions.count()
        if questions_count == 0:
            return 0.0
        return self.test.mark_constraint.max_value / questions_count

    def __str__(self):
        return "{}?".format(self.text)


class Answer(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=100)
    correct = models.BooleanField(default=False)

    @property
    def price(self):
        if self.correct:
            return self.question.price / self.question.correct_answers.count()
        return 0.0

    def __str__(self):
        return self.text


class UserTestBase(models.Model):
    test = models.OneToOneField(Test)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    class Meta:
        abstract = True


class UserTestResult(UserTestBase):
    mark = models.FloatField(default=0.0)
    elapsed_time = models.TimeField()
    mistakes_number = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return 'test: {}, user: {}, mark: {}'.format(self.test.title, self.user.username, str(self.mark))


class UserTestAttemptsCredit(UserTestBase):
    value = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return '{} has {} for {}'.format(self.user.username, str(self.value), self.test.title)
