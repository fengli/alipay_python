介绍
============

alipay_python 是支付宝接口的python版本，提供了担保交易，即时到帐和自动发货的接口。

fork自这个版本 `alipay <https://github.com/yefei/python-alipay>`_. 增加了担保交易，确认发货和简单的测试站点(django)。如果你在你的站点中使用了这个接口，可以考虑告诉我们 ( okidogiii@gmail.com )。

使用
---------
* 下载解压到python_alipay目录
* 修改alipay/config.py配置文件，根据你的支付宝帐号进行相应的设置
* python manage.py syncdb
* python manage.py runserver

组成
----------

* alipay/: 包含了支付宝的即时到帐，担保交易和确认发货的接口
* payment/：你的站点订单系统调用接口的简单例子
* accounts/：用户登录

接口描述 (alipay/alipay.py)
---------

提供了即时到帐，担保交易和确认发货的接口。

* 即时到帐

  def create_direct_pay_by_user(tn, subject, body, total_fee)

  tn - 'out_trade_no', 应该是你的网站订单系统中唯一订单匹配号
  subject - 'subject', 你的订单名称
  body - 'body', 订单描述
  total_fee - 'total_fee', 订单的总金额

  返回应该跳转的支付宝链接

* 担保交易

  def create_partner_trade_by_buyer (tn, subject, body, price)

  tn - 'out_trade_no', 应该是你的网站订单系统中唯一订单匹配号
  subject - 'subject', 你的订单名称
  body - 'body', 订单描述
  price - 'price', 商品单价

  返回应该跳转的支付宝链接

  note: 物流的类型等的设置在接口內默认设置，如果你需要每次修改可以扩展这个接口。

* 确认发货

  def send_goods_confirm_by_platform (tn)

  tn - 'trade_no', 注意这个不是你站点的唯一订单号，而是支付宝返回的在支付宝系统内唯一的订单号。

  返回确认发货应该跳转的链接。

测试接口 (payment/views.py)
------------------

* notify_url_handler (request): 支付宝异步通知的接口。验证并且根据交易状态更新订单。如果用户已经付款等待发货，调用确认发货接口。对应的ALIPAY_NOTIFY_URL设置应该是http://your_domain_name/notify_url

* return_url_handler (request): 支付宝同步通知的接口。验证并且根据交易状态更新订单。如果用户已经付款等待发货，调用确认发货接口。对应的ALIPAY_RETURN_URL设置应该是http://your_domain_name/return_url

* upgrade_account (request, acc_type): 根据升级账户的类别ACC_TYPE创建账单。并且跳转至支付宝的付款接口(担保交易)。

Bring to you by
--------------------

* `ikindle杂志订阅 <http://ikindle.mobi>`_:每天推送新鲜的报纸和杂志到你的Kindle.
* `ikindle万卷书 <http://ikindle.mobi/book>`_: mobi格式和6寸pdf的图书共享站点，可以下载或者直接推送到你的Kindle。
