from .models import *
from django.db.models import Q
from io import BytesIO, StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


class PayslipGenerator:
    def __init__(self, employee, from_date, to_date):
        self.employee = employee
        self.from_date = from_date
        self.to_date = to_date
        self.workslots = []

    def generate_payslip(self):
        self.workslots = self.__get_included_workslots()
        return self.__create_payslip_pdf()

    def __get_included_workslots(self):
        workslots = WorkSlot.objects.filter(
            Q(employee=self.employee)
            & Q(date__gte=self.from_date)
            & Q(date__lte=self.to_date)
        ).order_by("date")
        return workslots

    def __get_template_context(self):
        total_amount = Decimal(0)
        for workslot in self.workslots:
            total_amount += workslot.amount

        return {
            "employee": self.employee,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "workslots": self.workslots,
            "total_amount": total_amount,
            "page_size": "A4",
        }

    def __create_payslip_pdf(self):
        template = get_template("employees/payslips/payslip_template.html")
        html = template.render(self.__get_template_context())
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type="application/pdf")
        return HttpResponse("We had some errors<pre>%s</pre>" % html)
