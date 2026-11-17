from odoo import api, fields, models
from odoo.exceptions import UserError


class TrainingReplaceWizard(models.TransientModel):
    _name = 'training.replace.wizard'
    _description = 'Replace Course Students'

    course_id = fields.Many2one('training.course', string='Course', required=True)
    student_ids = fields.Many2many('training.student', 'training_replace_wizard_student_rel','wizard_id', 'student_id', string='New Students')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'training.course':
            res['course_id'] = self.env.context.get('active_id')
        return res

    # ---------- Requirement 7: replace all enrollments ----------
    def action_replace(self):
        if not self.student_ids:
            raise UserError("Select at least one student.")
        self.course_id.write({'student_ids': [(6, 0, self.student_ids.ids)]})
        return {'type': 'ir.actions.act_window_close'}