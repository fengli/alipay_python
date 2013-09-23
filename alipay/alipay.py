# -*- coding: utf-8 -*-
'''
Created on 2011-4-21
支付宝接口
@author: Yefe
'''
import types
from urllib import urlencode, urlopen
from hashcompat import md5_constructor as md5
from config import settings

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

# 网关地址
_GATEWAY = 'https://mapi.alipay.com/gateway.do?'


# 对数组排序并除去数组中的空值和签名参数
# 返回数组和链接串
def params_filter(params):
    ks = params.keys()
    ks.sort()
    newparams = {}
    prestr = ''
    for k in ks:
        v = params[k]
        k = smart_str(k, settings.ALIPAY_INPUT_CHARSET)
        if k not in ('sign','sign_type') and v != '':
            newparams[k] = smart_str(v, settings.ALIPAY_INPUT_CHARSET)
            prestr += '%s=%s&' % (k, newparams[k])
    prestr = prestr[:-1]
    return newparams, prestr


# 生成签名结果
def build_mysign(prestr, key, sign_type = 'MD5'):
    if sign_type == 'MD5':
        return md5(prestr + key).hexdigest()
    return ''


# 即时到账交易接口
def create_direct_pay_by_user(tn, subject, body, total_fee):
    params = {}
    params['service']       = 'create_direct_pay_by_user'
    params['payment_type']  = '1'
    
    # 获取配置文件
    params['partner']           = settings.ALIPAY_PARTNER
    params['seller_email']      = settings.ALIPAY_SELLER_EMAIL
    params['return_url']        = settings.ALIPAY_RETURN_URL
    params['notify_url']        = settings.ALIPAY_NOTIFY_URL
    params['_input_charset']    = settings.ALIPAY_INPUT_CHARSET
    params['show_url']          = settings.ALIPAY_SHOW_URL
    
    # 从订单数据中动态获取到的必填参数
    params['out_trade_no']  = tn        # 请与贵网站订单系统中的唯一订单号匹配
    params['subject']       = subject   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    params['body']          = body      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
    params['total_fee']     = total_fee # 订单总金额，显示在支付宝收银台里的“应付总额”里
    
    # 扩展功能参数——网银提前
    params['paymethod'] = 'directPay'   # 默认支付方式，四个值可选：bankPay(网银); cartoon(卡通); directPay(余额); CASH(网点支付)
    params['defaultbank'] = ''          # 默认网银代号，代号列表见http://club.alipay.com/read.php?tid=8681379
    
    # 扩展功能参数——防钓鱼
    params['anti_phishing_key'] = ''
    params['exter_invoke_ip'] = ''
    
    # 扩展功能参数——自定义参数
    params['buyer_email'] = ''
    params['extra_common_param'] = ''
    
    # 扩展功能参数——分润
    params['royalty_type'] = ''
    params['royalty_parameters'] = ''
    
    params,prestr = params_filter(params)
    
    params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    params['sign_type'] = settings.ALIPAY_SIGN_TYPE
    
    return _GATEWAY + urlencode(params)


# 纯担保交易接口
def create_partner_trade_by_buyer (tn, subject, body, price):
    params = {}
    # 基本参数
    params['service']       = 'create_partner_trade_by_buyer'
    params['partner']           = settings.ALIPAY_PARTNER
    params['_input_charset']    = settings.ALIPAY_INPUT_CHARSET
    params['notify_url']        = settings.ALIPAY_NOTIFY_URL
    params['return_url']        = settings.ALIPAY_RETURN_URL

    # 业务参数
    params['out_trade_no']  = tn        # 请与贵网站订单系统中的唯一订单号匹配
    params['subject']       = subject   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    params['payment_type']  = '1'
    params['logistics_type'] = 'POST'   # 第一组物流类型
    params['logistics_fee'] = '0.00'
    params['logistics_payment'] = 'BUYER_PAY'
    params['price'] = price             # 订单总金额，显示在支付宝收银台里的“应付总额”里
    params['quantity'] = 1              # 商品的数量
    params['seller_email']      = settings.ALIPAY_SELLER_EMAIL
    params['body']          = body      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
    params['show_url'] = settings.ALIPAY_SHOW_URL
    
    params,prestr = params_filter(params)
    
    params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    params['sign_type'] = settings.ALIPAY_SIGN_TYPE
    
    return _GATEWAY + urlencode(params)

# 确认发货接口
def send_goods_confirm_by_platform (tn):
    params = {}

    # 基本参数
    params['service']       = 'send_goods_confirm_by_platform'
    params['partner']           = settings.ALIPAY_PARTNER
    params['_input_charset']    = settings.ALIPAY_INPUT_CHARSET

    # 业务参数
    params['trade_no']  = tn
    params['logistics_name'] = u'银河列车'   # 物流公司名称
    params['transport_type'] = u'POST'
    
    params,prestr = params_filter(params)
    
    params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    params['sign_type'] = settings.ALIPAY_SIGN_TYPE
    
    return _GATEWAY + urlencode(params)

def notify_verify(post):
    # 初级验证--签名
    _,prestr = params_filter(post)
    mysign = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    if mysign != post.get('sign'):
        return False
    
    # 二级验证--查询支付宝服务器此条信息是否有效
    params = {}
    params['partner'] = settings.ALIPAY_PARTNER
    params['notify_id'] = post.get('notify_id')
    if settings.ALIPAY_TRANSPORT == 'https':
        params['service'] = 'notify_verify'
        gateway = 'https://mapi.alipay.com/gateway.do'
    else:
        gateway = 'http://notify.alipay.com/trade/notify_query.do'
    veryfy_result = urlopen(gateway, urlencode(params)).read()
    if veryfy_result.lower().strip() == 'true':
        return True
    return False

