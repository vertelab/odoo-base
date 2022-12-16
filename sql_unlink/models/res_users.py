from odoo import models, api, _
import logging
_logger = logging.getLogger(__name__)
_schema = logging.getLogger(__name__ + '.schema')
_unlink = logging.getLogger(__name__ + '.unlink')


class User(models.Model):
    _inherit = "res.users"

    def unlink(self):
        if not self:
            return True

        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        self._check_concurrency()

        # mark fields that depend on 'self' to recompute them after 'self' has
        # been deleted (like updating a sum of lines after deleting one line)
        self.flush()
        self.modified(self._fields, before=True)

        with self.env.norecompute():
            cr = self._cr

            for sub_ids in cr.split_for_in_conditions(self.ids):
                query = "DELETE FROM %s WHERE id IN %%s" % 'res_users'
                cr.execute(query, (sub_ids, ))
        #
        self.invalidate_cache()
        self.flush()
        # auditing: deletions are infrequent and leave no trace in the database
        _unlink.info('User #%s deleted %s records with IDs: %r', self._uid, self._name, self.ids)
        return True
