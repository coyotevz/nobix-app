# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

BaseModel = db.Model

KNOWN_MEMBERS = ('query', 'to_dict', 'default_fields', 'hidden_fields',
                 'query_class', 'metadata')
class Model(BaseModel):

    __abstract__ = True

    def to_dict(self, show=None, hide=None, path=None, show_all=False):

        if not show:
            show = []
        if not hide:
            hide = []
        hidden = []
        if hasattr(self, 'hidden_fields'):
            hidden = self.hidden_fields
        default = []
        if hasattr(self, 'default_fields'):
            default = self.default_fields

        ret_data = {}

        if not path:
            path = self.__tablename__.lower()
            def prepend_path(item):
                item = item.lower()
                if item.split('.', 1)[0] == path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != '.':
                    item = '.%s' % item
                item = '%s%s' % (path, item)
                return item
            show[:] = [prepend_path(x) for x in show]
            hide[:] = [prepend_path(x) for x in hide]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        for key in columns:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or key is 'id' or check in show or key in default:
                ret_data[key] = getattr(self, key)

        for key in relationships:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                hide.append(check)
                is_list = self.__mapper__.relationship[key].uselist
                if is_list:
                    rel_data[key] = []
                    for item in getattr(self, key):
                        ret_data[key].append(item.to_dict(
                            show=show,
                            hide=hide,
                            path=('%s.%s' % (path, key.lower())),
                            show_all=show_all,
                        ))
                else:
                    if self.__mapper__.relationship[key].query_class is not None:
                        ret_data[key] = getattr(self, key).to_dict(
                                show=show,
                                hide=hide,
                                path=('%s.%s' % (path, key.lower())),
                                show_all=show_all,
                        )
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith('_'):
                continue
            if key in KNOWN_MEMBERS:
                continue
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                val = getattr(self, key)
                if isinstance(getattr(type(self), key), property):
                    ret_data[key] = val
                else:
                    # FIXME: unefficient way to check for properties
                    try:
                        ret_data[key] = json.loads(json.dumps(val))
                    except:
                        pass

        return ret_data

db.Model = Model

def configure_db(app):
    db.init_app(app)


from nbs.models.supplier import Supplier
