from odoo import http, models, fields
from odoo.http import request
import requests
from zipfile import ZipFile
import os
import shutil
import odoo.tools as tools
import logging

_logger = logging.getLogger(__name__)


class AppStore(models.TransientModel):
    _name = 'oh.app.store'


class HttpRequest(http.Controller):

    # ''' receives jsonrpc call'''
    @http.route("/ohrms/download", type='json', auth="user")
    def download(self, url):
        try:
            # '''reads the addon path'''
            path = tools.config['addons_path'].split(',')
            path = path[0].split('/')
            # '''removes the last directory from path'''
            path.pop()
            # '''make path a string again'''
            path = "/".join([str(x) for x in path])
            # '''goto the path'''
            os.chdir(path)
            # '''make a temporary directory'''
            os.mkdir('temp')
            file_name = 'temp/temp.zip'
            r = requests.get(url, stream=True)
        except Exception as e:
            _logger.warn('Exception'+str(e))
            return False
        try:
            # '''opens the file and downloads it'''
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
                f.close()
            # '''specifying the zip file name'''
            # '''opening the zip file in READ mode'''
            ad_path = tools.config['addons_path'].split(',')
            shutil.move('temp/temp.zip', ad_path[0])
            os.chdir(str(path))
            os.rmdir('temp')
            os.chdir(ad_path[0])
            # '''exstracts the zip'''
            with ZipFile('temp.zip', 'r') as zip:
                zip.extractall()
            # '''deletes the zip'''
            os.remove('temp.zip')
            os.chdir(path)
        except Exception as e:
            _logger.warn('Exception'+str(e))
            return False
        return True
