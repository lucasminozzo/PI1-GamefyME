import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


## Validator para requisitos de senha  RF 01 - RN 6 -  A senha deve ter no mínimo 6 caracteres,
##                                                     pelo menos uma letra maiúscula e um caractere especial.
class RequisitosSenhaValidator:
    def validate(self, password, user=None):
        if len(password) < 6:
            raise ValidationError(
                _("A senha deve ter no mínimo 6 caracteres."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra maiúscula."),
                code='password_no_upper',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um caractere especial."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Sua senha deve conter no mínimo 6 caracteres, incluindo uma letra maiúscula e um caractere especial."
        )