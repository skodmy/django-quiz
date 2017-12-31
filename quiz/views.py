from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from datetime import time, datetime
from .models import Test, UserTestResult, Answer


class TestListView(LoginRequiredMixin, ListView):
    model = Test
    context_object_name = 'tests'
    template_name = 'quiz/list.html'

    def get_queryset(self):
        return self.model.objects.filter(users__in=(self.request.user, ))


class TestDetailView(LoginRequiredMixin, DetailView):
    model = Test
    pk_url_kwarg = 'test_pk'
    template_name = 'quiz/test/detail.html'


class PassTestView(TestDetailView):
    template_name = 'quiz/test/pass.html'

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
    template_name = 'quiz/test/result.html'


@login_required
def examine(request, test_pk):
    """
    Examines user's test "paper".

    :param request: a HTTPRequest object.
    :param test_pk: a primary key of corresponding Test object.
    :return:
    """
    # querying needed test object from database by the given primary key 'test_pk'
    test = Test.objects.get(pk=test_pk)
    # constructing questions correct answers mapping using dictionary
    questions_correct_answers = {question.pk: question.correct_answers for question in test.questions}
    # creating a copy of sent data for possibility of clean up
    request_data = request.POST.copy()
    # removing 'csrfmiddlewaretoken' from copy of sent data due to that it's unnecessary
    request_data.pop('csrfmiddlewaretoken')
    # extracting end time
    end_time = datetime.strptime(request_data.pop('end_time')[0], '%H:%M:%S').time()
    now_time = datetime.now().time()
    if now_time > end_time:
        return render(request, 'quiz/test/fail.html')

    mark = 0.0
    for user_answer, user_answer_value in request_data.items():
        question_pk, answer_pk = user_answer.split('a')
        question_pk = question_pk.replace('q', '')
        answer = Answer.objects.get(pk=int(answer_pk))
        if answer in questions_correct_answers[int(question_pk)]:
            mark += answer.price

    return render(
        request,
        'quiz/test/result.html',
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
