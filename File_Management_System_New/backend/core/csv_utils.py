import csv, os
from django.shortcuts import HttpResponse
from django.conf import settings
from dateutil.parser import parse


def generate_data_csv(csv_header, csv_rows, csv_file_name):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    writer = csv.writer(response)

    writer.writerow(csv_header)

    for row in csv_rows:
        writer.writerow(row)

    media_root = settings.MEDIA_ROOT
    file_dir = os.path.join(media_root, 'csv')  # Create a directory within the media directory
    os.makedirs(file_dir, exist_ok=True)  # Create the directory if it doesn't exist
    file_path = os.path.join(file_dir, csv_file_name)

    with open(file_path, 'w') as file:
        file.write(response.content.decode())

    return {
        'csv_path': '/media/csv/'+csv_file_name
    }




def format_datetime(date_object):
    try:
        if not date_object:
            return ''
        return parse(str(date_object)).strftime('%d %b %Y')
    except Exception:
        return date_object