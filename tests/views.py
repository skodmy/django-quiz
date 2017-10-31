from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from datetime import time, datetime
from .models import Test, UserTestResult, Answer


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
        now_time = datetime.now().time()
        context['end_time'] = str(
            time(
                context['test'].time_constraint.max_value.hour + now_time.hour + 1,
                (context['test'].time_constraint.max_value.minute + now_time.minute) // 60,
            ),
        )
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
    end_time = datetime.strptime(request_data.pop('end_time')[0], '%H:%M:%S').time()
    now_time = datetime.now().time()
    if now_time > end_time:
        return render(request, 'tests/test/fail.html')

    request_data.pop('csrfmiddlewaretoken')
    for user_answer, user_answer_value in request_data.items():
        question_pk, answer_pk = user_answer.split('a')
        question_pk = question_pk.replace('q', '')
        answer = Answer.objects.get(pk=int(answer_pk))
        if answer in questions_correct_answers[int(question_pk)]:
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
                    abs(now_time.hour - (end_time.hour - test.time_constraint.max_value.hour)) // 24,
                    abs(now_time.minute - (end_time.minute - test.time_constraint.max_value.minute)) // 60,
                    abs(now_time.second - (end_time.second - test.time_constraint.max_value.second)) // 60,
                ),
                mistakes_number=0
            ),
        }
    )
