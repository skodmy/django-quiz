from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from datetime import time, datetime
from .models import Test, UserTestResult, Question, Answer


class TestListView(LoginRequiredMixin, ListView):
    model = Test
    context_object_name = 'tests'
    template_name = 'tests/list.html'

    def get_queryset(self):
        return self.model.objects.filter(users__in=(self.request.user, ))


class TestDetailView(LoginRequiredMixin, DetailView):
    model = Test
    pk_url_kwarg = 'test_pk'
    template_name = 'tests/test/detail.html'


class PassTestView(TestDetailView):
    template_name = 'tests/test/pass.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['end_time'] = datetime.strftime(context['test'].time_constraint.value + datetime.now().time(), '%H:%M')
        return context


class TestResultDetailView(LoginRequiredMixin, DetailView):
    model = UserTestResult
    pk_url_kwarg = 'test_result_pk'
    context_object_name = 'test_result'
    template_name = 'tests/test/result.html'


def examine(request, test_pk):
    test = Test.objects.get(pk=test_pk)
    questions_correct_answers = {question.pk: question.correct_answers for question in test.questions}
    mark = 0.0
    request_data = request.POST.copy()
    end_time = datetime.strptime(request_data.pop('end_time'), '%H:%M').time()
    now_time = datetime.now().time()
    if now_time > end_time:
        return render(request, 'tests/test/fail.html')

    for user_answer, user_answer_value in request_data:
        question_pk, answer_pk = user_answer.split('a')
        question_pk.replace('q', '')
        answer = Answer.objects.get(pk=answer_pk)
        if answer in questions_correct_answers[question_pk]:
            mark += answer.price

    return render(
        request,
        'tests/test/result.html',
        {
            'test_result': UserTestResult.objects.create(
                test=test,
                user=request.user,
                mark=mark,
                elapsed_time=time(
                    now_time.hour - (end_time.hour - test.time_constraint.value.hour),
                    now_time.minute - (end_time.minute - test.time_constraint.value.minute),
                    now_time.second - (end_time.second - test.time_constraint.value.second),
                ),
                mistakes_number=0
            ),
        }
    )
