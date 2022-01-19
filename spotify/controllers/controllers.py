# -*- coding: utf-8 -*-
from odoo import http


class Spotify(http.Controller):
    @http.route('/spotify', auth='public')
    def index(self, **kw):
        return "Hello, world"


