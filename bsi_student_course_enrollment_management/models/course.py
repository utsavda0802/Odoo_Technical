
from odoo import models, fields
from odoo.exceptions import UserError


class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Training Course'

    name = fields.Char(string='Course Name', required=True)
    description = fields.Text(string='Description')
    course_fee = fields.Float(string='Course Fee')
    student_ids = fields.Many2many(
        comodel_name='training.student',
        relation='training_course_student_rel',
        column1='course_id',
        column2='student_id',
        string='Students',
    )
    session_ids = fields.One2many('training.course.session','course_id',string='Course Sessions')

    _sql_constraints = [('name_unique', 'unique(name)','A course with this name already exists.'),]

    def _notify(self, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Done',
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                },
            },
        }

    def _student_command(self, name, email, age):
        existing = self.env['training.student'].search([('email', '=ilike', email)],limit=1)

        if existing:
            return (4, existing.id)

        return (0, 0, {'name': name,'email': email,'age': age,})

    def _open_course_form(self, course):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'training.course',
            'view_mode': 'form',
            'res_id': course.id,
        }

    def action_create_course_with_students(self):
        demo_students = [
            ('Patel Dev', 'patel.dev@botspot.com', 21),
            ('Maktarpara Shloak', 'maktarpara.shloak@botspot.com', 21),
            ('Zala Anjali', 'zala.anjali@botspot.com', 24),
        ]

        course = self.search([('name', '=', 'Python Basics')],limit=1)

        if not course:
            commands = [self._student_command(name, email, age)for name, email, age in demo_students]

            course = self.create({
                'name': 'Python Basics',
                'description': 'This is a basic Python course for beginners.',
                'course_fee': 10000.0,
                'student_ids': commands,
            })

        elif not course.student_ids:
            commands = [self._student_command(name, email, age) for name, email, age in demo_students]

            course.write({'student_ids': commands})

        return self._open_course_form(course)

    # ---------- Requirement 3: Remove First Student ----------
    def action_remove_first_student(self):
        self.ensure_one()

        if not self.student_ids:
            raise UserError("This course has no students.")

        student = self.student_ids[0]
        student_id = student.id
        name = student.name

        self.write({'student_ids': [(3, student_id)]})

        found = self.env['training.student'].search_count([('id', '=', student_id)])

        return self._notify("%s removed from the course. ""Student records still existing: %d" % (name, found))

    # ---------- Requirement 5: Delete Last Student ----------
    def action_delete_last_student(self):
        self.ensure_one()

        if not self.student_ids:
            raise UserError("This course has no students.")

        student = self.student_ids[-1]
        student_id = student.id
        name = student.name

        self.write({'student_ids': [(2, student_id, 0)]})
        found = self.env['training.student'].search_count([('id', '=', student_id)])

        return self._notify("Student %s deleted. Records found with that id: %d. ""The course still exists." % (name, found))

    # ---------- Requirement 6: Clear All Students ----------
    def action_clear_students(self):
        self.ensure_one()

        self.write({'student_ids': [(5, 0, 0)]})

        return self._notify("All students removed from the course. "
            "The student records are still in the system."
        )

    # ---------- Enroll Students Wizard ----------
    def action_open_enroll_wizard(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Enroll Students',
            'res_model': 'training.enroll.student.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_course_id': self.id,
            },
        }