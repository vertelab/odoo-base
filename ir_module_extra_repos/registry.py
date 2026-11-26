import os
import logging
import threading
import odoo

from odoo.modules.registry import Registry, _REGISTRY_CACHES
from contextlib import closing, contextmanager
from collections import defaultdict, deque
from odoo.tools import config, lazy_classproperty
from odoo.tools.misc import Collector, OrderedSet
# 18.0 keeps lazy_property in odoo.tools; 19.0 dropped it.
from odoo.tools import lazy_property  # noqa: F401
from odoo.tools.lru import LRU

_logger = logging.getLogger(__name__)


def init(self, db_name):
    """
    Override of Registry's init method with custom functionality.
    Inherits all original functionality and adds custom features.
    """
    self.models = {}  # model name/model instance mapping
    self._sql_constraints = set()
    self._init = True
    self._database_translated_fields = ()  # names of translated fields in database
    self._assertion_report = odoo.tests.result.OdooTestResult()
    self._fields_by_model = None
    self._ordinary_tables = None
    self._constraint_queue = deque()

    # Initialize caches with correct name mangling
    self._Registry__caches = {cache_name: LRU(cache_size) for cache_name, cache_size in _REGISTRY_CACHES.items()}

    # Module loading state
    self._init_modules = set()
    self.updated_modules = []
    self.loaded_xmlids = set()

    # Database connection
    self.db_name = db_name
    self._db = odoo.sql_db.db_connect(db_name)

    # Check for database-specific addons directory
    addons_data_parent = os.path.dirname(odoo.tools.config.addons_data_dir)
    db_addons_path = os.path.join(addons_data_parent, self.db_name)
    if os.path.exists(db_addons_path):
        _logger.info("Found database-specific addons directory: %s", db_addons_path)
        odoo.addons.__path__.append(db_addons_path)

    # Test mode attributes
    self.test_cr = None
    self.test_lock = None

    # Registry state
    self.loaded = False
    self.ready = False

    # Field dependencies
    self.field_depends = Collector()
    self.field_depends_context = Collector()
    self.field_inverses = Collector()

    # Cache for field triggers
    self._field_trigger_trees = {}
    self._is_modifying_relations = {}

    # Inter-process signaling
    self.registry_sequence = None
    self.cache_sequences = {}

    # Thread-local invalidation flags
    self._invalidation_flags = threading.local()

    with closing(self.cursor()) as cr:
        self.has_unaccent = odoo.modules.db.has_unaccent(cr)
        self.has_trigram = odoo.modules.db.has_trigram(cr)


# Monkey patch the Registry class
Registry.init = init
