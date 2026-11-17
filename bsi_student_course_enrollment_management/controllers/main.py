from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
PAGE_SIZE = 5
MODULE = 'bsi_student_course_enrollment_management'
class StudentWebsite(http.Controller):
    # ---------- helpers ----------
    def _statuses(self):
        # [('new', 'New'), ('active', 'Active'), ('inactive', 'Inactive')]
        return request.env['training.student']._fields['status'].selection
    def _can_edit(self):
        # public (not logged in) visitors cannot edit
        return not request.env.user._is_public()
    def _check_form(self, post, student):
        """Return (error_message, values_to_write)."""
        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()
        age = (post.get('age') or '').strip()
        status = post.get('status') or ''
        valid_status = [key for key, label in self._statuses()]

        if not name:
            return 'Name is required.', {}
        if not email or '@' not in email:
            return 'Please enter a valid email address.', {}
        other = request.env['training.student'].search(
            [('email', '=ilike', email), ('id', '!=', student.id)], limit=1)
        if other:
            return 'Another student already uses this email.', {}
        if not age.isdigit():
            return 'Age must be a whole number.', {}
        if status not in valid_status:
            return 'Please choose a valid status.', {}

        return '', {'name': name,'email': email,'age': int(age),'status': status,}

    # ---------- list page with search + pagination ----------
    @http.route(['/students', '/students/page/<int:page>'],type='http', auth='public', website=True)
    def student_list(self, page=1, search='', age='', course='', status='', **kwargs):
        Student = request.env['training.student'].sudo()
        domain = []
        url_args = {}            # the filters are kept in the page links
        search = search.strip()
        if search:
            domain.append(('name', 'ilike', search))
            url_args['search'] = search
        age = age.strip()
        if age.isdigit():
            domain.append(('age', '=', int(age)))
            url_args['age'] = age
        else:
            age = ''
        course = course.strip()
        if course.isdigit():
            domain.append(('course_ids', 'in', [int(course)]))
            url_args['course'] = course
        else:
            course = ''
        valid_status = [key for key, label in self._statuses()]
        if status in valid_status:
            domain.append(('status', '=', status))
            url_args['status'] = status
        else:
            status = ''
        total = Student.search_count(domain)
        pager = request.website.pager(
            url='/students',
            total=total,
            page=page,
            step=PAGE_SIZE,
            scope=5,
            url_args=url_args,
        )
        students = Student.search(
            domain, order='name, id', limit=PAGE_SIZE, offset=pager['offset'])

        return request.render(MODULE + '.student_list_page', {
            'students': students,
            'pager': pager,
            'total': total,
            'search': search,
            'age': age,
            'course': course,
            'status': status,
            'courses': request.env['training.course'].sudo().search([], order='name'),
            'statuses': self._statuses(),
            'can_edit': self._can_edit(),
        })

    # ---------- detail page ----------
    @http.route('/students/<int:student_id>', type='http', auth='public', website=True)
    def student_detail(self, student_id, updated=None, **kwargs):
        student = request.env['training.student'].sudo().browse(student_id).exists()
        if not student:
            return request.not_found()
        return request.render(MODULE + '.student_detail_page', {
            'student': student,
            'updated': bool(updated),
            'can_edit': self._can_edit(),
        })

    # ---------- edit form ----------
    @http.route('/students/<int:student_id>/edit', type='http', auth='user', website=True)
    def student_edit(self, student_id, **kwargs):
        student = request.env['training.student'].browse(student_id).exists()
        if not student:
            return request.not_found()
        return request.render(MODULE + '.student_edit_page', {
            'student': student,
            'values': {
                'name': student.name,
                'email': student.email or '',
                'age': student.age,
                'status': student.status,
            },
            'statuses': self._statuses(),
            'error': '',
        })

    # ---------- save the changes ----------
    @http.route('/students/<int:student_id>/update', type='http', auth='user',website=True, methods=['POST'])
    def student_update(self, student_id, **post):
        student = request.env['training.student'].browse(student_id).exists()
        if not student:
            return request.not_found()
        error, vals = self._check_form(post, student)
        if not error:
            try:
                with request.env.cr.savepoint():     # undo the write if a constraint fails
                    student.write(vals)
            except (ValidationError, UserError) as e:
                error = str(e)
        if error:
            return request.render(MODULE + '.student_edit_page', {
                'student': student,
                'values': post,
                'statuses': self._statuses(),
                'error': error,
            })
        return request.redirect('/students/%d?updated=1' % student_id)