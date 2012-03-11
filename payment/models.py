#-*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import datetime

ACCOUNT_TYPE={'free':u'免费账户','bronze':u'付费订阅(bronze)','silver':u'付费订阅(silver)','gold':u'付费订阅(gold)'}

class Bill (models.Model):
  user = models.OneToOneField (User)
  account_type = models.CharField (max_length=20, default='free', null=True)
  upgrade_type = models.CharField (max_length=20, default='free', null=True)

  # It'll be one of the 4 status ('WAIT_BUYER_PAY', 'WAIT_SELLER_SEND_GOODS',
  # 'WAIT_BUYER_CONFIRM_GOODS', 'TRADE_FINISHED', 'TRADE_CLOSED'), the inital
  # status will be 'INIT'.
  trade_status = models.CharField (max_length=50, default='INIT', null=True)
  start_date = models.DateTimeField (default=datetime.datetime(1900,1,1))
  expire_date = models.DateTimeField (default=datetime.datetime(1900,1,1))

  def __unicode__ (self):
    return self.user.username+" "+self.account_type
admin.site.register (Bill)
