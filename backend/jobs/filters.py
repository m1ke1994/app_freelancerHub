from django.db.models import Q, Case, When, F, Value, IntegerField
from django_filters import rest_framework as filters
from .models import Job

class JobFilter(filters.FilterSet):
    q = filters.CharFilter(method="filter_q")
    category = filters.CharFilter(field_name="category", lookup_expr="iexact")
    remote = filters.BooleanFilter()
    urgent = filters.BooleanFilter()
    budget_min = filters.NumberFilter(method="filter_budget_min")
    budget_max = filters.NumberFilter(method="filter_budget_max")

    # Аннотируем «универсальный» интервал бюджета:
    # для fixed: bmin=bmax=budget_fixed; для range: как есть
    def _with_budget_bounds(self, qs):
        return qs.annotate(
            bmin=Case(
                When(budget_type=Job.BudgetType.FIXED, then=F("budget_fixed")),
                default=F("budget_min"),
                output_field=IntegerField(),
            ),
            bmax=Case(
                When(budget_type=Job.BudgetType.FIXED, then=F("budget_fixed")),
                default=F("budget_max"),
                output_field=IntegerField(),
            ),
            # плейсхолдер, пока нет модели откликов
            responses_count_annot=Value(0, output_field=IntegerField()),
        )

    def filter_q(self, qs, name, value):
        if not value:
            return qs
        return qs.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )

    # Пересечение диапазонов: job.bmax >= ui_min
    def filter_budget_min(self, qs, name, value):
        if value in (None, ""):
            return qs
        return self._with_budget_bounds(qs).filter(bmax__gte=value)

    # Пересечение диапазонов: job.bmin <= ui_max
    def filter_budget_max(self, qs, name, value):
        if value in (None, ""):
            return qs
        return self._with_budget_bounds(qs).filter(bmin__lte=value)

    class Meta:
        model = Job
        fields = ["category", "remote", "urgent"]
