#-*- coding:utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from alipay.alipay import *
from payment.models import Bill
from settings import LOGGING_PAYMENT
import datetime
import logging
import urllib

logger1 =logging.getLogger(__name__)
logger1.setLevel(logging.INFO)
logger1.addHandler (logging.FileHandler(LOGGING_PAYMENT))

def upgrade_bill (bill, valide_days):
  """
  Upgrade bill BILL valide for VALIDE_DAYS from today. And update
  bill account_type.
  """
  bill.account_type = bill.upgrade_type
  start_date = datetime.datetime.now()
  expire_date=start_date+datetime.timedelta(days=valide_days)
  bill.start_date=start_date
  bill.expire_date=expire_date
  bill.save()

@login_required
def upgrade_account (request, acc_type):
  """
  Request for upgrade account to acc_type. Redirect to alipay
  payment web page due to ACC_TYPE.
  """
  user = request.user
  bill = None
  try: bill = user.bill
  except: bill = Bill (user=user)
  bill.upgrade_type = acc_type
  bill.save()
  tn = bill.pk
  if acc_type == "bronze":
    url=create_partner_trade_by_buyer (tn, u'ikindle杂志订阅(4份)',
                                       u'订阅杂志到你的Kindle， 2.99x6个月', '0.01')
    return HttpResponseRedirect (url)
  elif acc_type == "silver":
    url=create_partner_trade_by_buyer (tn, u'ikindle杂志订阅(6份)',
                                       u'订阅杂志到你的Kindle，3.99x6个月', '0.01')
    return HttpResponseRedirect (url)
  elif acc_type == "gold":
    url=create_partner_trade_by_buyer (tn, u'ikindle杂志订阅(无限制)',
                                       u'订阅杂志到你的Kindle，5.99x6个月', '0.01')
    return HttpResponseRedirect (url)
  else:
    return HttpResponseRedirect (reverse ('payment_error'))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def notify_url_handler (request):
  """
  Handler for notify_url for asynchronous updating billing information.
  Logging the information.
  """
  logger1.info ('>>notify url handler start...')
  if request.method == 'POST':
    if notify_verify (request.POST):
      logger1.info ('pass verification...')
      tn = request.POST.get('out_trade_no')
      logger1.info('Change the status of bill %s'%tn)
      bill = Bill.objects.get (pk=tn)
      trade_status = request.POST.get('trade_status')
      logger1.info('the status of bill %s changed to %s'% (tn,trade_status))
      bill.trade_status = trade_status
      bill.save ()
      trade_no=request.POST.get('trade_no')
      if trade_status == 'WAIT_SELLER_SEND_GOODS':
        logger1.info ('It is WAIT_SELLER_SEND_GOODS, so upgrade bill')
        upgrade_bill (bill, 6*30+7)
        url = send_goods_confirm_by_platform (trade_no)
        logger1.info('send goods confirmation. %s'%url)        
        req=urllib.urlopen (url)
        return HttpResponse("success")
      else:
        logger1.info ('##info: Status of %s' % trade_status)
        return HttpResponse ("success")
  return HttpResponse ("fail")

def return_url_handler (request):
  """
  Handler for synchronous updating billing information.
  """
  logger1.info('>> return url handler start')
  if notify_verify (request.GET):
    tn = request.GET.get('out_trade_no')
    trade_no = request.GET.get('trade_no')
    logger1.info('Change the status of bill %s'%tn)
    bill = Bill.objects.get (pk=tn)
    trade_status = request.GET.get('trade_status')
    logger1.info('the status changed to %s'%trade_status)
    bill.trade_status = trade_status
    upgrade_bill (bill, 30*6+7)
    url=send_goods_confirm_by_platform (trade_no)
    req=urllib.urlopen (url)
    logger1.info('send goods confirmation. %s'%url)
    return HttpResponseRedirect (reverse ('payment_success'))
  return HttpResponseRedirect (reverse ('payment_error'))
