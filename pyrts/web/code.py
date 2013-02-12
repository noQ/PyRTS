import sys
if not '/var/www' in sys.path:
    sys.path.append('/var/www')
    sys.path.append('/var/www/pyrts')

import base64
import random
import inspect
import json
import traceback
import web
import os
import urllib
import time
import smtplib
import hashlib
import mimetypes
from cgi import FieldStorage
from os.path import basename
from pyrts import *
import pyrts.web.rest as rest
from pyrts.settings import *
from pyrts.core.decorators.security import *
from pyrts.core.util import generate_random_name
from pyrts.core.params import *
from pyrts.core.restexception import RestException, ServerParametersNotFound, rest_error
from pyrts.core.util import inspect_clazz, get_clazz_methods, create_file
from pyrts.core.controller.pluginmonitor import *
from pyrts.core.controller.session import GameSession
from pyrts.web.urls import *

SUCCESS = 0
JSON_PROTOCOL_ERROR = 1
METHOD_NOT_DEFINED  = 2
REST_METHOD_ERROR = 3
JSON_INVALID = 4
HTTPS_NOT_USED = 5
SESSION_ID_INVALID = 6
PLUGIN_INVALID = 7
SESSION_ERROR = 8

''' inspect clazz and return methods '''
main_methods = get_clazz_methods(rest.REST)
main_methods_map = inspect_clazz(rest.REST)
main_restobj = rest.REST()


''' Load games plugin. store plugin class in memory '''
plugin_methods = {}
plugin_methods_map = {}
try:
    plugin_handler = PluginHandler(PLUGINS_PATH)
    plugin_handler.load_plugins()
    for game, game_module in LOADED_PLUGINS.items():
        plugin_methods[game] = get_clazz_methods(game_module.__class__)
        plugin_methods_map[game] = inspect_clazz(game_module.__class__)
except:
    traceback.print_exc()
    raise ServerException("Unable to load plugins")

global render
def get_render():
    return web.template.render(os.path.join(os.path.dirname(__file__), 'templates'))
render = get_render()

def get_remote_ip_address():
    ''' get web context and extract user IP address '''
    web_context = web.ctx
    if not web_context.has_key(PARAM_IP_ADDR):
        raise ServerException("Unable to extract node IP address ")
    return web_context[PARAM_IP_ADDR]

class index_handler:
    def GET(self):
        return render.index()


class rest_handler:
    def GET(self):
        web.header('Content-Type', MIME_HTML)
        return {"STATUS":"OK"}
    
    def POST(self):
        web.header('Content-Type', MIME_JSON)
        web_data = web.data()

        if PRODUCTION_ENV in RUN_MODE:
            if web.ctx.protocol != SECURE_HTTP:
                if DEBUG_LEVEL:
                    print "WARNING::Client tried to call rest methods in application using protocol '"+web.ctx.protocol+"'"
                return json.dumps({'e': HTTPS_NOT_USED, 'm':'Not using HTTPS'})


        ''' read data from POST '''
        try:
            post_data =  json.loads(web_data)
        except:
            traceback.print_exc()
            return json.dumps({'e': STATUS_CODE_TEXT['JSON_INVALID'], 'm':'JSON not present or JSON is not valid!'})

        if post_data.has_key(WEB_PARAM_METHOD) and post_data.has_key(WEB_PARAM_PARAMS):
            ''' read web parameters '''
            methodname = post_data[WEB_PARAM_METHOD]
            kwparams = post_data[WEB_PARAM_PARAMS]
            callid = post_data[WEB_PARAM_CALLID]
            methods_map = main_methods_map
            restobj = main_restobj
            session = None
            fake_session = None
            initial_fake_dict = None
            
            
            if kwparams.has_key(PARAM_SESSION):
                ''' if parameter session exists then check session and load plugin '''
                session = GameSession.check_session(kwparams[PARAM_SESSION])
                if session is None:
                    return json.dumps({'e':SESSION_ID_INVALID, 'c':callid, 'm':'REST session id ' + str(kwparams["session"]) +"' not found."})
                if not plugin_methods_map.has_key(session.application_name):
                    return json.dumps({'e':PLUGIN_INVALID, 'c':callid, 'm':'REST plugin for session id ' + str(kwparams["session"]) +"' not found."})
                del kwparams[PARAM_SESSION]
                restobj = LOADED_PLUGINS[session.application_name]
                methods_map = plugin_methods_map[session.application_name]
                fake_session = plugin_session()
                initial_fake_dict = plugin_dict(session.info)
                fake_session.info = initial_fake_dict
                kwparams[PARAM_SESSION] = fake_session
            
            if methods_map.has_key(methodname):
                method = methods_map[methodname]
                kwparams = post_data[WEB_PARAM_PARAMS]
                argspec = inspect.getargspec(method)
                kwlen = 0
                if argspec[3] is not None:
                    kwlen = len(argspec[3])
                params = []
                for arg in argspec[0][1:-kwlen]:
                    if kwparams.has_key(arg):
                        params.append(kwparams[arg])
                        del kwparams[arg]
                try:
                    if DEBUG_LEVEL:
                        print "CALL METHOD:", methodname
                        print "CALL PARAMS:", params
                        print "CALL KWPARAMS:", kwparams
                    try:
                        allparams = params[:]
                        allparams.insert(0, restobj)
                        inspect.getcallargs(method, *allparams, **kwparams)
                    except TypeError as te:
                        return json.dumps({'e': REST_METHOD_ERROR, 'm':'REST method arguments are invalid: ' + str(te)})
                    s_time = time.time()
                    ''' execute method and return result '''
                    ret = method(restobj, *params, **kwparams)
                    if fake_session:
                        if not isinstance(fake_session.info, dict):
                            return json.dumps({'e':SESSION_ERROR, 'c':callid, 'm':'REST session info not dictionary after method call'})
                        if fake_session.info!=initial_fake_dict or fake_session.info.modified:
                            session.info = fake_session.info
                            try:
                                session.save()
                            except:
                                return json.dumps({'e':SESSION_ERROR, 'c':callid, 'm':'REST session info could not be saved'})
                    
                    e_time = time.time()
                    dt = int((e_time - s_time)*1000)
                    if DEBUG_LEVEL:
                        if dt > 50:
                            print "WARNING: method '" + methodname + "' took " + str(dt) + " msecs to execute"
                        print "CALL RESPONSE: " + str(ret)
                    return json.dumps( {'e': STATUS_CODE_TEXT['SUCCESS'], 'r':ret} )
                except RestException as e:
                    traceback.print_exc()
                    return json.dumps({'e': e.code, 'm': str(e)})
                except TypeError as texc:
                    traceback.print_exc()
                    return json.dumps({'e': STATUS_CODE_TEXT['REST_METHOD_ERROR'], 'm':'REST method exception: ' + str(texc)})
            else:
                return json.dumps({'e': STATUS_CODE_TEXT['METHOD_NOT_DEFINED'], 'm':'REST method not defined'})
        else:
            return json.dumps({'e': STATUS_CODE_TEXT['JSON_PROTOCOL_ERROR'], 'm':'JSON protocol error'})

class rest_handler_help:
    def GET(self):
        methods_help = []
        for methoddata in main_methods:
            method = methoddata[1]
            argspec = inspect.getargspec(method)
            kwlen = 0
            if argspec[3]!=None:
                kwlen = len(argspec[3])
                mandatory_args = argspec[0][1:-kwlen]
                optional_args = argspec[0][-kwlen:]
                optional_kwargs = zip(optional_args, argspec[3])
            else:
                mandatory_args = argspec[0][1:]
                optional_kwargs = []
            args = ""
            for arg in mandatory_args:
                args += arg
                if arg!=mandatory_args[-1]:
                    args += ", "
            if len(mandatory_args)>0 and len(optional_kwargs)>0:
                    args += ", "
            for kwarg in optional_kwargs:
                args += kwarg[0] + "="
                if isinstance(kwarg[1],str):
                    args += "'" + kwarg[1] + "'"
                else:
                    args += str(kwarg[1])
                if kwarg!=optional_kwargs[-1]:
                    args += ", "
            methods_help.append((methoddata[0], {
                'doc':inspect.getdoc(method),
                'args':args,
            }))
        return render.base(inspect.getdoc(rest.REST), methods_help)

class fav_handler:
    def GET(self):
        web.header("Cache-Control", "max-age=3600");
        return open(os.path.join(os.path.dirname(__file__), 'static', 'favicon.ico')).read()

''' RUN APPLICATION '''
app = web.application(urls, globals(), autoreload=True)
if(__name__=="__main__"):
    app.run()
else:
    application = app.wsgifunc()
