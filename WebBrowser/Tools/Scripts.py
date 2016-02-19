# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module containing function to generate JavaScript code.
"""

#
# This code was ported from QupZilla.
# Copyright (C) David Rosca <nowrep@gmail.com>
#

from __future__ import unicode_literals

from PyQt5.QtCore import QUrlQuery, QUrl

from .WebBrowserTools import readAllFileContents


def setupWebChannel():
    """
    Function generating  a script to setup the web channel.
    
    @return script to setup the web channel
    @rtype str
    """
    source = """
        (function() {{
            {0}
            
            function registerExternal(e) {{
                window.external = e;
                if (window.external) {{
                    var event = document.createEvent('Event');
                    event.initEvent('_eric_external_created', true, true);
                    document.dispatchEvent(event);
                }}
            }}
            
            if (self !== top) {{
                if (top.external)
                    registerExternal(top.external);
                else
                    top.document.addEventListener(
                        '_eric_external_created', function() {{
                            registerExternal(top.external);
                    }});
                return;
            }}

            new QWebChannel(qt.webChannelTransport, function(channel) {{
               registerExternal(channel.objects.eric_object);
            }});

            }})()"""
    
    return source.format(readAllFileContents(":/javascript/qwebchannel.js"))


def setStyleSheet(css):
    """
    Function generating a script to set a user style sheet.
    
    @param css style sheet to be applied
    @type str
    @return script to set a user style sheet
    @rtype str
    """
    source = """
        (function() {{
            var css = document.createElement('style');
            css.setAttribute('type', 'text/css');
            css.appendChild(document.createTextNode('{0}'));
            document.getElementsByTagName('head')[0].appendChild(css);
        }})()"""
    
    style = css.replace("'", "\\'").replace("\n", "\\n")
    return source.format(style)


def toggleMediaPause(pos):
    """
    Function generating a script to toggle the paused state of a media element.
    
    @param pos position of the media element
    @type QPoint
    @return script to toggle the element paused state
    @rtype str
    """
    source = """
        (function() {{
            var e = document.elementFromPoint({0}, {1});
            if (!e)
                return;
            if (e.paused)
                e.play();
            else
                e.pause();
        }})()"""
    return source.format(pos.x(), pos.y())


def toggleMediaMute(pos):
    """
    Function generating a script to toggle the mute state of a media element.
    
    @param pos position of the media element
    @type QPoint
    @return script to toggle the element mute state
    @rtype str
    """
    source = """
        (function() {[
            var e = document.elementFromPoint({0}, {1});
            if (!e)
                return;
            e.muted = !e.muted;
        }})()"""
    return source.format(pos.x(), pos.y())


def getFormData(pos):
    """
    Function generating a script to extract data for a form element.
    
    @param pos position to extract data at
    @type QPoint
    @return script to extract form data
    @rtype str
    """
    source = """
        (function() {{
            var e = document.elementFromPoint({0}, {1});
            if (!e || e.tagName != 'INPUT')
                return;
            var fe = e.parentElement;
            while (fe) {{
                if (fe.tagName == 'FORM')
                    break;
                fe = fe.parentElement;
            }}
            if (!fe)
                return;
            var res = {{
                method: fe.method.toLowerCase(),
                action: fe.action,
                inputName: e.name,
                inputs: [],
            }};
            for (var i = 0; i < fe.length; ++i) {{
                var input = fe.elements[i];
                res.inputs.push([input.name, input.value]);
            }}
            return res;
        }})()"""
    return source.format(pos.x(), pos.y())


def getAllMetaAttributes():
    """
    Function generating a script to extract all meta attributes of a web page.
    
    @return script to extract meta attributes
    @rtype str
    """
    source = """
        (function() {
            var out = [];
            var meta = document.getElementsByTagName('meta');
            for (var i = 0; i < meta.length; ++i) {
                var e = meta[i];
                out.push({
                    name: e.getAttribute('name'),
                    content: e.getAttribute('content'),
                    httpequiv: e.getAttribute('http-equiv')
                });
            }
            return out;
        })()"""
    return source


def getOpenSearchLinks():
    """
    Function generating a script to extract all open search links.
    
    @return script to extract all open serach links
    @rtype str
    """
    source = """
        (function() {
            var out = [];
            var links = document.getElementsByTagName('link');
            for (var i = 0; i < links.length; ++i) {
                var e = links[i];
                if (e.type == 'application/opensearchdescription+xml') {
                    out.push({
                        url: e.getAttribute('href'),
                        title: e.getAttribute('title')
                    });
                }
            }
            return out;
        })()"""
    return source


def sendPostData(url, data):
    """
    Function generating a script to send Post data.
    
    @param url URL to send the data to
    @type QUrl
    @param data data to be sent
    @type QByteArray
    @return script to send Post data
    @rtype str
    """
    source = """
        (function() {{
            var form = document.createElement('form');
            form.setAttribute('method', 'POST');
            form.setAttribute('action', '{0}');
            var val;
            {1}
            form.submit();
            }})()"""
    
    valueSource = """
        val = document.createElement('input');
        val.setAttribute('type', 'hidden');
        val.setAttribute('name', '{0}');
        val.setAttribute('value', '{1}');
        form.appendChild(val);"""
    
    values = ""
    query = QUrlQuery(data)
    for name, value in query.queryItems(QUrl.FullyDecoded):
        value = value.replace("'", "\\'")
        name = name.replace("'", "\\'")
        values += valueSource.format(name, value)
    
    return source.format(url.toString(), values)


def setupFormObserver():
    """
    Function generating a script to monitor a web form for user entries.
    
    @return script to monitor a web page
    @rtype str
    """
    source = """
        (function() {
            function findUsername(inputs) {
                for (var i = 0; i < inputs.length; ++i)
                    if (inputs[i].type == 'text' && inputs[i].value.length &&
                        inputs[i].name.indexOf('user') != -1)
                        return inputs[i].value;
                for (var i = 0; i < inputs.length; ++i)
                    if (inputs[i].type == 'text' && inputs[i].value.length &&
                        inputs[i].name.indexOf('name') != -1)
                        return inputs[i].value;
                for (var i = 0; i < inputs.length; ++i)
                    if (inputs[i].type == 'text' && inputs[i].value.length)
                        return inputs[i].value;
                for (var i = 0; i < inputs.length; ++i)
                    if (inputs[i].type == 'email' && inputs[i].value.length)
                        return inputs[i].value;
                return '';
            }
            
            function registerForm(form) {
                form.addEventListener('submit', function() {
                    var form = this;
                    var data = '';
                    var password = '';
                    var inputs = form.getElementsByTagName('input');
                    for (var i = 0; i < inputs.length; ++i) {
                        var input = inputs[i];
                        var type = input.type.toLowerCase();
                        if (type != 'text' && type != 'password' &&
                            type != 'email')
                            continue;
                        if (!password && type == 'password')
                            password = input.value;
                        data += encodeURIComponent(input.name);
                        data += '=';
                        data += encodeURIComponent(input.value);
                        data += '&';
                    }
                    if (!password)
                        return;
                    data = data.substring(0, data.length - 1);
                    var url = window.location.href;
                    var username = findUsername(inputs);
                    external.formSubmitted(url, username, password, data);
                }, true);
            }
            
            for (var i = 0; i < document.forms.length; ++i)
                registerForm(document.forms[i]);
            
            var observer = new MutationObserver(function(mutations) {
                for (var i = 0; i < mutations.length; ++i)
                    for (var j = 0; j < mutations[i].addedNodes.length; ++j)
                        if (mutations[i].addedNodes[j].tagName == 'form')
                            registerForm(mutations[i].addedNodes[j]);
            });
            observer.observe(document.documentElement, { childList: true });
            
            })()"""
    return source


def completeFormData(data):
    """
    Function generating a script to fill in form data.
    
    @param data data to be filled into the form
    @type QByteArray
    @return script to fill a form
    @rtype str
    """
    source = """
        (function() {{
            var data = '{0}'.split('&');
            var inputs = document.getElementsByTagName('input');
            
            for (var i = 0; i < data.length; ++i) {{
                var pair = data[i].split('=');
                if (pair.length != 2)
                    continue;
                var key = decodeURIComponent(pair[0]);
                var val = decodeURIComponent(pair[1]);
                for (var j = 0; j < inputs.length; ++j) {{
                    var input = inputs[j];
                    var type = input.type.toLowerCase();
                    if (type != 'text' && type != 'password' &&
                        type != 'email')
                        continue;
                    if (input.name == key)
                        input.value = val;
                }}
            }}
            
            }})()"""
    
    data = bytes(data).decode("utf-8")
    data = data.replace("'", "\\'")
    return source.format(data)
