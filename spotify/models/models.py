# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ..controllers import general
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from odoo.exceptions import ValidationError

general = general.General()


class spotify(models.Model):
    _name = 'spotify.persona'
    _description = 'Lista de usuarios que se registraron en la aplicación'

    primerNombre = fields.Char(string='Primer Nombre',required=True)
    primerApellido = fields.Char(string='Primer Apellido',required=True)
    segundoNombre = fields.Char(string='Segundo Nombre')
    segundoApellido = fields.Char(string='Segundo Apellido')
    generoMusical = fields.Many2many('spotify.generos',string='Géneros musicales',help='Géneros musicales que le gustan al usuario',required=True)
    recomendaciones = fields.Many2many('spotify.recomendaciones',string='Canciones recomendadas')

    @api.model
    def create(self,vals):
        sp = spotipy.Spotify()
        cid = general.clientID
        cSecret = general.clientSecret
        gestorCredenciales = SpotifyClientCredentials(client_id=cid, client_secret=cSecret)
        sp = spotipy.Spotify(client_credentials_manager=gestorCredenciales)
        generos = vals['generoMusical'][0][2]
        listRecomendaciones = []
        try:
            for genero in generos:
                objetoGeneroMusical = self.env['spotify.generos'].sudo().search([('id', '=', genero)])
                resultado = sp.category_playlists((objetoGeneroMusical.genero).lower(),limit=10,country="CO")
                playlist = resultado['playlists']['items']
                numeroAleatorio = random.randint(0, len(playlist)-1)
                playlist = playlist[numeroAleatorio]
                canciones = sp.playlist(playlist['id'])
                listaCanciones = canciones['tracks']['items']
                numeroAleatorio = random.randint(0, len(listaCanciones)-1)
                nombreCancion = listaCanciones[numeroAleatorio]['track']['name']
                urlCancion = listaCanciones[numeroAleatorio]['track']['external_urls']['spotify']
                cancionRecomendada = self.env['spotify.recomendaciones'].sudo().search(
                    [('nombreCancion', '=', nombreCancion)])
                if not cancionRecomendada:
                    cancionesRecomendadas = self.env['spotify.recomendaciones']
                    cancionRecomendada = cancionesRecomendadas.sudo().create(
                        {
                            'nombreCancion': nombreCancion,
                            'urlCanción': urlCancion
                        })
                listRecomendaciones.append(cancionRecomendada.id)
            vals['recomendaciones'] = [[6,False,listRecomendaciones]]
            return super(spotify, self).create(vals)
        except Exception as e:
            raise ValidationError(
                'Ocurrió un error, inténtelo más tarde')


class generosMusicales(models.Model):
    _name = 'spotify.generos'
    _description = 'Géneros musicales que le pueden gustar al usuario'
    _rec_name = "genero"

    genero = fields.Char(string="Géneros musicales")

class cancionesRecomendadas(models.Model):
    _name = 'spotify.recomendaciones'
    _description = 'Canciones recomendadas al usuario'

    nombreCancion = fields.Char(string="Nombre")
    urlCanción = fields.Char(string="URL")