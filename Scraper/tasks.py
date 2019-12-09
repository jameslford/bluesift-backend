from celery import shared_task
from celery.utils.log import get_task_logger
from config.celery import app
from .models import ScraperDepartment, ScraperSubgroup


@app.task
def subgroup_clean(pk: int):
    subgroup: ScraperSubgroup = ScraperSubgroup.objects.filter(pk=pk).first()
    if subgroup:
        subgroup.stock_clean()
        return str(subgroup) + ' cleaned'
    else:
        return f'no subgroup for pk {str(pk)}'

@app.task
def subgroup_scrape(pk: int):
    subgroup: ScraperSubgroup = ScraperSubgroup.objects.using('scraper_default').filter(pk=pk).first()
    if subgroup:
        subgroup.scrape()
        return str(subgroup) + ' scraped'
    else:
        return f'no subgroup for pk {str(pk)}'

@app.task
def department_scrape(pk: int):
    department: ScraperDepartment = ScraperDepartment.objects.filter(pk=pk).first()
    if department:
        department.scrape_all()
        return str(department) + ' scraped'
    else:
        return f'no department for pk {str(pk)}'

@app.task
def department_clean(pk: int):
    department: ScraperDepartment = ScraperDepartment.objects.filter(pk=pk).first()
    if department:
        department.clean_all()
        return str(department) + ' cleaned'
    else:
        return f'no department for pk {str(pk)}'









