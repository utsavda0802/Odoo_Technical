from odoo import api, fields, models
from odoo.exceptions import UserError


class TrainingUpdateStudentsWizard(models.TransientModel):
    _name = 'training.update.students.wizard'
    _description = 'Update Students of a Course'

    course_id = fields.Many2one('training.course', string='Course', required=True)
    line_ids = fields.One2many('training.wizard.student.line', 'update_wizard_id', string='Students')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'training.course':
            course = self.env['training.course'].browse(self.env.context.get('active_id'))
            res['course_id'] = course.id
            lines = []
            for student in course.student_ids[:3]:
                lines.append((0, 0, {
                    'student_id': student.id,
                    'name': student.name,
                    'email': student.email,
                    'age':student.age,
                }))
            res['line_ids'] = lines
        return res

    # Requirement 2: two students updated with ONE write on the course.
    def action_update(self):
        if not self.line_ids:
            raise UserError("The course has no students to update.")
        commands = []
        for line in self.line_ids:
            if not line.name:
                raise UserError("A student name cannot be empty.")
            commands.append((1, line.student_id.id, {
                'name': line.name,
                'email': line.email,
                'age':line.age,
            }))
        self.course_id.write({'student_ids': commands})
        return {'type': 'ir.actions.act_window_close'}