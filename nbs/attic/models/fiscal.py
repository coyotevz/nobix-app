# -*- coding: utf-8 -*-

from nbs.models import db


class FiscalData(db.Model):
    __tablename__ = 'fiscal_data'

    FISCAL_CONSUMIDOR_FINAL = 'FISCAL_CONSUMIDOR_FINAL'
    FISCAL_RESPONSABLE_INSCRIPTO = 'FISCAL_RESPONSABLE_INSCRIPTO'
    FISCAL_EXCENTO = 'FISCAL_EXCENTO'
    FISCAL_MONOTRIBUTO = 'FISCAL_MONOTRIBUTO'

    _fiscal_types = {
        FISCAL_CONSUMIDOR_FINAL: 'Consumidor Final',
        FISCAL_RESPONSABLE_INSCRIPTO: 'Responsable Inscripto',
        FISCAL_EXCENTO: 'Excento',
        FISCAL_MONOTRIBUTO: 'Monotributo',
    }

    id = db.Column(db.Integer, primary_key=True)
    cuit = db.Column(db.Unicode(13))
    fiscal_type = db.Column(db.Enum(*_fiscal_types.keys(),
                                    name='fiscal_type_enum'),
                            default=FISCAL_CONSUMIDOR_FINAL)

    @property
    def fiscal_type_str(self):
        return self._fiscal_types.get(self.fiscal_type, 'Unknown')

    @property
    def needs_cuit(self):
        return self.fiscal_type in (self.FISCAL_EXCENTO,
                                    self.FISCAL_RESPONSABLE_INSCRIPTO)

    def __repr__(self):
        return "<FiscaData '{} {}' of '{}'>".format(
                self.fiscal_type_str,
                self.cuit,
                self.supplier.name
        )
