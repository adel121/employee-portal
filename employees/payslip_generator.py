from .models import *
from django.db.models import Q
from io import BytesIO, StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from datetime import date
from .constants import *

class PayslipGenerator:
    def __init__(self, employee, from_date, to_date, mark_as_paid=False):
        self.employee = employee
        self.from_date = from_date
        self.to_date = to_date
        self.mark_as_paid = mark_as_paid
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

        if self.mark_as_paid:
            workslots = workslots.filter(is_paid = False)
            for workslot in workslots:
                workslot.is_paid = True
                workslot.payment_date = date.today()
        return workslots

    def __get_template_context(self):
        total_amount = Decimal(0)
        total_paid = Decimal(0)
        total_pending = Decimal(0)
        for workslot in self.workslots:
            if workslot.is_paid:
                total_paid += workslot.amount
            else:
                total_pending += workslot.amount
            
        total_amount = total_pending + total_paid

        return {
            "employee": self.employee,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "workslots": self.workslots,
            "total_amount": total_amount,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "extraction_mode": PROOF_OF_PAYMENT if self.mark_as_paid else READONLY,
            "page_size": "A4",
        }

    def __create_payslip_pdf(self):
        template = get_template("employees/payslips/payslip_template.html")
        html = template.render(self.__get_template_context())
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            result = HttpResponse(result.getvalue(), content_type="application/pdf")
            WorkSlot.objects.bulk_update(self.workslots, ["is_paid", "payment_date"], batch_size=1000,)
            return result
        return HttpResponse("We had some errors<pre>%s</pre>" % html)
