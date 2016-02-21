# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

from __future__ import unicode_literals

##class GM_UrlInterceptor : public UrlInterceptor
##{
##public:
##    explicit GM_UrlInterceptor(GM_Manager* manager);
##
##    void interceptRequest(QWebEngineUrlRequestInfo &info);
##
##private:
##    GM_Manager *m_manager;
##
##};


##GM_UrlInterceptor::GM_UrlInterceptor(GM_Manager *manager)
##    : UrlInterceptor(manager)
##    , m_manager(manager)
##{
##}
##
##void GM_UrlInterceptor::interceptRequest(QWebEngineUrlRequestInfo &info)
##{
##    if (info.requestUrl().toString().endsWith(QLatin1String(".user.js"))) {
##        m_manager->downloadScript(info.requestUrl());
##        info.block(true);
##    }
##}
