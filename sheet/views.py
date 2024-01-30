from django.shortcuts import render, redirect
from django.http import JsonResponse
from .service import get_sample_lib_list, CustomSampleLibSerializer
from samplelib.models import SampleLib
from django.http import HttpResponse
import csv
from django.contrib import messages


def filter_sheet(request):
    result = get_sample_lib_list(request)
    # print("result"*100, result)
    return JsonResponse(result)


def get_sheet(request):
    return render(request,"sheet_list.html",locals())


def create_csv_sheet(request):
    try:
        serializer = CustomSampleLibSerializer(SampleLib.objects.all(), many=True)
        result = dict()
        result['data'] = serializer.data
        class Report(object):
            no = 0
            patient = ""
            sample_lib = ""
            barcode = ""
            na_type = ""
            area_type = ""
            volume = 0
            conc = 0
            matching_normal_sl = ""

        res = []

        def get_matching(value):
            if value:
                return ", ".join([i["name"] for i in value])
            return

        for index, row in enumerate(result['data']):
            report = Report()
            report.no = index+1
            report.patient = row['patient']
            report.sample_lib = row['name']
            report.barcode = row['barcode']
            report.na_type = row['na_type']
            report.area_type = ", ".join(row['area_type'])
            report.volume = row['shear_volume']
            report.conc = row['qpcr_conc']
            report.matching_normal_sl = get_matching(row['matching_normal_sl'])
            res.append(report)


        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="sequencinglib.csv"'},
        )

        field_names = ["no","patient","sample_lib","barcode","na_type","area_type","volume","conc","matching_normal_sl"]
        writer = csv.writer(response)
        writer.writerow(field_names)
        for item in res:
            writer.writerow([getattr(item, field) for field in field_names])

        return response
    except Exception as e:
        print(e)
        # messages.error(request, "Sample Library could not be created.")
        return JsonResponse({'error': str(e)}, status=500)
