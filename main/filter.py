from main import *

@app.template_filter("formatdatetime")
def format_datetime(value):
    if value is None:
        return ""
    else:
        pubdate = datetime.fromtimestamp((int(value)+9*60*60*1000)/1000)
        return pubdate.strftime("%Y-%m-%d %H:%M:%S")


