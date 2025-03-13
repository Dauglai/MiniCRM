import openpyxl
from openpyxl.styles import Font
from openpyxl.chart import BarChart, Reference
from django.http import HttpResponse
from .models import Profile, Order, Task, Result
from django.utils.timezone import now

from .views import User


def generate_individual_report(profile_id):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Аналитика сотрудника"

    user = User.objects.get(id=profile_id)
    profile = Profile.objects.get(author=user)

    headers = [
        "ФИО", "Кол-во заказов", "Средний чек", "Задач вовремя", "Просроченные задачи",
        "Среднее время выполнения", "% Вовремя", "% Просроченных", "Средний рейтинг"
    ]
    sheet.append(headers)

    for col in range(1, len(headers) + 1):
        sheet.cell(row=1, column=col).font = Font(bold=True)

    total_orders = Order.objects.filter(outlet__outletInfo__profile=profile).count()
    completed_tasks = Result.objects.filter(author=profile, is_end=True)
    overdue_tasks = Task.objects.filter(addressee=profile, status="Завершена", deadline__lt=now().date()).count()
    avg_completion_time = (
        sum((res.task.deadline - res.task.datetime.date()).days for res in completed_tasks)
        / completed_tasks.count()
        if completed_tasks.count() > 0 else 0
    )
    completed_on_time = completed_tasks.count() - overdue_tasks
    percent_on_time = (completed_on_time / completed_tasks.count()) * 100 if completed_tasks.count() else 0
    percent_overdue = (overdue_tasks / completed_tasks.count()) * 100 if completed_tasks.count() else 0

    row = [
        f"{profile.surname} {profile.name}", total_orders, 0,  # Добавить расчет среднего чека
        completed_on_time, overdue_tasks, round(avg_completion_time, 1),
        round(percent_on_time, 1), round(percent_overdue, 1), "-"
    ]
    sheet.append(row)

    # Добавляем график
    chart = BarChart()
    chart.title = "Задачи вовремя и просроченные"
    chart.x_axis.title = "Метрики"
    chart.y_axis.title = "Количество"

    labels = Reference(sheet, min_col=4, min_row=1, max_col=5, max_row=2)
    values = Reference(sheet, min_col=4, min_row=2, max_col=5, max_row=2)

    chart.add_data(values, titles_from_data=True)
    chart.set_categories(labels)
    sheet.add_chart(chart, "H4")

    return workbook

def download_employee_report(request, author_id):
    workbook = generate_individual_report(author_id)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="employee_{author_id}_report.xlsx"'
    workbook.save(response)
    return response
