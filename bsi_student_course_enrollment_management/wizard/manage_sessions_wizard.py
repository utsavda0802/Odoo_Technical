from odoo import api, fields, models
from odoo.exceptions import UserError


class TrainingManageSessionsWizard(models.TransientModel):
    _name = 'training.manage.sessions.wizard'
    _description = 'Manage Sessions of a Course'

    course_id = fields.Many2one('training.course', string='Course', required=True)
    line_ids = fields.One2many(
        'training.wizard.session.line', 'manage_wizard_id', string='Sessions')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'training.course':
            course = self.env['training.course'].browse(self.env.context.get('active_id'))
            res['course_id'] = course.id
            lines = []
            for session in course.session_ids:
                lines.append((0, 0, {
                    'session_id': session.id,
                    'action': 'update',
                    'name': session.name,
                    'session_date': session.session_date,
                    'instructor': session.instructor,
                }))
            res['line_ids'] = lines
        return res

    # Requirement 8: update / delete / add sessions with ONE write on the course.
    def action_apply(self):
        commands = []
        for line in self.line_ids:
            values = {
                'name': line.name,
                'session_date': line.session_date,
                'instructor': line.instructor,
            }
            if line.action == 'add':
                if not line.name:
                    raise UserError("A new session needs a name.")
                commands.append((0, 0, values))
            elif line.action == 'update' and line.session_id:
                commands.append((1, line.session_id.id, values))
            elif line.action == 'delete' and line.session_id:
                commands.append((2, line.session_id.id, 0))
        if not commands:
            raise UserError("Nothing to apply.")
        self.course_id.write({'session_ids': commands})
        return {'type': 'ir.actions.act_window_close'}