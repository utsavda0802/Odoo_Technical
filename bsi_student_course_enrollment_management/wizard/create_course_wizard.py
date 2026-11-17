from odoo import fields, models
from odoo.exceptions import UserError


class TrainingWizardStudentLine(models.TransientModel):
    _name = 'training.wizard.student.line'
    _description = 'Wizard Student Line'

    create_wizard_id = fields.Many2one('training.create.course.wizard', ondelete='cascade')
    update_wizard_id = fields.Many2one('training.update.students.wizard', ondelete='cascade')
    student_id = fields.Many2one('training.student', string='Student')
    name = fields.Char(string='Name')
    email = fields.Char()
    age = fields.Integer()


class TrainingWizardSessionLine(models.TransientModel):
    _name = 'training.wizard.session.line'
    _description = 'Wizard Session Line'

    create_wizard_id = fields.Many2one('training.create.course.wizard', ondelete='cascade')
    manage_wizard_id = fields.Many2one('training.manage.sessions.wizard', ondelete='cascade')
    session_id = fields.Many2one('training.course.session', string='Existing Session')
    action = fields.Selection(
        [('add', 'Add'), ('update', 'Update'), ('delete', 'Delete')],
        default='add', required=True)
    name = fields.Char(string='Session Name')
    session_date = fields.Date()
    instructor = fields.Char()


class TrainingCreateCourseWizard(models.TransientModel):
    _name = 'training.create.course.wizard'
    _description = 'Create Course with Students and Sessions'

    name = fields.Char(string='Course Name', required=True)
    course_fee = fields.Float(string='Course Fee')
    description = fields.Text()
    student_line_ids = fields.One2many('training.wizard.student.line', 'create_wizard_id', string='New Students')
    session_line_ids = fields.One2many('training.wizard.session.line', 'create_wizard_id', string='Sessions')

    # Requirement 1 and the "create" part of Requirement 8:
    def action_create(self):
        self.ensure_one()

        student_commands = []

        for line in self.student_line_ids:
            if not line.name:
                raise UserError("Every student line needs a name.")

            student_commands.append((0, 0, {
                'name': line.name,
                'email': line.email,
                'age': line.age,
            }))

        session_commands = []

        for line in self.session_line_ids:
            if not line.name:
                raise UserError("Every session line needs a name.")

            session_commands.append((0, 0, {
                'name': line.name,
                'session_date': line.session_date,
                'instructor': line.instructor,
            }))

        course = self.env['training.course'].create({
            'name': self.name,
            'course_fee': self.course_fee,
            'description': self.description,
            'student_ids': student_commands,
            'session_ids': session_commands,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Created Course',
            'res_model': 'training.course',
            'res_id': course.id,
            'view_mode': 'form',
            'target': 'current',
        }