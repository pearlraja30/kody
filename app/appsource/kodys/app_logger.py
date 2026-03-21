# -*- coding: utf-8 -*-

import sys

def _fn():
    '''
    returns current function name
    '''
    func_name = sys._getframe(1).f_code.co_name
    return func_name

def _setmsg(success_msg,error_msg, flag):
    '''construct and return success or error messages based on the flag
        success_msg : success message
        error_msg : error message
        flag : result flag
    '''
    msg=''
    if flag:
        msg = success_msg
    else:
        msg = error_msg
    return flag, msg

def get_template_name(request, template_name, options=dict()):
    '''
        return function with .html
    '''
    if request.resolver_match.app_names:
        tn= request.resolver_match.app_names[-1]+"/"+template_name+'.html'
    else:
        tn= template_name+'.html'

    if 'common_template' in options and options['common_template']:
        tn= template_name+'.html'

    return tn

def start_log(request, fn):
    '''
        print current function loading msg
    '''
    log_msg = "{0} method is loading....".format(fn)
    return log_msg

def end_log(request, fn):
    '''
        print current function loading done msg
    '''
    log_msg = "{0} method is loading done....".format(fn)
    return log_msg

def mask_pii(msg):
    '''
    mask sensitive patient information in logs
    '''
    sensitive_patterns = ['"NAME":', '"MOBILE":', '"DOB":', '"EMAIL":', '"NAME"', '"MOBILE"']
    masked_msg = str(msg)
    for pattern in sensitive_patterns:
        if pattern in masked_msg:
            masked_msg = masked_msg.replace(pattern, pattern + ' "CONFIDENTIAL"')
    return masked_msg

def error_log(request, line_no, exp):
    '''
        print error message with line number
    '''
    exp = mask_pii(exp)
    err_msg = 'Error at %s:%s' %(line_no,exp)
    return err_msg

def internal_log(request, msg):
    '''
        print developer logs
    '''
    msg = mask_pii(msg)
    if request and hasattr(request, 'resolver_match') and request.resolver_match:
        internal_msg = "{0} {1}".format(request.resolver_match.app_name, msg)
    else:
        internal_msg = "{0}".format(msg)
    return internal_msg

def warning_log(request, msg):
    '''
        print warning logs
    '''
    warning_msg = "{0}".format(msg)
    return warning_msg
