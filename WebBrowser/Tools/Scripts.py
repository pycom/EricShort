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
