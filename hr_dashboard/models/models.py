# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request
import datetime
import logging

class HrDashboard(models.Model):
    _name = 'hr.dashboard'
    _description = 'HR Dashboard'
    name = fields.Char("")

    @api.model
    def get_employee_info(self):
        uid = request.session.uid
        cr = self.env.cr
        employee_id = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        project_id = self.env['project.project'].sudo().search([])
        drawing_id = self.env['construction.drawing'].sudo().search([])
        query = """
             select p.name,c.id,c.name_seq,
                round( CAST(c.total_deli as numeric), 2) as total_deli,
                round( CAST(c.total_erec as numeric), 2) as total_erec ,
                round( CAST(c.total_prod as numeric), 2) as total_prod,
                round( CAST(c.total_drawing as numeric), 2) as total_drawing,
                round( CAST(p.total_cost as numeric), 2) as total_drawing,
                c.nb_production,
                c.nb_deli,
                c.nb_ere,
                c.nb_total,
                c.division_copy,
                c.nb_item
             from construction_drawing c inner join project_project p on (p.id = project_id)
        """
        # coalesce(c.nombre_eff,0) as cible_categ, (coalesce(c.nombre_eff,0)-coalesce(m.effectif,0)) as ecart_categorie, b.id,b.status,COALESCE(b.code_besoin, 'aucun') as codes, m.int_site as magasin,p.code_poste, p.state, p.fammille_post, m.date_ouverture,m.etat_m,coalesce(p.effectif_reel,0) as nb_reel ,coalesce(p.effectif_cible,0) as nb_cible ,(coalesce(p.effectif_cible,0)-coalesce(p.effectif_reel,0)) as ecart
        #     from bs_poste p inner join magasin m on (m.id = magasin_id)
        #     left join besoin_recrutement b on (b.poste = p.id and (b.status='Demande non générée' or b.status='Demande générée' or b.status='En cours')) 
        #     left join hr_job j on (j.poste_id = p.id and (j.state='Besoin' or j.state='B' or j.state='D' or j.state='A'))
        #     left join categorie c on (c.id = m.categorie)

        cr.execute(query)
        employee_table = cr.dictfetchall()
        logging.info(employee_table)
        if employee_id:
            categories = self.env['hr.employee.category'].sudo().search([('id', 'in', employee_id[0]['category_ids'])])

            data = {
                'categories': [c.name for c in categories],
                'project_id': [p.name for p in project_id],
                'drawing_id':    [d.name_seq for d in drawing_id],
                'emp_table': employee_table,
            }
            employee_id[0].update(data)
        return employee_id
