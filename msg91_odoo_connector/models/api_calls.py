# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo import api, fields, models, tools, _
import time
import datetime
from odoo.tools.translate import _
import logging
#import urllib.parse as encode # Python URL functions
#import urllib.request as urllib2

import urllib.request
import urllib.parse

class ApiRequest(models.Model):
    _name='api.msg91'
    
    """ standard api request to msg91 API"""
    @api.multi
    

    def makecall(self,RequestData):
        print ("makecallmakecall",RequestData)
        sms_config_id=self.env['sms.config'].search([])
        print ("sms_config_idsms_config_idsms_config_id",sms_config_id)

        if sms_config_id:
            sms_details=sms_config_id.sms_config_details()
        authkey = sms_details.get('auth_key') # Your authentication key.

        mobiles = RequestData.get('mobile') # Multiple mobiles numbers separated by comma.

        message = RequestData.get('message') # Your message to send.

        sender = sms_details.get('senderid') # Sender ID,While using route4 sender id should be 6 characters long.

        route = sms_details.get('route') # Define route

        # Prepare you post parameters
        values = {
                  'authkey' : authkey,
                  'mobiles' : mobiles,
                  'message' : message,
                  'sender' : sender,
                  'route' : route
                  }

        print ("valuesvaluesvalues",values)
        url = sms_details.get('url') # API URL

        postdata = urllib.parse.urlencode(values) # URL encoding the data here.
        postdata = postdata.encode('utf-8') # data should be bytes

        print ("postdatapostdatapostdata",postdata)
        req = urllib.request.Request(url, postdata)
        resp = urllib.request.urlopen(req)
        print ("resprespresp",resp)
        respData = resp.read()


        print ("output------------------",respData) # Print Response
        
        self.env['sms.log'].create({ 'response_code':respData,
                            'partner_id':RequestData.get('partner_id'),
                            'model_id':RequestData.get('model_id'),
                            'message':message,
                            'model_name':RequestData.get('model_name')
                            })
        return True
    
    