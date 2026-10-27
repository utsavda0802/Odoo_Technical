from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request

class EmployeeController(http.Controller):
    @http.route('/employee/<int:employee_id>',type='http',auth='user',methods=['GET'])
    def employee_json(self,employee_id,**kwargs):
        employee = request.env['test.employee'].browse(employee_id).exists()
        if not employee:
            return request.make_json_response({'error':'Employee not found.'},status=404)
        try:
            data={
                'name':employee.name,
                'department':employee.department_id.name or "",
                'status':employee.status,
                'annual_salary':employee.annual_salary,
            }
        except AccessError:
            return request.make_json_response({'error':'Access denied'},status=403)
        return request.make_json_response(data)