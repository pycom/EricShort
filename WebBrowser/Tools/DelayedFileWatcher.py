# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

from __future__ import unicode_literals

##class DelayedFileWatcher : public QFileSystemWatcher
##{
##    Q_OBJECT
##
##public:
##    explicit DelayedFileWatcher(QObject* parent = 0);
##    explicit DelayedFileWatcher(const QStringList &paths, QObject* parent = 0);
##
##signals:
##    void delayedDirectoryChanged(const QString &path);
##    void delayedFileChanged(const QString &path);
##
##private slots:
##    void slotDirectoryChanged(const QString &path);
##    void slotFileChanged(const QString &path);
##
##    void dequeueDirectory();
##    void dequeueFile();
##
##private:
##    void init();
##
##    QQueue<QString> m_dirQueue;
##    QQueue<QString> m_fileQueue;
##};
##
##
##DelayedFileWatcher::DelayedFileWatcher(QObject* parent)
##    : QFileSystemWatcher(parent)
##{
##    init();
##}
##
##DelayedFileWatcher::DelayedFileWatcher(const QStringList &paths, QObject* parent)
##    : QFileSystemWatcher(paths, parent)
##{
##    init();
##}
##
##void DelayedFileWatcher::init()
##{
##    connect(this, SIGNAL(directoryChanged(QString)), this, SLOT(slotDirectoryChanged(QString)));
##    connect(this, SIGNAL(fileChanged(QString)), this, SLOT(slotFileChanged(QString)));
##}
##
##void DelayedFileWatcher::slotDirectoryChanged(const QString &path)
##{
##    m_dirQueue.enqueue(path);
##    QTimer::singleShot(500, this, SLOT(dequeueDirectory()));
##}
##
##void DelayedFileWatcher::slotFileChanged(const QString &path)
##{
##    m_fileQueue.enqueue(path);
##    QTimer::singleShot(500, this, SLOT(dequeueFile()));
##}
##
##void DelayedFileWatcher::dequeueDirectory()
##{
##    emit delayedDirectoryChanged(m_dirQueue.dequeue());
##}
##
##void DelayedFileWatcher::dequeueFile()
##{
##    emit delayedFileChanged(m_fileQueue.dequeue());
##}
