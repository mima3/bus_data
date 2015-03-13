# -*- coding: utf-8 -*-
import urllib
import grequests
import os
import zipfile


class CallBackDownload:
    def __init__(self, download_path): 
        self.download_path = download_path

    def save_local(self, res):
        path = os.path.join(self.download_path, os.path.basename(res.url))
        with open(path, 'wb') as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)

    def expand_zip(self, res):
        path = os.path.join(self.download_path, os.path.basename(res.url))
        with open(path, 'wb') as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        with zipfile.ZipFile(path, 'r') as zip_file:
            zip_file.extractall(path=self.download_path)


def download(download_path, srcs):
    callback = CallBackDownload(download_path)
    rs = (grequests.get(u) for u in srcs.keys())
    g = grequests.imap(rs)
    for r in g:
        if r.status_code != 200:
            raise Exception('Download failed.', r.url, r.status_code)
        getattr(callback, srcs[r.url])(r)
