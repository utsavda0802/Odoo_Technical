from odoo import fields, models
from odoo.exceptions import ValidationError


class SalaryRevisionWizard(models.TransientModel):
    _name = 'bsi.salary.revision.wizard'
    _description = 'Salary Revision Wizard'

    percentage = fields.Float(string='Revision Percentage',required=True)
    updated_count = fields.Integer(string='Updated Employees',readonly=True)
    skipped_count = fields.Integer(string='Skipped Employees',readonly=True)

    def action_apply(self):
        self.ensure_one()
        employee_ids = self.env.context.get('active_ids',[])
        employees = self.env['bsi.employee'].browse(employee_ids).exists()
        if not employees:
            raise ValidationError('Please select at least one employee.')

        updated_count = 0
        skipped_count = 0

        for employee in employees:
            if employee.status == 'confirmed':
                new_salary = (employee.basic_salary *(1 + self.percentage / 100))
                if new_salary <= 0:
                    raise ValidationError('Salary revision results in an ''invalid salary for %s.'% employee.name)
                employee.with_context(allow_salary_revision=True).write({'basic_salary': new_salary})
                updated_count += 1
            else:
                skipped_count += 1
        self.write({
            'updated_count': updated_count,
            'skipped_count': skipped_count,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Salary Revision Result',
            'res_model': 'bsi.salary.revision.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }