from odoo import models, fields
from odoo.exceptions import UserError


class EnrollStudentWizard(models.TransientModel):
    _name = 'training.enroll.student.wizard'
    _description = 'Enroll Students Wizard'

    course_id = fields.Many2one('training.course', string='Course', required=True, readonly=True)
    line_ids = fields.One2many('training.enroll.student.wizard.line', 'wizard_id', string='Students')

    def action_enroll(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("Please add at least one student.")

        student_obj = self.env['training.student']
        course = self.course_id
        commands = []
        created, enrolled, skipped = [], [], []
        seen_emails = set()

        for line in self.line_ids:
            name = (line.name or '').strip()
            email = (line.email or '').strip()
            if not email:
                continue
            key = email.lower()

            if key in seen_emails:
                skipped.append(name)
                continue
            seen_emails.add(key)

            matches = student_obj.search([('email', '=ilike', email)]).filtered(lambda s: (s.email or '').strip().lower() == key)

            if matches & course.student_ids:
                skipped.append(name)
            elif matches:
                commands.append((4, matches[0].id))
                enrolled.append(name)
            else:
                commands.append((0, 0, {'name': name, 'email': email, 'age': line.age}))
                created.append(name)

        if commands:
            course.write({'student_ids': commands})

        messages = []
        if created:
            messages.append("Created and enrolled: " + ", ".join(created))
        if enrolled:
            messages.append("Enrolled existing: " + ", ".join(enrolled))
        if skipped:
            messages.append("Already enrolled / duplicate (skipped): " + ", ".join(skipped))
        if not messages:
            messages.append("Nothing to enroll.")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Enrollment Result',
                'message': "\n".join(messages),
                'type': 'success' if commands else 'warning',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }


class EnrollStudentWizardLine(models.TransientModel):
    _name = 'training.enroll.student.wizard.line'
    _description = 'Enroll Students Wizard Line'

    wizard_id = fields.Many2one('training.enroll.student.wizard', required=True, ondelete='cascade')
    name = fields.Char(string='Student Name', required=True)
    email = fields.Char(string='Email', required=True)
    age = fields.Integer(string='Age')