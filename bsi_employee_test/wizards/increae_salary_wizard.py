from odoo import models, fields


class BulkSalaryIncrease(models.TransientModel):
    _name = 'bulk.salary.increase'
    _description = 'Increase Salary of bunch of Employees.'

    percentage = fields.Float(string='Enter percentage to increase salary')
    basic_salary = fields.Float(string='Basic Salary')
    increased_salary = fields.Float(string='Increased Salary',compute='_compute_increased_salary')

    @api.constrains('percentage')
    def _check_increment(self):
        for rec in self:
            if rec.percentage <= 0:
                raise ValidationError("Increment percentage must be greater than zero.")

    @api.depends('basic_salary','percentage')
    def _compute_increased_salary(self):
        for rec in self:
            rec.increased_salary = basic_salary + (rec.basic_salary*(rec.percentage/100))

    def action_increase_salary_wizard(self):
    invalid = self.filtered(lambda j: j.state not in ('confirmed'))
    if invalid:
        raise UserError(
            "Only Employee whose status is Confirmed can be increased.\n"
            "Please deselect: %s" % ', '.join(invalid.mapped('name'))
        )
    return {
        
    }

    def action_confirm_payment(self):
        self.ensure_one()
        self.env['employee'].create({
            'percentage': self.percentage,
            'basic_salary': self.basic_salary,
            'increased_salary': self.increased_salary,
        })
        return {'type': 'ir.actions.act_window_close'}