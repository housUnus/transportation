from django.http import HttpResponse
from django.http import response
from django.http.response import HttpResponseServerError, JsonResponse
from django.shortcuts import redirect, render

# Create your views here.
from django.views import View
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import time

from .main import Solver
import json
import numpy as np

from common.utils.utils import generate_pdf

template_name = "solver"
app_name = "solver"


class MainIndexView(View):
    template_name += "/index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
# ---------------------------------------------------------------------


def help_trans(data, method):
    print(method)
    data = np.array(data)
    data = data.astype(int)
    print(data)
    supply = data[0:-1, -1].tolist()
    demande = data[-1, 0:-1].tolist()
    costs = data[0:-1, 0:-1].tolist()
    print(supply, demande, costs)
    # try:
    sl = Solver(supply, demande, costs)
    sl.solve(method=method)
    sl.results()
    result = sl.paths
    # except:
    # result = None
    return result


def renderpdf(request):
    pdf_response = generate_pdf("solver/pdf.html", {})
    return pdf_response


class solve(View):
    def post(self, request, *args, **kwargs):
        # print('Raw Data: "%s"' % request.body)
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        data = body['data']
        method = int(body['method'])
        print(body['data'])
        result = help_trans(data, method)
        print(result)
        time.sleep(2)
        if result is None:
            return HttpResponse('Data entred not valid')
        json_str = json.dumps(result)

        return JsonResponse(json_str, safe=False)

    def get(self, request, *args, **kwargs):
        # received_json_data = JsonResponse.loads(request.POST['data'])
        print('Raw Data: "%s"' % request.body)
        print('hello')
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body['data'])
        return HttpResponse('success')
# ---------------------------------------------------------------------
